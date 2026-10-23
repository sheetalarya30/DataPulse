from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class IncidentResponse(BaseModel):
    id: str
    run_id: str
    pipeline_id: str
    title: str
    category: str
    severity: str
    status: str
    root_cause_summary: str
    confidence_score: float
    evidence_json: str
    recommendation: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IncidentDetailResponse(IncidentResponse):
    pipeline_name: Optional[str] = None
    pipeline_code: Optional[str] = None
    run_status: Optional[str] = None
    run_scenario: Optional[str] = None
    parsed_evidence: Dict[str, Any] = {}
    recovery_attempts: List[Dict[str, Any]] = []
