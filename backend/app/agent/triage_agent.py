import json
import time
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from app.services.rag_service import search_guidelines
from app.services.gemini_service import model
from app.services.emergency_service import get_emergency_response
from app import models
from PIL import Image
from app.services.hospital_service import find_nearby_hospitals


RED_FLAG_WEIGHTS = {
    "chest pain": 3, "difficulty breathing": 3, "can't breathe": 3, "unconscious": 3,
    "unresponsive": 3, "severe bleeding": 3, "stroke": 3, "seizure": 3, "suicidal": 3,
    "worst headache": 3, "blue lips": 3, "not breathing": 3,
    "confusion": 2, "blurred vision": 2, "high fever": 2, "persistent vomiting": 2,
    "severe pain": 2, "rapid heartbeat": 2, "fainting": 2, "vision loss": 2,
    "dizziness": 1, "mild pain": -1, "slight": -1,
}


class TriageState(TypedDict):
    symptoms_text: str
    image_path: Optional[str]
    audio_transcript: Optional[str]
    retrieved_guidelines: list
    red_flags_matched: list
    red_flag_score: int
    red_flag_level: str
    differential_text: str
    verdict: dict
    final_result: dict


def retrieve_guidelines_node(state: TriageState) -> TriageState:
    guidelines = search_guidelines(state["symptoms_text"], n_results=3)
    state["retrieved_guidelines"] = guidelines
    return state


def check_red_flags_node(state: TriageState) -> TriageState:
    text_lower = state["symptoms_text"].lower()
    matched = []
    score = 0
    for phrase, weight in RED_FLAG_WEIGHTS.items():
        if phrase in text_lower:
            matched.append({"phrase": phrase, "weight": weight})
            score += weight

    if score >= 3:
        level = "high"
    elif score >= 1:
        level = "moderate"
    else:
        level = "none"

    state["red_flags_matched"] = matched
    state["red_flag_score"] = score
    state["red_flag_level"] = level
    return state


def differential_node(state: TriageState) -> TriageState:
    guidelines_block = "\n".join(f"[{g['id']}] {g['text']}" for g in state["retrieved_guidelines"])
    flags_block = ", ".join(f["phrase"] for f in state["red_flags_matched"]) if state["red_flags_matched"] else "none detected"

    prompt = f"""You are a clinical triage assistant thinking through a case step by step.
You do NOT diagnose or prescribe treatment. This is an internal reasoning step, not the final answer.

Patient symptoms: {state['symptoms_text']}
Automated red-flag scan found: {flags_block} (severity score: {state['red_flag_score']}/{state['red_flag_level']})

Relevant guidelines retrieved from knowledge base:
{guidelines_block}

Think through this out loud in 3-5 sentences:
- What are 2-3 plausible categories of concern here (not diagnoses, just triage-relevant categories)?
- Which retrieved guideline(s) are most relevant and why?
- Does the red-flag scan result change your thinking?

Write your reasoning as plain text, not JSON.
"""

    content_parts = [prompt]
    if state.get("image_path"):
        content_parts.append(Image.open(state["image_path"]))

    response = model.generate_content(content_parts)
    state["differential_text"] = response.text.strip()
    return state


VERDICT_JSON_INSTRUCTIONS = """
Respond with ONLY valid JSON, no markdown fences, no extra text, in exactly this shape:
{
  "triage_level": "low" | "moderate" | "urgent" | "emergency",
  "confidence": "high" | "medium" | "low",
  "primary_guideline_id": "<id of the single most relevant guideline, or null>",
  "reasoning": "<2-4 sentence clinical reasoning>",
  "recommended_action": "<specific next step>"
}
"""

def reason_node(state: TriageState) -> TriageState:
    guidelines_block = "\n".join(f"[{g['id']}] {g['text']}" for g in state["retrieved_guidelines"])
    flags_block = ", ".join(f["phrase"] for f in state["red_flags_matched"]) if state["red_flags_matched"] else "none detected"

    context_lines = [f"Symptoms (typed): {state['symptoms_text']}"]
    if state.get("audio_transcript"):
        context_lines.append(f"Symptoms (spoken, transcribed): {state['audio_transcript']}")

    prompt = f"""You are a clinical triage assistant. You do NOT diagnose or prescribe treatment.

Your own prior step-by-step reasoning:
{state['differential_text']}

Relevant guidelines:
{guidelines_block}

Automated red-flag scan: {flags_block} (severity score: {state['red_flag_score']}, level: {state['red_flag_level']})

Patient information:
{chr(10).join(context_lines)}

Based on all of the above, give your final triage verdict.
{VERDICT_JSON_INSTRUCTIONS}
"""

    content_parts = [prompt]
    if state.get("image_path"):
        content_parts.append(Image.open(state["image_path"]))

    response = model.generate_content(
        content_parts,
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        verdict = json.loads(response.text)
    except json.JSONDecodeError:
        verdict = {
            "triage_level": "moderate",
            "confidence": "low",
            "primary_guideline_id": None,
            "reasoning": "Automated parsing failed; raw model output: " + response.text[:300],
            "recommended_action": "Manual clinician review required due to parsing error."
        }

    state["verdict"] = verdict
    return state


CRITIQUE_JSON_INSTRUCTIONS = """
Respond with ONLY valid JSON, no markdown fences, in exactly this shape:
{
  "was_appropriate": true | false,
  "final_triage_level": "low" | "moderate" | "urgent" | "emergency",
  "final_confidence": "high" | "medium" | "low",
  "final_reasoning": "<2-4 sentences, revised if needed>",
  "final_recommended_action": "<specific next step, revised if needed>",
  "critique_notes": "<1-2 sentences on what you checked or changed, or 'No changes needed.'>"
}
"""

def critique_node(state: TriageState) -> TriageState:
    verdict = state["verdict"]
    guidelines_block = "\n".join(f"[{g['id']}] {g['text']}" for g in state["retrieved_guidelines"])
    flags_block = ", ".join(f["phrase"] for f in state["red_flags_matched"]) if state["red_flags_matched"] else "none detected"

    prompt = f"""You are a senior clinical triage reviewer double-checking a junior assistant's verdict.
You do NOT diagnose or prescribe treatment. Be appropriately cautious: when in doubt, escalate urgency
rather than downgrade it, and never downgrade urgency if any high-severity red flags were detected.

Original symptoms: {state['symptoms_text']}
Automated red-flag scan: {flags_block} (severity score: {state['red_flag_score']}, level: {state['red_flag_level']})
Relevant guidelines:
{guidelines_block}

Junior assistant's proposed verdict:
- Triage level: {verdict.get('triage_level')}
- Confidence: {verdict.get('confidence')}
- Reasoning: {verdict.get('reasoning')}
- Recommended action: {verdict.get('recommended_action')}

Review this verdict critically. Check: Does it match the guidelines? Does it account for all red flags?
Is the triage level too low given the severity score? Revise if needed, otherwise confirm it.
{CRITIQUE_JSON_INSTRUCTIONS}
"""

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        critique = json.loads(response.text)
    except json.JSONDecodeError:
        critique = {
            "was_appropriate": True,
            "final_triage_level": verdict.get("triage_level", "moderate"),
            "final_confidence": "low",
            "final_reasoning": verdict.get("reasoning", ""),
            "final_recommended_action": verdict.get("recommended_action", ""),
            "critique_notes": "Critique step failed to parse; original verdict passed through unchanged."
        }

    if state["red_flag_level"] == "high" and critique.get("final_triage_level") in ("low", "moderate"):
        critique["final_triage_level"] = "urgent"
        critique["critique_notes"] = critique.get("critique_notes", "") + " [Auto-corrected: high-severity red flags require at least 'urgent' level.]"

    state["final_result"] = {
        "triage_level": critique.get("final_triage_level", "moderate"),
        "confidence": critique.get("final_confidence", "low"),
        "reasoning": critique.get("final_reasoning", ""),
        "recommended_action": critique.get("final_recommended_action", ""),
        "primary_guideline_id": verdict.get("primary_guideline_id"),
        "critique_notes": critique.get("critique_notes", ""),
        "red_flag_level": state["red_flag_level"],
        "differential_text": state["differential_text"]
    }
    return state


def build_triage_graph():
    graph = StateGraph(TriageState)

    graph.add_node("retrieve_guidelines", retrieve_guidelines_node)
    graph.add_node("check_red_flags", check_red_flags_node)
    graph.add_node("differential", differential_node)
    graph.add_node("reason", reason_node)
    graph.add_node("critique", critique_node)

    graph.set_entry_point("retrieve_guidelines")
    graph.add_edge("retrieve_guidelines", "check_red_flags")
    graph.add_edge("check_red_flags", "differential")
    graph.add_edge("differential", "reason")
    graph.add_edge("reason", "critique")
    graph.add_edge("critique", END)

    return graph.compile()


triage_graph = build_triage_graph()


def run_triage_agent(symptoms_text: str, image_path: str = None, audio_transcript: str = None) -> dict:
    initial_state: TriageState = {
        "symptoms_text": symptoms_text,
        "image_path": image_path,
        "audio_transcript": audio_transcript,
        "retrieved_guidelines": [],
        "red_flags_matched": [],
        "red_flag_score": 0,
        "red_flag_level": "none",
        "differential_text": "",
        "verdict": {},
        "final_result": {}
    }
    return triage_graph.invoke(initial_state)


def run_agent_and_save_proposal(case_id: int, db: Session) -> dict:
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise ValueError("Case not found")

    result = run_triage_agent(
        symptoms_text=case.symptoms_text,
        image_path=case.image_path,
        audio_transcript=case.audio_transcript
    )

    final = result["final_result"]

    reasoning_full = (
        f"{final['reasoning']}\n\n"
        f"[Confidence: {final['confidence']} | Red-flag level: {final['red_flag_level']} | "
        f"Primary guideline: {final.get('primary_guideline_id') or 'none'}]\n"
        f"[Critique: {final['critique_notes']}]"
    )

    new_proposal = models.AgentProposal(
        case_id=case.id,
        reasoning=reasoning_full,
        triage_level=final.get("triage_level", "unknown"),
        recommended_action=final.get("recommended_action", ""),
        status="pending"
    )
    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)

    emergency_info = get_emergency_response(
        triage_level=final.get("triage_level", "unknown"),
        red_flag_level=final.get("red_flag_level", "none")
    )
    nearby_hospitals = []
    if emergency_info["emergency_triggered"] and case.latitude and case.longitude:
        nearby_hospitals = find_nearby_hospitals(case.latitude, case.longitude)
        emergency_info["nearby_hospitals"] = nearby_hospitals

    if emergency_info["emergency_triggered"]:
        dispatch = models.EmergencyDispatch(
            case_id=case.id,
            triggered_reason=f"triage_level={final.get('triage_level')}, red_flag_level={final.get('red_flag_level')}",
            ambulance_number_shown=emergency_info["ambulance_number"],
            nearest_hospitals_json=json.dumps(nearby_hospitals)
        )
        db.add(dispatch)
        db.commit()

    return {
        "proposal": new_proposal,
        "emergency": emergency_info
    }