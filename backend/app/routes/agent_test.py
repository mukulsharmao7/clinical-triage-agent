from fastapi import APIRouter, Depends
from app.services.gemini_service import get_triage_reasoning, parse_triage_response
from app.auth import get_current_clinician
from app import models
from pydantic import BaseModel

router = APIRouter(prefix="/agent-test", tags=["agent-test"])

class SymptomsInput(BaseModel):
    symptoms_text: str
    
@router.post("/reason")
def test_reasoning(
    input: SymptomsInput,
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    raw_response = get_triage_reasoning(input.symptoms_text)
    parsed = parse_triage_response(raw_response)
    return {"raw_response": raw_response, "parsed": parsed}