from pathlib import Path

from app.database import SessionLocal
from app.models import CodeChunk


def get_repository_architecture(repository_id: int):
    db = SessionLocal()

    try:
        chunks = (
            db.query(CodeChunk)
            .filter(CodeChunk.repository_id == repository_id)
            .all()
        )

        architecture = {
            "controllers": [],
            "services": [],
            "repositories": [],
            "models": [],
            "security": [],
            "configuration": [],
        }

        seen = {
            key: set()
            for key in architecture
        }

        for chunk in chunks:
            file_path = Path(chunk.file_path)
            file_name = file_path.name
            lower_name = file_name.lower()
            lower_path = str(file_path).replace("\\", "/").lower()

            # Ignore test files
            if (
                lower_name.endswith("test.java")
                or "/test/" in lower_path
                or "/tests/" in lower_path
            ):
                continue

            # Controllers
            if lower_name.endswith("controller.java"):
                if file_name not in seen["controllers"]:
                    architecture["controllers"].append(file_name)
                    seen["controllers"].add(file_name)

            # Services
            elif lower_name.endswith("service.java"):
                if file_name not in seen["services"]:
                    architecture["services"].append(file_name)
                    seen["services"].add(file_name)

            # Repositories
            elif lower_name.endswith("repository.java"):
                if file_name not in seen["repositories"]:
                    architecture["repositories"].append(file_name)
                    seen["repositories"].add(file_name)

            # Models / Entities
            elif (
                lower_name.endswith(".java")
                and (
                    "/entity/" in lower_path
                    or "/entities/" in lower_path
                    or "/model/" in lower_path
                    or "/models/" in lower_path
                )
            ):
                if file_name not in seen["models"]:
                    architecture["models"].append(file_name)
                    seen["models"].add(file_name)

            # Security
            if (
                "security" in lower_path
                or "jwt" in lower_name
                or lower_name in {
                    "customuserdetails.java",
                    "customuserdetailsservice.java",
                }
            ):
                if file_name not in seen["security"]:
                    architecture["security"].append(file_name)
                    seen["security"].add(file_name)

            # Configuration
            if (
                "config" in lower_path
                or lower_name.endswith("config.java")
                or lower_name in {
                    "application.properties",
                    "application.yml",
                    "application.yaml",
                }
            ):
                if file_name not in seen["configuration"]:
                    architecture["configuration"].append(file_name)
                    seen["configuration"].add(file_name)

        return {
            "repository_id": repository_id,
            "architecture": architecture,
        }

    finally:
        db.close()