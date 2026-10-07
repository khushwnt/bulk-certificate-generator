def test_download_certificate(client, valid_payload):
    job_id = client.post("/api/v1/certificate-jobs", json=valid_payload).json()["job_id"]
    certs = client.get(f"/api/v1/certificate-jobs/{job_id}/certificates").json()["certificates"]
    assert len(certs) == 2
    resp = client.get(certs[0]["download_url"])
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")


def test_download_unknown_certificate_404(client):
    assert client.get("/api/v1/certificates/nope/download").status_code == 404


def test_list_certificates_unknown_job_404(client):
    assert client.get("/api/v1/certificate-jobs/nope/certificates").status_code == 404
