from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OpportunityCategory(str, Enum):
    job = "job"
    freelance = "freelance"
    client_lead = "client-lead"
    partnership = "partnership"


class OpportunityStatus(str, Enum):
    new = "new"
    reviewed = "reviewed"
    saved = "saved"
    contacted = "contacted"
    rejected = "rejected"


class DailyActionStatus(str, Enum):
    suggested = "suggested"
    in_review = "in_review"
    approved = "approved"
    completed = "completed"
    skipped = "skipped"
    blocked = "blocked"


class ActionChannel(str, Enum):
    linkedin_comment = "linkedin_comment"
    connection_request = "connection_request"
    outreach_dm = "outreach_dm"
    follow_up = "follow_up"
    job_application = "job_application"
    client_lead_discovery = "client_lead_discovery"
    referral_request = "referral_request"
    content_creation = "content_creation"


class OpportunityType(str, Enum):
    job = "job"
    freelance = "freelance"
    client_lead = "client-lead"
    partnership = "partnership"
    networking = "networking"
    content = "content"


class ConfidenceLabel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Opportunity(BaseModel):
    id: str
    title: str
    organization: str
    source: str
    category: OpportunityCategory
    relevance_score: int = Field(ge=0, le=100)
    summary: str
    why_it_matches: str
    suggested_action: str
    status: OpportunityStatus
    created_at: datetime


class ConfidenceSignal(BaseModel):
    label: str
    message: str


class TailoringDraft(BaseModel):
    id: str
    opportunity_id: str
    cv_bullets: list[str]
    motivation_letter: str
    outreach_draft: str
    project_emphasis: list[str]
    confidence_signals: list[ConfidenceSignal]
    human_approved: bool = False


class PipelineSummary(BaseModel):
    total: int
    by_status: dict[OpportunityStatus, int]
    by_category: dict[OpportunityCategory, int]


class RuleOf100Plan(BaseModel):
    id: str
    date: str
    target_count: int = Field(ge=50, le=100)
    min_target: int = 50
    max_target: int = 100
    default_mode: str = "rule_of_50"
    allocation: dict[ActionChannel, int]
    notes: str


class DailyAction(BaseModel):
    id: str
    date: str
    channel: ActionChannel
    action_type: str
    title: str
    target_name: str
    target_role: str
    target_organisation: str
    opportunity_type: OpportunityType
    source: str
    fit_score: int = Field(ge=1, le=10)
    confidence_label: ConfidenceLabel
    suggested_action: str
    suggested_message: str
    rationale: str
    proof_to_reference: str
    status: DailyActionStatus
    follow_up_date: Optional[str] = None
    created_at: datetime
    outbound_capable: bool = False
    approval_required: bool = False


class ApprovalRecord(BaseModel):
    id: str
    action_id: str
    approved_by: str
    approved_at: datetime
    note: Optional[str] = None


class DailyRollup(BaseModel):
    date: str
    target_count: int
    completed_count: int
    progress_percent: int
    pending_review_count: int
    approved_count: int
    completed_approved_count: int
    by_channel: dict[ActionChannel, int]


class ActionStatusUpdateRequest(BaseModel):
    status: DailyActionStatus


class ActionApprovalRequest(BaseModel):
    approved_by: str = "human.operator"
    note: Optional[str] = None


class RuleOf100PlanUpdateRequest(BaseModel):
    target_count: Optional[int] = Field(default=None, ge=50, le=100)
    allocation: Optional[dict[ActionChannel, int]] = None
