import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="cert_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp, 'test.db')}"
os.environ["OUTPUT_DIR"] = os.path.join(_tmp, "pdfs")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def valid_payload():
    return {
        "event_name": "Python Course",
        "course_name": "Backend Development",
        "issue_date": "2026-10-07",
        "issuer_name": "Acme Org",
        "recipients": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
        ],
    }
