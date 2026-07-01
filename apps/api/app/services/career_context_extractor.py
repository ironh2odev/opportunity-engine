import json
import os
import re
import urllib.error
import urllib.request
from io import BytesIO
from typing import Optional

from docx import Document
from pypdf import PdfReader

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

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "profile_summary": (
        "profile summary",
        "summary",
        "professional summary",
        "profile",
        "about",
    ),
    "projects": ("projects", "key projects", "selected projects", "project experience"),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment history",
    ),
    "education": ("education", "academic background", "qualifications"),
    "skills": (
        "skills",
        "technical skills",
        "technical proficiency",
        "tech stack",
    ),
    "languages": ("languages", "spoken languages"),
    "job_related_abilities": (
        "job related abilities",
        "abilities",
        "core competencies",
        "competencies",
        "strengths",
    ),
}

TECH_PATTERN_MAP: tuple[tuple[str, str], ...] = (
    (r"\bpython\b", "Python"),
    (r"\bfastapi\b", "FastAPI"),
    (r"\bnext\.?js\b", "Next.js"),
    (r"\btypescript\b", "TypeScript"),
    (r"\bjavascript\b", "JavaScript"),
    (r"\breact\b", "React"),
    (r"\bdocker\b", "Docker"),
    (r"\bkubernetes\b", "Kubernetes"),
    (r"\bpostgres(?:ql)?\b", "PostgreSQL"),
    (r"\bsql\b", "SQL"),
    (r"\baws\b", "AWS"),
    (r"\bazure\b", "Azure"),
    (r"\bgcp\b", "GCP"),
    (r"\bterraform\b", "Terraform"),
    (r"\bredis\b", "Redis"),
    (r"\bnode\.?js\b", "Node.js"),
    (r"\bllm\b", "LLM"),
)

SOFT_SKILL_KEYWORDS: tuple[str, ...] = (
    "communication",
    "leadership",
    "mentoring",
    "collaboration",
    "teamwork",
    "problem solving",
    "stakeholder management",
    "ownership",
    "adaptability",
    "presentation",
    "client communication",
    "analytical thinking",
)

ROLE_PATTERN = re.compile(
    r"\b(?:senior|lead|principal|staff|founding|junior)?\s*"
    r"(?:software|backend|front(?:-| )?end|full(?:-| )?stack|platform|ai|ml|data|product|cloud|devops|web)\s+"
    r"(?:engineer|developer|architect|manager|consultant|specialist)\b",
    flags=re.IGNORECASE,
)


def _extract_pdf_text(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
        chunks: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                chunks.append(page_text.strip())
        return "\n".join(chunks)
    except Exception as exc:
        raise ValueError("Could not read PDF file. Ensure the file is valid and not encrypted.") from exc


def _extract_docx_text(content: bytes) -> str:
    try:
        doc = Document(BytesIO(content))
        chunks = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n".join(chunks)
    except Exception as exc:
        raise ValueError("Could not read DOCX file. Ensure the file is valid and not corrupted.") from exc


def extract_text_from_uploaded_file(file_name: str, content: bytes) -> str:
    lower_name = file_name.lower()
    if lower_name.endswith(".txt"):
        return content.decode("utf-8", errors="replace")
    if lower_name.endswith(".pdf"):
        return _extract_pdf_text(content)
    if lower_name.endswith(".docx"):
        return _extract_docx_text(content)
    raise ValueError("Unsupported file type. Supported types: .txt, .pdf, .docx")


def _normalize_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _canonical_section_heading(line: str) -> Optional[str]:
    normalized = " ".join(re.sub(r"[^a-z ]", " ", line.lower()).split())
    if not normalized:
        return None
    for canonical, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if normalized == alias or normalized.startswith(f"{alias} "):
                return canonical
    return None


def _split_sections(raw_cv_text: str) -> tuple[list[str], dict[str, list[str]]]:
    header: list[str] = []
    sections = {key: [] for key in SECTION_ALIASES.keys()}
    current: Optional[str] = None

    for raw_line in raw_cv_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        section = _canonical_section_heading(line.rstrip(":"))
        if section is not None:
            current = section
            continue

        if current is None:
            header.append(line)
        else:
            sections[current].append(line)

    return header, sections


def _looks_like_contact_line(line: str) -> bool:
    lowered = line.lower()
    return any(
        marker in lowered
        for marker in ("@", "http", "linkedin", "github", "portfolio", "+", "phone", "email")
    )


def _extract_full_name(header_lines: list[str]) -> str:
    pattern = re.compile(r"^[A-Z][A-Za-z'`.-]+(?:\s+[A-Z][A-Za-z'`.-]+){1,3}$")
    for line in header_lines[:5]:
        if _looks_like_contact_line(line) or any(ch.isdigit() for ch in line):
            continue
        if pattern.match(line.strip()):
            return line.strip()
    return ""


def _extract_headline(header_lines: list[str], full_name: str) -> str:
    for line in header_lines[:8]:
        line = line.strip()
        if not line or line == full_name or _looks_like_contact_line(line):
            continue
        if 3 <= len(line.split()) <= 14 and len(line) <= 120:
            return line
    return ""


def _summary_text(header_lines: list[str], sections: dict[str, list[str]], full_name: str, headline: str) -> str:
    summary_lines = sections.get("profile_summary", [])
    if summary_lines:
        return " ".join(summary_lines)

    fallback: list[str] = []
    for line in header_lines[1:8]:
        if line in {full_name, headline} or _looks_like_contact_line(line):
            continue
        fallback.append(line)
    return " ".join(fallback[:4])


def _extract_target_roles(text: str) -> list[str]:
    roles: list[str] = []
    for match in ROLE_PATTERN.findall(text):
        cleaned = " ".join(match.split())
        formatted = cleaned.title().replace("Ai", "AI").replace("Ml", "ML").replace("Devops", "DevOps")
        if formatted.lower() not in {item.lower() for item in roles}:
            roles.append(formatted)
    return roles


def _extract_skills(text: str, vocab: set[str]) -> list[str]:
    lowered = text.lower()
    found = [item for item in sorted(vocab) if item in lowered]
    return found[:12]


def _extract_technical_stack(section_text: str) -> list[str]:
    found: list[str] = []
    lowered = section_text.lower()
    for pattern, canonical in TECH_PATTERN_MAP:
        if re.search(pattern, lowered) and canonical not in found:
            found.append(canonical)
    return found


def _extract_soft_skills(section_text: str) -> list[str]:
    lowered = section_text.lower()
    found: list[str] = []
    for keyword in SOFT_SKILL_KEYWORDS:
        if keyword in lowered:
            found.append(keyword.title())
    return found


def _extract_project_highlights(lines: list[str]) -> list[str]:
    highlights: list[str] = []
    action_words = (
        "built",
        "led",
        "shipped",
        "designed",
        "improved",
        "launched",
        "delivered",
        "deployed",
        "implemented",
        "optimized",
    )
    for line in lines:
        if len(line) < 24:
            continue
        lowered = line.lower()
        is_bullet = lowered.startswith(("-", "*", "•"))
        if any(word in lowered for word in action_words) or is_bullet:
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


def _extract_project_titles(project_lines: list[str]) -> list[str]:
    titles: list[str] = []
    for line in project_lines:
        stripped = line.strip("-•* ").strip()
        if not stripped or len(stripped) > 90:
            continue
        if re.search(r"\b(project|platform|portal|engine|system|dashboard|api)\b", stripped, re.IGNORECASE):
            titles.append(stripped)
        if len(titles) >= 5:
            break
    return titles


def _infer_roles_from_stack(technical_stack: list[str]) -> list[str]:
    inferred: list[str] = []
    lowered = {item.lower() for item in technical_stack}
    if {"python", "fastapi"}.intersection(lowered):
        inferred.append("Backend Engineer")
    if {"next.js", "typescript", "react"}.intersection(lowered):
        inferred.append("Frontend Engineer")
    if {"python", "fastapi"}.intersection(lowered) and {"next.js", "typescript", "react"}.intersection(lowered):
        inferred.insert(0, "Full Stack Engineer")
    if {"docker", "kubernetes", "aws", "azure", "gcp"}.intersection(lowered):
        inferred.append("Platform Engineer")
    if {"llm", "ai"}.intersection(lowered):
        inferred.append("AI Engineer")
    return inferred


def _extract_proof_points(lines: list[str]) -> list[str]:
    proof_points: list[str] = []
    action_markers = (
        "built",
        "launched",
        "deployed",
        "delivered",
        "implemented",
        "improved",
        "optimized",
        "reduced",
        "increased",
        "shipped",
    )
    for line in lines:
        if len(line) < 18:
            continue
        lowered = line.lower()
        has_metric = bool(re.search(r"\b\d+%\b|\b\d+x\b|\b\$\d+|\b\d+\+?\s+(?:teams|users|clients|projects)\b", line))
        has_action = any(marker in lowered for marker in action_markers)
        if has_metric or has_action:
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
    header_lines, sections = _split_sections(raw_cv_text)
    full_name = _extract_full_name(header_lines)
    headline = _extract_headline(header_lines, full_name)
    summary = _summary_text(header_lines, sections, full_name, headline)

    project_titles = _extract_project_titles(sections.get("projects", []))
    stack_sources = "\n".join(
        sections.get("projects", [])
        + sections.get("skills", [])
        + sections.get("experience", [])
        + [raw_cv_text]
    )
    technical_stack = _extract_technical_stack(stack_sources)
    if not technical_stack:
        technical_stack = _extract_skills(raw_cv_text, COMMON_TECH_STACK)

    soft_sources = "\n".join(
        sections.get("profile_summary", [])
        + sections.get("job_related_abilities", [])
        + sections.get("experience", [])
        + sections.get("languages", [])
    )
    core_skills = _extract_soft_skills(soft_sources)
    if not core_skills:
        # Fallback to non-technical general skills only.
        fallback = [item for item in _extract_skills(raw_cv_text, COMMON_CORE_SKILLS) if item not in {s.lower() for s in technical_stack}]
        core_skills = [item.title() for item in fallback]

    role_sources = "\n".join(
        [headline, summary, " ".join(project_titles), " ".join(technical_stack), raw_cv_text]
    )
    target_roles = _extract_target_roles(role_sources)
    for inferred in _infer_roles_from_stack(technical_stack):
        if inferred.lower() not in {item.lower() for item in target_roles}:
            target_roles.append(inferred)

    highlight_lines = sections.get("projects", []) + sections.get("experience", [])
    project_highlights = _extract_project_highlights(highlight_lines)
    proof_points = _extract_proof_points(project_highlights)
    if not proof_points:
        proof_points = _extract_proof_points(lines)

    combined_for_location = "\n".join(header_lines + sections.get("profile_summary", []))

    context = CareerContextUpdateRequest(
        current_headline=headline,
        target_roles=target_roles[:8],
        core_skills=core_skills,
        technical_stack=technical_stack,
        project_highlights=project_highlights,
        industries=_extract_industries(raw_cv_text),
        location_preferences=_extract_location_preferences(combined_for_location),
        visa_notes=_extract_visa_notes(raw_cv_text),
        preferred_opportunity_types=_infer_opportunity_types(raw_cv_text),
        positioning_statement=_extract_positioning_statement(_normalize_lines(summary) or lines, technical_stack),
        proof_points=proof_points,
        raw_cv_text=raw_cv_text,
    )

    missing = _missing_fields(context)
    warnings: list[str] = []
    if len(raw_cv_text.strip()) < 300:
        warnings.append("Input CV text is brief; extraction may be incomplete.")
    section_count = sum(1 for value in sections.values() if value)
    if section_count < 2:
        warnings.append("CV section structure is limited; some fields may require manual edits.")
    if missing:
        warnings.append("Some fields need manual completion before saving.")
    if not full_name:
        warnings.append("Could not confidently extract full name from document header.")
    if not target_roles:
        warnings.append("Could not confidently infer target roles; please review manually.")
    if not context.proof_points:
        warnings.append("Could not find clear measurable proof points; add at least one verified outcome.")
    warnings.append("Reframe real experience only. Do not invent or exaggerate claims.")

    return CareerContextExtractionResponse(
        extracted_full_name=full_name,
        suggested_career_context=context,
        extraction_confidence=_confidence(raw_cv_text, missing),
        missing_fields=missing,
        review_warnings=warnings,
        reasoning_summary=(
            "Local deterministic extraction used section-aware parsing of header, summary, projects, experience, skills, education, languages, and abilities. Review every field before saving."
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
    full_name = _extract_full_name(_normalize_lines(text)[:6])
    if extraction_mode == CareerContextExtractionMode.ai_assisted:
        ai_result = _openai_extract(text)
        if ai_result is not None:
            ai_result.suggested_career_context.raw_cv_text = text
            if not ai_result.extracted_full_name:
                ai_result.extracted_full_name = full_name
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
