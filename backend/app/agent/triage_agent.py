from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from app.services.rag_service import search_guidelines
from app.services.gemini_service import model, parse_triage_response
from app import models
from PIL import Image


class TriageState(TypedDict):
    symptoms_text: str
    image_path: Optional[str]
    audio_transcript: Optional[str]
    retrieved_guidelines: list
    red_flags: list
    raw_reasoning: str
    parsed_result: dict


RED_FLAG_KEYWORDS = ["chest pain", "difficulty breathing", "unconscious", "severe bleeding",
                     "stroke", "seizure", "suicidal", "can't breathe"]


def retrieve_guidelines_node(state: TriageState) -> TriageState:
    guidelines = search_guidelines(state["symptoms_text"], n_results=2)
    state["retrieved_guidelines"] = guidelines
    return state


def check_red_flags_node(state: TriageState) -> TriageState:
    text_lower = state["symptoms_text"].lower()
    flags_found = [kw for kw in RED_FLAG_KEYWORDS if kw in text_lower]
    state["red_flags"] = flags_found
    return state


def reason_node(state: TriageState) -> TriageState:
    guidelines_text = "\n".join(f"- {g}" for g in state["retrieved_guidelines"])
    red_flags_text = ", ".join(state["red_flags"]) if state["red_flags"] else "None detected"

    context_lines = [f"Symptoms (typed): {state['symptoms_text']}"]
    if state.get("audio_transcript"):
        context_lines.append(f"Symptoms (spoken, transcribed): {state['audio_transcript']}")

    prompt = f"""You are a clinical triage assistant. You do NOT diagnose or prescribe treatment.

Relevant clinical triage guidelines retrieved from the knowledge base:
{guidelines_text}

Automated red-flag keyword check found: {red_flags_text}

Patient information:
{chr(10).join(context_lines)}

Using the guidelines and red-flag findings above as reference where relevant, provide:
1. A triage urgency level: one of "low", "moderate", "urgent", "emergency"
2. A brief reasoning (2-3 sentences) that references the guidelines where applicable
3. A recommended next step

Respond in this exact format:
TRIAGE_LEVEL: <level>
REASONING: <reasoning>
RECOMMENDED_ACTION: <action>
"""

    content_parts = [prompt]
    if state.get("image_path"):
        image = Image.open(state["image_path"])
        content_parts.append(image)

    response = model.generate_content(content_parts)
    state["raw_reasoning"] = response.text
    return state


def parse_node(state: TriageState) -> TriageState:
    state["parsed_result"] = parse_triage_response(state["raw_reasoning"])
    return state


def build_triage_graph():
    graph = StateGraph(TriageState)

    graph.add_node("retrieve_guidelines", retrieve_guidelines_node)
    graph.add_node("check_red_flags", check_red_flags_node)
    graph.add_node("reason", reason_node)
    graph.add_node("parse", parse_node)

    graph.set_entry_point("retrieve_guidelines")
    graph.add_edge("retrieve_guidelines", "check_red_flags")
    graph.add_edge("check_red_flags", "reason")
    graph.add_edge("reason", "parse")
    graph.add_edge("parse", END)

    return graph.compile()


triage_graph = build_triage_graph()


def run_triage_agent(symptoms_text: str, image_path: str = None, audio_transcript: str = None) -> dict:
    initial_state: TriageState = {
        "symptoms_text": symptoms_text,
        "image_path": image_path,
        "audio_transcript": audio_transcript,
        "retrieved_guidelines": [],
        "red_flags": [],
        "raw_reasoning": "",
        "parsed_result": {}
    }

    final_state = triage_graph.invoke(initial_state)
    return final_state


def run_agent_and_save_proposal(case_id: int, db: Session) -> models.AgentProposal:
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise ValueError("Case not found")

    result = run_triage_agent(
        symptoms_text=case.symptoms_text,
        image_path=case.image_path,
        audio_transcript=case.audio_transcript
    )

    parsed = result["parsed_result"]

    new_proposal = models.AgentProposal(
        case_id=case.id,
        reasoning=parsed.get("reasoning", "") or result["raw_reasoning"],
        triage_level=parsed.get("triage_level", "unknown"),
        recommended_action=parsed.get("recommended_action", ""),
        status="pending"
    )
    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)

    return new_proposal