# 🎓 Bulk Certificate Generator

> Accept one request with many recipients → validate → generate a PDF certificate
> per recipient → track job progress → download the results.

A simple, explainable FastAPI backend. No Celery, no Redis, no Docker — just
FastAPI `BackgroundTasks`, SQLAlchemy, SQLite, and ReportLab.

---

## ✨ Features

- 📮 **Bulk job creation** — one POST creates a job for any number of recipients
- ✅ **Two-level validation** — Pydantic for request shape, service-level for recipient data
- 🛡️ **Failure isolation** — one bad recipient never stops the others
- 📈 **Progress tracking** — status + success/failure counts, pollable any time
- 📄 **PDF certificates** — one predefined ReportLab template, UUID filenames
- 🧪 **Tested** — 14 pytest tests covering the whole flow

---

## 🧱 Tech Stack

| Layer      | Choice                              |
|------------|-------------------------------------|
| API        | FastAPI                             |
| DB         | SQLAlchemy + SQLite                 |
| Validation | Pydantic (request/response models)  |
| PDFs       | ReportLab                           |
| Background | FastAPI BackgroundTasks             |
| Tests      | pytest + FastAPI TestClient         |

## 🗂 Project Layout

```
app/
├── main.py                      # FastAPI app, lifespan startup, routers
├── config.py                    # env-driven settings (DB URL, output dir)
├── database.py                  # engine, SessionLocal, Base, get_db, init_db
├── models.py                    # Job / Recipient / Certificate tables
├── schemas.py                   # Pydantic request & response models
├── routers/
│   ├── jobs.py                  # POST job, GET job, GET job certificates
│   └── certificates.py          # GET certificate download
└── services/
    ├── job_service.py           # create job, background processing loop
    └── certificate_service.py   # recipient validation, PDF generation
tests/                           # 6 test files, 14 tests
generated_certificates/          # PDF output folder (runtime)
```

---

## 🚀 Getting Started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Interactive API docs: **http://localhost:8000/docs**

---

## 🔌 API Endpoints

### 1️⃣ Create a job — `POST /api/v1/certificate-jobs`

```bash
curl -X POST http://localhost:8000/api/v1/certificate-jobs \
  -H 'Content-Type: application/json' \
  -d '{
    "event_name": "Python Course",
    "course_name": "Backend Development",
    "issue_date": "2026-10-07",
    "issuer_name": "Acme Org",
    "recipients": [
      {"name": "Alice", "email": "alice@example.com"},
      {"name": "Bob",   "email": "bob@example.com"}
    ]
  }'
```

**`202 Accepted`**
```json
{"job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "status": "pending", "total_recipients": 2}
```

### 2️⃣ Job status & details — `GET /api/v1/certificate-jobs/{job_id}`

```json
{
  "job_id": "3fa85f64-...",
  "status": "completed_with_errors",
  "total_recipients": 3,
  "success_count": 1,
  "failed_count": 2,
  "recipients": [
    {"name": "Alice", "email": "alice@example.com", "status": "success", "certificate_id": "..."},
    {"name": "",      "email": "ok@example.com",    "status": "failed",  "error_message": "Recipient name is required"},
    {"name": "Carol", "email": "not-an-email",      "status": "failed",  "error_message": "Invalid email address"}
  ]
}
```

### 3️⃣ List certificates — `GET /api/v1/certificate-jobs/{job_id}/certificates`

```json
{"job_id": "3fa85f64-...", "certificates": [
  {"certificate_id": "...", "recipient_name": "Alice", "download_url": "/api/v1/certificates/.../download"}
]}
```

### 4️⃣ Download a PDF — `GET /api/v1/certificates/{certificate_id}/download`

Returns the PDF file (`application/pdf`).

---

## 🚦 Job Statuses

```
            ┌────────────┐   ┌─────────────┐
            │  pending   │──▶│ processing  │
            └────────────┘   └──────┬──────┘
                                    │
              ┌─────────────────────┼──────────────────────┐
              ▼                     ▼                      ▼
        ┌───────────┐  ┌────────────────────────┐  ┌─────────┐
        │ completed │  │ completed_with_errors  │  │ failed  │
        └───────────┘  └────────────────────────┘  └─────────┘
```

## ✅ Validation Strategy

| Level        | Where     | Examples                                                    | Outcome                     |
|--------------|-----------|-------------------------------------------------------------|-----------------------------|
| Top-level    | Pydantic  | missing `event_name`, empty `recipients`, bad date          | whole request rejected, 422 |
| Per-recipient| Service   | blank name, invalid email, over-long name, PDF error        | that recipient `failed`, job continues |

## 🛡 Failure Handling

Each recipient is validated and processed inside its own `try/except` with its
own commit. A bad recipient gets `status="failed"` + `error_message`; everyone
else still succeeds. The final job status is the roll-up of recipient results.

## ⚙️ Background Processing

1. `POST` creates the Job + Recipient rows (`pending`) and returns `202` immediately.
2. FastAPI `BackgroundTasks` runs `process_job(job_id)` in the same process.
3. It flips status to `processing`, handles each recipient, commits per recipient,
   then sets the final status.
4. Clients poll the GET endpoint for progress.

> 💡 **Why BackgroundTasks?** Simple and explicit — no broker, no workers, no
> Docker. For production scale you'd swap `process_job` for Celery/RQ; the
> service functions stay the same.

## 📁 File Storage

PDFs are written to `./generated_certificates/<uuid>.pdf`; the DB stores the
path. UUID names avoid collisions. Production would use S3-style object storage.

## 🧪 Tests

```bash
python -m pytest -v
```

Covers: job creation · top-level validation (422s) · certificate generation ·
job status/progress · per-recipient failure isolation · PDF download · 404s.

## 🧠 Design Decisions & Trade-offs

- **BackgroundTasks** — simple; not durable, single-process. Documented above.
- **Recipient table instead of JSON** — queryable per-recipient details.
- **Commit per recipient** — visible progress, failure isolation.
- **One hardcoded template** — explainable; no template CRUD.
- **Plain functions in services** — no DI magic, easy to read top-to-bottom.
