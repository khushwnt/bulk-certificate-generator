You are a senior Python developer building a Bulk Certificate Generator backend.

Tech stack constraints:
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- ReportLab for PDF generation
- pytest + FastAPI TestClient for tests
- FastAPI BackgroundTasks for bulk processing

Do NOT use Celery, Redis, Docker, Alembic, async DB, or complex queues.
Use only simple, explicit, easily explainable code.
Prefer plain functions and small services over clever abstractions.

Project goal:
Build a backend API that accepts one request containing many recipients,
validates them, generates one PDF certificate per valid recipient using one
predefined template, tracks job progress, and lets the client retrieve
generated certificates.

Required API endpoints:
1. POST /api/v1/certificate-jobs
   - Accepts event/certificate info and a list of recipients.
   - Creates a job and starts background processing.
   - Returns job id and initial status.

2. GET /api/v1/certificate-jobs/{job_id}
   - Returns job status, counts, and per-recipient success/failure details.

3. GET /api/v1/certificate-jobs/{job_id}/certificates
   - Returns generated certificates for a job.

4. GET /api/v1/certificates/{certificate_id}/download
   - Downloads the generated PDF.

Suggested request body:
{
  "event_name": "Python Course",
  "course_name": "Backend Development",
  "issue_date": "2026-10-07",
  "issuer_name": "Acme Org",
  "recipients": [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
  ]
}

Job statuses:
- pending
- processing
- completed
- completed_with_errors
- failed

Recipient statuses:
- pending
- success
- failed

Validation rules:
- Top-level Pydantic validation rejects missing event_name, empty recipients list, etc.
- Per-recipient validation happens in the service.
- If one recipient is invalid, mark that recipient failed but continue others.
- Example: empty recipient name -> failed with error message.
- Invalid email -> failed if email is provided.

Bulk processing decision:
- Use FastAPI BackgroundTasks.
- Document that this is simple and good for this exercise.
- For production, a real queue like Celery/RQ would be better.

File storage:
- Save PDFs to a local folder like ./generated_certificates.
- Store the file path in the database.
- Use UUID filenames to avoid collisions.

Certificate template:
- One predefined ReportLab PDF template.
- Include recipient name, event/course name, issue date, issuer name.
- Simple border, title, and signature line.

Explainability rule:
After each code change, explain and write in this master.md file with changest as index in simple terms:
- What files were added/changed.
- What each main function/class does.
- Why the design choice was made.
- How to run and verify it.

---

# Change index

## 1. Project skeleton + dependencies
Files added: `requirements.txt`, `app/config.py`, `app/database.py`, `app/__init__.py`, `app/routers/__init__.py`, `app/services/__init__.py`, `tests/__init__.py`, `generated_certificates/`.
- `config.py`: reads `DATABASE_URL` and `OUTPUT_DIR` from env with sensible defaults so tests can point at a temp DB/folder.
- `database.py`: creates the SQLAlchemy engine, `SessionLocal`, declarative `Base`, the `get_db` request dependency, and `init_db()` which creates all tables. Plain functions, no framework magic.
Why: keeping DB setup in one small module makes the SQLite swap-out for tests trivial.
Verify: `python -c "from app.database import init_db; init_db()"`.

## 2. Models
Files added: `app/models.py`.
- `Job`: event/course/date/issuer, status, total/success/failed counts, optional job-level error, created_at; has many `Recipient` and `Certificate`.
- `Recipient`: name, email, status (pending/success/failed), error_message, link to its `Certificate`.
- `Certificate`: recipient snapshot (name/email), file_path, timestamps.
Why: separate `Recipient` rows give per-recipient success/failure details without parsing JSON blobs.

## 3. Schemas
Files added: `app/schemas.py`.
- `RecipientIn` / `JobCreateRequest`: top-level validation (non-empty event fields, valid date, at least one recipient) -> FastAPI returns 422 on violation.
- `JobResponse`, `RecipientDetail`, `JobCreateResponse`, `CertificateResponse`, `CertificateListResponse`: response shapes with download URLs.
Why: Pydantic handles shape errors up front; email/name content is checked later in the service.

## 4. Certificate service
Files added: `app/services/certificate_service.py`.
- `validate_recipient(name, email)`: returns an error string for blank/over-long names or invalid emails (validated with pydantic `EmailStr`), else None.
- `generate_certificate_pdf(job, recipient, output_dir=None)`: draws the one predefined template (border, title, name, course/event, date, issuer, signature line) and writes a UUID-named PDF. Returns the file path.
Why: one simple ReportLab canvas function, no template engine; UUID filenames avoid collisions.

## 5. Job service
Files added: `app/services/job_service.py`.
- `create_job(db, payload)`: inserts Job + pending Recipients, commits, returns the job.
- `process_job(job_id)`: own SessionLocal session; sets status=processing; loops recipients calling `_process_recipient`; then sets final status (completed / completed_with_errors / failed). Any unexpected exception marks the job failed.
- `_process_recipient(db, job, recipient)`: validates, generates PDF, creates Certificate row; on any error marks only that recipient failed with a message. Commits per recipient so progress is visible and one failure cannot roll back the others.
Why: plain functions + explicit commits; BackgroundTasks call `process_job` because it manages its own session (request-scoped sessions must not be reused in background work).

## 6. Routers + app
Files added: `app/routers/jobs.py`, `app/routers/certificates.py`, `app/main.py`.
- `POST /api/v1/certificate-jobs`: validates payload, creates job, enqueues `process_job`, returns 202 with job id + pending status.
- `GET /api/v1/certificate-jobs/{job_id}`: job status, counts, recipient details (404 if unknown).
- `GET /api/v1/certificate-jobs/{job_id}/certificates`: generated certificate list (404 if unknown job).
- `GET /api/v1/certificates/{certificate_id}/download`: FileResponse with application/pdf (404 if missing).
- `main.py`: builds the FastAPI app, includes routers, uses a lifespan handler to create the output dir and DB tables.
Verify manually: `uvicorn app.main:app --reload`, curl the POST, then GET the job.

## 7. Tests
Files added: `tests/conftest.py`, `tests/test_generation.py`, `tests/test_validation.py`, `tests/test_job_status.py`, `tests/test_recipient_failure.py`, `tests/test_retrieval.py`.
- `conftest.py`: sets `DATABASE_URL`/`OUTPUT_DIR` env vars to a temp dir BEFORE importing the app, and provides a session-scoped TestClient plus a valid_payload fixture. Under TestClient, BackgroundTasks finish before the client returns, so tests can assert final state without sleeps.
- Coverage: creation returns 202/pending; top-level validation 422s; certificate generation produces 2 PDFs and status completed; per-recipient failure isolation (blank name/bad email -> completed_with_errors, others succeed); all-failed -> failed; unknown job/certificate 404s; PDF download returns %PDF bytes.
Run: `python -m pytest -q` (14 passed).

## 8. Docs
Files added: `README.md`. Setup, run, curl examples for all endpoints, job statuses, validation rules, background-processing explanation (and Celery/RQ production note), file storage, tests, design decisions.
