from fastapi import APIRouter

from app.mock_data import TAILORING_DRAFTS
from app.schemas import TailoringDraft

router = APIRouter(prefix="/tailoring", tags=["tailoring"])


@router.get("/drafts", response_model=list[TailoringDraft])
def list_tailoring_drafts() -> list[TailoringDraft]:
    return TAILORING_DRAFTS
