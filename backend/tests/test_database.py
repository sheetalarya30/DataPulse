from datetime import datetime, timezone
from app.models.pipeline import Pipeline, PipelineRun
from app.models.incident import Incident
from app.models.quality import QualityCheckResult


def test_database_models_and_integrity(db_session):
    # Verify seeded pipelines
    pipelines = db_session.query(Pipeline).all()
    assert len(pipelines) >= 3

    # Verify seeded runs
    runs = db_session.query(PipelineRun).all()
    assert len(runs) >= 5

    # Verify incidents
    incidents = db_session.query(Incident).all()
    assert len(incidents) >= 2

    # Verify quality checks
    quality_checks = db_session.query(QualityCheckResult).all()
    assert len(quality_checks) >= 3

    # Verify relationships
    p1 = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    assert p1 is not None
    assert len(p1.runs) >= 3
    assert len(p1.incidents) >= 2
