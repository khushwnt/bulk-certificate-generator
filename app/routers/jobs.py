from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job
from app.schemas import (
    CertificateListResponse,
    CertificateResponse,
    JobCreateRequest,
    JobCreateResponse,
    JobResponse,
)
from app.services import job_service

router = APIRouter(prefix="/api/v1", tags=["certificate-jobs"])


@router.post("/certificate-jobs", response_model=JobCreateResponse, status_code=202)
def create_certificate_job(
    payload: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = job_service.create_job(db, payload)
    background_tasks.add_task(job_service.process_job, job.id)
    return JobCreateResponse(job_id=job.id, status=job.status, total_recipients=job.total_recipients)


@router.get("/certificate-jobs/{job_id}", response_model=JobResponse)
def get_certificate_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(
        job_id=job.id,
        status=job.status,
        event_name=job.event_name,
        course_name=job.course_name,
        issue_date=job.issue_date,
        issuer_name=job.issuer_name,
        total_recipients=job.total_recipients,
        success_count=job.success_count,
        failed_count=job.failed_count,
        error_message=job.error_message,
        created_at=job.created_at,
        recipients=[
            {
                "recipient_id": r.id,
                "name": r.name,
                "email": r.email,
                "status": r.status,
                "error_message": r.error_message,
                "certificate_id": r.certificate_id,
            }
            for r in job.recipients
        ],
    )


@router.get("/certificate-jobs/{job_id}/certificates", response_model=CertificateListResponse)
def list_job_certificates(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return CertificateListResponse(
        job_id=job.id,
        certificates=[
            CertificateResponse(
                certificate_id=c.id,
                recipient_name=c.recipient_name,
                email=c.email,
                download_url=f"/api/v1/certificates/{c.id}/download",
                created_at=c.created_at,
            )
            for c in job.certificates
        ],
    )
