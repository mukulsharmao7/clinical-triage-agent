from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ---------- Patient ----------

class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    name: str
    age: Optional[int]
    gender: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True   # lets Pydantic read data from SQLAlchemy objects directly


# ---------- Case ----------

class CaseCreate(BaseModel):
    patient_id: int
    symptoms_text: str
    image_path: Optional[str] = None
    audio_transcript: Optional[str] = None

class CaseResponse(BaseModel):
    id: int
    patient_id: int
    symptoms_text: str
    image_path: Optional[str]
    audio_transcript: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True