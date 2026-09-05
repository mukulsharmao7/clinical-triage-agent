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
    latitude: Optional[str] = None
    longitude: Optional[str] = None

class CaseResponse(BaseModel):
    id: int
    patient_id: int
    symptoms_text: str
    image_path: Optional[str]
    audio_transcript: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
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


# ---------- Patient Profile ----------

class PatientProfileCreate(BaseModel):
    patient_id: int
    chronic_conditions: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

class PatientProfileResponse(BaseModel):
    id: int
    patient_id: int
    chronic_conditions: Optional[str]
    allergies: Optional[str]
    current_medications: Optional[str]
    blood_group: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Insurance ----------

class InsurancePolicyCreate(BaseModel):
    patient_id: int
    provider_name: str
    policy_number: str
    coverage_amount: Optional[int] = None
    valid_until: Optional[datetime] = None

class InsurancePolicyResponse(BaseModel):
    id: int
    patient_id: int
    provider_name: str
    policy_number: str
    coverage_amount: Optional[int]
    valid_until: Optional[datetime]
    is_synthetic: str
    created_at: datetime

    class Config:
        from_attributes = True


class InsuranceClaimCreate(BaseModel):
    policy_id: int
    claim_amount: int
    claim_reason: str

class InsuranceClaimResponse(BaseModel):
    id: int
    policy_id: int
    claim_amount: int
    claim_reason: str
    status: str
    filed_at: datetime

    class Config:
        from_attributes = True


# ---------- Hospitalization ----------

class HospitalizationCreate(BaseModel):
    patient_id: int
    hospital_name: str
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    diagnosis: str
    treatment_summary: Optional[str] = None

class HospitalizationResponse(BaseModel):
    id: int
    patient_id: int
    hospital_name: str
    admission_date: datetime
    discharge_date: Optional[datetime]
    diagnosis: str
    treatment_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Diet Plan ----------

class DietPlanCreate(BaseModel):
    patient_id: int
    diet_type: Optional[str] = None
    daily_calorie_target: Optional[int] = None
    activity_level: Optional[str] = None
    sleep_hours_avg: Optional[int] = None
    notes: Optional[str] = None

class DietPlanResponse(BaseModel):
    id: int
    patient_id: int
    diet_type: Optional[str]
    daily_calorie_target: Optional[int]
    activity_level: Optional[str]
    sleep_hours_avg: Optional[int]
    notes: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True
        
class PatientDocumentResponse(BaseModel):
    id: int
    patient_id: int
    file_path: str
    document_type: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True