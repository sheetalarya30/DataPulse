import uuid
import json
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.pipeline import Pipeline, PipelineRun, ExecutionLog
from app.models.demo_orders import DemoTargetOrder
from app.etl.scenarios import get_scenario_data
from app.quality.quality_engine import QualityEngine
from app.diagnosis.rule_diagnosis import RuleDiagnosisEngine
from app.core.logging import logger


class PipelineRunner:
    """
    Executes real e-commerce data pipeline workflows:
    Extract -> Validate -> Transform -> Load -> Quality Check -> Diagnosis
    """

    @classmethod
    def execute(
        cls,
        db: Session,
        pipeline_id: str,
        scenario: str = "success",
        is_retry: bool = False,
        parent_run_id: Optional[str] = None,
    ) -> PipelineRun:
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        if not pipeline:
            raise ValueError(f"Pipeline with ID '{pipeline_id}' not found.")

        run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        start_time = datetime.now(timezone.utc)
        start_ticks = time.time()

        run = PipelineRun(
            id=run_id,
            pipeline_id=pipeline.id,
            scenario=scenario,
            status="running",
            started_at=start_time,
            is_retry=is_retry,
            parent_run_id=parent_run_id,
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        logs: List[ExecutionLog] = []

        def append_log(level: str, stage: str, message: str, context: Optional[Dict[str, Any]] = None):
            log_entry = ExecutionLog(
                run_id=run.id,
                timestamp=datetime.now(timezone.utc),
                level=level,
                stage=stage,
                message=message,
                context_data=json.dumps(context or {}),
            )
            db.add(log_entry)
            logs.append(log_entry)

        try:
            # -------------------------------------------------------------
            # Stage 1: EXTRACT
            # -------------------------------------------------------------
            append_log("INFO", "EXTRACT", f"Extracting batch orders for scenario '{scenario}' from source system.")
            source_df, scenario_meta = get_scenario_data(scenario)
            source_count = len(source_df)
            run.source_record_count = source_count
            append_log(
                "INFO",
                "EXTRACT",
                f"Extracted {source_count} records from source successfully.",
                {"source_rows": source_count, "scenario": scenario},
            )

            # -------------------------------------------------------------
            # Stage 2: VALIDATE
            # -------------------------------------------------------------
            append_log("INFO", "VALIDATE", "Executing initial structural and pre-load validation rules.")
            expected_cols = ["order_id", "customer_id", "customer_email", "order_date", "amount"]
            missing_cols = [c for c in expected_cols if c not in source_df.columns]

            if missing_cols:
                err_msg = f"Pre-load validation failed: missing columns {missing_cols}"
                append_log("ERROR", "VALIDATE", err_msg, {"missing_columns": missing_cols})
                raise ValueError(err_msg)

            append_log("INFO", "VALIDATE", "Pre-load structural validation passed.")

            # -------------------------------------------------------------
            # Stage 3: TRANSFORM
            # -------------------------------------------------------------
            append_log("INFO", "TRANSFORM", "Beginning data cleansing, type normalization, and transformations.")
            transformed_df = source_df.copy()

            # If scenario is missing_records, simulate worker partition dropout
            dropped_ids = []
            if scenario == "missing_records":
                drop_count = scenario_meta.get("drop_count", 10)
                dropped_ids = scenario_meta.get("dropped_ids", [])
                transformed_df = transformed_df.iloc[: source_count - drop_count].copy()
                append_log(
                    "WARNING",
                    "TRANSFORM",
                    f"Micro-partition dropout encountered in worker thread: {drop_count} records omitted.",
                    {"dropped_count": drop_count, "sample_dropped": dropped_ids[:5]},
                )

            # Normalization
            transformed_df["status"] = transformed_df["status"].fillna("COMPLETED")
            transformed_df["currency"] = transformed_df["currency"].fillna("USD")
            append_log(
                "INFO",
                "TRANSFORM",
                f"Transformation stage completed. {len(transformed_df)} records prepared for loading.",
            )

            # -------------------------------------------------------------
            # Stage 4: LOAD (Target Table: demo_target_orders)
            # -------------------------------------------------------------
            append_log("INFO", "LOAD", "Staging transformed records into PostgreSQL analytics warehouse.")

            if scenario == "pipeline_failure":
                append_log("ERROR", "LOAD", "FATAL: Connection to PostgreSQL target pool reset by peer.")
                raise ConnectionError("Simulated database connection reset by peer during bulk batch insert.")

            # Load into database using idempotent upsert / merge logic
            records_inserted = 0
            records_updated = 0
            records_rejected = 0

            seen_in_batch: Dict[str, Any] = {}
            target_records = []

            for _, row in transformed_df.iterrows():
                try:
                    order_id_val = str(row["order_id"])

                    # If this key was already seen in the current batch, reject as duplicate
                    if order_id_val in seen_in_batch:
                        records_rejected += 1
                        append_log("WARNING", "LOAD", f"Duplicate primary key '{order_id_val}' detected in batch. Row omitted.")
                        continue

                    # Clean and parse order date
                    order_date_raw = row["order_date"]
                    parsed_date = pd.to_datetime(order_date_raw, errors="coerce")
                    if pd.isna(parsed_date):
                        parsed_date = datetime.now(timezone.utc)

                    amt_raw = row["amount"]
                    try:
                        parsed_amt = float(amt_raw) if not pd.isna(amt_raw) else 0.0
                    except Exception:
                        parsed_amt = 0.0

                    # Check if already exists in target table (Idempotent Merge)
                    existing_order = (
                        db.query(DemoTargetOrder)
                        .filter(DemoTargetOrder.order_id == order_id_val)
                        .first()
                    )

                    if existing_order:
                        # Update record idempotently
                        existing_order.customer_id = str(row["customer_id"])
                        existing_order.customer_email = str(row.get("customer_email") or "")
                        existing_order.order_date = parsed_date
                        existing_order.amount = parsed_amt
                        existing_order.currency = str(row.get("currency") or "USD")
                        existing_order.status = str(row.get("status") or "COMPLETED")
                        existing_order.etl_batch_id = run.id
                        records_updated += 1
                        seen_in_batch[order_id_val] = existing_order
                    else:
                        new_order = DemoTargetOrder(
                            order_id=order_id_val,
                            customer_id=str(row["customer_id"]),
                            customer_email=str(row.get("customer_email") or ""),
                            order_date=parsed_date,
                            amount=parsed_amt,
                            currency=str(row.get("currency") or "USD"),
                            status=str(row.get("status") or "COMPLETED"),
                            etl_batch_id=run.id,
                        )
                        db.add(new_order)
                        records_inserted += 1
                        seen_in_batch[order_id_val] = new_order

                    target_records.append(row)
                except Exception as row_err:
                    records_rejected += 1
                    append_log("WARNING", "LOAD", f"Row rejection on key {row.get('order_id')}: {str(row_err)}")

            db.flush()
            target_df = pd.DataFrame(target_records)
            run.target_record_count = len(target_df)
            run.records_inserted = records_inserted
            run.records_updated = records_updated
            run.records_rejected = records_rejected

            append_log(
                "INFO",
                "LOAD",
                f"Load stage complete: {records_inserted} inserted, {records_updated} updated, {records_rejected} rejected.",
                {
                    "inserted": records_inserted,
                    "updated": records_updated,
                    "rejected": records_rejected,
                    "target_count": len(target_df),
                },
            )

            # -------------------------------------------------------------
            # Stage 5: QUALITY CHECK
            # -------------------------------------------------------------
            append_log("INFO", "QUALITY_CHECK", "Executing post-load automated quality validation suite.")
            qc_results = QualityEngine.run_all_checks(
                run_id=run.id,
                source_df=source_df,
                target_df=target_df,
                dropped_ids=dropped_ids,
            )
            for qc in qc_results:
                db.add(qc)
            db.flush()

            failed_checks = [qc for qc in qc_results if qc.status in ["FAILED", "WARNING"]]

            if failed_checks:
                run.status = "failed"
                run.error_message = (
                    f"Quality verification failed: {len(failed_checks)} checks reported violations "
                    f"({', '.join([c.check_type for c in failed_checks])})."
                )
                append_log(
                    "ERROR",
                    "QUALITY_CHECK",
                    run.error_message,
                    {"failed_checks": [c.check_name for c in failed_checks]},
                )
            else:
                run.status = "success"
                append_log("INFO", "QUALITY_CHECK", "All 6 automated quality check suites PASSED with 100% compliance.")

        except Exception as e:
            db.rollback()
            # Fetch fresh run reference after rollback
            run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if not run:
                run = PipelineRun(
                    id=run_id,
                    pipeline_id=pipeline.id,
                    scenario=scenario,
                    status="failed",
                    started_at=start_time,
                )
                db.add(run)
            run.status = "failed"
            run.error_message = str(e)
            append_log("CRITICAL", "LOAD" if "Connection" in str(e) else "VALIDATE", f"Pipeline aborted: {str(e)}")


        # -------------------------------------------------------------
        # Finalization & Metrics
        # -------------------------------------------------------------
        end_ticks = time.time()
        run.completed_at = datetime.now(timezone.utc)
        run.duration_ms = int((end_ticks - start_ticks) * 1000)

        db.commit()
        db.refresh(run)

        # -------------------------------------------------------------
        # Stage 6: DIAGNOSIS (Triggered on failure or warnings)
        # -------------------------------------------------------------
        if run.status == "failed":
            logger.info(f"Triggering automated diagnosis for failed run {run.id}...")
            RuleDiagnosisEngine.diagnose_run(db, run.id)

        return run
