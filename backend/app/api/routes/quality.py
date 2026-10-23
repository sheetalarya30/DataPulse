from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.session import get_db
from app.models.quality import QualityCheckResult
from app.schemas.quality import QualitySummaryResponse, QualityCheckResultResponse

router = APIRouter(prefix="/quality", tags=["Data Quality"])


@router.get("/summary", response_model=QualitySummaryResponse)
def get_quality_summary(db: Session = Depends(get_db)):
    """Retrieve aggregate data quality check statistics and breakdown by check type."""
    total_checks = db.query(func.count(QualityCheckResult.id)).scalar() or 0
    passed_checks = (
        db.query(func.count(QualityCheckResult.id))
        .filter(QualityCheckResult.status == "PASSED")
        .scalar()
        or 0
    )
    warning_checks = (
        db.query(func.count(QualityCheckResult.id))
        .filter(QualityCheckResult.status == "WARNING")
        .scalar()
        or 0
    )
    failed_checks = (
        db.query(func.count(QualityCheckResult.id))
        .filter(QualityCheckResult.status == "FAILED")
        .scalar()
        or 0
    )

    pass_rate = round((passed_checks / total_checks * 100), 1) if total_checks > 0 else 100.0

    # Group by check type
    type_counts = (
        db.query(
            QualityCheckResult.check_type,
            QualityCheckResult.status,
            func.count(QualityCheckResult.id),
        )
        .group_by(QualityCheckResult.check_type, QualityCheckResult.status)
        .all()
    )

    checks_by_type: Dict[str, Dict[str, int]] = {}
    for c_type, status, count in type_counts:
        if c_type not in checks_by_type:
            checks_by_type[c_type] = {"PASSED": 0, "WARNING": 0, "FAILED": 0, "TOTAL": 0}
        checks_by_type[c_type][status] = count
        checks_by_type[c_type]["TOTAL"] += count

    recent_failures_db = (
        db.query(QualityCheckResult)
        .filter(QualityCheckResult.status.in_(["FAILED", "WARNING"]))
        .order_by(desc(QualityCheckResult.created_at))
        .limit(10)
        .all()
    )

    return QualitySummaryResponse(
        total_checks=total_checks,
        passed_checks=passed_checks,
        warning_checks=warning_checks,
        failed_checks=failed_checks,
        pass_rate=pass_rate,
        checks_by_type=checks_by_type,
        recent_failures=[QualityCheckResultResponse.model_validate(q) for q in recent_failures_db],
    )
