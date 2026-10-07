from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "target",
    "build",
    "dist",
}


IGNORED_FILES = {
    "README",
    "README.md",
    "README.MD",
    "readme.md",
}


ALLOWED_EXTENSIONS = {
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


SPECIAL_FILES = {
    "LICENSE",
    "Dockerfile",
}


def scan_repository(repository_path: str):

    repository = Path(repository_path)

    files = []

    for file_path in repository.rglob("*"):

        if not file_path.is_file():
            continue

        if any(
            ignored in file_path.parts
            for ignored in IGNORED_DIRECTORIES
        ):
            continue

        if file_path.name in IGNORED_FILES:
            continue

        if (
            file_path.suffix.lower() not in ALLOWED_EXTENSIONS
            and file_path.name not in SPECIAL_FILES
        ):
            continue

        files.append(file_path)

    return files