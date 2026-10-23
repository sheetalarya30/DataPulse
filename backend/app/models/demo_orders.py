from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DemoSourceOrder(Base):
    """Source Orders table simulating source database or extracted files."""
    __tablename__ = "demo_source_orders"

    order_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_email: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    order_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)
    scenario_tag: Mapped[str] = mapped_column(String(64), default="success", index=True, nullable=False)


class DemoTargetOrder(Base):
    """Clean Target PostgreSQL table representing the analytics orders warehouse table."""
    __tablename__ = "demo_target_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(128), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)
    etl_batch_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


Index("idx_target_order_customer", DemoTargetOrder.customer_id)
Index("idx_target_order_batch", DemoTargetOrder.etl_batch_id)
