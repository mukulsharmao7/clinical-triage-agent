from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import shutil
import os
from app.database import SessionLocal
from app import models, schemas
from app.auth import get_current_clinician

router = APIRouter(prefix="/documents", tags=["documents"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=schemas.PatientDocumentResponse)
async def upload_document(
    patient_id: int = Form(...),
    document_type: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    upload_dir = "app/uploads/documents"
    os.makedirs(upload_dir, exist_ok=True)
    safe_filename = f"{patient_id}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = models.PatientDocument(
        patient_id=patient_id,
        file_path=file_path,
        document_type=document_type
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@router.get("/", response_model=list[schemas.PatientDocumentResponse])
def list_documents(
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    query = db.query(models.PatientDocument)
    if patient_id is not None:
        query = query.filter(models.PatientDocument.patient_id == patient_id)
    return query.order_by(models.PatientDocument.uploaded_at.desc()).all()

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    doc = db.query(models.PatientDocument).filter(models.PatientDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
    return {"detail": "Document deleted"}