from pathlib import Path


IGNORED_DIRECTORIES={
    ".git",
    "node_modules",
    "venv",
    "__pychache__",
    ".idea",
    ".vscode",
    "target",
    "build",
    "dist",
}

ALLOVED_EXTENSIONS={
    ".py",
    ".java",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".sql",
    ".md",
    ".json",
    ".xml",
    ".yml",
    ".yaml",
}


def scan_repository(repository_path:str):
    repository=Path(repository_path)

    files=[]

    for file_path in repository.rglob("*"):

        if not file_path.is_file():
            continue
        if any(
            ignored in file_path.parts
            for ignored in IGNORED_DIRECTORIES
        ):
            continue
        if file_path.suffix.lower() not in ALLOVED_EXTENSIONS:
            continue
        files.append(file_path)

    return files