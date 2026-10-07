import os
import uuid
from typing import Optional, Tuple

from pydantic import BaseModel, EmailStr, ValidationError

from app.config import OUTPUT_DIR
from app.models import Certificate, Job, Recipient

MAX_NAME_LENGTH = 200


class _EmailCheck(BaseModel):
    email: EmailStr


def validate_recipient(name: Optional[str], email: Optional[str]) -> Optional[str]:
    if name is None or not name.strip():
        return "Recipient name is required"
    if len(name.strip()) > MAX_NAME_LENGTH:
        return f"Recipient name exceeds {MAX_NAME_LENGTH} characters"
    if email is not None and email.strip():
        try:
            _EmailCheck(email=email.strip())
        except ValidationError:
            return "Invalid email address"
    return None


def generate_certificate_pdf(job: Job, recipient: Recipient, output_dir: Optional[str] = None) -> str:
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas

    directory = output_dir or OUTPUT_DIR
    os.makedirs(directory, exist_ok=True)
    filename = f"{uuid.uuid4()}.pdf"
    path = os.path.join(directory, filename)

    c = canvas.Canvas(path, pagesize=landscape(letter))
    width, height = landscape(letter)

    c.setStrokeColorRGB(0.2, 0.2, 0.6)
    c.setLineWidth(3)
    c.rect(0.5 * inch, 0.5 * inch, width - inch, height - inch)

    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0.1, 0.1, 0.4)
    c.drawCentredString(width / 2, height - 1.8 * inch, "Certificate of Completion")

    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 2.6 * inch, "This is to certify that")

    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 3.4 * inch, recipient.name.strip())

    c.setFont("Helvetica", 16)
    c.drawCentredString(
        width / 2,
        height - 4.2 * inch,
        f"has successfully completed {job.course_name} ({job.event_name})",
    )

    c.drawCentredString(width / 2, height - 4.9 * inch, f"Issued on {job.issue_date.isoformat()}")

    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(width / 2, height - 5.6 * inch, f"{job.issuer_name}")

    c.setLineWidth(1)
    c.line(width / 2 - 1.5 * inch, 1.3 * inch, width / 2 + 1.5 * inch, 1.3 * inch)
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 1.1 * inch, "Authorized Signature")

    c.save()
    return path
