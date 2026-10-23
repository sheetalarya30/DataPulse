import pytest
from app.etl.pipeline_runner import PipelineRunner
from app.models.pipeline import Pipeline, PipelineRun, ExecutionLog
from app.models.quality import QualityCheckResult
from app.models.incident import Incident


def test_scenario_1_success(db_session):
    pipeline = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    assert pipeline is not None

    run = PipelineRunner.execute(db_session, pipeline.id, scenario="success")
    assert run.status == "success"
    assert run.source_record_count == 50
    assert run.target_record_count == 50
    assert run.records_inserted > 0
    assert run.records_rejected == 0
    assert run.error_message is None

    # Check logs
    logs = db_session.query(ExecutionLog).filter(ExecutionLog.run_id == run.id).all()
    stages = [l.stage for l in logs]
    assert "EXTRACT" in stages
    assert "VALIDATE" in stages
    assert "TRANSFORM" in stages
    assert "LOAD" in stages
    assert "QUALITY_CHECK" in stages

    # Check quality check results
    qcs = db_session.query(QualityCheckResult).filter(QualityCheckResult.run_id == run.id).all()
    assert len(qcs) == 6
    for qc in qcs:
        assert qc.status == "PASSED"


def test_scenario_2_missing_records(db_session):
    pipeline = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    run = PipelineRunner.execute(db_session, pipeline.id, scenario="missing_records")

    assert run.status == "failed"
    assert run.source_record_count == 50
    assert run.target_record_count == 40  # 10 records dropped in transform
    assert "Quality verification failed" in run.error_message

    # Reconciliation check must have failed
    recon = (
        db_session.query(QualityCheckResult)
        .filter(QualityCheckResult.run_id == run.id, QualityCheckResult.check_type == "RECONCILIATION")
        .first()
    )
    assert recon is not None
    assert recon.status == "FAILED"

    # Incident must be generated
    inc = db_session.query(Incident).filter(Incident.run_id == run.id).first()
    assert inc is not None
    assert inc.category == "RECORD_LOSS"
    assert inc.status == "UNRESOLVED"
    assert "Missing" in inc.title or "Incomplete" in inc.title


def test_scenario_3_duplicate_orders(db_session):
    pipeline = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    run = PipelineRunner.execute(db_session, pipeline.id, scenario="duplicate_orders")

    assert run.status == "failed"
    uniq = (
        db_session.query(QualityCheckResult)
        .filter(QualityCheckResult.run_id == run.id, QualityCheckResult.check_type == "UNIQUENESS")
        .first()
    )
    assert uniq is not None
    assert uniq.status == "FAILED"

    inc = db_session.query(Incident).filter(Incident.run_id == run.id).first()
    assert inc is not None
    assert inc.category == "DUPLICATE_KEYS"


def test_scenario_4_null_values(db_session):
    pipeline = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    run = PipelineRunner.execute(db_session, pipeline.id, scenario="null_values")

    assert run.status == "failed"
    comp = (
        db_session.query(QualityCheckResult)
        .filter(QualityCheckResult.run_id == run.id, QualityCheckResult.check_type == "COMPLETENESS")
        .first()
    )
    assert comp is not None
    assert comp.status == "FAILED"

    inc = db_session.query(Incident).filter(Incident.run_id == run.id).first()
    assert inc is not None
    assert inc.category == "NULL_VIOLATION"


def test_scenario_5_invalid_formats(db_session):
    pipeline = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    run = PipelineRunner.execute(db_session, pipeline.id, scenario="invalid_formats")

    assert run.status == "failed"
    fmt = (
        db_session.query(QualityCheckResult)
        .filter(QualityCheckResult.run_id == run.id, QualityCheckResult.check_type == "FORMAT")
        .first()
    )
    assert fmt is not None
    assert fmt.status == "FAILED"

    inc = db_session.query(Incident).filter(Incident.run_id == run.id).first()
    assert inc is not None
    assert inc.category == "FORMAT_ERROR"


def test_scenario_6_schema_mismatch(db_session):
    pipeline = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    run = PipelineRunner.execute(db_session, pipeline.id, scenario="schema_mismatch")

    assert run.status == "failed"
    assert "missing columns" in run.error_message.lower()

    inc = db_session.query(Incident).filter(Incident.run_id == run.id).first()
    assert inc is not None
    assert inc.category in ["SCHEMA_MISMATCH", "SYSTEM_FAILURE"]


def test_scenario_7_pipeline_failure(db_session):
    pipeline = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    run = PipelineRunner.execute(db_session, pipeline.id, scenario="pipeline_failure")

    assert run.status == "failed"
    assert "Simulated database connection" in run.error_message

    inc = db_session.query(Incident).filter(Incident.run_id == run.id).first()
    assert inc is not None
    assert inc.category == "SYSTEM_FAILURE"
