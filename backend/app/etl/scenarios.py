import os
import pandas as pd
from typing import Tuple, Dict, Any, Optional

SOURCE_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "sample_data", "orders_source.csv")
)


def get_scenario_data(scenario: str = "success") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Produces deterministic data for each of the 7 test scenarios.
    Returns (DataFrame, metadata_dict).
    """
    if not os.path.exists(SOURCE_CSV_PATH):
        raise FileNotFoundError(f"Source sample data not found at: {SOURCE_CSV_PATH}")

    df = pd.read_csv(SOURCE_CSV_PATH)
    meta = {
        "scenario": scenario,
        "source_rows": len(df),
        "injected_fault": None,
    }

    if scenario == "success":
        meta["description"] = "Standard clean dataset with 50 valid orders."
        return df.copy(), meta

    elif scenario == "missing_records":
        # Source has 50 records, but metadata indicates 10 records will be dropped in pipeline
        meta["description"] = "Incomplete load: 10 records dropped during transform stage."
        meta["injected_fault"] = "RECORD_LOSS"
        meta["drop_count"] = 10
        meta["dropped_ids"] = df["order_id"].iloc[40:50].tolist()
        return df.copy(), meta

    elif scenario == "duplicate_orders":
        # Inject 5 duplicate order IDs
        meta["description"] = "Upstream replication glitch created 5 duplicate order_id records."
        meta["injected_fault"] = "DUPLICATE_KEYS"
        dup_rows = df.iloc[:5].copy()
        meta["duplicate_ids"] = dup_rows["order_id"].tolist()
        df_mod = pd.concat([df, dup_rows], ignore_index=True)
        meta["source_rows"] = len(df_mod)
        return df_mod, meta

    elif scenario == "null_values":
        # Inject nulls in required columns: customer_email (4 rows) and amount (3 rows)
        meta["description"] = "Data completeness violation: null customer_email and amount fields."
        meta["injected_fault"] = "NULL_VIOLATION"
        df_mod = df.copy()
        df_mod.loc[5:8, "customer_email"] = None
        df_mod.loc[12:14, "amount"] = None
        meta["affected_columns"] = ["customer_email", "amount"]
        meta["null_count"] = 7
        return df_mod, meta

    elif scenario == "invalid_formats":
        # Inject malformed dates and invalid negative amounts
        meta["description"] = "Format validation failure: corrupted order_date timestamps and negative amounts."
        meta["injected_fault"] = "FORMAT_ERROR"
        df_mod = df.copy()
        df_mod.loc[2:4, "order_date"] = "CORRUPT_TIMESTAMP_2026_99_99"
        df_mod.loc[7:9, "amount"] = -550.00
        meta["format_violations"] = 6
        return df_mod, meta

    elif scenario == "schema_mismatch":
        # Rename columns to simulate upstream schema drift
        meta["description"] = "Schema drift: upstream renamed order_id to order_tracking_num."
        meta["injected_fault"] = "SCHEMA_MISMATCH"
        df_mod = df.copy().rename(
            columns={
                "order_id": "order_tracking_num",
                "customer_email": "contact_email",
            }
        )
        meta["missing_expected_columns"] = ["order_id", "customer_email"]
        return df_mod, meta

    elif scenario == "pipeline_failure":
        # Simulated database crash / fatal load error
        meta["description"] = "System failure: simulated network timeout / DB deadlock during LOAD stage."
        meta["injected_fault"] = "SYSTEM_FAILURE"
        return df.copy(), meta

    else:
        # Default fallback to clean
        meta["description"] = f"Unknown scenario '{scenario}'. Defaulting to clean run."
        return df.copy(), meta
