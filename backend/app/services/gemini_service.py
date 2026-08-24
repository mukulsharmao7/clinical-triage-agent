import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

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
    
def parse_triage_response(raw_text: str) -> dict:
    lines = raw_text.strip().split("\n")
    result = {"triage_level": "", "reasoning": "", "recommended_action": ""}
    for line in lines:
        if line.startswith("TRIAGE_LEVEL:"):
            result["triage_level"] = line.replace("TRIAGE_LEVEL:", "").strip().lower()
        elif line.startswith("REASONING:"):
            result["reasoning"] = line.replace("REASONING:", "").strip()
        elif line.startswith("RECOMMENDED_ACTION:"):
            result["recommended_action"] = line.replace("RECOMMENDED_ACTION:", "").strip()
        return result