from datetime import datetime

from app.schemas import ConfidenceSignal, Opportunity, PipelineSummary, TailoringDraft


OPPORTUNITIES = [
    Opportunity(
        id="opp_1",
        title="Senior Product Engineer (AI Tooling)",
        organization="North Harbor Labs",
        source="LinkedIn",
        category="job",
        relevance_score=91,
        summary="High-growth SaaS team shipping workflow automation for revenue operations.",
        why_it_matches=(
            "Strong overlap with React platform work, AI-assisted feature delivery, and B2B dashboard systems."
        ),
        suggested_action="Draft tailored CV bullets around internal tools and measurable outcomes.",
        status="new",
        created_at=datetime.fromisoformat("2026-05-20T08:00:00"),
    ),
    Opportunity(
        id="opp_2",
        title="Fractional Growth Engineer",
        organization="Arclight Commerce",
        source="Warm intro",
        category="freelance",
        relevance_score=87,
        summary="8-week engagement for conversion funnel diagnostics and experiment velocity.",
        why_it_matches="Matches your recent growth experimentation and dashboard instrumentation work.",
        suggested_action="Send concise proposal draft with scope boundaries.",
        status="saved",
        created_at=datetime.fromisoformat("2026-05-20T10:00:00"),
    ),
]

TAILORING_DRAFTS = [
    TailoringDraft(
        id="draft_1",
        opportunity_id="opp_1",
        cv_bullets=[
            "Built internal workflow tooling used weekly by cross-functional teams.",
            "Shipped AI-assisted drafting UX with human review gates.",
        ],
        motivation_letter=(
            "I am excited by your practical approach to AI tooling and measurable product impact."
        ),
        outreach_draft=(
            "I can help accelerate feature delivery while keeping quality and trust at the center."
        ),
        project_emphasis=[
            "Workflow systems",
            "Human-in-the-loop product design",
            "Typed service contracts",
        ],
        confidence_signals=[
            ConfidenceSignal(
                label="needs-refinement",
                message="Needs refinement: add one measurable delivery outcome.",
            ),
            ConfidenceSignal(
                label="ground-with-example",
                message="Consider grounding this with an example from a recent project.",
            ),
        ],
        human_approved=False,
    )
]

PIPELINE_SUMMARY = PipelineSummary(
    total=len(OPPORTUNITIES),
    by_status={
        "new": 1,
        "reviewed": 0,
        "saved": 1,
        "contacted": 0,
        "rejected": 0,
    },
    by_category={
        "job": 1,
        "freelance": 1,
        "client-lead": 0,
        "partnership": 0,
    },
)
