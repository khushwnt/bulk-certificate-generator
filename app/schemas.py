from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientIn(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class JobCreateRequest(BaseModel):
    event_name: str = Field(min_length=1)
    course_name: str = Field(min_length=1)
    issue_date: date
    issuer_name: str = Field(min_length=1)
    recipients: list[RecipientIn] = Field(min_length=1)


class RecipientDetail(BaseModel):
    recipient_id: int
    name: Optional[str]
    email: Optional[str]
    status: str
    error_message: Optional[str]
    certificate_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    job_id: str
    status: str
    event_name: str
    course_name: str
    issue_date: date
    issuer_name: str
    total_recipients: int
    success_count: int
    failed_count: int
    error_message: Optional[str]
    created_at: datetime
    recipients: list[RecipientDetail]


class JobCreateResponse(BaseModel):
    job_id: str
    status: str
    total_recipients: int


class CertificateResponse(BaseModel):
    certificate_id: str
    recipient_name: str
    email: Optional[str]
    download_url: str
    created_at: datetime


class CertificateListResponse(BaseModel):
    job_id: str
    certificates: list[CertificateResponse]
