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

# AGENT PROPOSALS  

# ---------- Agent Proposal ----------

class AgentProposalCreate(BaseModel):
    case_id: int
    reasoning: str
    triage_level: str
    recommended_action: str

class AgentProposalResponse(BaseModel):
    id: int
    case_id: int
    reasoning: str
    triage_level: str
    recommended_action: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Clinician Action ----------

class ClinicianActionCreate(BaseModel):
    proposal_id: int
    decision: str
    notes: Optional[str] = None

class ClinicianActionResponse(BaseModel):
    id: int
    proposal_id: int
    decision: str
    notes: Optional[str]
    decided_at: datetime

    class Config:
        from_attributes = True
        
        
        

class ClinicianCreate(BaseModel):
    email: str
    password: str
    full_name: str
class ClinicianResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str