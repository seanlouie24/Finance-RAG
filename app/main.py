from fastapi import FastAPI
from app.routers import query

app = FastAPI(title="FinRAG", description="RAG-powered financial research assistant")

app.include_router(query.router)

@app.get("/")
def root():
    return {"status": "FinRAG is running"}