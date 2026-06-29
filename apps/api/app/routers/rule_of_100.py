from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.mock_data import (
    APPROVAL_RECORDS,
    RULE_OF_100_ACTIONS,
    RULE_OF_100_PLAN,
    get_daily_rollup,
    has_approval,
)
from app.schemas import (
    ActionApprovalRequest,
    ActionStatusUpdateRequest,
    ApprovalRecord,
    DailyAction,
    DailyActionStatus,
    DailyRollup,
    RuleOf100Plan,
)

router = APIRouter(prefix="/rule-of-100", tags=["rule-of-100"])


def _find_action(action_id: str) -> DailyAction:
    for action in RULE_OF_100_ACTIONS:
        if action.id == action_id:
            return action
    raise HTTPException(status_code=404, detail="Action not found")


def _assert_completion_allowed(action: DailyAction) -> None:
    if action.approval_required and not has_approval(action.id):
        raise HTTPException(
            status_code=409,
            detail=(
                "Outbound-capable actions require explicit human approval before completion."
            ),
        )


@router.get("/today-plan", response_model=RuleOf100Plan)
def get_today_plan() -> RuleOf100Plan:
    return RULE_OF_100_PLAN


@router.get("/actions", response_model=list[DailyAction])
def get_daily_actions(date: str | None = None) -> list[DailyAction]:
    if date is None:
        return RULE_OF_100_ACTIONS
    return [item for item in RULE_OF_100_ACTIONS if item.date == date]


@router.get("/rollup", response_model=DailyRollup)
def get_rollup() -> DailyRollup:
    return get_daily_rollup()


@router.patch("/actions/{action_id}/status", response_model=DailyAction)
def update_action_status(
    action_id: str,
    payload: ActionStatusUpdateRequest,
) -> DailyAction:
    action = _find_action(action_id)

    if payload.status == DailyActionStatus.completed:
        _assert_completion_allowed(action)

    action.status = payload.status
    return action


@router.post("/actions/{action_id}/approve", response_model=ApprovalRecord)
def approve_action(action_id: str, payload: ActionApprovalRequest) -> ApprovalRecord:
    action = _find_action(action_id)

    existing = next((record for record in APPROVAL_RECORDS if record.action_id == action_id), None)
    if existing is not None:
        action.status = DailyActionStatus.approved
        return existing

    record = ApprovalRecord(
        id=f"approval_{len(APPROVAL_RECORDS) + 1:03d}",
        action_id=action_id,
        approved_by=payload.approved_by,
        approved_at=datetime.utcnow(),
        note=payload.note or "Approved for manual execution. No auto-send or auto-apply.",
    )
    APPROVAL_RECORDS.append(record)
    action.status = DailyActionStatus.approved
    return record


@router.post("/actions/{action_id}/complete", response_model=DailyAction)
def complete_action(action_id: str) -> DailyAction:
    action = _find_action(action_id)
    _assert_completion_allowed(action)
    action.status = DailyActionStatus.completed
    return action
