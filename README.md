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