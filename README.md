# Clinical Triage Agent

## Problem Statement
Emergency and outpatient triage requires synthesizing multiple data types —
patient-reported symptoms, visual evidence (e.g. X-rays), and clinical notes —
usually reviewed sequentially by a human. This project is a full-stack AI
assistant that ingests text and image inputs, reasons about urgency through
an agentic pipeline grounded in retrieved medical guidelines, and proposes a
triage action that a clinician must approve. The system never acts
autonomously on patient care — every action requires human sign-off.

## Tech Stack
| Layer | Tool |
|---|---|
| Frontend | React (Vite) + Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy |
| Vector DB (RAG) | ChromaDB |
| Agent orchestration | LangGraph |
| LLM | Google Gemini API (multimodal — text + image) |
| Deployment | Vercel (frontend), Render (backend + DB) |
| Database | PostgreSQL (via Docker) + SQLAlchemy ORM |

## Known Limitations
- Uses Gemini's free tier for development, which has daily rate limits —
  fine for demo/learning purposes, not production-scale.
- This is a learning/portfolio project demonstrating agentic architecture
  and human-in-the-loop safety design — not a clinical-grade diagnostic tool.

## 🚧 Build Log

| Day | Date | What was done |
|-----|------|----------------|
| 1 | 2026-08-18 | Project architecture defined, repo structure created (backend/frontend split), Python venv + backend dependencies installed, React (Vite) frontend scaffolded, Gemini API integrated, .gitignore + .env configured for secret safety |
| 2 | 2026-08-19 | Dockerized PostgreSQL via docker-compose, FastAPI skeleton with health check endpoint, SQLAlchemy database connection setup, first table (patients) created and verified |
| 3 | 2026-08-20 | Remaining models added (cases, agent_proposals, clinician_actions) with relationships, Pydantic schemas introduced, Alembic migrations set up and applied, first CRUD endpoints built and tested (POST/GET patients) via /docs |
| 4 | 2026-08-21 | CRUD endpoints built for cases, agent_proposals, and clinician_actions; query filtering added (cases by patient, proposals by status); business logic enforced (no duplicate proposal resolution); full end-to-end relationship chain tested via /docs |
| 5 | 2026-08-22 | JWT authentication added — Clinician model, password hashing (bcrypt), signup/login endpoints, protected clinician-actions route via dependency injection, tested full auth flow |
| 6 | 2026-08-22 | Gemini API integrated via google-generativeai SDK, service module pattern introduced, structured prompt engineering for triage reasoning, response parsing, protected test endpoint built and verified |
| 7 | 2026-08-25 | Multimodal Gemini integration — image upload endpoint added (UploadFile + Form), get_multimodal_triage_reasoning() combines text + image in single Gemini call, tested via /docs with real image upload |
| 8 | 2026-08-26 | Audio input added — transcribe_audio() using direct bytes (bypassed deprecated upload_file() bug), get_full_multimodal_triage_reasoning() combines text+image+audio, new routes (/transcribe, /reason-full), fixed model deprecation (gemini-2.5-flash → gemini-3.6-flash), tested Hindi audio transcription successfully |
| 9 | 2026-08-27 | ChromaDB (persistent vector store) set up, synthetic triage guidelines dataset created, RAG service built (Gemini embeddings for document storage + semantic query search), fixed embedding model deprecation (text-embedding-004 → gemini-embedding-001), tested and confirmed semantic matching works correctly |
| 10 | 2026-08-28 | LangGraph agent built — TriageState defined, 3-node graph (retrieve_guidelines → reason → parse), RAG integrated directly into agent reasoning flow, tested end-to-end — agent correctly retrieved relevant guideline, explicitly referenced it in reasoning, and produced accurate emergency-level triage with actionable recommendation |