from fastapi import FastAPI
from app.routes import patients, cases, proposals, clinician_actions
from app.routes import patients, cases, proposals, clinician_actions, auth

from app.routes import patients, cases, proposals, clinician_actions, auth, agent_test

from app.routes import patients, cases, proposals, clinician_actions, auth, agent_test, rag_test



app = FastAPI(title="Clinical Triage Agent API")

app.include_router(patients.router)
app.include_router(cases.router)
app.include_router(proposals.router)
app.include_router(clinician_actions.router)
app.include_router(auth.router)

app.include_router(agent_test.router)
app.include_router(rag_test.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Clinical Triage Agent API is running"}