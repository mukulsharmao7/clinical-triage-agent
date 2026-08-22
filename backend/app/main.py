from fastapi import FastAPI
from app.routes import patients, cases, proposals, clinician_actions

app = FastAPI(title="Clinical Triage Agent API")

app.include_router(patients.router)
app.include_router(cases.router)
app.include_router(proposals.router)
app.include_router(clinician_actions.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Clinical Triage Agent API is running"}