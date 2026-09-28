from app.services.github_service import clone_repository


github_url="https://github.com/faseehhassant2003-commits/Gym-Management-System"
result=clone_repository(
    github_url,"repositories/test-repo"
)

print(f"Repository cloud to:{result}")