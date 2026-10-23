from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.pipeline import PipelineRunResponse
from app.schemas.incident import IncidentResponse


class FailureTrendPoint(BaseModel):
    date: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float


class QualityMetricSummary(BaseModel):
    total_checks: int
    passed_checks: int
    failed_checks: int
    pass_rate: float


class DashboardSummaryResponse(BaseModel):
    total_pipeline_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    avg_duration_ms: float
    unresolved_incidents: int
    recent_runs: List[PipelineRunResponse]
    active_incidents: List[IncidentResponse]
    failure_trends: List[FailureTrendPoint]
    quality_summary: QualityMetricSummary
