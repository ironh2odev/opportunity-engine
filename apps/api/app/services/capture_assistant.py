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

SKILL_ALIASES: dict[str, list[str]] = {
    "python": ["python"],
    "fastapi": ["fastapi"],
    "react": ["react", "react.js"],
    "typescript": ["typescript"],
    "llm apis": ["llm api", "llm apis", "openai api", "gpt api", "gpt-4 api"],
    "rag/context management": ["rag", "retrieval augmented generation", "context management", "vector database"],
    "product feature development": [
        "feature development",
        "product feature",
        "product features",
        "product development",
        "product engineering",
        "product systems",
        "product implementation",
        "full-stack product",
        "full stack product",
        "end-to-end feature",
        "end to end feature",
        "feature ownership",
        "built product features",
        "launched product features",
        "deployed product features",
        "mvp delivery",
        "mvp",
        "full-stack platform",
        "full stack platform",
        "platform delivery",
        "end-to-end builder",
    ],
    "full-stack engineering": ["full-stack", "full stack", "frontend and backend", "end-to-end", "end to end"],
    "kotlin/jvm": ["kotlin", "jvm"],
    "spring boot": ["spring boot", "springboot"],
    "hibernate": ["hibernate"],
    "postgresql": ["postgresql", "postgres", "postgre sql"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "langgraph": ["langgraph"],
    "owasp/security-first engineering": ["owasp", "security-first", "secure by design", "application security"],
    "german language": ["german", "deutsch"],
}

LINKEDIN_BOILERPLATE_SNIPPETS = (
    "determine your fit",
    "how to stand out",
    "ai-powered advice",
    "try premium",
    "premium for",
    "show match details",
    "tailor my resume",
    "help me stand out",
    "see how you compare",
    "over 100 others",
    "exclusive applicant insights",
    "applicant insights",
    "promoted by hirer",
    "responses managed off linkedin",
    "apply",
    "save",
)

JOB_ROLE_KEYWORDS = (
    "engineer",
    "developer",
    "manager",
    "architect",
    "lead",
    "specialist",
    "consultant",
    "analyst",
)

JOB_SECTION_HINTS = {
    "about the job",
    "deine aufgaben",
    "dein profil",
    "warum wir",
    "uber uns",
    "über uns",
}

FORBIDDEN_JOB_HEADER_CANDIDATES = {
    "about the job",
    "deine aufgaben",
    "dein profil",
    "warum wir",
    "uber uns",
    "über uns",
    "apply",
    "save",
    "premium",
    "try premium",
    "determine your fit",
    "show match details",
    "tailor my resume",
    "help me stand out",
    "responses managed off linkedin",
    "promoted by hirer",
}

WORK_MODE_TERMS = {
    "on-site": "on-site",
    "onsite": "on-site",
    "hybrid": "hybrid",
    "remote": "remote",
}

EMPLOYMENT_TERMS = {
    "full-time": "full-time",
    "full time": "full-time",
    "part-time": "part-time",
    "part time": "part-time",
    "contract": "contract",
    "internship": "internship",
    "temporary": "temporary",
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
    if re.search(r"\b(premium|try premium|apply|save)\b", text, flags=re.IGNORECASE):
        return ""
    patterns = [
        r"(?:hiring manager|contact|recruiter)[:\-]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"(?:posted by|author)[:\-]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _line_normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" \t-•|")


def _contains_phrase(text: str, phrase: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _is_linkedin_boilerplate_line(line: str) -> bool:
    lowered = line.lower()
    return any(snippet in lowered for snippet in LINKEDIN_BOILERPLATE_SNIPPETS)


def _is_forbidden_job_candidate(line: str) -> bool:
    lowered = line.lower().strip()
    if lowered in FORBIDDEN_JOB_HEADER_CANDIDATES:
        return True
    return any(snippet in lowered for snippet in LINKEDIN_BOILERPLATE_SNIPPETS)


def _dedupe_lines(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for line in lines:
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(line)
    return deduped


def _preprocess_capture_text(raw_text: str, source_type: str) -> str:
    normalized_lines = [_line_normalize(line) for line in raw_text.splitlines()]
    filtered: list[str] = []
    for line in normalized_lines:
        if not line:
            continue
        lowered = line.lower()
        if source_type == CaptureSourceType.job_listing.value and _is_linkedin_boilerplate_line(line):
            continue
        if lowered in JOB_SECTION_HINTS:
            filtered.append(line)
            continue
        if source_type == CaptureSourceType.job_listing.value and len(line) <= 2:
            continue
        filtered.append(line)
    return "\n".join(_dedupe_lines(filtered))


def _normalize_location(value: str) -> str:
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if not parts:
        return ""
    compact: list[str] = []
    seen: set[str] = set()
    for part in parts:
        key = part.lower()
        if key in seen:
            continue
        seen.add(key)
        compact.append(part)
    if len(compact) >= 3 and compact[0].lower() == compact[1].lower():
        compact = [compact[0], *compact[2:]]
    if len(compact) >= 2 and compact[-1].lower() in {"germany", "usa", "united states", "uk", "united kingdom"}:
        return f"{compact[0]}, {compact[-1]}"
    if len(compact) >= 2:
        return f"{compact[0]}, {compact[-1]}"
    return compact[0]


def _looks_like_title(line: str) -> bool:
    lowered = line.lower()
    if any(token in lowered for token in ("company:", "location:", "employment:", "work type:")):
        return False
    if len(line) < 8 or len(line) > 140:
        return False
    if lowered in JOB_SECTION_HINTS or _is_forbidden_job_candidate(line):
        return False
    return any(keyword in lowered for keyword in JOB_ROLE_KEYWORDS) or "(m/w/d)" in lowered


def _is_metadata_line(line: str) -> bool:
    lowered = line.lower()
    metadata_tokens = (
        "location:",
        "work type:",
        "employment:",
        "posted",
        "applicant",
        "responses managed",
    )
    return any(token in lowered for token in metadata_tokens)


def _clean_org_candidate(value: str) -> str:
    cleaned = _line_normalize(value)
    cleaned = re.sub(r"^company logo for,?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(company|organisation|organization)[:\-]\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+[–-]\s+.*$", "", cleaned)
    return _line_normalize(cleaned)


def _clean_location_candidate(value: str) -> str:
    cleaned = _line_normalize(value)
    cleaned = re.split(r"\s*[·•|]\s*", cleaned, maxsplit=1)[0]
    cleaned = re.sub(r"\s+(?:reposted.*|promoted by hirer.*|responses managed off linkedin.*)$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+\b(?:onsite|on-site|hybrid|remote)\b.*$", "", cleaned, flags=re.IGNORECASE)
    return _line_normalize(cleaned)


def _extract_job_location_line(line: str) -> str:
    candidate = _clean_location_candidate(line)
    if not candidate:
        return ""
    normalized = _normalize_location(candidate)
    if normalized.lower() in {"remote", "hybrid", "on-site", "onsite"}:
        return ""
    return normalized


def _looks_like_company_line(line: str) -> bool:
    lowered = line.lower()
    if _is_forbidden_job_candidate(line):
        return False
    if _is_metadata_line(line) or _looks_like_title(line):
        return False
    if any(term in lowered for term in WORK_MODE_TERMS) or any(term in lowered for term in EMPLOYMENT_TERMS):
        return False
    if any(marker in lowered for marker in ("location:", "work type:", "employment:")):
        return False
    return bool(re.search(r"[A-Za-z]", line)) and len(line) <= 100


def _extract_job_header(processed_text: str) -> dict[str, str]:
    lines = [_line_normalize(line) for line in processed_text.splitlines() if _line_normalize(line)]
    top = lines[:30]
    role = ""
    organisation = ""
    location = ""
    work_mode = ""
    employment_type = ""
    role_index = -1

    header_lines: list[str] = []
    for line in top:
        if line.lower() in JOB_SECTION_HINTS:
            break
        header_lines.append(line)
    if not header_lines:
        header_lines = top

    for idx, line in enumerate(header_lines):
        match = re.search(r"(?:role|position|title)[:\-]\s*(.+)", line, flags=re.IGNORECASE)
        if match:
            candidate = _line_normalize(match.group(1))
            if not _is_forbidden_job_candidate(candidate):
                role = candidate
                role_index = idx
                break
    if not role:
        for idx, line in enumerate(header_lines):
            if _looks_like_title(line) and not _is_forbidden_job_candidate(line):
                role = line
                role_index = idx
                break

    for line in header_lines:
        match = re.search(r"(?:company|organisation|organization)[:\-]\s*(.+)", line, flags=re.IGNORECASE)
        if match:
            candidate = _clean_org_candidate(match.group(1))
            if candidate and not _is_forbidden_job_candidate(candidate):
                organisation = candidate
                break
    if not organisation:
        for line in header_lines:
            logo_match = re.search(r"company logo for,?\s*(.+)", line, flags=re.IGNORECASE)
            if logo_match:
                candidate = _clean_org_candidate(logo_match.group(1))
                if candidate and not _is_forbidden_job_candidate(candidate):
                    organisation = candidate
                    break

    if not organisation and role_index >= 0:
        start = max(0, role_index - 3)
        end = min(len(header_lines), role_index + 4)
        for idx in range(start, end):
            if idx == role_index:
                continue
            line = header_lines[idx]
            if not _looks_like_company_line(line):
                continue
            candidate = _clean_org_candidate(line)
            if candidate and not _is_forbidden_job_candidate(candidate):
                organisation = candidate
                break

    for line in header_lines:
        location_match = re.search(r"(?:location|ort)[:\-]\s*(.+)", line, flags=re.IGNORECASE)
        if location_match:
            candidate = _extract_job_location_line(location_match.group(1))
            if candidate:
                location = candidate
                break
        if "," in line and any(country in line.lower() for country in ("germany", "united", "usa", "uk")):
            candidate = _extract_job_location_line(line)
            if candidate:
                location = candidate
                break

    for line in header_lines:
        lowered = line.lower()
        for token, canonical in WORK_MODE_TERMS.items():
            if token in lowered and not work_mode:
                work_mode = canonical
                break
        for token, canonical in EMPLOYMENT_TERMS.items():
            if token in lowered and not employment_type:
                employment_type = canonical
                break

    role = "" if _is_forbidden_job_candidate(role) else role
    organisation = "" if _is_forbidden_job_candidate(organisation) else organisation

    return {
        "role": role,
        "organisation": organisation,
        "location": location,
        "work_mode": work_mode,
        "employment_type": employment_type,
    }


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
    found: list[str] = []
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_phrase(lowered, alias) for alias in aliases):
            found.append(canonical)
    return found


def _career_context_blob(career_context: CareerContext) -> str:
    parts = [
        career_context.current_headline,
        "\n".join(career_context.target_roles),
        "\n".join(career_context.core_skills),
        "\n".join(career_context.technical_stack),
        "\n".join(career_context.project_highlights),
        "\n".join(career_context.proof_points),
        career_context.positioning_statement,
        career_context.raw_cv_text,
    ]
    return "\n".join(part for part in parts if part)


def _match_skills(extracted_requirements: list[str], career_context: CareerContext) -> tuple[list[str], list[str]]:
    if not extracted_requirements:
        return [], []
    context_skills = set(_extract_skills(_career_context_blob(career_context)))
    matched = [skill for skill in extracted_requirements if skill in context_skills]
    gaps = [skill for skill in extracted_requirements if skill not in context_skills]
    return matched, gaps


def _fit_score(matched: list[str], gaps: list[str], use_career_context: bool, has_context: bool, requirement_count: int) -> int:
    if not use_career_context or not has_context:
        return 5
    if requirement_count <= 0:
        return 5
    coverage = len(matched) / max(requirement_count, 1)
    score = int(round(3 + (coverage * 6)))
    if len(matched) >= 5:
        score += 1
    if len(gaps) >= 5:
        score -= 1
    return max(1, min(10, score))


def _confidence(raw_text: str, missing_fields: list[str]) -> ConfidenceLabel:
    if len(raw_text.strip()) < 120 or len(missing_fields) >= 5:
        return ConfidenceLabel.low
    if len(missing_fields) >= 3:
        return ConfidenceLabel.medium
    return ConfidenceLabel.high


def _suggested_positioning(career_context: CareerContext, matched: list[str], source_type: str, gaps: list[str]) -> str:
    if source_type == CaptureSourceType.job_listing.value:
        points: list[str] = []
        if any(item in matched for item in ("full-stack engineering", "product feature development")):
            points.append("Lead with AI/full-stack product implementation outcomes")
        if any(item in matched for item in ("python", "fastapi", "react", "typescript")):
            points.append("Highlight Python/FastAPI + React/TypeScript delivery")
        if any(item in matched for item in ("llm apis", "rag/context management")):
            points.append("Show LLM/RAG product systems experience with concrete impact")
        points.append("Reference one deployed project proof with measurable result")
        if any(item in gaps for item in ("kotlin/jvm", "spring boot")):
            points.append("Be explicit about an honest Kotlin/Spring Boot ramp plan")
        return ". ".join(points) + "."

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


def _fit_reasoning(requirements: list[str], matched: list[str], gaps: list[str], use_career_context: bool, has_context: bool) -> str:
    if not use_career_context:
        return "Career context matching was disabled; score is neutral until reviewed manually."
    if not has_context:
        return "Career context is empty, so fit score uses only basic extraction confidence."
    if not requirements:
        return "No clear requirements were detected in the pasted text; score is conservative."
    matched_sample = ", ".join(matched[:4]) if matched else "none"
    gaps_sample = ", ".join(gaps[:4]) if gaps else "none"
    return (
        f"Matched {len(matched)} of {len(requirements)} extracted requirements. "
        f"Matches: {matched_sample}. Gaps to evaluate: {gaps_sample}."
    )


def _to_suggestion(
    payload: ExtractFromTextRequest,
    processed_text: str,
    career_context: CareerContext,
    extracted_skills: list[str],
    fit_score: int,
    gaps: list[str],
) -> CapturedLeadSuggestion:
    urls = _extract_urls(processed_text)
    if payload.optional_source_url:
        urls = [payload.optional_source_url, *urls]

    org_website = ""
    for url in urls:
        if "linkedin.com" not in url.lower():
            org_website = url
            break

    linkedin_url = _extract_linkedin(urls)
    header = _extract_job_header(processed_text) if payload.source_type == CaptureSourceType.job_listing.value else {}

    extracted_name = ""
    if payload.source_type != CaptureSourceType.job_listing.value:
        extracted_name = _extract_name(processed_text)

    role = header.get("role", "") or _extract_role(processed_text)
    organisation = header.get("organisation", "") or _extract_org(processed_text)
    location = header.get("location", "") or _extract_location(processed_text)

    job_meta = []
    if header.get("work_mode"):
        job_meta.append(f"work mode: {header['work_mode']}")
    if header.get("employment_type"):
        job_meta.append(f"employment: {header['employment_type']}")

    notes = processed_text.strip()[:600]
    tags = extracted_skills[:6]
    if job_meta:
        notes = f"{notes}\n\nJob metadata: {', '.join(job_meta)}".strip()
        tags = [*tags, *job_meta]
    if payload.source_type == CaptureSourceType.job_listing.value:
        tags = [*tags, "linkedin"]

    why_relevant = "Potential fit based on extracted context and selected goal."
    if payload.source_type == CaptureSourceType.job_listing.value and (role or organisation):
        why_relevant = f"Role appears to be {role or 'unknown role'} at {organisation or 'unknown organisation'}; fit reviewed against captured requirements."

    next_action = "review and tailor first outreach draft"
    if payload.source_type == CaptureSourceType.job_listing.value:
        next_action = "draft tailored application summary" if fit_score >= 7 else "review and tailor application"

    suggestion = CapturedLeadSuggestion(
        name=extracted_name,
        role=role,
        organisation=organisation,
        organisation_website=org_website,
        linkedin_url=linkedin_url,
        email=_extract_email(processed_text),
        location=location,
        source=f"capture:{payload.source_type}",
        opportunity_type=payload.user_goal,
        relationship_strength=_infer_relationship_strength(payload.source_type),
        problem_observed=_infer_problem(processed_text),
        why_relevant=why_relevant,
        suggested_angle=_suggested_positioning(career_context, extracted_skills, payload.source_type, gaps),
        notes=notes,
        tags=list(dict.fromkeys(tags))[:8],
        next_action=next_action,
        follow_up_date=None,
        fit_score=fit_score,
        priority=_infer_priority(fit_score),
    )
    return suggestion


def _missing_fields(suggestion: CapturedLeadSuggestion, source_type: str) -> list[str]:
    missing = []
    required = ["role", "organisation", "location", "why_relevant", "next_action"]
    if not (suggestion.opportunity_type == "job" or source_type == CaptureSourceType.job_listing.value):
        required = ["name", *required]
    for field_name in required:
        if not getattr(suggestion, field_name):
            missing.append(field_name)
    return missing


def _mock_extract(payload: ExtractFromTextRequest, career_context: CareerContext) -> ExtractFromTextResponse:
    processed_text = _preprocess_capture_text(payload.raw_text, payload.source_type)
    extracted_skills = _extract_skills(processed_text)
    has_context = any(
        [
            bool(career_context.raw_cv_text.strip()),
            len(career_context.core_skills) > 0,
            len(career_context.technical_stack) > 0,
            len(career_context.target_roles) > 0,
        ]
    )

    matched, gaps = _match_skills(extracted_skills, career_context)
    fit_score = _fit_score(matched, gaps, payload.use_career_context, has_context, len(extracted_skills))
    suggestion = _to_suggestion(payload, processed_text, career_context, extracted_skills, fit_score, gaps)
    missing_fields = _missing_fields(suggestion, payload.source_type)
    warnings = []
    if payload.use_career_context and not has_context:
        warnings.append("Career context is empty; fit scoring is limited.")
    if len(processed_text.strip()) < 180:
        warnings.append("Input text is brief; extraction may miss important details.")
    if missing_fields:
        warnings.append("Some important fields are missing and require manual review.")

    confidence = _confidence(payload.raw_text, missing_fields)
    recommendation = _recommended_action(payload.source_type, suggestion.opportunity_type, fit_score)

    return ExtractFromTextResponse(
        suggested_lead=suggestion,
        extraction_confidence=confidence,
        career_fit_score=fit_score,
        career_fit_reasoning=_fit_reasoning(extracted_skills, matched, gaps, payload.use_career_context, has_context),
        matched_skills=matched,
        missing_skills_or_gaps=gaps,
        suggested_positioning_angle=_suggested_positioning(career_context, matched, payload.source_type, gaps),
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
