import os
import re
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.6-flash")


def get_triage_reasoning(symptoms_text: str) -> str:
    prompt = f"""You are a clinical triage assistant. You do NOT diagnose or prescribe treatment.
Given the following patient-reported symptoms, provide:
1. A triage urgency level: one of "low", "moderate", "urgent", "emergency"
2. A brief reasoning (2-3 sentences) for that level
3. A recommended next step (e.g. "refer to ER", "schedule routine visit")

Symptoms: {symptoms_text}

Respond in this exact format:
TRIAGE_LEVEL: <level>
REASONING: <reasoning>
RECOMMENDED_ACTION: <action>
"""
    response = model.generate_content(prompt)
    return response.text


def get_multimodal_triage_reasoning(symptoms_text: str, image_path: str) -> str:
    image = Image.open(image_path)

    prompt = f"""You are a clinical triage assistant. You do NOT diagnose or prescribe treatment.
You are given a patient's symptom description AND a medical image (e.g. X-ray, skin photo).
Analyze both together and provide:
1. A triage urgency level: one of "low", "moderate", "urgent", "emergency"
2. A brief reasoning (2-3 sentences) referencing BOTH the text and visible image findings
3. A recommended next step

Symptoms: {symptoms_text}

Respond in this exact format:
TRIAGE_LEVEL: <level>
REASONING: <reasoning>
RECOMMENDED_ACTION: <action>
"""
    response = model.generate_content([prompt, image])
    return response.text


def transcribe_audio(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    prompt = "Transcribe this audio recording word-for-word. Return ONLY the transcribed text, nothing else."

    response = model.generate_content([
        prompt,
        {"mime_type": "audio/mp4", "data": audio_bytes}
    ])
    return response.text.strip()
def get_full_multimodal_triage_reasoning(symptoms_text: str, image_path: str = None, audio_transcript: str = None) -> str:
    combined_context = f"Symptoms (typed): {symptoms_text}"
    if audio_transcript:
        combined_context += f"\nSymptoms (spoken, transcribed): {audio_transcript}"

    prompt = f"""You are a clinical triage assistant. You do NOT diagnose or prescribe treatment.
You are given patient information that may include typed symptoms, a spoken description
(already transcribed to text), and a medical image. Analyze all available information together.

{combined_context}

Provide:
1. A triage urgency level: one of "low", "moderate", "urgent", "emergency"
2. A brief reasoning (2-3 sentences) referencing all available inputs
3. A recommended next step

Respond in this exact format:
TRIAGE_LEVEL: <level>
REASONING: <reasoning>
RECOMMENDED_ACTION: <action>
"""

    content_parts = [prompt]
    if image_path:
        image = Image.open(image_path)
        content_parts.append(image)

    response = model.generate_content(content_parts)
    return response.text


def parse_triage_response(raw_text: str) -> dict:
    clean_text = raw_text.replace("*", "").replace("#", "")

    result = {"triage_level": "", "reasoning": "", "recommended_action": ""}

    triage_match = re.search(r"TRIAGE_LEVEL:\s*(.+)", clean_text, re.IGNORECASE)
    if triage_match:
        result["triage_level"] = triage_match.group(1).strip().split("\n")[0].lower()

    reasoning_match = re.search(
        r"REASONING:\s*(.+?)(?=RECOMMENDED_ACTION:|$)", clean_text, re.IGNORECASE | re.DOTALL
    )
    if reasoning_match:
        result["reasoning"] = reasoning_match.group(1).strip()

    action_match = re.search(r"RECOMMENDED_ACTION:\s*(.+)", clean_text, re.IGNORECASE | re.DOTALL)
    if action_match:
        result["recommended_action"] = action_match.group(1).strip()

    return result