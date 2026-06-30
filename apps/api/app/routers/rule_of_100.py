from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from app import personal_store
from app.mock_data import (
    APPROVAL_RECORDS,
    RULE_OF_100_ACTIONS,
    get_daily_rollup,
    get_rule_of_100_plan,
    has_approval,
    update_rule_of_100_plan,
)
from app.schemas import (
    ActionApprovalRequest,
    ActionStatusUpdateRequest,
    ApprovalRecord,
    DailyAction,
    DailyActionStatus,
    DailyRollup,
    OpportunityType,
    RuleOf100Plan,
    RuleOf100PlanUpdateRequest,
)

router = APIRouter(prefix="/rule-of-100", tags=["rule-of-100"])


def _personal_source_label(lead) -> str:
    if lead.name.strip():
        return lead.name.strip()
    if lead.organisation.strip():
        return lead.organisation.strip()
    return "Personal lead"


def _personal_opportunity_type(lead) -> OpportunityType:
    if lead.opportunity_type in {"job"}:
        return OpportunityType.job
    if lead.opportunity_type in {"content"}:
        return OpportunityType.content
    if lead.opportunity_type in {"client", "professional_service", "founder"}:
        return OpportunityType.client_lead
    return OpportunityType.networking


def _personal_action_to_daily_action(action, lead) -> DailyAction:
    created_at = action.created_at if isinstance(action.created_at, datetime) else datetime.fromisoformat(action.created_at)
    return DailyAction(
        id=action.id,
        date=created_at.date().isoformat(),
        channel=action.channel,
        action_type=action.action_type,
        title="Private lead action",
        target_name=lead.name or lead.organisation or "Personal lead",
        target_role=lead.role,
        target_organisation=lead.organisation,
        opportunity_type=_personal_opportunity_type(lead),
        source="Personal Mode",
        fit_score=lead.fit_score,
        confidence_label="medium",
        suggested_action=action.suggested_action,
        suggested_message=action.suggested_message,
        rationale=action.rationale,
        proof_to_reference=action.proof_to_reference,
        status=action.status,
        follow_up_date=action.follow_up_date,
        created_at=created_at,
        outbound_capable=action.approval_required,
        approval_required=action.approval_required,
        source_type="personal_lead",
        source_lead_id=lead.id,
        source_lead_name=_personal_source_label(lead),
        source_lead_organisation=lead.organisation or None,
        private_mode=True,
    )


def _mock_action_to_daily_action(action: DailyAction) -> DailyAction:
    action.source_type = "mock_demo"
    action.private_mode = False
    return action


def _list_personal_actions(date: Optional[str] = None) -> list[DailyAction]:
    if date is None:
        personal_actions = personal_store.list_rule_actions()
    else:
        personal_actions = personal_store.list_rule_actions_for_date(date)

    merged: list[DailyAction] = []
    for action in personal_actions:
        lead = personal_store.get_lead(action.source_lead_id)
        if lead is None:
            continue
        merged.append(_personal_action_to_daily_action(action, lead))
    return merged


def _merged_actions(date: Optional[str] = None) -> list[DailyAction]:
    mock_actions = RULE_OF_100_ACTIONS
    if date is not None:
        mock_actions = [item for item in RULE_OF_100_ACTIONS if item.date == date]

    merged = [_mock_action_to_daily_action(action) for action in mock_actions]
    merged.extend(_list_personal_actions(date))
    merged.sort(key=lambda item: item.created_at, reverse=True)
    return merged


def _find_action(action_id: str) -> tuple[str, DailyAction]:
    for action in RULE_OF_100_ACTIONS:
        if action.id == action_id:
            return "mock", _mock_action_to_daily_action(action)

    personal_action = personal_store.get_rule_action(action_id)
    if personal_action is not None:
        lead = personal_store.get_lead(personal_action.source_lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Action source lead not found")
        return "personal", _personal_action_to_daily_action(personal_action, lead)

    raise HTTPException(status_code=404, detail="Action not found")


def _has_approval(action_id: str) -> bool:
    return any(record.action_id == action_id for record in APPROVAL_RECORDS) or personal_store.has_rule_action_approval(action_id)


def _approval_record_for_personal_action(action_id: str):
    approval = personal_store.get_rule_action_approval(action_id)
    if approval is None:
        return None
    return ApprovalRecord(
        id=approval["id"],
        action_id=approval["action_id"],
        approved_by=approval["approved_by"],
        approved_at=datetime.fromisoformat(approval["approved_at"]),
        note=approval["note"],
    )


def _list_approvals() -> list[ApprovalRecord]:
    approvals = list(APPROVAL_RECORDS)
    for item in personal_store.list_rule_action_approvals():
        approvals.append(
            ApprovalRecord(
                id=item["id"],
                action_id=item["action_id"],
                approved_by=item["approved_by"],
                approved_at=datetime.fromisoformat(item["approved_at"]),
                note=item["note"],
            )
        )
    approvals.sort(key=lambda item: item.approved_at, reverse=True)
    return approvals


def _assert_completion_allowed(action: DailyAction) -> None:
    if action.approval_required and not _has_approval(action.id):
        raise HTTPException(
            status_code=409,
            detail=(
                "Outbound-capable actions require explicit human approval before completion."
            ),
        )


@router.get("/today-plan", response_model=RuleOf100Plan)
def get_today_plan() -> RuleOf100Plan:
    return get_rule_of_100_plan()


@router.patch("/today-plan", response_model=RuleOf100Plan)
def update_today_plan(payload: RuleOf100PlanUpdateRequest) -> RuleOf100Plan:
    try:
        return update_rule_of_100_plan(
            target_count=payload.target_count,
            allocation=payload.allocation,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/actions", response_model=list[DailyAction])
def get_daily_actions(date: Optional[str] = None) -> list[DailyAction]:
    return _merged_actions(date)


@router.get("/rollup", response_model=DailyRollup)
def get_rollup() -> DailyRollup:
    actions = _merged_actions()
    completed_count = len([item for item in actions if item.status == DailyActionStatus.completed])
    pending_review_count = len([item for item in actions if item.status == DailyActionStatus.in_review])
    approved_count = len([item for item in actions if item.status == DailyActionStatus.approved])
    completed_approved_count = len(
        [
            item
            for item in actions
            if item.status == DailyActionStatus.completed and (not item.approval_required or _has_approval(item.id))
        ]
    )

    by_channel: dict = {}
    for item in actions:
        by_channel[item.channel] = by_channel.get(item.channel, 0) + 1

    return DailyRollup(
        date=get_rule_of_100_plan().date,
        target_count=get_rule_of_100_plan().target_count,
        completed_count=completed_count,
        progress_percent=round((completed_count / get_rule_of_100_plan().target_count) * 100),
        pending_review_count=pending_review_count,
        approved_count=approved_count,
        completed_approved_count=completed_approved_count,
        by_channel=by_channel,
    )


@router.get("/approvals", response_model=list[ApprovalRecord])
def get_approvals() -> list[ApprovalRecord]:
    return _list_approvals()


@router.patch("/actions/{action_id}/status", response_model=DailyAction)
def update_action_status(
    action_id: str,
    payload: ActionStatusUpdateRequest,
) -> DailyAction:
    action_source, action = _find_action(action_id)

    if payload.status == DailyActionStatus.completed:
        _assert_completion_allowed(action)

    if action_source == "mock":
        for item in RULE_OF_100_ACTIONS:
            if item.id == action_id:
                item.status = payload.status
                return item
        raise HTTPException(status_code=404, detail="Action not found")

    updated = personal_store.update_rule_action_status(action_id, payload.status)
    if updated is None:
        raise HTTPException(status_code=404, detail="Action not found")
    lead = personal_store.get_lead(updated.source_lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Action source lead not found")
    return _personal_action_to_daily_action(updated, lead)


@router.post("/actions/{action_id}/approve", response_model=ApprovalRecord)
def approve_action(
    action_id: str,
    payload: Optional[ActionApprovalRequest] = None,
) -> ApprovalRecord:
    action_source, action = _find_action(action_id)

    approval_payload = payload or ActionApprovalRequest()

    if action_source == "mock":
        existing = next((record for record in APPROVAL_RECORDS if record.action_id == action_id), None)
        if existing is not None:
            for item in RULE_OF_100_ACTIONS:
                if item.id == action_id:
                    item.status = DailyActionStatus.approved
            return existing

        record = ApprovalRecord(
            id=f"approval_{len(APPROVAL_RECORDS) + 1:03d}",
            action_id=action_id,
            approved_by=approval_payload.approved_by,
            approved_at=datetime.utcnow(),
            note=approval_payload.note
            or "Approved for manual execution. No auto-send or auto-apply.",
        )
        APPROVAL_RECORDS.append(record)
        for item in RULE_OF_100_ACTIONS:
            if item.id == action_id:
                item.status = DailyActionStatus.approved
        return record

    existing = personal_store.get_rule_action_approval(action_id)
    if existing is not None:
        updated = personal_store.update_rule_action_status(action_id, DailyActionStatus.approved)
        if updated is None:
            raise HTTPException(status_code=404, detail="Action not found")
        approval_record = _approval_record_for_personal_action(action_id)
        if approval_record is None:
            raise HTTPException(status_code=404, detail="Approval not found")
        return approval_record

    record = personal_store.record_rule_action_approval(
        action_id=action_id,
        approved_by=approval_payload.approved_by,
        note=approval_payload.note or "Approved for manual execution. No auto-send or auto-apply.",
    )
    updated = personal_store.update_rule_action_status(action_id, DailyActionStatus.approved)
    if updated is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return ApprovalRecord(
        id=record["id"],
        action_id=record["action_id"],
        approved_by=record["approved_by"],
        approved_at=datetime.fromisoformat(record["approved_at"]),
        note=record["note"],
    )


@router.post("/actions/{action_id}/complete", response_model=DailyAction)
def complete_action(action_id: str) -> DailyAction:
    action_source, action = _find_action(action_id)
    _assert_completion_allowed(action)
    if action_source == "mock":
        for item in RULE_OF_100_ACTIONS:
            if item.id == action_id:
                item.status = DailyActionStatus.completed
                return item
        raise HTTPException(status_code=404, detail="Action not found")

    updated = personal_store.update_rule_action_status(action_id, DailyActionStatus.completed)
    if updated is None:
        raise HTTPException(status_code=404, detail="Action not found")
    lead = personal_store.get_lead(updated.source_lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Action source lead not found")
    return _personal_action_to_daily_action(updated, lead)
