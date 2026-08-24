from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/signup", response_model=schemas.ClinicianResponse)
def signup(clinician: schemas.ClinicianCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Clinician).filter(models.Clinician.email == clinician.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_clinician = models.Clinician(
        email=clinician.email,
        hashed_password=hash_password(clinician.password),
        full_name=clinician.full_name
    )
    db.add(new_clinician)
    db.commit()
    db.refresh(new_clinician)
    return new_clinician



@router.post("/login", response_model=schemas.Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    clinician = db.query(models.Clinician).filter(models.Clinician.email == email).first()
    if not clinician or not verify_password(password, clinician.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": clinician.email})
    return {"access_token": access_token, "token_type": "bearer"}