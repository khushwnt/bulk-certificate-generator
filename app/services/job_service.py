from typing import List

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Certificate, Job, Recipient
from app.schemas import JobCreateRequest
from app.services import certificate_service


def create_job(db: Session, payload: JobCreateRequest) -> Job:
    job = Job(
        event_name=payload.event_name.strip(),
        course_name=payload.course_name.strip(),
        issue_date=payload.issue_date,
        issuer_name=payload.issuer_name.strip(),
        status="pending",
        total_recipients=len(payload.recipients),
    )
    db.add(job)
    db.flush()
    for r in payload.recipients:
        db.add(Recipient(job_id=job.id, name=r.name, email=r.email, status="pending"))
    db.commit()
    db.refresh(job)
    return job


def process_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return
        job.status = "processing"
        db.commit()

        for recipient in list(job.recipients):
            _process_recipient(db, job, recipient)

        if job.success_count == job.total_recipients and job.total_recipients > 0:
            job.status = "completed"
        elif job.success_count == 0:
            job.status = "failed"
        else:
            job.status = "completed_with_errors"
        db.commit()
    except Exception as exc:
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is not None:
            job.status = "failed"
            job.error_message = str(exc)
            db.commit()
    finally:
        db.close()


def _process_recipient(db: Session, job: Job, recipient: Recipient) -> None:
    try:
        error = certificate_service.validate_recipient(recipient.name, recipient.email)
        if error:
            recipient.status = "failed"
            recipient.error_message = error
            job.failed_count += 1
            db.commit()
            return

        path = certificate_service.generate_certificate_pdf(job, recipient)
        cert = Certificate(
            job_id=job.id,
            recipient_id=recipient.id,
            recipient_name=recipient.name.strip(),
            email=recipient.email,
            file_path=path,
        )
        db.add(cert)
        db.flush()
        recipient.status = "success"
        recipient.certificate_id = cert.id
        job.success_count += 1
        db.commit()
    except Exception as exc:
        db.rollback()
        recipient = db.query(Recipient).filter(Recipient.id == recipient.id).first()
        job = db.query(Job).filter(Job.id == job.id).first()
        if recipient is not None:
            recipient.status = "failed"
            recipient.error_message = f"Generation failed: {exc}"
        if job is not None:
            job.failed_count += 1
        db.commit()
