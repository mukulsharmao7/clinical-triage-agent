from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.auth import get_current_clinician

router = APIRouter(prefix="/diet-plan", tags=["diet-plan"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.DietPlanResponse)
def create_or_update_diet_plan(
    plan: schemas.DietPlanCreate,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    existing = db.query(models.DietPlan).filter(
        models.DietPlan.patient_id == plan.patient_id
    ).first()

    if existing:
        for key, value in plan.dict(exclude={"patient_id"}).items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    new_plan = models.DietPlan(**plan.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@router.get("/{patient_id}", response_model=schemas.DietPlanResponse)
def get_diet_plan(
    patient_id: int,
    db: Session = Depends(get_db),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    plan = db.query(models.DietPlan).filter(models.DietPlan.patient_id == patient_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    return plan