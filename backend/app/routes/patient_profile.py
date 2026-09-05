from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.auth import get_current_clinician

router = APIRouter(prefix="/patient-profile", tags=["patient-profile"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.PatientProfileResponse)
def create_or_update_profile(
    profile: schemas.PatientProfileCreate,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    existing = db.query(models.PatientProfile).filter(
        models.PatientProfile.patient_id == profile.patient_id
    ).first()

    if existing:
        for key, value in profile.dict(exclude={"patient_id"}).items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    new_profile = models.PatientProfile(**profile.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@router.get("/{patient_id}", response_model=schemas.PatientProfileResponse)
def get_profile(
    patient_id: int,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    profile = db.query(models.PatientProfile).filter(
        models.PatientProfile.patient_id == patient_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile