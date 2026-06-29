from datetime import datetime

from app.schemas import (
    ActionChannel,
    ApprovalRecord,
    ConfidenceSignal,
    DailyAction,
    DailyActionStatus,
    DailyRollup,
    Opportunity,
    PipelineSummary,
    RuleOf100Plan,
    TailoringDraft,
)


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

RULE_OF_100_PLAN = RuleOf100Plan(
    id="plan_2026-06-29",
    date="2026-06-29",
    target_count=50,
    min_target=50,
    max_target=100,
    default_mode="rule_of_50",
    allocation={
        "linkedin_comment": 20,
        "client_lead_discovery": 10,
        "connection_request": 5,
        "follow_up": 5,
        "content_creation": 5,
        "outreach_dm": 3,
        "job_application": 2,
    },
    notes=(
        "Allocation is editable. Connection requests are optional and can be reduced when platform limits apply."
    ),
)

CHANNEL_SEQUENCE: list[ActionChannel] = []
for channel_name, count in RULE_OF_100_PLAN.allocation.items():
    CHANNEL_SEQUENCE.extend([channel_name] * count)

OUTBOUND_CHANNELS: set[ActionChannel] = {
    "linkedin_comment",
    "connection_request",
    "outreach_dm",
    "follow_up",
    "job_application",
    "referral_request",
}

STATUS_CYCLE: list[DailyActionStatus] = [
    "suggested",
    "in_review",
    "approved",
    "completed",
    "suggested",
    "approved",
    "in_review",
    "completed",
]

NAME_POOL = [
    "Taylor Rowan",
    "Avery Pike",
    "Jordan Vale",
    "Morgan Hale",
    "Casey Flint",
    "Riley North",
    "Parker Lane",
    "Quinn Harbor",
]

ROLE_POOL = [
    "Growth Lead",
    "RevOps Manager",
    "Product Marketing Lead",
    "Talent Partner",
    "Founder",
    "Head of Partnerships",
]

ORG_POOL = [
    "Northfield Systems",
    "Summit Relay",
    "Blue Harbor Labs",
    "Cobalt Ridge",
    "Pioneer Signal",
    "Asterline Works",
]


def _profile_for(idx: int) -> tuple[str, str, str]:
    return (
        NAME_POOL[idx % len(NAME_POOL)],
        ROLE_POOL[idx % len(ROLE_POOL)],
        ORG_POOL[idx % len(ORG_POOL)],
    )


def _channel_meta(channel: ActionChannel) -> dict[str, str]:
    mapping = {
        "linkedin_comment": {
            "action_type": "Comment draft",
            "opportunity_type": "networking",
            "source": "Mock LinkedIn Feed",
            "title": "Comment on post about AI workflow operations",
        },
        "client_lead_discovery": {
            "action_type": "Lead profile save",
            "opportunity_type": "client-lead",
            "source": "Mock Lead List",
            "title": "Save and tag RevOps prospect profile",
        },
        "connection_request": {
            "action_type": "Connection request draft",
            "opportunity_type": "networking",
            "source": "Mock Network Search",
            "title": "Draft connection request with shared context",
        },
        "follow_up": {
            "action_type": "Follow-up draft",
            "opportunity_type": "freelance",
            "source": "Mock Outreach Queue",
            "title": "Draft follow-up for prior discovery note",
        },
        "content_creation": {
            "action_type": "Content research",
            "opportunity_type": "content",
            "source": "Mock Content Backlog",
            "title": "Outline a credibility-building content post",
        },
        "outreach_dm": {
            "action_type": "Outreach DM draft",
            "opportunity_type": "client-lead",
            "source": "Mock Warm Intro Queue",
            "title": "Draft personalized outbound intro",
        },
        "job_application": {
            "action_type": "Application draft",
            "opportunity_type": "job",
            "source": "Mock Job Board",
            "title": "Draft role-specific application summary",
        },
        "referral_request": {
            "action_type": "Referral request draft",
            "opportunity_type": "networking",
            "source": "Mock Alumni Network",
            "title": "Prepare referral request with proof points",
        },
    }
    return mapping[channel]


RULE_OF_100_ACTIONS: list[DailyAction] = []
for idx, channel in enumerate(CHANNEL_SEQUENCE, start=1):
    name, role, organisation = _profile_for(idx + 1)
    meta = _channel_meta(channel)
    status = STATUS_CYCLE[(idx - 1) % len(STATUS_CYCLE)]
    outbound_capable = channel in OUTBOUND_CHANNELS

    RULE_OF_100_ACTIONS.append(
        DailyAction(
            id=f"action_{idx:03d}",
            date="2026-06-29",
            channel=channel,
            action_type=meta["action_type"],
            title=f"{meta['title']} #{idx}",
            target_name=name,
            target_role=role,
            target_organisation=organisation,
            opportunity_type=meta["opportunity_type"],
            source=meta["source"],
            fit_score=((idx - 1) % 10) + 1,
            confidence_label=(
                "high" if idx % 3 == 0 else "medium" if idx % 3 == 1 else "low"
            ),
            suggested_action=(
                f"Prepare a concise draft for {name} and keep claims grounded in measurable outcomes."
            ),
            suggested_message=(
                f"Hi {name}, I appreciated your recent perspective. I drafted a short note tailored to {organisation} and can share if useful."
                if outbound_capable
                else f"Capture three notes from {organisation} and tag one follow-up hypothesis for tomorrow."
            ),
            rationale=(
                "This action supports consistent daily opportunity creation while avoiding low-quality spam behavior."
            ),
            proof_to_reference=(
                "Reference one measurable project result and one relevant implementation example."
            ),
            status=status,
            follow_up_date="2026-07-01" if idx % 4 == 0 else None,
            created_at=datetime.fromisoformat(
                f"2026-06-29T{7 + (idx % 10):02d}:{(idx * 7) % 60:02d}:00"
            ),
            outbound_capable=outbound_capable,
            approval_required=outbound_capable,
        )
    )

APPROVAL_RECORDS: list[ApprovalRecord] = []
for idx, action in enumerate(RULE_OF_100_ACTIONS, start=1):
    if action.status in {"approved", "completed"} and action.approval_required:
        APPROVAL_RECORDS.append(
            ApprovalRecord(
                id=f"approval_{idx:03d}",
                action_id=action.id,
                approved_by="human.operator",
                approved_at=datetime.fromisoformat(
                    f"2026-06-29T15:{(idx * 5) % 60:02d}:00"
                ),
                note="Approved for manual execution. Do not auto-send.",
            )
        )


def has_approval(action_id: str) -> bool:
    return any(record.action_id == action_id for record in APPROVAL_RECORDS)


def get_daily_rollup() -> DailyRollup:
    completed_count = len([item for item in RULE_OF_100_ACTIONS if item.status == "completed"])
    pending_review_count = len([item for item in RULE_OF_100_ACTIONS if item.status == "in_review"])
    approved_count = len([item for item in RULE_OF_100_ACTIONS if item.status == "approved"])
    completed_approved_count = len(
        [
            item
            for item in RULE_OF_100_ACTIONS
            if item.status == "completed"
            and (
                not item.approval_required
                or has_approval(item.id)
            )
        ]
    )

    by_channel: dict[ActionChannel, int] = {}
    for item in RULE_OF_100_ACTIONS:
        by_channel[item.channel] = by_channel.get(item.channel, 0) + 1

    return DailyRollup(
        date=RULE_OF_100_PLAN.date,
        target_count=RULE_OF_100_PLAN.target_count,
        completed_count=completed_count,
        progress_percent=round((completed_count / RULE_OF_100_PLAN.target_count) * 100),
        pending_review_count=pending_review_count,
        approved_count=approved_count,
        completed_approved_count=completed_approved_count,
        by_channel=by_channel,
    )
