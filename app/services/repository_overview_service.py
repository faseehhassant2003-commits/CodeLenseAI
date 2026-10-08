from pathlib import Path
from collections import Counter

from app.database import SessionLocal
from app.models import CodeChunk


LANGUAGE_MAP = {
    ".java": "Java",
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
    ".json": "JSON",
    ".xml": "XML",
    ".yml": "YAML",
    ".yaml": "YAML",
}


def get_repository_overview(repository_id: int):

    db = SessionLocal()

    try:
        chunks = (
            db.query(CodeChunk)
            .filter(
                CodeChunk.repository_id == repository_id
            )
            .all()
        )

        if not chunks:
            return {
                "repository_id": repository_id,
                "languages": [],
                "backend": [],
                "frontend": [],
                "database": [],
                "ai": [],
                "authentication": [],
                "modules": [],
            }

        # =====================================================
        # Languages
        # =====================================================

        language_counter = Counter()

        for chunk in chunks:

            extension = Path(
                chunk.file_path
            ).suffix.lower()

            language = LANGUAGE_MAP.get(
                extension
            )

            if language:
                language_counter[language] += 1

        languages = [
            language
            for language, _ in language_counter.most_common()
        ]

        # =====================================================
        # Detect technologies from file paths/content
        # =====================================================

        all_text = " ".join(
            chunk.content.lower()
            for chunk in chunks
        )

        all_paths = " ".join(
            chunk.file_path.lower()
            for chunk in chunks
        )

        backend = []
        frontend = []
        database = []
        ai = []
        authentication = []
        modules = []

        # =====================================================
        # Backend
        # =====================================================

        if (
            "springframework" in all_text
            or "spring boot" in all_text
            or "pom.xml" in all_paths
        ):
            backend.append("Spring Boot")

        if "fastapi" in all_text:
            backend.append("FastAPI")

        if "flask" in all_text:
            backend.append("Flask")

        # =====================================================
        # Frontend
        # =====================================================

        if (
            "react" in all_text
            or ".jsx" in all_paths
            or ".tsx" in all_paths
        ):
            frontend.append("React")

        if "vite" in all_text:
            frontend.append("Vite")

        if "next.js" in all_text or "nextjs" in all_text:
            frontend.append("Next.js")

        # =====================================================
        # Database
        # =====================================================

        if "postgresql" in all_text:
            database.append("PostgreSQL")

        if "mysql" in all_text:
            database.append("MySQL")

        if "mongodb" in all_text:
            database.append("MongoDB")

        # =====================================================
        # AI
        # =====================================================

        if "gemini" in all_text:
            ai.append("Google Gemini")

        if "openai" in all_text:
            ai.append("OpenAI")

        if "groq" in all_text:
            ai.append("Groq")

        # =====================================================
        # Authentication
        # =====================================================

        if (
            "jwt" in all_text
            or "jsonwebtoken" in all_text
            or "jjwt" in all_text
        ):
            authentication.append("JWT")

        if "spring security" in all_text:
            authentication.append("Spring Security")

        # =====================================================
        # Modules
        # =====================================================

        module_keywords = {
            "Authentication": [
                "auth",
                "security",
                "login",
                "register",
            ],
            "Members": [
                "member",
            ],
            "Trainers": [
                "trainer",
            ],
            "Diet": [
                "diet",
            ],
            "Workout": [
                "workout",
            ],
            "Payments": [
                "payment",
                "razorpay",
            ],
            "Attendance": [
                "attendance",
                "qr",
            ],
        }

        for module, keywords in module_keywords.items():

            if any(
                keyword in all_paths
                for keyword in keywords
            ):
                modules.append(module)

        return {
            "repository_id": repository_id,
            "languages": languages,
            "backend": backend,
            "frontend": frontend,
            "database": database,
            "ai": ai,
            "authentication": authentication,
            "modules": modules,
        }

    finally:
        db.close()