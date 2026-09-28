from git import Repo
from pathlib import Path

def clone_repository(github_url:url,destination:str):
    destination_path=Path(destination)

    Repo.clone_from(github_url,destination_path)

    return destination_path