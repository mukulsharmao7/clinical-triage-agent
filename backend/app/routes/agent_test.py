from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.services.gemini_service import (
    get_triage_reasoning,
    get_multimodal_triage_reasoning,
    transcribe_audio,
    get_full_multimodal_triage_reasoning,
    parse_triage_response
)
from app.auth import get_current_clinician
from app import models
from pydantic import BaseModel
import shutil
import os
from app.agent.triage_agent import run_triage_agent


router = APIRouter(prefix="/agent-test", tags=["agent-test"])


class SymptomsInput(BaseModel):
    symptoms_text: str


def save_upload(upload_file: UploadFile, upload_dir: str = "app/uploads") -> str:
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, upload_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path


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
    file_path = save_upload(image)
    raw_response = get_multimodal_triage_reasoning(symptoms_text, file_path)
    parsed = parse_triage_response(raw_response)
    return {"raw_response": raw_response, "parsed": parsed, "image_saved_as": image.filename}


@router.post("/transcribe")
async def test_transcribe(
    audio: UploadFile = File(...),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    file_path = save_upload(audio)
    transcript = transcribe_audio(file_path)
    return {"transcript": transcript, "audio_saved_as": audio.filename}


@router.post("/reason-full")
async def test_full_reasoning(
    symptoms_text: str = Form(...),
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    image_path = save_upload(image) if image else None

    audio_transcript = None
    if audio:
        audio_path = save_upload(audio)
        audio_transcript = transcribe_audio(audio_path)

    raw_response = get_full_multimodal_triage_reasoning(symptoms_text, image_path, audio_transcript)
    parsed = parse_triage_response(raw_response)

    return {
        "raw_response": raw_response,
        "parsed": parsed,
        "audio_transcript": audio_transcript
    }
@router.post("/reason-agent")
async def test_agent_reasoning(
    symptoms_text: str = Form(...),
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    image_path = save_upload(image) if image else None

    audio_transcript = None
    if audio:
        from app.services.gemini_service import transcribe_audio
        audio_path = save_upload(audio)
        audio_transcript = transcribe_audio(audio_path)

    result = run_triage_agent(symptoms_text, image_path, audio_transcript)

    return {
        "retrieved_guidelines": result["retrieved_guidelines"],
        "raw_reasoning": result["raw_reasoning"],
        "parsed_result": result["parsed_result"]
    }