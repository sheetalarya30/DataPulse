def test_dashboard_summary_metrics(client):
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()

    # Verify all required top-level summary metrics are present and calculated
    assert "total_pipeline_runs" in data
    assert "successful_runs" in data
    assert "failed_runs" in data
    assert "success_rate" in data
    assert "avg_duration_ms" in data
    assert "unresolved_incidents" in data
    assert "recent_runs" in data
    assert "failure_trends" in data
    assert "quality_summary" in data

    # Arithmetic consistency verification
    total = data["total_pipeline_runs"]
    succ = data["successful_runs"]
    failed = data["failed_runs"]
    assert total >= 5
    assert succ + failed == total
    expected_rate = round((succ / total) * 100, 1)
    assert data["success_rate"] == expected_rate

    # Incidents count verification
    assert data["unresolved_incidents"] >= 2

    # Failure trends verification
    trends = data["failure_trends"]
    assert len(trends) > 0
    for t in trends:
        assert "date" in t
        assert "total_runs" in t
        assert "success_rate" in t

    # Quality check summary verification
    qc = data["quality_summary"]
    assert qc["total_checks"] >= 3
    assert qc["passed_checks"] + qc["failed_checks"] == qc["total_checks"]
