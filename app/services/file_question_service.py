from pathlib import Path

from sqlalchemy import select

from app.database import SessionLocal
from app.models import CodeChunk
from app.services.embedding_service import create_embedding


def search_file_chunks(
    question: str,
    repository_id: int,
    file_path: str,
    limit: int = 5
):
    question_embedding = create_embedding(question)

    db = SessionLocal()

    try:
        # Normalize requested path
        requested_path = file_path.replace(
            "\\", "/"
        ).strip("/")

        # Get all chunks for this repository
        chunks = (
            db.query(CodeChunk)
            .filter(
                CodeChunk.repository_id == repository_id
            )
            .all()
        )

        # Find chunks belonging to the selected file
        matching_ids = []

        for chunk in chunks:

            stored_path = str(
                Path(chunk.file_path)
            ).replace("\\", "/")

            repository_folder = (
                f"repository-{repository_id}/"
            )

            if repository_folder in stored_path:
                clean_path = stored_path.split(
                    repository_folder,
                    1
                )[1]
            else:
                clean_path = stored_path

            clean_path = clean_path.strip("/")

            if clean_path == requested_path:
                matching_ids.append(chunk.id)

        if not matching_ids:
            return []

        # Perform vector search only among
        # chunks belonging to the selected file
        statement = (
            select(CodeChunk)
            .where(
                CodeChunk.id.in_(matching_ids),
                CodeChunk.embedding.is_not(None)
            )
            .order_by(
                CodeChunk.embedding.cosine_distance(
                    question_embedding
                )
            )
            .limit(limit)
        )

        results = db.execute(
            statement
        ).scalars().all()

        return results

    finally:
        db.close()