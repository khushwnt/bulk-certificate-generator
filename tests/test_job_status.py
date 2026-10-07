def test_job_status_and_progress_counts(client, valid_payload):
    job_id = client.post("/api/v1/certificate-jobs", json=valid_payload).json()["job_id"]
    job = client.get(f"/api/v1/certificate-jobs/{job_id}").json()
    assert job["status"] == "completed"
    assert job["total_recipients"] == 2
    assert job["success_count"] == 2
    assert job["failed_count"] == 0
    assert len(job["recipients"]) == 2
    for r in job["recipients"]:
        assert r["status"] == "success"
        assert r["certificate_id"] is not None


def test_unknown_job_404(client):
    assert client.get("/api/v1/certificate-jobs/does-not-exist").status_code == 404
