import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Pipeline(Base, TimestampMixin):
    __tablename__ = "pipelines"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, default="CSV / Source DB")
    target_type: Mapped[str] = mapped_column(String(64), nullable=False, default="PostgreSQL Analytics")
    schedule: Mapped[str] = mapped_column(String(64), nullable=False, default="Hourly")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")  # active, paused, failed

    # Relationships
    runs: Mapped[List["PipelineRun"]] = relationship(
        "PipelineRun", back_populates="pipeline", cascade="all, delete-orphan", order_by="desc(PipelineRun.started_at)"
    )
    incidents: Mapped[List["Incident"]] = relationship(
        "Incident", back_populates="pipeline", cascade="all, delete-orphan"
    )


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"run-{uuid.uuid4().hex[:12]}")
    pipeline_id: Mapped[str] = mapped_column(String(64), ForeignKey("pipelines.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario: Mapped[str] = mapped_column(String(64), nullable=False, default="success")  # success, missing_records, duplicate_orders, null_values, invalid_formats, schema_mismatch, pipeline_failure
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="pending")  # pending, running, success, failed
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    source_record_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    target_record_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_retry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_run_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("pipeline_runs.id"), nullable=True)

    # Relationships
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="runs")
    logs: Mapped[List["ExecutionLog"]] = relationship(
        "ExecutionLog", back_populates="run", cascade="all, delete-orphan", order_by="ExecutionLog.timestamp"
    )
    quality_checks: Mapped[List["QualityCheckResult"]] = relationship(
        "QualityCheckResult", back_populates="run", cascade="all, delete-orphan"
    )
    incidents: Mapped[List["Incident"]] = relationship(
        "Incident", back_populates="run", cascade="all, delete-orphan"
    )
    recovery_attempts: Mapped[List["RecoveryAttempt"]] = relationship(
        "RecoveryAttempt",
        back_populates="original_run",
        foreign_keys="RecoveryAttempt.original_run_id",
        cascade="all, delete-orphan",
    )


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("pipeline_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    stage: Mapped[str] = mapped_column(String(32), nullable=False)  # EXTRACT, VALIDATE, TRANSFORM, LOAD, QUALITY_CHECK, RECOVERY
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON formatted extra data

    # Relationship
    run: Mapped["PipelineRun"] = relationship("PipelineRun", back_populates="logs")


# Create indices for high-performance dashboard querying
Index("idx_run_started_status", PipelineRun.started_at, PipelineRun.status)
Index("idx_run_pipeline_started", PipelineRun.pipeline_id, PipelineRun.started_at)
