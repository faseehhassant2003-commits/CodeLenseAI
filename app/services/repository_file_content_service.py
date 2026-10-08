from pathlib import Path

from app.database import SessionLocal
from app.models import CodeChunk


def get_file_content(repository_id: int, file_path: str):
    db = SessionLocal()

    try:
        chunks = (
            db.query(CodeChunk)
            .filter(
                CodeChunk.repository_id == repository_id
            )
            .order_by(CodeChunk.chunk_index)
            .all()
        )

        requested_path = file_path.replace("\\", "/").strip("/")

        matching_chunks = []

        for chunk in chunks:
            stored_path = str(
                Path(chunk.file_path)
            ).replace("\\", "/")

            repository_folder = f"repository-{repository_id}/"

            if repository_folder in stored_path:
                clean_path = stored_path.split(
                    repository_folder,
                    1
                )[1]
            else:
                clean_path = stored_path

            clean_path = clean_path.strip("/")

            if clean_path == requested_path:
                matching_chunks.append(chunk)

        if not matching_chunks:
            return None

        content = "\n".join(
            chunk.content
            for chunk in matching_chunks
        )

        return {
            "repository_id": repository_id,
            "file": requested_path,
            "language": matching_chunks[0].language,
            "content": content
        }

    finally:
        db.close()