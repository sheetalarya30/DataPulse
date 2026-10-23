import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.pipeline import PipelineRun, ExecutionLog
from app.models.quality import QualityCheckResult
from app.models.incident import Incident
from app.core.logging import logger


class RuleDiagnosisEngine:
    """
    Forensic root-cause diagnosis engine that inspects actual execution logs,
    quality check results, and record reconciliations to generate factual,
    evidence-backed diagnoses and safe recovery recommendations.
    """

    @classmethod
    def diagnose_run(cls, db: Session, run_id: str) -> Optional[Incident]:
        run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        if not run:
            logger.warning(f"Diagnosis requested for unknown run {run_id}")
            return None

        # Check if an incident already exists for this run
        existing_incident = db.query(Incident).filter(Incident.run_id == run_id).first()
        if existing_incident:
            return existing_incident

        quality_checks = db.query(QualityCheckResult).filter(QualityCheckResult.run_id == run_id).all()
        logs = (
            db.query(ExecutionLog)
            .filter(ExecutionLog.run_id == run_id)
            .order_by(ExecutionLog.timestamp)
            .all()
        )

        failed_checks = [qc for qc in quality_checks if qc.status in ["FAILED", "WARNING"]]

        # If run is success and all checks passed, no incident needed
        if run.status == "success" and not failed_checks:
            return None

        # Determine Category, Title, Root Cause, Evidence, and Recommendation
        category = "SYSTEM_FAILURE"
        severity = "HIGH"
        confidence_score = 0.95
        title = "Pipeline Execution Failure"
        root_cause = "Pipeline execution failed or produced abnormal quality verification results."
        evidence: Dict[str, Any] = {
            "run_id": run_id,
            "pipeline_id": run.pipeline_id,
            "scenario": run.scenario,
            "status": run.status,
            "failed_checks_count": len(failed_checks),
        }
        recommendation = "Review execution logs and retry the pipeline after resolving upstream data flaws."

        # Rule 1: Schema Mismatch Detection
        schema_fail = next((qc for qc in failed_checks if qc.check_type == "SCHEMA"), None)
        if schema_fail:
            category = "SCHEMA_MISMATCH"
            severity = "CRITICAL"
            title = "Schema Drift: Missing or Renamed Expected Columns"
            details = json.loads(schema_fail.details_json) if schema_fail.details_json else {}
            missing = details.get("missing_columns", [])
            unexpected = details.get("unexpected_columns", [])
            root_cause = (
                f"Source schema does not match pipeline expectations. "
                f"Missing mandatory columns: {', '.join(missing) if missing else 'None'}. "
                f"Unexpected incoming columns: {', '.join(unexpected) if unexpected else 'None'}."
            )
            evidence["schema_details"] = details
            evidence["missing_columns"] = missing
            evidence["unexpected_columns"] = unexpected
            confidence_score = 0.99
            recommendation = (
                "Update upstream extraction mappings or run a Schema Compatibility Reload "
                "to align incoming column aliases before ingesting."
            )

        # Rule 2: Primary Key Duplication Detection
        elif any(qc.check_type == "UNIQUENESS" for qc in failed_checks):
            uniq_fail = next(qc for qc in failed_checks if qc.check_type == "UNIQUENESS")
            category = "DUPLICATE_KEYS"
            severity = "HIGH"
            details = json.loads(uniq_fail.details_json) if uniq_fail.details_json else {}
            dup_ids = details.get("unique_duplicate_ids", [])
            dup_count = details.get("duplicate_rows_count", 0)
            title = f"Primary Key Violation: {dup_count} Duplicate Order Records Detected"
            root_cause = (
                f"Ingestion batch contains {dup_count} non-unique order_id instances. "
                f"Sample duplicate keys: {', '.join(dup_ids[:5])}."
            )
            evidence["duplicate_count"] = dup_count
            evidence["sample_duplicate_ids"] = dup_ids
            confidence_score = 0.98
            recommendation = (
                "Execute an Idempotent Merge Recovery. DataPulse will apply windowed "
                "deduplication (retaining latest record per key) and upsert safely into the warehouse."
            )

        # Rule 3: Record Count Discrepancy & Reconciliation Loss
        elif any(qc.check_type == "RECONCILIATION" for qc in failed_checks):
            recon_fail = next(qc for qc in failed_checks if qc.check_type == "RECONCILIATION")
            category = "RECORD_LOSS"
            severity = "CRITICAL"
            details = json.loads(recon_fail.details_json) if recon_fail.details_json else {}
            src = details.get("source_record_count", run.source_record_count)
            tgt = details.get("target_record_count", run.target_record_count)
            delta = details.get("record_discrepancy", src - tgt)
            missing_ids = details.get("missing_order_ids", [])
            title = f"Incomplete Load: {delta} Source Records Missing from Target Warehouse"
            root_cause = (
                f"Post-load reconciliation shortfall: extracted {src} records from source, "
                f"but target warehouse only received {tgt} records. Net deficit: -{delta} records."
            )
            evidence["source_count"] = src
            evidence["target_count"] = tgt
            evidence["discrepancy"] = delta
            evidence["missing_ids_sample"] = missing_ids[:10]
            confidence_score = 0.98
            recommendation = (
                "Initiate an Idempotent Staging Reload. DataPulse will re-extract missing delta keys "
                "and load them idempotently without creating duplicates."
            )

        # Rule 4: Completeness (Null Violations)
        elif any(qc.check_type == "COMPLETENESS" for qc in failed_checks):
            comp_fail = next(qc for qc in failed_checks if qc.check_type == "COMPLETENESS")
            category = "NULL_VIOLATION"
            severity = "HIGH"
            details = json.loads(comp_fail.details_json) if comp_fail.details_json else {}
            null_cols = details.get("null_violations_by_column", {})
            total_nulls = details.get("total_null_values", 0)
            title = f"Data Completeness Violation: {total_nulls} Null Values in Mandatory Fields"
            root_cause = (
                f"Mandatory columns contain null values that violate integrity rules: "
                f"{', '.join([f'{k} ({v} nulls)' for k, v in null_cols.items()])}."
            )
            evidence["null_violations_by_column"] = null_cols
            evidence["total_null_values"] = total_nulls
            confidence_score = 0.96
            recommendation = (
                "Quarantine affected records into dead-letter storage, apply default cleansing rules, "
                "and recover valid transactions."
            )

        # Rule 5: Format Errors
        elif any(qc.check_type == "FORMAT" for qc in failed_checks):
            fmt_fail = next(qc for qc in failed_checks if qc.check_type == "FORMAT")
            category = "FORMAT_ERROR"
            severity = "MEDIUM"
            details = json.loads(fmt_fail.details_json) if fmt_fail.details_json else {}
            err_count = details.get("format_error_count", 0)
            err_dict = details.get("errors", {})
            title = f"Data Format Validation Failure: {err_count} Syntax / Boundary Violations"
            root_cause = f"Detected {err_count} invalid data values (e.g. malformed date strings or negative currency amounts)."
            evidence["format_errors"] = err_dict
            evidence["format_error_count"] = err_count
            confidence_score = 0.95
            recommendation = (
                "Apply regex date coercion and numeric clamp transforms before retrying load."
            )

        # Rule 6: Fatal Pipeline / System Exception
        elif run.status == "failed":
            category = "SYSTEM_FAILURE"
            severity = "CRITICAL"
            title = "Pipeline Runtime Failure"
            error_log = next((l for l in reversed(logs) if l.level in ["ERROR", "CRITICAL"]), None)
            err_msg = error_log.message if error_log else (run.error_message or "Unknown runtime error")
            failed_stage = error_log.stage if error_log else "LOAD"
            root_cause = f"Pipeline execution crashed in {failed_stage} stage: {err_msg}"
            evidence["failed_stage"] = failed_stage
            evidence["error_message"] = err_msg
            confidence_score = 0.92
            recommendation = (
                "Verify database connection pool health and execute an Idempotent Retry."
            )

        incident = Incident(
            id=f"inc-{uuid.uuid4().hex[:12]}",
            run_id=run.id,
            pipeline_id=run.pipeline_id,
            title=title,
            category=category,
            severity=severity,
            status="UNRESOLVED",
            root_cause_summary=root_cause,
            confidence_score=confidence_score,
            evidence_json=json.dumps(evidence),
            recommendation=recommendation,
            created_at=datetime.now(timezone.utc),
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)
        logger.info(f"Generated incident {incident.id} for run {run_id} [Category: {category}]")
        return incident
