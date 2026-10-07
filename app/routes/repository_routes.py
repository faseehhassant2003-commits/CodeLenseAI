from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Repository
from app.services.repository_ingestion_service import ingest_repository


router = APIRouter(
    prefix="/api/repositories",
    tags=["Repositories"]
)


class RepositoryRequest(BaseModel):
    github_url: str


# =========================================================
# START REPOSITORY INGESTION
# =========================================================

@router.post("/")
def create_repository(
    request: RepositoryRequest,
    background_tasks: BackgroundTasks
):

    # Create repository record immediately
    db = SessionLocal()

    try:

        repository = Repository(
            github_url=request.github_url,
            status="PROCESSING",
            files_processed=0,
            chunks_created=0
        )

        db.add(repository)
        db.commit()
        db.refresh(repository)

        repository_id = repository.id

    finally:
        db.close()

    # Start ingestion in background
    background_tasks.add_task(
        ingest_repository,
        request.github_url,
        repository_id
    )

    return {
        "repository_id": repository_id,
        "status": "PROCESSING",
        "message": "Repository ingestion started"
    }


# =========================================================
# GET REPOSITORY STATUS
# =========================================================

@router.get("/{repository_id}/status")
def get_repository_status(repository_id: int):

    db = SessionLocal()

    try:

        statement = select(Repository).where(
            Repository.id == repository_id
        )

        repository = db.execute(statement).scalar_one_or_none()

        if repository is None:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )

        return {
            "repository_id": repository.id,
            "github_url": repository.github_url,
            "status": repository.status,
            "files_processed": repository.files_processed,
            "chunks_created": repository.chunks_created,
            "embedding_batches_processed": repository.embedding_batches_processed,
            "total_embedding_batches": repository.total_embedding_batches
        
        }

    finally:
        db.close()