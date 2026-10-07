def test_create_job_returns_202(client, valid_payload):
    resp = client.post("/api/v1/certificate-jobs", json=valid_payload)
    assert resp.status_code == 202
    data = resp.json()
    assert "job_id" in data
    assert data["total_recipients"] == 2
    assert data["status"] in ("pending", "processing", "completed", "completed_with_errors")


def test_certificate_generated(client, valid_payload):
    resp = client.post("/api/v1/certificate-jobs", json=valid_payload)
    job_id = resp.json()["job_id"]
    certs = client.get(f"/api/v1/certificate-jobs/{job_id}/certificates").json()["certificates"]
    assert len(certs) == 2
    job = client.get(f"/api/v1/certificate-jobs/{job_id}").json()
    assert job["status"] == "completed"
    assert job["success_count"] == 2
