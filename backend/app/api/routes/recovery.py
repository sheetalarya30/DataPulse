from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.incident import IncidentResponse
from app.schemas.recovery import (
    RecoveryActionPlan,
    RecoveryExecuteRequest,
    RecoveryAttemptResponse,
)
from app.diagnosis.rule_diagnosis import RuleDiagnosisEngine
from app.recovery.recovery_engine import RecoveryEngine
from app.core.exceptions import EntityNotFoundError, ValidationFailedError

router = APIRouter(tags=["Diagnosis & Recovery"])


@router.post("/runs/{run_id}/diagnose", response_model=IncidentResponse)
def diagnose_run(run_id: str, db: Session = Depends(get_db)):
    """
    Execute forensic diagnostic evaluation on a run's execution logs and quality checks.
    Uses AI if configured, with an automatic rule-based diagnosis fallback.
    Produces evidence-backed root-cause analysis and recovery recommendations.
    """
    from app.diagnosis.ai_diagnosis import AIDiagnosisService
    incident = AIDiagnosisService.diagnose(db, run_id)
    if not incident:
        raise ValidationFailedError(f"Run '{run_id}' does not have any diagnostic anomalies or failures.")
    return incident



@router.get("/runs/{run_id}/recovery-plan", response_model=RecoveryActionPlan)
def preview_recovery_plan(run_id: str, db: Session = Depends(get_db)):
    """
    Inspect planned recovery strategy, safety verification, and duplicate prevention
    measures before executing a recovery attempt.
    """
    return RecoveryEngine.get_recovery_plan(db, run_id)


@router.post("/runs/{run_id}/retry", response_model=RecoveryAttemptResponse)
def execute_retry(
    run_id: str,
    body: RecoveryExecuteRequest,
    db: Session = Depends(get_db),
):
    """
    Safely re-executes an eligible failed demo pipeline run using idempotent upsert/merge logic.
    Validates resulting target data, resolves associated incidents, and records audit history.
    """
    if not body.confirm:
        raise ValidationFailedError("Confirmation must be explicitly granted before executing a recovery retry.")
    
    return RecoveryEngine.execute_recovery(db, run_id, strategy=body.strategy or "IDEMPOTENT_MERGE")
