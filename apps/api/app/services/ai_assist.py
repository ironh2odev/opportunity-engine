import json
import os
import urllib.error
import urllib.request
from typing import Optional

from app.schemas import AIDraftActionRequest, AIDraftActionResponse


OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def _make_short_version(text: str, max_len: int = 200) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_len:
        return compact
    trimmed = compact[: max_len - 3].rstrip()
    return f"{trimmed}..."


def _requires_connection_limit(payload: AIDraftActionRequest) -> bool:
    if payload.channel == "connection_request":
        return True
    constraints_text = " ".join(payload.constraints).lower()
    return "200" in constraints_text and "connection" in constraints_text


def _review_notes() -> list[str]:
    return [
        "Needs refinement: tighten one claim so it is concrete and verifiable.",
        "Could be more specific: add one relevant outcome or metric.",
        "Consider grounding this with an example from actual work.",
    ]


def _job_safety_risks(payload: AIDraftActionRequest) -> list[str]:
    if payload.opportunity_type != "job" and payload.channel != "job_application":
        return []
    return [
        "Reframe real experience only; do not invent achievements.",
        "Treat CV and cover letter outputs as starting points for human editing.",
    ]


def _mock_confidence(payload: AIDraftActionRequest) -> str:
    if payload.channel in {"job_application", "outreach_dm", "connection_request"}:
        return "medium"
    return "high"


def _mock_draft(payload: AIDraftActionRequest) -> AIDraftActionResponse:
    opening = f"Hi {payload.target_name},"
    if payload.channel == "linkedin_comment":
        opening = "Appreciate this perspective"

    draft = (
        f"{opening} {payload.suggested_action} "
        f"I am keeping this concise and grounded in real outcomes, especially around {payload.target_organisation}. "
        f"Context: {payload.rationale} "
        f"Proof point to include: {payload.proof_to_reference}."
    )

    short_version: Optional[str] = None
    if _requires_connection_limit(payload):
        short_version = _make_short_version(draft, 200)
    else:
        short_version = _make_short_version(draft, 280)

    risks = [
        "Message may still be generic without one concrete reference to current context.",
        "Double-check that claims map to verifiable real work before use.",
    ]
    risks.extend(_job_safety_risks(payload))

    return AIDraftActionResponse(
        draft_message=draft,
        short_version=short_version,
        reasoning_summary=(
            "Draft emphasizes clear intent, one proof anchor, and a respectful tone while staying manual-only."
        ),
        risks_or_gaps=risks,
        confidence_label=_mock_confidence(payload),
        review_notes=_review_notes(),
    )


def _build_openai_prompt(payload: AIDraftActionRequest) -> str:
    return (
        "You are generating draft-only professional communication. "
        "Never imply automation, never send messages, and never fabricate experience. "
        "Return strict JSON with keys: draft_message, short_version, reasoning_summary, risks_or_gaps, confidence_label, review_notes. "
        "confidence_label must be low, medium, or high. "
        "review_notes must include these themes: Needs refinement, Could be more specific, Consider grounding this with an example. "
        f"Action context: {payload.model_dump_json()}"
    )


def _openai_draft(payload: AIDraftActionRequest) -> Optional[AIDraftActionResponse]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    request_body = {
        "model": os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Draft-only assistant for opportunity workflows. "
                    "No auto-send, no auto-apply, no scraping, no fabricated claims."
                ),
            },
            {"role": "user", "content": _build_openai_prompt(payload)},
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
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None

    try:
        content = raw["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        draft = AIDraftActionResponse(**parsed)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError):
        return None

    if _requires_connection_limit(payload) and draft.short_version:
        draft.short_version = _make_short_version(draft.short_version, 200)
    elif _requires_connection_limit(payload) and not draft.short_version:
        draft.short_version = _make_short_version(draft.draft_message, 200)

    if _job_safety_risks(payload):
        draft.risks_or_gaps = [*draft.risks_or_gaps, *_job_safety_risks(payload)]

    return draft


def generate_action_draft(payload: AIDraftActionRequest) -> AIDraftActionResponse:
    openai_result = _openai_draft(payload)
    if openai_result is not None:
        return openai_result
    return _mock_draft(payload)
