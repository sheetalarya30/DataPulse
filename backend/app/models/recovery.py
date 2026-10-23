import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"rec-{uuid.uuid4().hex[:12]}")
    incident_id: Mapped[str] = mapped_column(String(64), ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False)
    original_run_id: Mapped[str] = mapped_column(String(64), ForeignKey("pipeline_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    recovery_run_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("pipeline_runs.id", ondelete="SET NULL"), nullable=True)
    
    strategy: Mapped[str] = mapped_column(String(64), nullable=False, default="IDEMPOTENT_MERGE")  # IDEMPOTENT_MERGE, STAGING_RELOAD, SCHEMA_COMPAT_RELOAD
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="INITIATED")  # INITIATED, IN_PROGRESS, SUCCESS, FAILED
    records_recovered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    validation_passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="recovery_attempts")
    original_run: Mapped["PipelineRun"] = relationship(
        "PipelineRun", foreign_keys=[original_run_id], back_populates="recovery_attempts"
    )
    recovery_run: Mapped[Optional["PipelineRun"]] = relationship("PipelineRun", foreign_keys=[recovery_run_id])


Index("idx_recovery_incident_status", RecoveryAttempt.incident_id, RecoveryAttempt.status)
