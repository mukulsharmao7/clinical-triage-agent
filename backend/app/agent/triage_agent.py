from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.services.rag_service import search_guidelines
from app.services.gemini_service import model, parse_triage_response
from PIL import Image


class TriageState(TypedDict):
    symptoms_text: str
    image_path: Optional[str]
    audio_transcript: Optional[str]
    retrieved_guidelines: list
    raw_reasoning: str
    parsed_result: dict


def retrieve_guidelines_node(state: TriageState) -> TriageState:
    guidelines = search_guidelines(state["symptoms_text"], n_results=2)
    state["retrieved_guidelines"] = guidelines
    return state


def reason_node(state: TriageState) -> TriageState:
    guidelines_text = "\n".join(f"- {g}" for g in state["retrieved_guidelines"])

    context_lines = [f"Symptoms (typed): {state['symptoms_text']}"]
    if state.get("audio_transcript"):
        context_lines.append(f"Symptoms (spoken, transcribed): {state['audio_transcript']}")

    prompt = f"""You are a clinical triage assistant. You do NOT diagnose or prescribe treatment.

Relevant clinical triage guidelines retrieved from the knowledge base:
{guidelines_text}

Patient information:
{chr(10).join(context_lines)}

Using the guidelines above as reference where relevant, provide:
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
    graph.add_node("reason", reason_node)
    graph.add_node("parse", parse_node)

    graph.set_entry_point("retrieve_guidelines")
    graph.add_edge("retrieve_guidelines", "reason")
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
        "raw_reasoning": "",
        "parsed_result": {}
    }

    final_state = triage_graph.invoke(initial_state)
    return final_state