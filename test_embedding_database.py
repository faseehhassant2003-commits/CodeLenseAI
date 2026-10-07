from app.database import SessionLocal
from app.models import CodeChunk
from app.services.embedding_service import create_embedding

db = SessionLocal()

chunk = db.query(CodeChunk).first()

if chunk is None:
    print("No code chunks found!")
else:
    embedding = create_embedding(chunk.content)

    chunk.embedding = embedding

    db.commit()

    print("Embedding saved successfully!")
    print("Chunk ID:", chunk.id)
    print("Vector dimensions:", len(embedding))


db.close()