from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app import models, schemas
from app.auth import get_current_clinician

router = APIRouter(prefix="/insurance", tags=["insurance"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/policies", response_model=schemas.InsurancePolicyResponse)
def create_policy(
    policy: schemas.InsurancePolicyCreate,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    new_policy = models.InsurancePolicy(**policy.dict(), is_synthetic="true")
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    return new_policy

@router.get("/policies", response_model=list[schemas.InsurancePolicyResponse])
def list_policies(
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    query = db.query(models.InsurancePolicy)
    if patient_id is not None:
        query = query.filter(models.InsurancePolicy.patient_id == patient_id)
    return query.all()

@router.post("/claims", response_model=schemas.InsuranceClaimResponse)
def create_claim(
    claim: schemas.InsuranceClaimCreate,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    policy = db.query(models.InsurancePolicy).filter(
        models.InsurancePolicy.id == claim.policy_id
    ).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    new_claim = models.InsuranceClaim(**claim.dict())
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    return new_claim

@router.get("/claims", response_model=list[schemas.InsuranceClaimResponse])
def list_claims(
    policy_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    query = db.query(models.InsuranceClaim)
    if policy_id is not None:
        query = query.filter(models.InsuranceClaim.policy_id == policy_id)
    return query.all()