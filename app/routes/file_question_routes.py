from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.file_question_service import search_file_chunks
from app.services.llm_service import generate_answer

router = APIRouter(
    prefix="/api",
    tags=["File Questions"]
)


class FileQuestionRequest(BaseModel):
    repository_id: int
    file_path: str
    question: str


@router.post("/ask-file")
def ask_about_file(request: FileQuestionRequest):

    results = search_file_chunks(
        question=request.question,
        repository_id=request.repository_id,
        file_path=request.file_path,
        limit=5
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="File or relevant code not found"
        )

    context_parts = []

    for result in results:
        context_parts.append(
            f"""
File: {request.file_path}
Lines: {result.start_line}-{result.end_line}
Chunk: {result.chunk_index}

{result.content}
"""
        )

    context = "\n".join(context_parts)

    answer = generate_answer(
        question=request.question,
        context=context
    )

    sources = []

    for result in results:
        sources.append({
            "file": request.file_path,
            "chunk": result.chunk_index,
            "start_line": result.start_line,
            "end_line": result.end_line
        })

    return {
        "repository_id": request.repository_id,
        "file": request.file_path,
        "question": request.question,
        "answer": answer,
        "sources": sources
    }