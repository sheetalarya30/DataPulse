from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.crud.crud_dashboard import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    """
    Retrieve real-time metrics calculated from database execution records:
    total runs, success rate, unresolved incidents, failure trends, and quality check metrics.
    """
    return get_dashboard_summary(db)
