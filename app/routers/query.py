from fastapi import APIRouter, UploadFile, File
from app.services.rag import query_rag
from app.services.ingest import ingest_pdf
import shutil

router = APIRouter()

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    temp_path = f"data/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = ingest_pdf(temp_path)
    return result

@router.get("/query")
def query(q: str):
    return query_rag(q)