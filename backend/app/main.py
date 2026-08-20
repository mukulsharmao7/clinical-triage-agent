from fastapi import FastAPI
from app.routes import patients

app = FastAPI(title="Clinical Triage Agent API")

app.include_router(patients.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Clinical Triage Agent API is running"}