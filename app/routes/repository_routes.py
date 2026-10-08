from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.services.repository_file_service import get_repository_files
from app.services.repository_file_content_service import get_file_content
from app.services.github_service import get_latest_commit

from app.database import SessionLocal
from app.models import Repository
from app.services.repository_ingestion_service import ingest_repository

from app.services.repository_overview_service import get_repository_overview

from app.services.repository_architecture_service import (
    get_repository_architecture
)
from app.services.github_service import get_remote_latest_commit

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
    db = SessionLocal()

    try:
        statement = select(Repository).where(
            Repository.github_url == request.github_url
        )

        existing_repository = db.execute(
            statement
        ).scalar_one_or_none()

        # Repository already exists
        if existing_repository:

            # Already processing
            if existing_repository.status == "PROCESSING":
                return {
                    "repository_id": existing_repository.id,
                    "status": "PROCESSING",
                    "message": "Repository is already being processed"
                }

            # Check latest commit on GitHub
            remote_commit = get_remote_latest_commit(
                request.github_url
            )

            # Same commit → reuse existing data
            if (
                existing_repository.latest_commit
                == remote_commit
                and existing_repository.status == "COMPLETED"
            ):
                return {
                    "repository_id": existing_repository.id,
                    "status": "COMPLETED",
                    "message": "Repository is already up to date"
                }

            # New commit → update existing repository
            existing_repository.status = "PROCESSING"
            existing_repository.files_processed = 0
            existing_repository.chunks_created = 0
            existing_repository.embedding_batches_processed = 0
            existing_repository.total_embedding_batches = 0

            db.commit()

            repository_id = existing_repository.id

            background_tasks.add_task(
                ingest_repository,
                request.github_url,
                repository_id
            )

            return {
                "repository_id": repository_id,
                "status": "PROCESSING",
                "message": "Repository update started"
            }

        # New repository
        repository = Repository(
            github_url=request.github_url,
            status="PROCESSING",
            files_processed=0,
            chunks_created=0,
            embedding_batches_processed=0,
            total_embedding_batches=0
        )

        db.add(repository)
        db.commit()
        db.refresh(repository)

        repository_id = repository.id

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

    finally:
        db.close()

@router.get("/{repository_id}/overview")
def get_overview(repository_id: int):
    return get_repository_overview(repository_id)
# =========================================================
# GET REPOSITORY STATUS
# =========================================================
@router.get("/{repository_id}/architecture")
def get_architecture(repository_id: int):
    return get_repository_architecture(repository_id)


@router.get("/{repository_id}/files")
def get_files(repository_id: int):
    return get_repository_files(repository_id)

@router.get("/{repository_id}/file")
def get_file(
    repository_id: int,
    path: str
):
    content = get_file_content(
        repository_id=repository_id,
        file_path=path
    )

    if content is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return content

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