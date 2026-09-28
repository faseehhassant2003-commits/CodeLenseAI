from fastapi import FastAPI

app=FastAPI(
    title="CodeLense AI",
    description="RAG-powered GitHub Repository Intelligence Platfform",
    version="1.0.0"
)


@app.get("/")
def root():
    return{
        "message" :"codeLense AI API is running!"
    }
@app.get("/health")
def health():
    return {
        "status" : "ok"
    }