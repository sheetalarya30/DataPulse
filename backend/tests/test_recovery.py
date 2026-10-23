from app.etl.pipeline_runner import PipelineRunner
from app.models.pipeline import Pipeline, PipelineRun
from app.models.incident import Incident
from app.models.recovery import RecoveryAttempt
from app.models.demo_orders import DemoTargetOrder


def test_recovery_lifecycle_and_idempotency(client, db_session):
    pipeline = db_session.query(Pipeline).filter(Pipeline.id == "pipe-ecommerce-orders").first()
    assert pipeline is not None

    # Step 1: Trigger a failed run (missing records)
    failed_run = PipelineRunner.execute(db_session, pipeline.id, scenario="missing_records")
    assert failed_run.status == "failed"

    incident = db_session.query(Incident).filter(Incident.run_id == failed_run.id).first()
    assert incident is not None
    assert incident.status == "UNRESOLVED"

    # Step 2: Request Recovery Plan via API
    plan_resp = client.get(f"/api/runs/{failed_run.id}/recovery-plan")
    assert plan_resp.status_code == 200
    plan = plan_resp.json()
    assert plan["run_id"] == failed_run.id
    assert plan["safety_checks_passed"] is True
    assert plan["duplicate_protection_active"] is True
    assert "re-extract" in plan["action_description"].lower()

    # Step 3: Attempt retry without confirmation (must fail validation)
    unconfirmed_resp = client.post(f"/api/runs/{failed_run.id}/retry", json={"confirm": False})
    assert unconfirmed_resp.status_code == 422

    # Record target count before recovery
    initial_target_count = db_session.query(DemoTargetOrder).count()

    # Step 4: Execute safe retry with confirmation
    retry_resp = client.post(f"/api/runs/{failed_run.id}/retry", json={"confirm": True, "strategy": "IDEMPOTENT_MERGE"})
    assert retry_resp.status_code == 200
    retry_data = retry_resp.json()
    assert retry_data["status"] == "SUCCESS"
    assert retry_data["validation_passed"] is True
    assert retry_data["original_run_id"] == failed_run.id

    # Step 5: Verify original run is preserved
    preserved_run = db_session.query(PipelineRun).filter(PipelineRun.id == failed_run.id).first()
    assert preserved_run is not None
    assert preserved_run.status == "failed"  # Remains as audit record of original failure

    # Step 6: Verify new recovery run
    recovery_run_id = retry_data["recovery_run_id"]
    recovery_run = db_session.query(PipelineRun).filter(PipelineRun.id == recovery_run_id).first()
    assert recovery_run is not None
    assert recovery_run.status == "success"
    assert recovery_run.is_retry is True
    assert recovery_run.parent_run_id == failed_run.id

    # Step 7: Verify incident is now resolved
    db_session.refresh(incident)
    assert incident.status == "RESOLVED"
    assert incident.resolved_at is not None

    # Step 8: Verify idempotency - target table rows should not have duplicate order_ids!
    final_target_count = db_session.query(DemoTargetOrder).count()
    unique_orders = db_session.query(DemoTargetOrder.order_id).distinct().count()
    assert final_target_count == unique_orders  # Every single order_id is completely unique!
