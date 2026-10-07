import time

from sqlalchemy import select

from app.database import SessionLocal
from app.models import CodeChunk
from app.services.embedding_service import create_embedding


def search_similar_chunks(
    question: str,
    repository_id: int,
    limit: int = 5
):
    total_start = time.perf_counter()

    # 1. Create question embedding
    embedding_start = time.perf_counter()

    question_embedding = create_embedding(question)

    embedding_time = time.perf_counter() - embedding_start

    # 2. Vector database search
    database_start = time.perf_counter()

    db = SessionLocal()

    try:
        statement = (
            select(CodeChunk)
            .where(
                CodeChunk.repository_id == repository_id,
                CodeChunk.embedding.is_not(None)
            )
            .order_by(
                CodeChunk.embedding.cosine_distance(question_embedding)
            )
            .limit(limit)
        )

        results = db.execute(statement).scalars().all()

        database_time = time.perf_counter() - database_start

        total_time = time.perf_counter() - total_start

        print("=" * 50)
        print(f"Embedding time: {embedding_time:.2f}s")
        print(f"Database time: {database_time:.2f}s")
        print(f"Total retrieval: {total_time:.2f}s")
        print("=" * 50)

        return results

    finally:
        db.close()