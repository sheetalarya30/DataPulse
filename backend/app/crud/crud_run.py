from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.pipeline import PipelineRun, ExecutionLog
from app.models.quality import QualityCheckResult
from app.models.incident import Incident
from app.models.recovery import RecoveryAttempt


def get_run(db: Session, run_id: str) -> Optional[PipelineRun]:
    return db.query(PipelineRun).filter(PipelineRun.id == run_id).first()


def get_runs_by_pipeline(
    db: Session, pipeline_id: str, skip: int = 0, limit: int = 50
) -> List[PipelineRun]:
    return (
        db.query(PipelineRun)
        .filter(PipelineRun.pipeline_id == pipeline_id)
        .order_by(desc(PipelineRun.started_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_recent_runs(db: Session, limit: int = 10) -> List[PipelineRun]:
    return db.query(PipelineRun).order_by(desc(PipelineRun.started_at)).limit(limit).all()


def get_run_logs(db: Session, run_id: str) -> List[ExecutionLog]:
    return (
        db.query(ExecutionLog)
        .filter(ExecutionLog.run_id == run_id)
        .order_by(ExecutionLog.timestamp)
        .all()
    )


def get_run_quality_checks(db: Session, run_id: str) -> List[QualityCheckResult]:
    return (
        db.query(QualityCheckResult)
        .filter(QualityCheckResult.run_id == run_id)
        .order_by(QualityCheckResult.id)
        .all()
    )


def get_run_incidents(db: Session, run_id: str) -> List[Incident]:
    return db.query(Incident).filter(Incident.run_id == run_id).all()


def get_run_recovery_attempts(db: Session, run_id: str) -> List[RecoveryAttempt]:
    return (
        db.query(RecoveryAttempt)
        .filter(RecoveryAttempt.original_run_id == run_id)
        .order_by(desc(RecoveryAttempt.created_at))
        .all()
    )
