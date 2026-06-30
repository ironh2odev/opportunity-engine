from fastapi import APIRouter

from app.schemas import AIDraftActionRequest, AIDraftActionResponse
from app.services.ai_assist import generate_action_draft

router = APIRouter(prefix="/ai", tags=["ai-assist"])


@router.post("/draft-action", response_model=AIDraftActionResponse)
def draft_action(payload: AIDraftActionRequest) -> AIDraftActionResponse:
    return generate_action_draft(payload)
