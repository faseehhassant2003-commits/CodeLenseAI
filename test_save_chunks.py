from app.services.chunk_database_service import save_chunks

chunks = [
    "This is the first code chunk.",
    "This is the second code chunk.",
    "This is the third code chunk."
]

save_chunks(
    repository_id=1,
    file_path="test/example.py",
    language="Python",
    chunks=chunks
)