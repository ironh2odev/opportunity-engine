import json
import os
import re
import urllib.error
import urllib.request
from typing import Optional

from app.schemas import (
    CaptureRecommendedAction,
    CaptureSourceType,
    CareerContext,
    CapturedLeadSuggestion,
    ConfidenceLabel,
    ExtractFromTextRequest,
    ExtractFromTextResponse,
)

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

ALLOWED_SOURCE_TYPES = {item.value for item in CaptureSourceType}

COMMON_SKILLS = {
    "python",
    "fastapi",
    "react",
    "next.js",
    "typescript",
    "sql",
    "postgres",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "machine learning",
    "ai",
    "llm",
    "prompt",
    "analytics",
    "growth",
    "sales",
    "revops",
}


def _extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def _extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s)\]]+", text)


def _extract_linkedin(urls: list[str]) -> str:
    for url in urls:
        if "linkedin.com" in url.lower():
            return url
    return ""


def _extract_name(text: str) -> str:
    patterns = [
        r"(?:hiring manager|contact|recruiter)[:\-]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"(?:posted by|author)[:\-]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_org(text: str) -> str:
    patterns = [
        r"(?:company|organization|organisation)[:\-]\s*([^\n,]+)",
        r"(?:at|with)\s+([A-Z][A-Za-z0-9& .-]{2,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _extract_role(text: str) -> str:
    patterns = [
        r"(?:role|position|title)[:\-]\s*([^\n,]+)",
        r"(?:hiring for|looking for)\s+([^\n,.]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _extract_location(text: str) -> str:
    patterns = [
        r"(?:location|based in)[:\-]?\s*([^\n,]+)",
        r"\b(remote|hybrid|onsite)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _infer_relationship_strength(source_type: str) -> str:
    if source_type in {CaptureSourceType.recruiter_message.value, CaptureSourceType.personal_notes.value}:
        return "warm"
    return "cold"


def _infer_priority(fit_score: int) -> str:
    if fit_score >= 8:
        return "high"
    if fit_score >= 5:
        return "medium"
    return "low"


def _extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = [skill for skill in COMMON_SKILLS if skill in lowered]
    found.sort()
    return found


def _match_skills(extracted_skills: list[str], career_context: CareerContext) -> tuple[list[str], list[str]]:
    context_skills = {item.lower() for item in career_context.core_skills + career_context.technical_stack}
    matched = [skill for skill in extracted_skills if skill.lower() in context_skills]
    gaps = [skill for skill in context_skills if skill not in {item.lower() for item in extracted_skills}]
    return matched, sorted(gaps)[:6]


def _fit_score(matched: list[str], gaps: list[str], use_career_context: bool, has_context: bool) -> int:
    if not use_career_context or not has_context:
        return 5
    score = 4 + min(len(matched), 5)
    score -= min(len(gaps), 3)
    return max(1, min(10, score))


def _confidence(raw_text: str, missing_fields: list[str]) -> ConfidenceLabel:
    if len(raw_text.strip()) < 120 or len(missing_fields) >= 5:
        return ConfidenceLabel.low
    if len(missing_fields) >= 3:
        return ConfidenceLabel.medium
    return ConfidenceLabel.high


def _suggested_positioning(career_context: CareerContext, matched: list[str]) -> str:
    if career_context.positioning_statement.strip():
        return career_context.positioning_statement.strip()
    if matched:
        return f"Anchor on demonstrated experience with {', '.join(matched[:3])}."
    return "Lead with one concrete result and a clear next step."


def _recommended_action(source_type: str, opportunity_type: str, fit_score: int) -> CaptureRecommendedAction:
    if fit_score <= 3:
        return CaptureRecommendedAction.research_more
    if opportunity_type == "job" or source_type == CaptureSourceType.job_listing.value:
        return CaptureRecommendedAction.apply
    if source_type == CaptureSourceType.linkedin_post.value:
        return CaptureRecommendedAction.comment
    if source_type in {CaptureSourceType.recruiter_message.value, CaptureSourceType.linkedin_profile.value}:
        return CaptureRecommendedAction.outreach
    return CaptureRecommendedAction.save


def _infer_problem(text: str) -> str:
    snippets = []
    for marker in ["pain", "challenge", "problem", "struggle", "slow", "manual"]:
        if marker in text.lower():
            snippets.append(marker)
    if not snippets:
        return ""
    return f"Observed context includes: {', '.join(sorted(set(snippets)))}."


def _to_suggestion(payload: ExtractFromTextRequest, career_context: CareerContext, extracted_skills: list[str], fit_score: int) -> CapturedLeadSuggestion:
    urls = _extract_urls(payload.raw_text)
    org_website = ""
    for url in urls:
        if "linkedin.com" not in url.lower():
            org_website = url
            break

    notes = payload.raw_text.strip()[:600]
    suggestion = CapturedLeadSuggestion(
        name=_extract_name(payload.raw_text),
        role=_extract_role(payload.raw_text),
        organisation=_extract_org(payload.raw_text),
        organisation_website=org_website,
        linkedin_url=_extract_linkedin(urls),
        email=_extract_email(payload.raw_text),
        location=_extract_location(payload.raw_text),
        source=f"capture:{payload.source_type}",
        opportunity_type=payload.user_goal,
        relationship_strength=_infer_relationship_strength(payload.source_type),
        problem_observed=_infer_problem(payload.raw_text),
        why_relevant="Potential fit based on extracted context and selected goal.",
        suggested_angle=_suggested_positioning(career_context, extracted_skills),
        notes=notes,
        tags=extracted_skills[:6],
        next_action="review and tailor first outreach draft",
        follow_up_date=None,
        fit_score=fit_score,
        priority=_infer_priority(fit_score),
    )
    return suggestion


def _missing_fields(suggestion: CapturedLeadSuggestion) -> list[str]:
    missing = []
    for field_name in [
        "name",
        "role",
        "organisation",
        "location",
        "problem_observed",
        "why_relevant",
        "next_action",
    ]:
        if not getattr(suggestion, field_name):
            missing.append(field_name)
    return missing


def _mock_extract(payload: ExtractFromTextRequest, career_context: CareerContext) -> ExtractFromTextResponse:
    extracted_skills = _extract_skills(payload.raw_text)
    has_context = any(
        [
            bool(career_context.raw_cv_text.strip()),
            len(career_context.core_skills) > 0,
            len(career_context.technical_stack) > 0,
            len(career_context.target_roles) > 0,
        ]
    )

    matched, gaps = _match_skills(extracted_skills, career_context)
    fit_score = _fit_score(matched, gaps, payload.use_career_context, has_context)
    suggestion = _to_suggestion(payload, career_context, extracted_skills, fit_score)
    missing_fields = _missing_fields(suggestion)
    warnings = []
    if payload.use_career_context and not has_context:
        warnings.append("Career context is empty; fit scoring is limited.")
    if len(payload.raw_text.strip()) < 180:
        warnings.append("Input text is brief; extraction may miss important details.")
    if missing_fields:
        warnings.append("Some important fields are missing and require manual review.")

    confidence = _confidence(payload.raw_text, missing_fields)
    recommendation = _recommended_action(payload.source_type, suggestion.opportunity_type, fit_score)

    return ExtractFromTextResponse(
        suggested_lead=suggestion,
        extraction_confidence=confidence,
        career_fit_score=fit_score,
        career_fit_reasoning=(
            "Fit score is based on overlap between extracted keywords and saved career context, then adjusted for gaps."
        ),
        matched_skills=matched,
        missing_skills_or_gaps=gaps,
        suggested_positioning_angle=_suggested_positioning(career_context, matched),
        recommended_action=recommendation,
        missing_fields=missing_fields,
        review_warnings=warnings,
        reasoning_summary=(
            "Draft-only extraction generated from pasted text with conservative assumptions and no automated actions."
        ),
    )


def _openai_extract(payload: ExtractFromTextRequest, career_context: CareerContext) -> Optional[ExtractFromTextResponse]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    prompt = (
        "Extract a conservative opportunity lead suggestion from raw text. "
        "Never invent names, companies, links, emails, skills, or claims. "
        "If unknown, return empty fields and list them in missing_fields. "
        "No auto-send, no auto-apply, no scraping, draft-only. "
        "Return strict JSON matching this schema keys: suggested_lead, extraction_confidence, career_fit_score, "
        "career_fit_reasoning, matched_skills, missing_skills_or_gaps, suggested_positioning_angle, recommended_action, "
        "missing_fields, review_warnings, reasoning_summary. "
        f"Input payload: {payload.model_dump_json()}. "
        f"Career context: {career_context.model_dump_json()}."
    )

    request_body = {
        "model": os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a conservative extraction assistant. Draft-only output. "
                    "No fabricated data and no autonomous actions."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    req = urllib.request.Request(
        OPENAI_CHAT_URL,
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = json.loads(response.read().decode("utf-8"))
        content = raw["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return ExtractFromTextResponse(**parsed)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError):
        return None


def extract_from_text(payload: ExtractFromTextRequest, career_context: CareerContext) -> ExtractFromTextResponse:
    ai_result = _openai_extract(payload, career_context)
    if ai_result is not None:
        return ai_result
    return _mock_extract(payload, career_context)
