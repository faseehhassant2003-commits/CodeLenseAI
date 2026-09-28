from pathlib import Path

def read_file(file_path:str):
    path=Path(file_path)

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None