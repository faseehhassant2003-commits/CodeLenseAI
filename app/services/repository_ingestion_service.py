from pathlib import Path

from git import Repo

from app.database import SessionLocal
from app.models import Repository, CodeChunk
from app.services.file_scanner import scan_repository
from app.services.file_reader import read_file
from app.services.chunker import create_chunks
from app.services.embedding_service import create_embedding


def ingest_repository(github_url: str):

    db = SessionLocal()

    try:
        # 1. Save repository information
        repository = Repository(
            github_url=github_url
        )

        db.add(repository)
        db.commit()
        db.refresh(repository)

        repository_id = repository.id

        # 2. Create local repository path
        repository_path = Path(
            f"repositories/repository-{repository_id}"
        )

        # 3. Clone repository
        Repo.clone_from(
            github_url,
            repository_path
        )

        # Save local path
        repository.local_path = str(repository_path)
        db.commit()

        # 4. Scan repository files
        files = scan_repository(str(repository_path))

        total_chunks = 0

        # 5. Process every file
        for file_path in files:

            content = read_file(str(file_path))

            if content is None:
                continue

            chunks = create_chunks(content)

            # 6. Create embedding and save every chunk
            for index, chunk in enumerate(chunks):

                embedding = create_embedding(chunk)

                code_chunk = CodeChunk(
                    repository_id=repository_id,
                    file_path=str(file_path),
                    language=file_path.suffix,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding
                )

                db.add(code_chunk)

                total_chunks += 1

        db.commit()

        return {
            "repository_id": repository_id,
            "github_url": github_url,
            "files_processed": len(files),
            "chunks_created": total_chunks
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()