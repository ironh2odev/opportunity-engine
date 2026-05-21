from datetime import datetime
from enum import Enum

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
