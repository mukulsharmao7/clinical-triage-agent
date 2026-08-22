from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app import models, schemas

router = APIRouter(prefix="/proposals", tags=["proposals"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.AgentProposalResponse)
def create_proposal(proposal: schemas.AgentProposalCreate, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.id == proposal.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found — cannot create proposal for a nonexistent case")

    new_proposal = models.AgentProposal(**proposal.dict(), status="pending")
    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)
    return new_proposal

@router.get("/", response_model=list[schemas.AgentProposalResponse])
def list_proposals(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.AgentProposal)
    if status is not None:
        query = query.filter(models.AgentProposal.status == status)
    return query.all()

@router.get("/{proposal_id}", response_model=schemas.AgentProposalResponse)
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(models.AgentProposal).filter(models.AgentProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal