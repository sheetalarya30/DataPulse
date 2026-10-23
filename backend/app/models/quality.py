from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class QualityCheckResult(Base):
    __tablename__ = "quality_check_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("pipeline_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    check_name: Mapped[str] = mapped_column(String(128), nullable=False)
    check_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # COMPLETENESS, UNIQUENESS, RECONCILIATION, FORMAT, SCHEMA, VOLUME
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=False)  # PASSED, WARNING, FAILED
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    
    records_evaluated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    run: Mapped["PipelineRun"] = relationship("PipelineRun", back_populates="quality_checks")


Index("idx_quality_type_status", QualityCheckResult.check_type, QualityCheckResult.status)
Index("idx_quality_run_status", QualityCheckResult.run_id, QualityCheckResult.status)
