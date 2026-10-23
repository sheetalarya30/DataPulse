from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, ConfigDict


class QualityCheckResultResponse(BaseModel):
    id: int
    run_id: str
    check_name: str
    check_type: str
    status: str
    severity: str
    records_evaluated: int
    records_failed: int
    details_json: str
    execution_time_ms: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QualitySummaryResponse(BaseModel):
    total_checks: int
    passed_checks: int
    warning_checks: int
    failed_checks: int
    pass_rate: float
    checks_by_type: Dict[str, Dict[str, int]]
    recent_failures: List[QualityCheckResultResponse]
