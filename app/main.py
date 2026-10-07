from fastapi import FastAPI
from app.routes.ask_routes import router as ask_router
from app.routes.repository_routes import router as repository_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CodeLense AI",
    description="RAG-powered GitHub Repository Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(repository_router)
app.include_router(ask_router)


@app.get("/")
def root():
    return {"message": "CodeLense AI API is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}