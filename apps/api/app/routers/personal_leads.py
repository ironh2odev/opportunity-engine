import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from app import personal_store
from app.mock_data import OUTBOUND_CHANNELS, RULE_OF_100_ACTIONS
from app.schemas import (
    ActionChannel,
    DailyAction,
    DailyActionStatus,
    DeleteResponse,
    PersonalLead,
    PersonalLeadCreateRequest,
    PersonalLeadCsvImportRequest,
    PersonalLeadUpdateRequest,
)

router = APIRouter(prefix="/personal/leads", tags=["personal-leads"])


def _to_channel_from_next_action(next_action: str) -> ActionChannel:
    text = (next_action or "").strip().lower()
    if "comment" in text:
        return ActionChannel.linkedin_comment
    if "connection" in text:
        return ActionChannel.connection_request
    if "follow" in text:
        return ActionChannel.follow_up
    if "job" in text or "application" in text:
        return ActionChannel.job_application
    if "website" in text or "profile" in text or "research" in text:
        return ActionChannel.client_lead_discovery
    if "referral" in text:
        return ActionChannel.referral_request
    return ActionChannel.outreach_dm


def _to_rule_action(lead: PersonalLead) -> DailyAction:
    channel = _to_channel_from_next_action(lead.next_action)
    outbound_capable = channel in OUTBOUND_CHANNELS
    now = datetime.utcnow().replace(microsecond=0).isoformat()

    return DailyAction(
        id=f"personal_action_{lead.id}",
        date=now.split("T")[0],
        channel=channel,
        action_type="Lead-driven draft action",
        title=f"Prepare draft action for {lead.name or lead.organisation}",
        target_name=lead.name,
        target_role=lead.role,
        target_organisation=lead.organisation,
        opportunity_type="client-lead",
        source=f"Personal lead ({lead.source})",
        fit_score=lead.fit_score,
        confidence_label="medium",
        suggested_action=lead.next_action or "Review profile and prepare manual outreach draft.",
        suggested_message=(
            f"Hi {lead.name}, I reviewed your current priorities and drafted a short message tailored to {lead.organisation}."
            if outbound_capable
            else "Review this lead context and prepare a next-step note for manual execution."
        ),
        rationale=lead.why_relevant or "Lead is relevant to current opportunity priorities.",
        proof_to_reference=lead.problem_observed or "Reference one relevant outcome before sending.",
        status=DailyActionStatus.suggested,
        follow_up_date=lead.follow_up_date,
        created_at=now,
        outbound_capable=outbound_capable,
        approval_required=outbound_capable,
    )


@router.get("", response_model=list[PersonalLead])
def list_personal_leads(
    opportunity_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> list[PersonalLead]:
    return personal_store.list_leads(
        opportunity_type=opportunity_type,
        status=status,
        priority=priority,
    )


@router.post("", response_model=PersonalLead)
def create_personal_lead(payload: PersonalLeadCreateRequest) -> PersonalLead:
    try:
        return personal_store.create_lead(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{lead_id}", response_model=PersonalLead)
def get_personal_lead(lead_id: str) -> PersonalLead:
    lead = personal_store.get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=PersonalLead)
def update_personal_lead(lead_id: str, payload: PersonalLeadUpdateRequest) -> PersonalLead:
    try:
        updated = personal_store.update_lead(lead_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated


@router.delete("/{lead_id}", response_model=DeleteResponse)
def delete_personal_lead(lead_id: str) -> DeleteResponse:
    deleted = personal_store.delete_lead(lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead not found")
    return DeleteResponse(deleted=True)


@router.post("/import-csv", response_model=list[PersonalLead])
def import_personal_leads_csv(payload: PersonalLeadCsvImportRequest) -> list[PersonalLead]:
    reader = csv.DictReader(io.StringIO(payload.csv_text))
    required_columns = {
        "name",
        "role",
        "organisation",
        "organisationWebsite",
        "linkedinUrl",
        "email",
        "location",
        "source",
        "opportunityType",
        "relationshipStrength",
        "problemObserved",
        "whyRelevant",
        "suggestedAngle",
        "notes",
        "tags",
        "nextAction",
        "followUpDate",
    }

    if not required_columns.issubset(set(reader.fieldnames or [])):
        raise HTTPException(status_code=400, detail="CSV columns are invalid or missing")

    created: list[PersonalLead] = []
    for row_number, row in enumerate(reader, start=2):
        try:
            tags = [item.strip() for item in (row.get("tags") or "").split(",") if item.strip()]
            payload_model = PersonalLeadCreateRequest(
                name=(row.get("name") or "").strip(),
                role=(row.get("role") or "").strip(),
                organisation=(row.get("organisation") or "").strip(),
                organisation_website=(row.get("organisationWebsite") or "").strip(),
                linkedin_url=(row.get("linkedinUrl") or "").strip(),
                email=(row.get("email") or "").strip(),
                location=(row.get("location") or "").strip(),
                source=(row.get("source") or "csv").strip(),
                opportunity_type=(row.get("opportunityType") or "client").strip(),
                relationship_strength=(row.get("relationshipStrength") or "cold").strip(),
                problem_observed=(row.get("problemObserved") or "").strip(),
                why_relevant=(row.get("whyRelevant") or "").strip(),
                suggested_angle=(row.get("suggestedAngle") or "").strip(),
                notes=(row.get("notes") or "").strip(),
                tags=tags,
                next_action=(row.get("nextAction") or "").strip(),
                follow_up_date=(row.get("followUpDate") or "").strip() or None,
            )
            created.append(personal_store.create_lead(payload_model))
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid CSV row {row_number}: {exc}",
            ) from exc

    return created


@router.post("/{lead_id}/create-rule-action", response_model=DailyAction)
def create_rule_action_from_lead(lead_id: str) -> DailyAction:
    lead = personal_store.get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    action = _to_rule_action(lead)
    RULE_OF_100_ACTIONS.append(action)
    return action
