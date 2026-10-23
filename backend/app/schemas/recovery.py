from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class RecoveryActionPlan(BaseModel):
    run_id: str
    incident_id: Optional[str] = None
    strategy: str  # IDEMPOTENT_MERGE, STAGING_RELOAD
    action_description: str
    safety_checks_passed: bool
    requires_confirmation: bool = True
    estimated_records_to_process: int = 0
    duplicate_protection_active: bool = True
    warning_notes: Optional[str] = None


class RecoveryExecuteRequest(BaseModel):
    confirm: bool = True
    strategy: Optional[str] = "IDEMPOTENT_MERGE"


class RecoveryAttemptResponse(BaseModel):
    id: str
    incident_id: str
    original_run_id: str
    recovery_run_id: Optional[str] = None
    strategy: str
    status: str
    records_recovered: int
    validation_passed: bool
    notes: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
