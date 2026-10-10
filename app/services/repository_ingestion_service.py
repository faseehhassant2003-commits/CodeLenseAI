
from pathlib import Path
import math
import shutil
import traceback

from git import Repo
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Repository, CodeChunk
from app.services.file_scanner import scan_repository
from app.services.file_reader import read_file
from app.services.chunker import create_chunks
from app.services.embedding_service import create_embeddings


def ingest_repository(github_url: str, repository_id: int):
    print(f"[INGEST] Started repository {repository_id}", flush=True)

    db = SessionLocal()

    try:
        repository = db.execute(
            select(Repository).where(
                Repository.id == repository_id
            )
        ).scalar_one()

        repository.status = "PROCESSING"
        repository.files_processed = 0
        repository.chunks_created = 0
        repository.embedding_batches_processed = 0
        repository.total_embedding_batches = 0
        db.commit()

        repository_path = Path(
            f"repositories/repository-{repository_id}"
        )

        if repository_path.exists():
            shutil.rmtree(repository_path)

        db.query(CodeChunk).filter(
            CodeChunk.repository_id == repository_id
        ).delete(synchronize_session=False)
        db.commit()

        print("[INGEST] Cloning repository...", flush=True)

        Repo.clone_from(github_url, repository_path)

        repo = Repo(repository_path)
        repository.local_path = str(repository_path)
        repository.latest_commit = repo.head.commit.hexsha
        db.commit()

        print("[INGEST] Scanning files...", flush=True)

        files = scan_repository(str(repository_path))
        all_chunks = []

        for file_index, file_path in enumerate(files, start=1):
            content = read_file(str(file_path))

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
                    "content": chunk["content"],
                })

            repository.files_processed = file_index
            repository.chunks_created = len(all_chunks)

            if file_index % 10 == 0:
                db.commit()

        db.commit()

        total_chunks = len(all_chunks)
        batch_size = 8
        total_batches = math.ceil(total_chunks / batch_size)

        repository.total_embedding_batches = total_batches
        repository.embedding_batches_processed = 0
        db.commit()

        print(
            f"[INGEST] Created {total_chunks} chunks; "
            f"embedding batches: {total_batches}",
            flush=True,
        )

        for batch_start in range(0, total_chunks, batch_size):
            batch_end = min(batch_start + batch_size, total_chunks)
            batch_chunks = all_chunks[batch_start:batch_end]

            print(
                f"[INGEST] Generating embeddings "
                f"{batch_start + 1}-{batch_end}",
                flush=True,
            )

            batch_texts = [chunk["content"] for chunk in batch_chunks]
            embeddings = create_embeddings(batch_texts)

            if len(embeddings) != len(batch_chunks):
                raise ValueError(
                    f"Expected {len(batch_chunks)} embeddings, "
                    f"received {len(embeddings)}"
                )

            for chunk, embedding in zip(batch_chunks, embeddings):
                if len(embedding) != 384:
                    raise ValueError(
                        f"Expected 384 embedding values, got {len(embedding)}"
                    )

                db.add(CodeChunk(
                    repository_id=repository_id,
                    file_path=chunk["file_path"],
                    language=chunk["language"],
                    chunk_index=chunk["chunk_index"],
                    start_line=chunk["start_line"],
                    end_line=chunk["end_line"],
                    content=chunk["content"],
                    embedding=embedding,
                ))

            db.commit()

            repository.embedding_batches_processed += 1
            db.commit()

            print(
                f"[INGEST] Saved batch "
                f"{repository.embedding_batches_processed}/{total_batches}",
                flush=True,
            )

        repository.status = "COMPLETED"
        repository.files_processed = len(files)
        repository.chunks_created = total_chunks
        repository.embedding_batches_processed = total_batches
        repository.total_embedding_batches = total_batches
        db.commit()

        print(
            f"[INGEST] Repository {repository_id} completed!",
            flush=True,
        )

    except Exception as e:
        db.rollback()

        print(
            f"[INGEST] Repository {repository_id} failed: {e}",
            flush=True,
        )
        traceback.print_exc()

        try:
            repository = db.execute(
                select(Repository).where(
                    Repository.id == repository_id
                )
            ).scalar_one_or_none()

            if repository:
                repository.status = "FAILED"
                db.commit()
        except Exception:
            db.rollback()

        raise

    finally:
        db.close()
