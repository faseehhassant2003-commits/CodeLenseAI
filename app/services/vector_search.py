from sqlalchemy import select

from app.database import SessionLocal
from app.models import CodeChunk
from app.services.embedding_service import create_embedding


def search_similar_chunks(
    question: str,
    repository_id: int,
    limit: int = 5
):

    question_embedding = create_embedding(question)

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

        return results

    finally:
        db.close()