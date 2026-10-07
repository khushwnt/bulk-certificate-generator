import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    issue_date = Column(Date, nullable=False)
    issuer_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    total_recipients = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    recipients = relationship("Recipient", back_populates="job", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="job", cascade="all, delete-orphan")


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    certificate_id = Column(String, ForeignKey("certificates.id"), nullable=True)

    job = relationship("Job", back_populates="recipients")
    certificate = relationship("Certificate", foreign_keys=[certificate_id])


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=False)
    recipient_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    job = relationship("Job", back_populates="certificates")
