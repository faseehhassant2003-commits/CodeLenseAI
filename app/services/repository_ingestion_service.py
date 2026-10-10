
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


BATCH_SIZE = 1


def ingest_repository(github_url: str, repository_id: int):
    print(f"[INGEST] Started repository {repository_id}", flush=True)

    db = SessionLocal()
    repository_path = Path(f"repositories/repository-{repository_id}")

    try:
        repository = db.execute(
            select(Repository).where(Repository.id == repository_id)
        ).scalar_one()

        repository.status = "PROCESSING"
        repository.files_processed = 0
        repository.chunks_created = 0
        repository.embedding_batches_processed = 0
        repository.total_embedding_batches = 0
        db.commit()

        if repository_path.exists():
            shutil.rmtree(repository_path)

        # Remove old chunks for this repository.
        db.query(CodeChunk).filter(
            CodeChunk.repository_id == repository_id
        ).delete(synchronize_session=False)
        db.commit()

        print("[INGEST] Cloning repository...", flush=True)
        Repo.clone_from(
            github_url,
            repository_path,
            depth=1,
            single_branch=True,
        )

        repo = Repo(repository_path)
        repository.local_path = str(repository_path)
        repository.latest_commit = repo.head.commit.hexsha
        db.commit()

        print("[INGEST] Scanning files...", flush=True)
        files = scan_repository(str(repository_path))

        # First pass: count chunks without retaining their contents.
        total_chunks = 0

        for file_path in files:
            content = read_file(str(file_path))
            if content is not None:
                total_chunks += len(create_chunks(content))

        total_batches = math.ceil(total_chunks / BATCH_SIZE)
        repository.total_embedding_batches = total_batches
        db.commit()

        print(
            f"[INGEST] Files: {len(files)}, chunks: {total_chunks}, "
            f"embedding batches: {total_batches}",
            flush=True,
        )

        batch = []
        processed_files = 0
        processed_chunks = 0
        processed_batches = 0

        for file_path in files:
            content = read_file(str(file_path))
            if content is None:
                continue

            chunks = create_chunks(content)

            for index, chunk in enumerate(chunks):
                batch.append({
                    "file_path": str(file_path.relative_to(repository_path)),
                    "language": file_path.suffix,
                    "chunk_index": index,
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "content": chunk["content"],
                })

                if len(batch) >= BATCH_SIZE:
                    texts = [item["content"] for item in batch]
                    embeddings = create_embeddings(texts)

                    if len(embeddings) != len(batch):
                        raise ValueError("Embedding count does not match batch size")

                    for item, embedding in zip(batch, embeddings):
                        if len(embedding) != 384:
                            raise ValueError(
                                f"Expected 384 dimensions, got {len(embedding)}"
                            )

                        db.add(CodeChunk(
                            repository_id=repository_id,
                            file_path=item["file_path"],
                            language=item["language"],
                            chunk_index=item["chunk_index"],
                            start_line=item["start_line"],
                            end_line=item["end_line"],
                            content=item["content"],
                            embedding=embedding,
                        ))

                    db.commit()
                    batch.clear()

                    processed_chunks += len(texts)
                    processed_batches += 1

                    repository.chunks_created = processed_chunks
                    repository.embedding_batches_processed = processed_batches
                    db.commit()

                    print(
                        f"[INGEST] Saved batch "
                        f"{processed_batches}/{total_batches}",
                        flush=True,
                    )

            processed_files += 1
            repository.files_processed = processed_files
            db.commit()

        repository.status = "COMPLETED"
        repository.files_processed = processed_files
        repository.chunks_created = processed_chunks
        repository.embedding_batches_processed = processed_batches
        repository.total_embedding_batches = total_batches
        db.commit()

        print(f"[INGEST] Repository {repository_id} completed!", flush=True)

    except Exception as exc:
        db.rollback()
        print(f"[INGEST] Repository {repository_id} failed: {exc}", flush=True)
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

    finally:
        db.close()

        try:
            if repository_path.exists():
                shutil.rmtree(repository_path)
                print("[INGEST] Temporary repository cleaned up.", flush=True)
        except Exception as cleanup_error:
            print(
                f"[INGEST] Cleanup warning: {cleanup_error}",
                flush=True,
            )
