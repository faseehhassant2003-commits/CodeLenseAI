from pathlib import Path

from git import Repo
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Repository, CodeChunk
from app.services.file_scanner import scan_repository
from app.services.file_reader import read_file
from app.services.chunker import create_chunks
from app.services.embedding_service import create_embeddings


def ingest_repository(github_url: str, repository_id: int):

    db = SessionLocal()

    try:
        # =====================================================
        # 1. Get existing repository record
        # =====================================================

        statement = select(Repository).where(
            Repository.id == repository_id
        )

        repository = db.execute(statement).scalar_one()

        # =====================================================
        # 2. Create local repository path
        # =====================================================

        repository_path = Path(
            f"repositories/repository-{repository_id}"
        )

        # =====================================================
        # 3. Clone repository
        # =====================================================

        Repo.clone_from(
            github_url,
            repository_path
        )

        repository.local_path = str(repository_path)
        db.commit()

        # =====================================================
        # 4. Scan repository
        # =====================================================

        files = scan_repository(
            str(repository_path)
        )

        all_chunks = []

        # =====================================================
        # 5. Read files and create chunks
        # =====================================================

        for file_index, file_path in enumerate(files, start=1):

            content = read_file(
                str(file_path)
            )

            if content is None:
                continue

            chunks = create_chunks(content)

            for index, chunk in enumerate(chunks):

                all_chunks.append({
                    "file_path": str(file_path),
                    "language": file_path.suffix,
                    "chunk_index": index,
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "content": chunk["content"]
                })

            # Update progress
            repository.files_processed = file_index
            repository.chunks_created = len(all_chunks)

            db.commit()

        # =====================================================
        # 6. Create embeddings in batches
        # =====================================================

        texts = [
            chunk["content"]
            for chunk in all_chunks
        ]

        embeddings = create_embeddings(texts)

        # =====================================================
        # 7. Save chunks + embeddings
        # =====================================================

        for chunk, embedding in zip(
            all_chunks,
            embeddings
        ):

            code_chunk = CodeChunk(
                repository_id=repository_id,
                file_path=chunk["file_path"],
                language=chunk["language"],
                chunk_index=chunk["chunk_index"],
                start_line=chunk["start_line"],
                end_line=chunk["end_line"],
                content=chunk["content"],
                embedding=embedding
            )

            db.add(code_chunk)

        db.commit()

        # =====================================================
        # 8. Mark repository as completed
        # =====================================================

        repository.status = "COMPLETED"
        repository.files_processed = len(files)
        repository.chunks_created = len(all_chunks)

        db.commit()

        print(
            f"Repository {repository_id} ingestion completed!"
        )

    except Exception as e:

        # Rollback current transaction
        db.rollback()

        # Mark repository as failed
        try:

            statement = select(Repository).where(
                Repository.id == repository_id
            )

            repository = db.execute(
                statement
            ).scalar_one_or_none()

            if repository:
                repository.status = "FAILED"
                db.commit()

        except Exception:
            db.rollback()

        print(
            f"Repository {repository_id} ingestion failed: {e}"
        )

        raise

    finally:
        db.close()