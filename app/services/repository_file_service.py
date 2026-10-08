from pathlib import Path

from app.database import SessionLocal
from app.models import CodeChunk


def get_repository_files(repository_id: int):
    db = SessionLocal()

    try:
        chunks = (
            db.query(CodeChunk)
            .filter(CodeChunk.repository_id == repository_id)
            .all()
        )

        files = {}

        for chunk in chunks:
            path = Path(chunk.file_path)
            parts = path.parts

            repository_folder = f"repository-{repository_id}"

            if repository_folder in parts:
                index = parts.index(repository_folder)
                clean_path = Path(*parts[index + 1:])
            else:
                clean_path = path

            clean_path = str(clean_path).replace("\\", "/")

            if clean_path not in files:
                files[clean_path] = {
                    "path": clean_path,
                    "language": chunk.language
                }

        return {
            "repository_id": repository_id,
            "files": sorted(
                files.values(),
                key=lambda x: x["path"]
            )
        }

    finally:
        db.close()