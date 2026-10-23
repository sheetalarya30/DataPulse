import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.pipeline import (
    PipelineRunResponse,
    PipelineRunDetailResponse,
    ExecutionLogResponse,
)
from app.schemas.quality import QualityCheckResultResponse
from app.crud.crud_run import (
    get_run,
    get_run_logs,
    get_run_quality_checks,
    get_run_incidents,
    get_run_recovery_attempts,
)
from app.core.exceptions import EntityNotFoundError

router = APIRouter(prefix="/runs", tags=["Runs"])


@router.get("/{run_id}", response_model=PipelineRunDetailResponse)
def get_run_details(run_id: str, db: Session = Depends(get_db)):
    """Retrieve complete execution metadata, logs, and quality check records for a run."""
    run = get_run(db, run_id)
    if not run:
        raise EntityNotFoundError("PipelineRun", run_id)

    logs = get_run_logs(db, run_id)
    quality_checks = get_run_quality_checks(db, run_id)
    incidents = get_run_incidents(db, run_id)
    recovery_attempts = get_run_recovery_attempts(db, run_id)

    formatted_qc = []
    for qc in quality_checks:
        try:
            details = json.loads(qc.details_json) if qc.details_json else {}
        except Exception:
            details = {}
        formatted_qc.append({
            "id": qc.id,
            "check_name": qc.check_name,
            "check_type": qc.check_type,
            "status": qc.status,
            "severity": qc.severity,
            "records_evaluated": qc.records_evaluated,
            "records_failed": qc.records_failed,
            "details": details,
            "execution_time_ms": qc.execution_time_ms,
            "created_at": qc.created_at.isoformat(),
        })

    formatted_incidents = []
    for inc in incidents:
        try:
            evidence = json.loads(inc.evidence_json) if inc.evidence_json else {}
        except Exception:
            evidence = {}
        formatted_incidents.append({
            "id": inc.id,
            "title": inc.title,
            "category": inc.category,
            "severity": inc.severity,
            "status": inc.status,
            "root_cause_summary": inc.root_cause_summary,
            "confidence_score": inc.confidence_score,
            "evidence": evidence,
            "recommendation": inc.recommendation,
            "created_at": inc.created_at.isoformat(),
        })

    formatted_recovery = [
        {
            "id": rec.id,
            "strategy": rec.strategy,
            "status": rec.status,
            "records_recovered": rec.records_recovered,
            "validation_passed": rec.validation_passed,
            "notes": rec.notes,
            "created_at": rec.created_at.isoformat(),
        }
        for rec in recovery_attempts
    ]

    return PipelineRunDetailResponse(
        id=run.id,
        pipeline_id=run.pipeline_id,
        pipeline_name=run.pipeline.name if run.pipeline else None,
        pipeline_code=run.pipeline.code if run.pipeline else None,
        scenario=run.scenario,
        status=run.status,
        started_at=run.started_at,
        completed_at=run.completed_at,
        duration_ms=run.duration_ms,
        source_record_count=run.source_record_count,
        target_record_count=run.target_record_count,
        records_inserted=run.records_inserted,
        records_updated=run.records_updated,
        records_rejected=run.records_rejected,
        error_message=run.error_message,
        is_retry=run.is_retry,
        parent_run_id=run.parent_run_id,
        logs=[ExecutionLogResponse.model_validate(l) for l in logs],
        quality_checks=formatted_qc,
        incidents=formatted_incidents,
        recovery_attempts=formatted_recovery,
    )


@router.get("/{run_id}/logs", response_model=List[ExecutionLogResponse])
def get_logs_for_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieve chronological execution logs for a specific run."""
    run = get_run(db, run_id)
    if not run:
        raise EntityNotFoundError("PipelineRun", run_id)
    logs = get_run_logs(db, run_id)
    return [ExecutionLogResponse.model_validate(l) for l in logs]


@router.get("/{run_id}/quality-checks", response_model=List[QualityCheckResultResponse])
def get_quality_checks_for_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieve quality validation records executed during a pipeline run."""
    run = get_run(db, run_id)
    if not run:
        raise EntityNotFoundError("PipelineRun", run_id)
    checks = get_run_quality_checks(db, run_id)
    return [QualityCheckResultResponse.model_validate(c) for c in checks]
