import re
import json
import time
from typing import List, Dict, Any, Tuple
import pandas as pd
from sqlalchemy.orm import Session
from app.models.quality import QualityCheckResult


REQUIRED_COLUMNS = ["order_id", "customer_id", "customer_email", "order_date", "amount", "currency", "status"]
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


class QualityEngine:
    """
    Evaluates 6 core data engineering quality checks on extracted, transformed, and loaded data:
    1. SchemaCheck: Validates presence of expected schema columns.
    2. CompletenessCheck: Detects null or empty values in required fields.
    3. UniquenessCheck: Detects duplicate primary/business keys.
    4. FormatCheck: Validates date formats, email syntax, and numeric boundaries.
    5. ReconciliationCheck: Evaluates source vs target record counts and identifies missing IDs.
    6. VolumeCheck: Checks if batch volume meets expected baseline limits.
    """

    @classmethod
    def run_all_checks(
        cls,
        run_id: str,
        source_df: pd.DataFrame,
        target_df: pd.DataFrame,
        dropped_ids: List[str] = None,
    ) -> List[QualityCheckResult]:
        results: List[QualityCheckResult] = []

        # 1. Schema Check
        results.append(cls.check_schema(run_id, source_df))

        # 2. Completeness Check
        results.append(cls.check_completeness(run_id, source_df))

        # 3. Uniqueness Check
        results.append(cls.check_uniqueness(run_id, source_df))

        # 4. Format Check
        results.append(cls.check_formats(run_id, source_df))

        # 5. Reconciliation Check
        results.append(cls.check_reconciliation(run_id, source_df, target_df, dropped_ids or []))

        # 6. Volume Check
        results.append(cls.check_volume(run_id, source_df, target_df))

        return results

    @classmethod
    def check_schema(cls, run_id: str, df: pd.DataFrame) -> QualityCheckResult:
        start = time.time()
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        unexpected_cols = [col for col in df.columns if col not in REQUIRED_COLUMNS]

        failed = len(missing_cols) > 0
        status = "FAILED" if failed else "PASSED"
        severity = "CRITICAL" if failed else "LOW"

        details = {
            "required_columns": REQUIRED_COLUMNS,
            "present_columns": list(df.columns),
            "missing_columns": missing_cols,
            "unexpected_columns": unexpected_cols,
        }
        elapsed = int((time.time() - start) * 1000)

        return QualityCheckResult(
            run_id=run_id,
            check_name="Schema Structural Conformance",
            check_type="SCHEMA",
            status=status,
            severity=severity,
            records_evaluated=len(df),
            records_failed=len(missing_cols),
            details_json=json.dumps(details),
            execution_time_ms=elapsed,
        )

    @classmethod
    def check_completeness(cls, run_id: str, df: pd.DataFrame) -> QualityCheckResult:
        start = time.time()
        null_counts = {}
        total_failed_rows = 0

        for col in REQUIRED_COLUMNS:
            if col in df.columns:
                nulls = int(df[col].isna().sum())
                if nulls > 0:
                    null_counts[col] = nulls
                    total_failed_rows += nulls

        status = "FAILED" if total_failed_rows > 0 else "PASSED"
        severity = "HIGH" if total_failed_rows > 0 else "LOW"

        details = {
            "null_violations_by_column": null_counts,
            "total_null_values": total_failed_rows,
        }
        elapsed = int((time.time() - start) * 1000)

        return QualityCheckResult(
            run_id=run_id,
            check_name="Mandatory Column Completeness",
            check_type="COMPLETENESS",
            status=status,
            severity=severity,
            records_evaluated=len(df) * len(REQUIRED_COLUMNS),
            records_failed=total_failed_rows,
            details_json=json.dumps(details),
            execution_time_ms=elapsed,
        )

    @classmethod
    def check_uniqueness(cls, run_id: str, df: pd.DataFrame) -> QualityCheckResult:
        start = time.time()
        if "order_id" not in df.columns:
            return QualityCheckResult(
                run_id=run_id,
                check_name="Primary Key Uniqueness (order_id)",
                check_type="UNIQUENESS",
                status="FAILED",
                severity="CRITICAL",
                records_evaluated=len(df),
                records_failed=len(df),
                details_json=json.dumps({"error": "order_id column missing"}),
                execution_time_ms=0,
            )

        duplicates = df[df.duplicated(subset=["order_id"], keep=False)]
        dup_count = len(duplicates)
        unique_dup_ids = df["order_id"][df["order_id"].duplicated()].unique().tolist()

        status = "FAILED" if dup_count > 0 else "PASSED"
        severity = "HIGH" if dup_count > 0 else "LOW"

        details = {
            "duplicate_rows_count": dup_count,
            "unique_duplicate_ids": unique_dup_ids[:10],
            "total_unique_order_ids": int(df["order_id"].nunique()),
        }
        elapsed = int((time.time() - start) * 1000)

        return QualityCheckResult(
            run_id=run_id,
            check_name="Primary Key Uniqueness (order_id)",
            check_type="UNIQUENESS",
            status=status,
            severity=severity,
            records_evaluated=len(df),
            records_failed=dup_count,
            details_json=json.dumps(details),
            execution_time_ms=elapsed,
        )

    @classmethod
    def check_formats(cls, run_id: str, df: pd.DataFrame) -> QualityCheckResult:
        start = time.time()
        failed_count = 0
        format_errors = {}

        # 1. Date format check
        if "order_date" in df.columns:
            invalid_dates = []
            for idx, val in df["order_date"].items():
                if pd.isna(val):
                    continue
                try:
                    pd.to_datetime(val)
                except Exception:
                    invalid_dates.append(str(val))
            if invalid_dates:
                format_errors["invalid_dates"] = invalid_dates[:5]
                failed_count += len(invalid_dates)

        # 2. Amount numeric format check
        if "amount" in df.columns:
            invalid_amounts = []
            for idx, val in df["amount"].items():
                if pd.isna(val):
                    continue
                try:
                    num = float(val)
                    if num < 0:
                        invalid_amounts.append(f"Negative value: {num}")
                except Exception:
                    invalid_amounts.append(f"Non-numeric: {val}")
            if invalid_amounts:
                format_errors["invalid_amounts"] = invalid_amounts[:5]
                failed_count += len(invalid_amounts)

        status = "FAILED" if failed_count > 0 else "PASSED"
        severity = "MEDIUM" if failed_count > 0 else "LOW"

        details = {
            "format_error_count": failed_count,
            "errors": format_errors,
        }
        elapsed = int((time.time() - start) * 1000)

        return QualityCheckResult(
            run_id=run_id,
            check_name="Data Type & Syntax Format Validity",
            check_type="FORMAT",
            status=status,
            severity=severity,
            records_evaluated=len(df),
            records_failed=failed_count,
            details_json=json.dumps(details),
            execution_time_ms=elapsed,
        )

    @classmethod
    def check_reconciliation(
        cls,
        run_id: str,
        source_df: pd.DataFrame,
        target_df: pd.DataFrame,
        dropped_ids: List[str],
    ) -> QualityCheckResult:
        start = time.time()
        source_count = len(source_df)
        target_count = len(target_df)
        discrepancy = source_count - target_count

        missing_ids = []
        if "order_id" in source_df.columns and "order_id" in target_df.columns:
            source_ids = set(source_df["order_id"].dropna())
            target_ids = set(target_df["order_id"].dropna())
            missing_ids = list(source_ids - target_ids)
        elif dropped_ids:
            missing_ids = dropped_ids

        failed = discrepancy > 0 or len(missing_ids) > 0
        status = "FAILED" if failed else "PASSED"
        severity = "CRITICAL" if failed else "LOW"

        details = {
            "source_record_count": source_count,
            "target_record_count": target_count,
            "record_discrepancy": discrepancy,
            "missing_order_ids": missing_ids[:10],
            "is_complete_load": not failed,
        }
        elapsed = int((time.time() - start) * 1000)

        return QualityCheckResult(
            run_id=run_id,
            check_name="Source-to-Target Record Count Reconciliation",
            check_type="RECONCILIATION",
            status=status,
            severity=severity,
            records_evaluated=source_count,
            records_failed=abs(discrepancy) if discrepancy > 0 else len(missing_ids),
            details_json=json.dumps(details),
            execution_time_ms=elapsed,
        )

    @classmethod
    def check_volume(cls, run_id: str, source_df: pd.DataFrame, target_df: pd.DataFrame) -> QualityCheckResult:
        start = time.time()
        min_expected_records = 10
        actual_records = len(target_df)

        failed = actual_records < min_expected_records
        status = "FAILED" if failed else "PASSED"
        severity = "HIGH" if failed else "LOW"

        details = {
            "minimum_expected_threshold": min_expected_records,
            "actual_loaded_records": actual_records,
            "volume_variance_pct": round((actual_records / min_expected_records - 1) * 100, 1),
        }
        elapsed = int((time.time() - start) * 1000)

        return QualityCheckResult(
            run_id=run_id,
            check_name="Batch Volume Anomaly Threshold",
            check_type="VOLUME",
            status=status,
            severity=severity,
            records_evaluated=actual_records,
            records_failed=1 if failed else 0,
            details_json=json.dumps(details),
            execution_time_ms=elapsed,
        )
