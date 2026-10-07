def test_one_bad_recipient_does_not_stop_others(client, valid_payload):
    valid_payload["recipients"] = [
        {"name": "", "email": "ok@example.com"},
        {"name": "Carol", "email": "not-an-email"},
        {"name": "Dave", "email": "dave@example.com"},
    ]
    job_id = client.post("/api/v1/certificate-jobs", json=valid_payload).json()["job_id"]
    job = client.get(f"/api/v1/certificate-jobs/{job_id}").json()
    assert job["status"] == "completed_with_errors"
    assert job["success_count"] == 1
    assert job["failed_count"] == 2
    by_name = {r["name"]: r for r in job["recipients"]}
    assert by_name["Carol"]["status"] == "failed"
    assert "email" in by_name["Carol"]["error_message"].lower()
    assert by_name[""]["status"] == "failed"
    assert by_name["Dave"]["status"] == "success"


def test_all_failed_marks_job_failed(client, valid_payload):
    valid_payload["recipients"] = [{"name": "", "email": None}]
    job_id = client.post("/api/v1/certificate-jobs", json=valid_payload).json()["job_id"]
    job = client.get(f"/api/v1/certificate-jobs/{job_id}").json()
    assert job["status"] == "failed"
    assert job["failed_count"] == 1
