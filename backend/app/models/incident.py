import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"inc-{uuid.uuid4().hex[:12]}")
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("pipeline_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    pipeline_id: Mapped[str] = mapped_column(String(64), ForeignKey("pipelines.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # RECORD_LOSS, DUPLICATE_KEYS, NULL_VIOLATION, FORMAT_ERROR, SCHEMA_MISMATCH, SYSTEM_FAILURE
    severity: Mapped[str] = mapped_column(String(16), index=True, nullable=False, default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="UNRESOLVED")  # UNRESOLVED, INVESTIGATING, RECOVERING, RESOLVED
    
    root_cause_summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.95, nullable=False)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # Log excerpts, affected IDs, count deltas
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    run: Mapped["PipelineRun"] = relationship("PipelineRun", back_populates="incidents")
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="incidents")
    recovery_attempts: Mapped[List["RecoveryAttempt"]] = relationship(
        "RecoveryAttempt", back_populates="incident", cascade="all, delete-orphan"
    )


Index("idx_incident_status_severity", Incident.status, Incident.severity)
