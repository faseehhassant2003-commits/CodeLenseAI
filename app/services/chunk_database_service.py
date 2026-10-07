from app.database import SessionLocal
from app.models import CodeChunk


def save_chunks(repository_id, file_path, language, chunks):

    db = SessionLocal()

    try:
        for index, chunk in enumerate(chunks):

            code_chunk = CodeChunk(
                repository_id=repository_id,
                file_path=file_path,
                language=language,
                chunk_index=index,
                start_line=chunk["start_line"],
                end_line=chunk["end_line"],
                content=chunk["content"]
            )

            db.add(code_chunk)

        db.commit()
      
        print(f"Saved {len(chunks)} chunks from {file_path}")

    finally:
        db.close()