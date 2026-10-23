from datetime import datetime, timedelta, timezone
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.pipeline import PipelineRun
from app.models.incident import Incident
from app.models.quality import QualityCheckResult
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    FailureTrendPoint,
    QualityMetricSummary,
)
from app.schemas.pipeline import PipelineRunResponse
from app.schemas.incident import IncidentResponse


def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    # 1. Total and status metrics
    total_runs = db.query(func.count(PipelineRun.id)).scalar() or 0
    successful_runs = (
        db.query(func.count(PipelineRun.id))
        .filter(PipelineRun.status == "success")
        .scalar()
        or 0
    )
    failed_runs = (
        db.query(func.count(PipelineRun.id))
        .filter(PipelineRun.status == "failed")
        .scalar()
        or 0
    )
    
    success_rate = (
        round((successful_runs / total_runs) * 100, 1) if total_runs > 0 else 0.0
    )

    # 2. Average Duration
    avg_duration = (
        db.query(func.avg(PipelineRun.duration_ms)).scalar() or 0.0
    )

    # 3. Unresolved Incidents
    unresolved_count = (
        db.query(func.count(Incident.id))
        .filter(Incident.status.in_(["UNRESOLVED", "INVESTIGATING", "RECOVERING"]))
        .scalar()
        or 0
    )

    # 4. Recent Runs
    recent_runs_db = (
        db.query(PipelineRun)
        .order_by(desc(PipelineRun.started_at))
        .limit(10)
        .all()
    )
    recent_runs = [PipelineRunResponse.model_validate(r) for r in recent_runs_db]

    # 5. Active Incidents
    active_incidents_db = (
        db.query(Incident)
        .filter(Incident.status.in_(["UNRESOLVED", "INVESTIGATING", "RECOVERING"]))
        .order_by(desc(Incident.created_at))
        .limit(5)
        .all()
    )
    active_incidents = [IncidentResponse.model_validate(inc) for inc in active_incidents_db]

    # 6. Quality Checks Summary
    total_checks = db.query(func.count(QualityCheckResult.id)).scalar() or 0
    passed_checks = (
        db.query(func.count(QualityCheckResult.id))
        .filter(QualityCheckResult.status == "PASSED")
        .scalar()
        or 0
    )
    failed_checks = (
        db.query(func.count(QualityCheckResult.id))
        .filter(QualityCheckResult.status.in_(["FAILED", "WARNING"]))
        .scalar()
        or 0
    )
    quality_pass_rate = (
        round((passed_checks / total_checks) * 100, 1) if total_checks > 0 else 100.0
    )

    quality_summary = QualityMetricSummary(
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        pass_rate=quality_pass_rate,
    )

    # 7. Failure Trends (Past 7-14 days aggregated by date)
    # Query runs from recent history
    runs_for_trends = (
        db.query(PipelineRun.started_at, PipelineRun.status)
        .order_by(PipelineRun.started_at)
        .all()
    )

    trends_map: Dict[str, Dict[str, int]] = {}
    for started_at, status in runs_for_trends:
        date_str = started_at.strftime("%Y-%m-%d")
        if date_str not in trends_map:
            trends_map[date_str] = {"total": 0, "success": 0, "failed": 0}
        trends_map[date_str]["total"] += 1
        if status == "success":
            trends_map[date_str]["success"] += 1
        elif status == "failed":
            trends_map[date_str]["failed"] += 1

    failure_trends: List[FailureTrendPoint] = []
    for date_str, data in trends_map.items():
        total = data["total"]
        succ = data["success"]
        rate = round((succ / total) * 100, 1) if total > 0 else 0.0
        failure_trends.append(
            FailureTrendPoint(
                date=date_str,
                total_runs=total,
                successful_runs=succ,
                failed_runs=data["failed"],
                success_rate=rate,
            )
        )

    # Return completed dashboard summary
    return DashboardSummaryResponse(
        total_pipeline_runs=total_runs,
        successful_runs=successful_runs,
        failed_runs=failed_runs,
        success_rate=success_rate,
        avg_duration_ms=round(avg_duration, 1),
        unresolved_incidents=unresolved_count,
        recent_runs=recent_runs,
        active_incidents=active_incidents,
        failure_trends=failure_trends,
        quality_summary=quality_summary,
    )
