from fastapi import APIRouter

from app.mock_data import OPPORTUNITIES, PIPELINE_SUMMARY
from app.schemas import Opportunity, PipelineSummary

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=list[Opportunity])
def list_opportunities() -> list[Opportunity]:
    return OPPORTUNITIES


@router.get("/pipeline-summary", response_model=PipelineSummary)
def get_pipeline_summary() -> PipelineSummary:
    return PIPELINE_SUMMARY
