from pathlib import Path
import math
import shutil

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
        statement = select(Repository).where(
            Repository.id == repository_id
        )

        repository = db.execute(
            statement
        ).scalar_one()

        # Reset processing status
        repository.status = "PROCESSING"
        repository.files_processed = 0
        repository.chunks_created = 0
        repository.embedding_batches_processed = 0
        repository.total_embedding_batches = 0

        db.commit()

        repository_path = Path(
            f"repositories/repository-{repository_id}"
        )

        # --------------------------------------------------
        # Remove old repository files
        # --------------------------------------------------

        if repository_path.exists():
            shutil.rmtree(repository_path)

        # --------------------------------------------------
        # Remove old chunks / embeddings
        # --------------------------------------------------

        db.query(CodeChunk).filter(
            CodeChunk.repository_id == repository_id
        ).delete(
            synchronize_session=False
        )

        db.commit()

        # --------------------------------------------------
        # Clone latest repository
        # --------------------------------------------------

        Repo.clone_from(
            github_url,
            repository_path
        )

        repo = Repo(repository_path)

        latest_commit = repo.head.commit.hexsha

        repository.local_path = str(repository_path)
        repository.latest_commit = latest_commit

        db.commit()

        print(
            f"Repository {repository_id} "
            f"latest commit: {latest_commit}"
        )

        # --------------------------------------------------
        # Scan files
        # --------------------------------------------------

        files = scan_repository(
            str(repository_path)
        )

        all_chunks = []

        for file_index, file_path in enumerate(
            files,
            start=1
        ):
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

            repository.files_processed = file_index
            repository.chunks_created = len(all_chunks)

            db.commit()

        # --------------------------------------------------
        # Create embeddings
        # --------------------------------------------------

        batch_size = 32

        total_chunks = len(all_chunks)

        total_batches = math.ceil(
            total_chunks / batch_size
        )

        repository.total_embedding_batches = total_batches
        repository.embedding_batches_processed = 0

        db.commit()

        print(
            f"Creating embeddings: "
            f"{total_chunks} chunks in "
            f"{total_batches} batches"
        )

        for batch_start in range(
            0,
            total_chunks,
            batch_size
        ):

            batch_end = min(
                batch_start + batch_size,
                total_chunks
            )

            batch_chunks = all_chunks[
                batch_start:batch_end
            ]

            batch_texts = [
                chunk["content"]
                for chunk in batch_chunks
            ]

            embeddings = create_embeddings(
                batch_texts
            )

            for chunk, embedding in zip(
                batch_chunks,
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

            repository.embedding_batches_processed += 1

            db.commit()

            print(
                f"Embedding progress: "
                f"{repository.embedding_batches_processed}/"
                f"{total_batches}"
            )

        # --------------------------------------------------
        # Completed
        # --------------------------------------------------

        repository.status = "COMPLETED"
        repository.files_processed = len(files)
        repository.chunks_created = total_chunks
        repository.embedding_batches_processed = total_batches
        repository.total_embedding_batches = total_batches

        db.commit()

        print(
            f"Repository {repository_id} "
            f"ingestion completed!"
        )

    except Exception as e:

        db.rollback()

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
            f"Repository {repository_id} "
            f"ingestion failed: {e}"
        )

        raise

    finally:
        db.close()