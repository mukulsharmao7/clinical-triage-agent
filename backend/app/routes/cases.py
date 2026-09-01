from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app import models, schemas
from app.agent.triage_agent import run_agent_and_save_proposal
from app.auth import get_current_clinician

router = APIRouter(prefix="/cases", tags=["cases"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.CaseResponse)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == case.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found — cannot create case for a nonexistent patient")

    new_case = models.Case(**case.dict())
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

@router.get("/", response_model=list[schemas.CaseResponse])
def list_cases(patient_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Case)
    if patient_id is not None:
        query = query.filter(models.Case.patient_id == patient_id)
    return query.all()

from app.services.hospital_service import find_nearby_hospitals

@router.get("/nearby-hospitals")
def get_nearby_hospitals(
    latitude: str,
    longitude: str,
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    hospitals = find_nearby_hospitals(latitude, longitude)
    return {"hospitals": hospitals}

@router.get("/{case_id}", response_model=schemas.CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/{case_id}/run-agent")
def run_agent_for_existing_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    result = run_agent_and_save_proposal(case_id, db)
    proposal = result["proposal"]
    emergency = result["emergency"]

    return {
        "case_id": case_id,
        "proposal_id": proposal.id,
        "triage_level": proposal.triage_level,
        "status": proposal.status,
        "emergency": emergency
    }
