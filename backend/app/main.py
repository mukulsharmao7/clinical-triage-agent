from fastapi import FastAPI
from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinical Triage Agent API")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Clinical Triage Agent API is running"}