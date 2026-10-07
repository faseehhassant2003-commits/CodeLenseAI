from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/api",
    tags=["RAG"]
)


class AskRequest(BaseModel):
    repository_id: int
    question: str


@router.post("/ask")
def ask_question(request: AskRequest):

    result = answer_question(
        question=request.question,
        repository_id=request.repository_id
    )

    return {
        "repository_id": request.repository_id,
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }