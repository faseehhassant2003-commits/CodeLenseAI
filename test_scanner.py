from app.services.file_scanner import scan_repository

repository_path="repositories/test-repo"

files=scan_repository(repository_path)

print(f"found {len(files)}source files:\n")

for file in files:
    print(file)