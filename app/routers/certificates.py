import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate

router = APIRouter(prefix="/api/v1/certificates", tags=["certificates"])


@router.get("/{certificate_id}/download")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate file missing")
    return FileResponse(cert.file_path, media_type="application/pdf", filename=f"certificate_{cert.id}.pdf")
