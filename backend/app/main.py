from fastapi import FastAPI
from app.routes import (
    patients, cases, proposals, clinician_actions, auth, agent_test, rag_test,
    patient_profile, insurance, hospitalization, diet_plan
)

app = FastAPI(title="Clinical Triage Agent API")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(cases.router)
app.include_router(proposals.router)
app.include_router(clinician_actions.router)
app.include_router(agent_test.router)
app.include_router(rag_test.router)
app.include_router(patient_profile.router)
app.include_router(insurance.router)
app.include_router(hospitalization.router)
app.include_router(diet_plan.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Clinical Triage Agent API is running"}

from app.routes import (
    patients, cases, proposals, clinician_actions, auth, agent_test, rag_test,
    patient_profile, insurance, hospitalization, diet_plan, documents
)

app.include_router(documents.router)