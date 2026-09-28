from app.services.file_reader import read_file


file_path=(
    "repositories/test-repo/" 
    "backend/src/main/java/com/gymmanagement/security/JwtService.java"


)
content=read_file(file_path)
if content:
    print("file content:\n")
    print(content)

else:
    print("could  not find the contends")