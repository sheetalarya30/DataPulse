def test_list_pipelines(client):
    response = client.get("/api/pipelines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    # Verify calculated stats on pipelines
    first = data[0]
    assert "total_runs" in first
    assert "success_rate" in first
    assert "last_run_status" in first


def test_get_single_pipeline(client):
    response = client.get("/api/pipelines/pipe-ecommerce-orders")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "pipe-ecommerce-orders"
    assert data["code"] == "ECOMMERCE_ORDERS_ETL"


def test_get_nonexistent_pipeline(client):
    response = client.get("/api/pipelines/nonexistent-pipeline-id")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["error"]["message"].lower()


def test_get_pipeline_runs(client):
    response = client.get("/api/pipelines/pipe-ecommerce-orders/runs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_get_run_details(client):
    response = client.get("/api/runs/run-20261021-002")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "run-20261021-002"
    assert data["status"] == "failed"
    assert data["source_record_count"] == 500
    assert data["target_record_count"] == 482
    assert len(data["logs"]) >= 5
    assert len(data["quality_checks"]) >= 1


def test_get_run_logs(client):
    response = client.get("/api/runs/run-20261021-002/logs")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 5
    stages = [l["stage"] for l in logs]
    assert "EXTRACT" in stages
    assert "QUALITY_CHECK" in stages
