import json
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import (
    Pipeline,
    PipelineRun,
    ExecutionLog,
    QualityCheckResult,
    Incident,
    RecoveryAttempt,
    DemoSourceOrder,
    DemoTargetOrder,
)
from app.core.logging import logger


def init_db():
    """Create all relational tables defined in the SQLAlchemy models."""
    logger.info("Initializing database schema and creating tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")


def seed_reproducible_data(db: Session):
    """Populates reproducible baseline pipelines, historical runs, logs, quality checks, and incidents."""
    # Check if pipelines already exist to prevent duplicate seeding
    if db.query(Pipeline).first():
        logger.info("Database already contains pipeline data. Skipping seed.")
        return

    logger.info("Seeding reproducible baseline data for DataPulse...")
    now = datetime.now(timezone.utc)

    # 1. Seed Master Pipelines
    p1 = Pipeline(
        id="pipe-ecommerce-orders",
        name="E-Commerce Orders Ingestion & Cleansing",
        code="ECOMMERCE_ORDERS_ETL",
        description="Ingests customer purchases, validates schema & email integrity, deduplicates order IDs, and stages clean records to PostgreSQL analytics.",
        source_type="CSV / Source DB",
        target_type="PostgreSQL Analytics",
        schedule="Hourly",
        status="active",
        created_at=now - timedelta(days=14),
        updated_at=now,
    )
    p2 = Pipeline(
        id="pipe-inventory-sync",
        name="Warehouse Inventory & Stock Synchronizer",
        code="WAREHOUSE_INVENTORY_SYNC",
        description="Syncs real-time SKU stock levels across regional fulfillment centers to prevent stockouts and overselling.",
        source_type="Warehouse ERP API",
        target_type="PostgreSQL Warehouse",
        schedule="Every 15 min",
        status="active",
        created_at=now - timedelta(days=14),
        updated_at=now,
    )
    p3 = Pipeline(
        id="pipe-clickstream-events",
        name="Website Clickstream Event Processor",
        code="CLICKSTREAM_INGESTION",
        description="Processes user interaction events, validates payload schema, and loads aggregated session metrics.",
        source_type="Kafka Stream",
        target_type="PostgreSQL Lakehouse",
        schedule="Continuous",
        status="active",
        created_at=now - timedelta(days=14),
        updated_at=now,
    )
    db.add_all([p1, p2, p3])
    db.flush()

    # 2. Seed Historical Pipeline Runs
    # Run 1: Successful Baseline Run (3 days ago)
    r1_start = now - timedelta(days=3, hours=4)
    r1 = PipelineRun(
        id="run-20261020-001",
        pipeline_id=p1.id,
        scenario="success",
        status="success",
        started_at=r1_start,
        completed_at=r1_start + timedelta(seconds=12, milliseconds=420),
        duration_ms=12420,
        source_record_count=500,
        target_record_count=500,
        records_inserted=500,
        records_updated=0,
        records_rejected=0,
        is_retry=False,
    )

    # Run 2: Missing Records Discrepancy (2 days ago) - Incomplete load
    r2_start = now - timedelta(days=2, hours=6)
    r2 = PipelineRun(
        id="run-20261021-002",
        pipeline_id=p1.id,
        scenario="missing_records",
        status="failed",
        started_at=r2_start,
        completed_at=r2_start + timedelta(seconds=8, milliseconds=110),
        duration_ms=8110,
        source_record_count=500,
        target_record_count=482,
        records_inserted=482,
        records_updated=0,
        records_rejected=18,
        error_message="Reconciliation Failure: 18 source records missing from target warehouse.",
        is_retry=False,
    )

    # Run 3: Duplicate Order IDs Incident (1 day ago)
    r3_start = now - timedelta(days=1, hours=2)
    r3 = PipelineRun(
        id="run-20261022-003",
        pipeline_id=p1.id,
        scenario="duplicate_orders",
        status="failed",
        started_at=r3_start,
        completed_at=r3_start + timedelta(seconds=9, milliseconds=50),
        duration_ms=9050,
        source_record_count=500,
        target_record_count=488,
        records_inserted=488,
        records_updated=0,
        records_rejected=12,
        error_message="Primary Key Violation: 12 duplicate order IDs detected in source batch.",
        is_retry=False,
    )

    # Run 4: Inventory Sync Success (4 hours ago)
    r4_start = now - timedelta(hours=4)
    r4 = PipelineRun(
        id="run-20261023-004",
        pipeline_id=p2.id,
        scenario="success",
        status="success",
        started_at=r4_start,
        completed_at=r4_start + timedelta(seconds=4, milliseconds=210),
        duration_ms=4210,
        source_record_count=1200,
        target_record_count=1200,
        records_inserted=150,
        records_updated=1050,
        records_rejected=0,
        is_retry=False,
    )

    # Run 5: Clickstream Success (1 hour ago)
    r5_start = now - timedelta(hours=1)
    r5 = PipelineRun(
        id="run-20261023-005",
        pipeline_id=p3.id,
        scenario="success",
        status="success",
        started_at=r5_start,
        completed_at=r5_start + timedelta(seconds=15, milliseconds=80),
        duration_ms=15080,
        source_record_count=8500,
        target_record_count=8500,
        records_inserted=8500,
        records_updated=0,
        records_rejected=0,
        is_retry=False,
    )

    db.add_all([r1, r2, r3, r4, r5])
    db.flush()

    # 3. Seed Execution Logs for Run 2 (Missing Records)
    logs_r2 = [
        ExecutionLog(
            run_id=r2.id,
            timestamp=r2_start,
            level="INFO",
            stage="EXTRACT",
            message="Extracted 500 order records from source dataset.",
            context_data=json.dumps({"source_format": "CSV", "batch_size": 500}),
        ),
        ExecutionLog(
            run_id=r2.id,
            timestamp=r2_start + timedelta(seconds=2),
            level="INFO",
            stage="VALIDATE",
            message="Schema check passed. Validating row structure and required columns.",
            context_data=json.dumps({"validated_columns": ["order_id", "customer_id", "amount", "order_date"]}),
        ),
        ExecutionLog(
            run_id=r2.id,
            timestamp=r2_start + timedelta(seconds=5),
            level="WARNING",
            stage="TRANSFORM",
            message="Encountered batch partition dropout during parallel worker aggregation: 18 records dropped.",
            context_data=json.dumps({"partition_id": "worker-03", "dropped_count": 18}),
        ),
        ExecutionLog(
            run_id=r2.id,
            timestamp=r2_start + timedelta(seconds=7),
            level="INFO",
            stage="LOAD",
            message="Loaded 482 records into demo_target_orders staging table.",
            context_data=json.dumps({"rows_inserted": 482}),
        ),
        ExecutionLog(
            run_id=r2.id,
            timestamp=r2_start + timedelta(seconds=8),
            level="ERROR",
            stage="QUALITY_CHECK",
            message="Post-load reconciliation failed: expected 500 records, target table contains 482 records. Discrepancy: -18.",
            context_data=json.dumps({"expected": 500, "actual": 482, "delta": -18}),
        ),
    ]
    db.add_all(logs_r2)

    # 4. Seed Quality Checks for Run 2
    qc_r2 = [
        QualityCheckResult(
            run_id=r2.id,
            check_name="Source-to-Target Row Count Reconciliation",
            check_type="RECONCILIATION",
            status="FAILED",
            severity="CRITICAL",
            records_evaluated=500,
            records_failed=18,
            details_json=json.dumps({
                "source_count": 500,
                "target_count": 482,
                "discrepancy": 18,
                "missing_order_ids": [
                    "ORD-90214", "ORD-90215", "ORD-90216", "ORD-90217", "ORD-90218",
                    "ORD-90219", "ORD-90220", "ORD-90221", "ORD-90222", "ORD-90223"
                ]
            }),
            execution_time_ms=145,
            created_at=r2_start + timedelta(seconds=8),
        ),
        QualityCheckResult(
            run_id=r2.id,
            check_name="Order ID Primary Key Uniqueness",
            check_type="UNIQUENESS",
            status="PASSED",
            severity="HIGH",
            records_evaluated=482,
            records_failed=0,
            details_json=json.dumps({"duplicates_found": 0}),
            execution_time_ms=62,
            created_at=r2_start + timedelta(seconds=8),
        ),
        QualityCheckResult(
            run_id=r2.id,
            check_name="Customer Email & Amount Completeness",
            check_type="COMPLETENESS",
            status="PASSED",
            severity="MEDIUM",
            records_evaluated=482,
            records_failed=0,
            details_json=json.dumps({"null_values": 0}),
            execution_time_ms=54,
            created_at=r2_start + timedelta(seconds=8),
        ),
    ]
    db.add_all(qc_r2)

    # 5. Seed Incident for Run 2
    inc1 = Incident(
        id="inc-20261021-001",
        run_id=r2.id,
        pipeline_id=p1.id,
        title="Incomplete Load: 18 Records Missing Between Source and Analytics Target",
        category="RECORD_LOSS",
        severity="CRITICAL",
        status="UNRESOLVED",
        root_cause_summary="Post-load reconciliation detected an unexpected shortfall of 18 records. Worker-03 dropped a micro-partition during transformation due to network socket timeout.",
        confidence_score=0.98,
        evidence_json=json.dumps({
            "expected_count": 500,
            "actual_count": 482,
            "missing_records_count": 18,
            "sample_missing_ids": ["ORD-90214", "ORD-90215", "ORD-90216", "ORD-90217", "ORD-90218"],
            "failed_stage": "QUALITY_CHECK",
            "triggering_log": "Post-load reconciliation failed: expected 500 records, target table contains 482 records."
        }),
        recommendation="Trigger an Idempotent Merge Recovery Run. DataPulse will re-extract the missing batch slice and merge into target using unique order_id keys without duplicating existing rows.",
        created_at=r2_start + timedelta(seconds=8),
    )
    db.add(inc1)

    # 6. Seed Incident for Run 3 (Duplicate Keys)
    inc2 = Incident(
        id="inc-20261022-002",
        run_id=r3.id,
        pipeline_id=p1.id,
        title="Primary Key Violation: 12 Duplicate Order IDs in Ingestion Batch",
        category="DUPLICATE_KEYS",
        severity="HIGH",
        status="UNRESOLVED",
        root_cause_summary="The upstream order transaction generator produced 12 duplicate order identifiers. Duplicate keys were caught by uniqueness validation before corrupting the target warehouse.",
        confidence_score=0.96,
        evidence_json=json.dumps({
            "duplicate_count": 12,
            "sample_duplicate_ids": ["ORD-88102", "ORD-88103", "ORD-88104"],
            "validation_rule": "UNIQUENESS (order_id)"
        }),
        recommendation="Apply deduplication windowing on order_id keeping the latest timestamp record, then trigger a safe re-run.",
        created_at=r3_start + timedelta(seconds=9),
    )
    db.add(inc2)

    # 7. Seed Sample Source Orders for Testing
    demo_orders = [
        DemoSourceOrder(
            order_id=f"ORD-100{i:03d}",
            customer_id=f"CUST-{1000 + i}",
            customer_email=f"user_{i}@example.com",
            order_date=(now - timedelta(days=1, hours=i % 24)).strftime("%Y-%m-%d %H:%M:%S"),
            amount=round(24.50 + (i * 3.75) % 350.0, 2),
            currency="USD",
            status="COMPLETED",
            scenario_tag="success",
        )
        for i in range(1, 51)
    ]
    db.add_all(demo_orders)

    db.commit()
    logger.info("Successfully seeded reproducible DataPulse baseline data.")
