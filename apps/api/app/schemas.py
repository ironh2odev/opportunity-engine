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


class PersonalOpportunityType(str, Enum):
    job = "job"
    client = "client"
    collaborator = "collaborator"
    referrer = "referrer"
    content = "content"
    recruiter = "recruiter"
    founder = "founder"
    professional_service = "professional_service"


class RelationshipStrength(str, Enum):
    cold = "cold"
    warm = "warm"
    engaged = "engaged"
    connected = "connected"
    previous_client = "previous_client"
    referral = "referral"


class PersonalLeadStatus(str, Enum):
    new = "new"
    saved = "saved"
    reviewed = "reviewed"
    action_planned = "action_planned"
    contacted = "contacted"
    follow_up_due = "follow_up_due"
    archived = "archived"


class LeadPriority(str, Enum):
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
    source_type: str = "mock_demo"
    source_lead_id: Optional[str] = None
    source_lead_name: Optional[str] = None
    source_lead_organisation: Optional[str] = None
    private_mode: bool = False


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


class PersonalLead(BaseModel):
    id: str
    name: str = ""
    role: str = ""
    organisation: str = ""
    organisation_website: str = ""
    linkedin_url: str = ""
    email: str = ""
    location: str = ""
    source: str = ""
    opportunity_type: PersonalOpportunityType
    relationship_strength: RelationshipStrength
    status: PersonalLeadStatus
    fit_score: int = Field(ge=1, le=10)
    priority: LeadPriority
    problem_observed: str = ""
    why_relevant: str = ""
    suggested_angle: str = ""
    notes: str = ""
    tags: list[str] = []
    next_action: str = ""
    follow_up_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PersonalLeadCreateRequest(BaseModel):
    name: str = ""
    role: str = ""
    organisation: str = ""
    organisation_website: str = ""
    linkedin_url: str = ""
    email: str = ""
    location: str = ""
    source: str = "manual"
    opportunity_type: PersonalOpportunityType = PersonalOpportunityType.client
    relationship_strength: RelationshipStrength = RelationshipStrength.cold
    status: PersonalLeadStatus = PersonalLeadStatus.new
    fit_score: int = Field(default=5, ge=1, le=10)
    priority: LeadPriority = LeadPriority.medium
    problem_observed: str = ""
    why_relevant: str = ""
    suggested_angle: str = ""
    notes: str = ""
    tags: list[str] = []
    next_action: str = ""
    follow_up_date: Optional[str] = None


class PersonalLeadUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    organisation: Optional[str] = None
    organisation_website: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    opportunity_type: Optional[PersonalOpportunityType] = None
    relationship_strength: Optional[RelationshipStrength] = None
    status: Optional[PersonalLeadStatus] = None
    fit_score: Optional[int] = Field(default=None, ge=1, le=10)
    priority: Optional[LeadPriority] = None
    problem_observed: Optional[str] = None
    why_relevant: Optional[str] = None
    suggested_angle: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    next_action: Optional[str] = None
    follow_up_date: Optional[str] = None


class PersonalLeadCsvImportRequest(BaseModel):
    csv_text: str


class DeleteResponse(BaseModel):
    deleted: bool


class PersonalRuleAction(BaseModel):
    id: str
    source_lead_id: str
    channel: ActionChannel
    action_type: str
    suggested_action: str
    suggested_message: str
    rationale: str
    proof_to_reference: str
    status: DailyActionStatus
    approval_required: bool
    follow_up_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime
