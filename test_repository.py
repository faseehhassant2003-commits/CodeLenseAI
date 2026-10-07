from app.database import SessionLocal
from app.models import Repository

db = SessionLocal()

repository = Repository(
    github_url="https://github.com/example/test-repository",
    local_path="repositories/test-repository"
)

db.add(repository)
db.commit()
db.refresh(repository)

print("Repository saved successfully!")
print("Repository ID:", repository.id)

db.close()