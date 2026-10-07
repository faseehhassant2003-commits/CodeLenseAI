from app.services.file_reader import read_file
from app.services.chunker import create_chunks

file_path=(
    "repositories/test-repo/"
    "backend/src/main/java/com/gymmanagement/security/JwtService.java"
)
content=read_file(file_path)
chunks=create_chunks(content,500)
print(f"total chunks:{len(chunks)}")
for index,chunk in enumerate(chunks,start=1):
    print(f"\n=========CHUNK{index}=======\n")
    print(chunk)