from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cases = relationship("Case", back_populates="patient")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    symptoms_text = Column(Text, nullable=False)
    image_path = Column(String, nullable=True)
    audio_transcript = Column(Text, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="cases")
    proposals = relationship("AgentProposal", back_populates="case")
    
    
class AgentProposal(Base):
    __tablename__ = "agent_proposals"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    reasoning = Column(Text, nullable=False)
    triage_level = Column(String, nullable=False)
    recommended_action = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, approved, edited, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="proposals")
    clinician_action = relationship("ClinicianAction", back_populates="proposal", uselist=False)


class ClinicianAction(Base):
    __tablename__ = "clinician_actions"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("agent_proposals.id"), nullable=False)
    decision = Column(String, nullable=False)  # approved, edited, rejected
    notes = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), server_default=func.now())

    proposal = relationship("AgentProposal", back_populates="clinician_action")
    
class Clinician(Base):
    __tablename__="Clinicians"
    id = Column(Integer,primary_key=True,index =True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, unique=True)
    chronic_conditions = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    blood_group = Column(String, nullable=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", backref="profile")


class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_name = Column(String, nullable=False)
    policy_number = Column(String, nullable=False)
    coverage_amount = Column(Integer, nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_synthetic = Column(String, default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", backref="insurance_policies")


class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("insurance_policies.id"), nullable=False)
    claim_amount = Column(Integer, nullable=False)
    claim_reason = Column(String, nullable=False)
    status = Column(String, default="submitted")
    filed_at = Column(DateTime(timezone=True), server_default=func.now())

    policy = relationship("InsurancePolicy", backref="claims")


class Hospitalization(Base):
    __tablename__ = "hospitalizations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    hospital_name = Column(String, nullable=False)
    admission_date = Column(DateTime(timezone=True), nullable=False)
    discharge_date = Column(DateTime(timezone=True), nullable=True)
    diagnosis = Column(Text, nullable=False)
    treatment_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", backref="hospitalizations")


class DietPlan(Base):
    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, unique=True)
    diet_type = Column(String, nullable=True)
    daily_calorie_target = Column(Integer, nullable=True)
    activity_level = Column(String, nullable=True)
    sleep_hours_avg = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    patient = relationship("Patient", backref="diet_plan")


class PatientDocument(Base):
    __tablename__ = "patient_documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    file_path = Column(String, nullable=False)
    document_type = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", backref="documents")


class EmergencyDispatch(Base):
    __tablename__ = "emergency_dispatches"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    triggered_reason = Column(String, nullable=False)
    ambulance_number_shown = Column(String, default="108")
    nearest_hospitals_json = Column(Text, nullable=True)
    acknowledged = Column(String, default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", backref="emergency_dispatch")
