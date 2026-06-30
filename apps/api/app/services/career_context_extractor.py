import json
import os
import re
import urllib.error
import urllib.request
from typing import Optional

from app.schemas import (
    CareerContextExtractionMode,
    CareerContextExtractionResponse,
    CareerContextUpdateRequest,
    ConfidenceLabel,
)

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

COMMON_CORE_SKILLS = {
    "python",
    "typescript",
    "javascript",
    "fastapi",
    "react",
    "next.js",
    "node",
    "sql",
    "postgres",
    "analytics",
    "product",
    "leadership",
    "communication",
    "strategy",
    "project management",
}

COMMON_TECH_STACK = {
    "python",
    "fastapi",
    "react",
    "next.js",
    "typescript",
    "javascript",
    "node",
    "postgres",
    "mysql",
    "sqlite",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "terraform",
    "pandas",
    "numpy",
}

INDUSTRY_KEYWORDS = {
    "saas": "SaaS",
    "fintech": "Fintech",
    "health": "Healthcare",
    "healthcare": "Healthcare",
    "edtech": "EdTech",
    "ecommerce": "Ecommerce",
    "b2b": "B2B",
    "marketplace": "Marketplace",
    "ai": "AI",
}


def _normalize_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _extract_headline(lines: list[str]) -> str:
    if not lines:
        return ""
    first = lines[0]
    if len(first) <= 120:
        return first
    return ""


def _extract_target_roles(text: str) -> list[str]:
    patterns = [
        r"(?:target role|target roles|seeking|looking for)[:\-]\s*([^\n]+)",
        r"(?:experience as|worked as)\s+([^\n,.]+)",
    ]
    roles: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            for item in re.split(r"[,/|]", match):
                role = item.strip()
                if role and role.lower() not in {value.lower() for value in roles}:
                    roles.append(role)
    return roles[:6]


def _extract_skills(text: str, vocab: set[str]) -> list[str]:
    lowered = text.lower()
    found = [item for item in sorted(vocab) if item in lowered]
    return found[:12]


def _extract_project_highlights(lines: list[str]) -> list[str]:
    highlights: list[str] = []
    action_words = ("built", "led", "shipped", "designed", "improved", "launched", "delivered")
    for line in lines:
        if len(line) < 24:
            continue
        if any(word in line.lower() for word in action_words):
            highlights.append(line)
        if len(highlights) >= 5:
            break
    return highlights


def _extract_industries(text: str) -> list[str]:
    lowered = text.lower()
    industries = [value for key, value in INDUSTRY_KEYWORDS.items() if key in lowered]
    deduped: list[str] = []
    for item in industries:
        if item not in deduped:
            deduped.append(item)
    return deduped[:6]


def _extract_location_preferences(text: str) -> list[str]:
    lowered = text.lower()
    prefs: list[str] = []
    if "remote" in lowered:
        prefs.append("Remote")
    if "hybrid" in lowered:
        prefs.append("Hybrid")
    if "onsite" in lowered or "on-site" in lowered:
        prefs.append("Onsite")
    location_match = re.search(r"(?:based in|location)[:\-]?\s*([^\n,]+)", text, flags=re.IGNORECASE)
    if location_match:
        loc = location_match.group(1).strip()
        if loc and loc not in prefs:
            prefs.append(loc)
    return prefs[:4]


def _extract_visa_notes(text: str) -> str:
    match = re.search(
        r"([^\n]{0,80}(visa|sponsorship|work authorization)[^\n]{0,120})",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return ""
    return match.group(1).strip()


def _infer_opportunity_types(text: str) -> list[str]:
    lowered = text.lower()
    inferred: list[str] = []
    mapping = [
        ("job", "job"),
        ("client", "client"),
        ("consult", "client"),
        ("contract", "client"),
        ("collabor", "collaborator"),
        ("referral", "referrer"),
        ("content", "content"),
        ("recruit", "recruiter"),
        ("founder", "founder"),
        ("service", "professional_service"),
    ]
    for keyword, value in mapping:
        if keyword in lowered and value not in inferred:
            inferred.append(value)
    return inferred[:5]


def _extract_positioning_statement(lines: list[str], fallback_skills: list[str]) -> str:
    for line in lines:
        if len(line) < 30 or len(line) > 220:
            continue
        lowered = line.lower()
        if " i " in f" {lowered} " or lowered.startswith("i "):
            return line
    if fallback_skills:
        return f"Focus on practical outcomes with {', '.join(fallback_skills[:3])}."
    return ""


def _extract_proof_points(lines: list[str]) -> list[str]:
    proof_points: list[str] = []
    for line in lines:
        if len(line) < 18:
            continue
        if re.search(r"\b\d+%\b|\b\d+x\b|\b\$\d+", line):
            proof_points.append(line)
        if len(proof_points) >= 5:
            break
    return proof_points


def _missing_fields(context: CareerContextUpdateRequest) -> list[str]:
    missing: list[str] = []
    if not context.current_headline:
        missing.append("current_headline")
    if not context.target_roles:
        missing.append("target_roles")
    if not context.core_skills:
        missing.append("core_skills")
    if not context.technical_stack:
        missing.append("technical_stack")
    if not context.project_highlights:
        missing.append("project_highlights")
    if not context.positioning_statement:
        missing.append("positioning_statement")
    if not context.proof_points:
        missing.append("proof_points")
    return missing


def _confidence(raw_cv_text: str, missing_fields: list[str]) -> ConfidenceLabel:
    if len(raw_cv_text.strip()) < 200 or len(missing_fields) >= 6:
        return ConfidenceLabel.low
    if len(missing_fields) >= 3:
        return ConfidenceLabel.medium
    return ConfidenceLabel.high


def _local_extract(raw_cv_text: str, mode: CareerContextExtractionMode) -> CareerContextExtractionResponse:
    lines = _normalize_lines(raw_cv_text)
    core_skills = _extract_skills(raw_cv_text, COMMON_CORE_SKILLS)
    technical_stack = _extract_skills(raw_cv_text, COMMON_TECH_STACK)

    context = CareerContextUpdateRequest(
        current_headline=_extract_headline(lines),
        target_roles=_extract_target_roles(raw_cv_text),
        core_skills=core_skills,
        technical_stack=technical_stack,
        project_highlights=_extract_project_highlights(lines),
        industries=_extract_industries(raw_cv_text),
        location_preferences=_extract_location_preferences(raw_cv_text),
        visa_notes=_extract_visa_notes(raw_cv_text),
        preferred_opportunity_types=_infer_opportunity_types(raw_cv_text),
        positioning_statement=_extract_positioning_statement(lines, core_skills),
        proof_points=_extract_proof_points(lines),
        raw_cv_text=raw_cv_text,
    )

    missing = _missing_fields(context)
    warnings: list[str] = []
    if len(raw_cv_text.strip()) < 300:
        warnings.append("Input CV text is brief; extraction may be incomplete.")
    if missing:
        warnings.append("Some fields need manual completion before saving.")
    warnings.append("Reframe real experience only. Do not invent or exaggerate claims.")

    return CareerContextExtractionResponse(
        suggested_career_context=context,
        extraction_confidence=_confidence(raw_cv_text, missing),
        missing_fields=missing,
        review_warnings=warnings,
        reasoning_summary=(
            "Local deterministic extraction used keyword and pattern matching. Review every field before saving."
        ),
        extraction_mode_used=mode,
        ai_used=False,
    )


def _openai_extract(raw_cv_text: str) -> Optional[CareerContextExtractionResponse]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    prompt = (
        "Extract structured career context from CV text. "
        "Do not invent experience, titles, skills, metrics, or industries. "
        "If uncertain, leave fields empty and add a review warning. "
        "Return strict JSON with keys: suggested_career_context, extraction_confidence, "
        "missing_fields, review_warnings, reasoning_summary, extraction_mode_used, ai_used. "
        "suggested_career_context keys must be: current_headline, target_roles, core_skills, technical_stack, "
        "project_highlights, industries, location_preferences, visa_notes, preferred_opportunity_types, "
        "positioning_statement, proof_points, raw_cv_text. "
        "Set extraction_mode_used to ai_assisted and ai_used to true. "
        f"CV text: {raw_cv_text}"
    )

    body = {
        "model": os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You produce conservative, review-first structured extraction. "
                    "No fabricated content."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    req = urllib.request.Request(
        OPENAI_CHAT_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        model = CareerContextExtractionResponse(**parsed)
        return model
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
    ):
        return None


def extract_career_context(
    raw_cv_text: str,
    extraction_mode: CareerContextExtractionMode,
) -> CareerContextExtractionResponse:
    text = raw_cv_text.strip()
    if extraction_mode == CareerContextExtractionMode.ai_assisted:
        ai_result = _openai_extract(text)
        if ai_result is not None:
            ai_result.suggested_career_context.raw_cv_text = text
            if "Reframe real experience only. Do not invent or exaggerate claims." not in ai_result.review_warnings:
                ai_result.review_warnings.append(
                    "Reframe real experience only. Do not invent or exaggerate claims."
                )
            return ai_result
        fallback = _local_extract(text, CareerContextExtractionMode.local)
        fallback.review_warnings.append(
            "AI-assisted extraction unavailable (missing key or request failed). Local extraction used instead."
        )
        return fallback

    return _local_extract(text, CareerContextExtractionMode.local)
