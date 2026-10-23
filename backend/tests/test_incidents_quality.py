def test_list_incidents(client):
    response = client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_incident_detail(client):
    response = client.get("/api/incidents/inc-20261021-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "inc-20261021-001"
    assert data["category"] == "RECORD_LOSS"
    assert data["severity"] == "CRITICAL"
    assert "evidence_json" in data
    assert "parsed_evidence" in data
    assert data["parsed_evidence"]["missing_records_count"] == 18


def test_quality_summary(client):
    response = client.get("/api/quality/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_checks"] >= 3
    assert "checks_by_type" in data
    assert "RECONCILIATION" in data["checks_by_type"]
