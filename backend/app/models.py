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