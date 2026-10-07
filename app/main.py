from fastapi import FastAPI
from app.routes.ask_routes import router as ask_router
from app.routes.repository_routes import router as repository_router


app = FastAPI(
    title="CodeLense AI",
    description="RAG-powered GitHub Repository Intelligence Platform",
    version="1.0.0"
)


app.include_router(repository_router)
app.include_router(ask_router)


@app.get("/")
def root():
    return {"message": "CodeLense AI API is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}