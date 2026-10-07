from fastapi import APIRouter
from pydantic import BaseModel

from app.services.repository_ingestion_service import ingest_repository


router = APIRouter(
    prefix="/api/repositories",
    tags=["Repositories"]
)


class RepositoryRequest(BaseModel):
    github_url: str


@router.post("/")
def create_repository(request: RepositoryRequest):

    result = ingest_repository(request.github_url)

    return result