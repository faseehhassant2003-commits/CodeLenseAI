import subprocess

from git import Repo
from pathlib import Path


def clone_repository(github_url: str, destination: str):
    destination_path = Path(destination)

    Repo.clone_from(
        github_url,
        destination_path
    )

    return destination_path


def get_latest_commit(repository_path: str):
    repo = Repo(repository_path)

    return repo.head.commit.hexsha


def get_remote_latest_commit(github_url: str):
    result = subprocess.run(
        ["git", "ls-remote", github_url, "HEAD"],
        capture_output=True,
        text=True,
        check=True
    )

    output = result.stdout.strip()

    if not output:
        raise Exception("Could not determine remote repository commit")

    return output.split()[0]