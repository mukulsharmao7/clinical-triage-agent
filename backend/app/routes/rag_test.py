from fastapi import APIRouter, Depends
from app.services.rag_service import populate_guidelines, search_guidelines
from app.auth import get_current_clinician
from app import models
from pydantic import BaseModel

router = APIRouter(prefix="/rag-test", tags=["rag-test"])


class SearchQuery(BaseModel):
    query_text: str


@router.post("/populate")
def run_populate(current_clinician: models.Clinician = Depends(get_current_clinician)):
    result = populate_guidelines()
    return {"status": result}


@router.post("/search")
def run_search(
    query: SearchQuery,
    current_clinician: models.Clinician = Depends(get_current_clinician)
):
    results = search_guidelines(query.query_text)
    return {"matched_guidelines": results}