from app.services.file_scanner import scan_repository
from app.services.file_reader import read_file
from app.services.chunker import create_chunks
from app.services.chunk_database_service import save_chunks

repository_path = "repositories/test-repo"

files = scan_repository(repository_path)

print("Files found:", len(files))

file_path = files[0]

print("Processing:", file_path)

content = read_file(str(file_path))

if content is None:
    print("Could not read file")
else:
    chunks = create_chunks(content)

    print("Chunks created:", len(chunks))

    save_chunks(
        repository_id=1,
        file_path=str(file_path),
        language=file_path.suffix,
        chunks=chunks
    )
