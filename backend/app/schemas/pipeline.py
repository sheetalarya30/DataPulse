from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict


class ExecutionLogResponse(BaseModel):
    id: int
    run_id: str
    timestamp: datetime
    level: str
    stage: str
    message: str
    context_data: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PipelineBase(BaseModel):
    name: str
    code: str
    description: str
    source_type: str = "CSV / Source DB"
    target_type: str = "PostgreSQL Analytics"
    schedule: str = "Hourly"
    status: str = "active"


class PipelineCreate(PipelineBase):
    id: Optional[str] = None


class PipelineResponse(PipelineBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineWithStatsResponse(PipelineResponse):
    total_runs: int = 0
    last_run_status: Optional[str] = None
    last_run_time: Optional[datetime] = None
    last_run_duration_ms: Optional[int] = None
    success_rate: float = 0.0


class PipelineRunTriggerRequest(BaseModel):
    scenario: str = "success"  # success, missing_records, duplicate_orders, null_values, invalid_formats, schema_mismatch, pipeline_failure


class PipelineRunResponse(BaseModel):
    id: str
    pipeline_id: str
    scenario: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    source_record_count: int = 0
    target_record_count: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_rejected: int = 0
    error_message: Optional[str] = None
    is_retry: bool = False
    parent_run_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PipelineRunDetailResponse(PipelineRunResponse):
    pipeline_name: Optional[str] = None
    pipeline_code: Optional[str] = None
    logs: List[ExecutionLogResponse] = []
    quality_checks: List[Dict[str, Any]] = []
    incidents: List[Dict[str, Any]] = []
    recovery_attempts: List[Dict[str, Any]] = []
