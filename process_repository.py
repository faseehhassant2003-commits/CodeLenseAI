from app.services.file_scanner import scan_repository
from app.services.file_reader import read_file
from app.services.chunker import create_chunks
from app.services.chunk_database_service import save_chunks

repository_path = "repositories/test-repo"
repository_id = 1

files = scan_repository(repository_path)

print("Total files:", len(files))

total_chunks = 0

for file_path in files:

    content = read_file(str(file_path))

    if content is None:
        continue

    chunks = create_chunks(content)

    save_chunks(
        repository_id=repository_id,
        file_path=str(file_path),
        language=file_path.suffix,
        chunks=chunks
    )

    total_chunks += len(chunks)

print("Processing completed!")
print("Total chunks saved:", total_chunks)