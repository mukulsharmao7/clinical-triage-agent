from fastapi import APIRouter, Depends
from app.services.gemini_service import get_triage_reasoning, parse_triage_response
from app.auth import get_current_clinician
from app import models
from pydantic import BaseModel
from fastapi import UploadFile, File, Form
from app.services.gemini_service import get_multimodal_triage_reasoning, parse_triage_response
import shutil
import os

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

@router.post("/reason-multimodal")
async def test_multimodal_reasoning(
    symptoms_text: str = Form(...),
    image: UploadFile = File(...),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    upload_dir = "app/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, image.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    raw_response = get_multimodal_triage_reasoning(symptoms_text, file_path)
    parsed = parse_triage_response(raw_response)
    return {"raw_response": raw_response, "parsed": parsed, "image_saved_as": image.filename}