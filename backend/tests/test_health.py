def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "DataPulse"
    assert data["tagline"] == "Detect. Diagnose. Recover."
    assert "version" in data


def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "DataPulse"
    assert "database" in data
    assert data["database"]["status"] == "healthy"
