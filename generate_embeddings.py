from app.database import SessionLocal
from app.models import CodeChunk
from app.services.embedding_service import create_embedding


db = SessionLocal()

try:
    chunks = (
        db.query(CodeChunk)
        .filter(CodeChunk.embedding.is_(None))
        .all()
    )

    print("Chunks to process:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):

        chunk.embedding = create_embedding(chunk.content)

        if index % 10 == 0:
            db.commit()
            print(f"Processed: {index}/{len(chunks)}")

    db.commit()

    print("Embedding generation completed!")

finally:
    db.close()