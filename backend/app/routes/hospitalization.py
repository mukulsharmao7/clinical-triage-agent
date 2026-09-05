from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app import models, schemas
from app.auth import get_current_clinician

router = APIRouter(prefix="/hospitalizations", tags=["hospitalizations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.HospitalizationResponse)
def create_hospitalization(
    record: schemas.HospitalizationCreate,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    new_record = models.Hospitalization(**record.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.get("/", response_model=list[schemas.HospitalizationResponse])
def list_hospitalizations(
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    query = db.query(models.Hospitalization)
    if patient_id is not None:
        query = query.filter(models.Hospitalization.patient_id == patient_id)
    return query.order_by(models.Hospitalization.admission_date.desc()).all()