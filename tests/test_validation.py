def test_empty_recipients_rejected(client, valid_payload):
    valid_payload["recipients"] = []
    assert client.post("/api/v1/certificate-jobs", json=valid_payload).status_code == 422


def test_missing_event_name_rejected(client, valid_payload):
    del valid_payload["event_name"]
    assert client.post("/api/v1/certificate-jobs", json=valid_payload).status_code == 422


def test_blank_event_name_rejected(client, valid_payload):
    valid_payload["event_name"] = ""
    assert client.post("/api/v1/certificate-jobs", json=valid_payload).status_code == 422


def test_invalid_issue_date_rejected(client, valid_payload):
    valid_payload["issue_date"] = "not-a-date"
    assert client.post("/api/v1/certificate-jobs", json=valid_payload).status_code == 422


def test_missing_issuer_rejected(client, valid_payload):
    del valid_payload["issuer_name"]
    assert client.post("/api/v1/certificate-jobs", json=valid_payload).status_code == 422
