from app.models import CodeChunk
from app.database import SessionLocal

db=SessionLocal()

chunk=CodeChunk(
    repository_id=1,
    file_path="src/example.py",
    language="Python",
    chunk_index=0,
    content="def hello():\n    print('Hello CodeLense AI')"
)


db.add(chunk)
db.commit()
db.refresh(chunk)

print("code chunk saves seccussfully")
print("Chunk ID:",chunk.id)

db.close