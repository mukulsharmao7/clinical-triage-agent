from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas

from app.auth import get_current_clinician

router = APIRouter(prefix="/clinician-actions", tags=["clinician-actions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ClinicianActionResponse)


def create_clinician_action(
    action: schemas.ClinicianActionCreate,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    proposal = db.query(models.AgentProposal).filter(
        models.AgentProposal.id == action.proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != "pending":
        raise HTTPException(status_code=400,
            detail=f"Proposal already resolved with status '{proposal.status}'")

    new_action = models.ClinicianAction(**action.dict())
    db.add(new_action)
    proposal.status = action.decision
    db.add(proposal)
    db.commit()
    db.refresh(new_action)
    return new_action

@router.get("/{action_id}", response_model=schemas.ClinicianActionResponse)
def get_clinician_action(action_id: int, db: Session = Depends(get_db)):
    action = db.query(models.ClinicianAction).filter(models.ClinicianAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action



