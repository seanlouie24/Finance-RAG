from pypdf import PdfReader
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def ensure_index():
    index_name = os.getenv("PINECONE_INDEX")
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(index_name)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def ingest_pdf(filepath: str):
    index = ensure_index()
    reader = PdfReader(filepath)
    filename = os.path.basename(filepath)

    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + " "

    chunks = chunk_text(full_text)
    vectors = []

    for i, chunk in enumerate(chunks):
        embedding = client.embeddings.create(
            input=chunk,
            model="text-embedding-3-small"
        ).data[0].embedding

        vectors.append({
            "id": f"{filename}-chunk-{i}",
            "values": embedding,
            "metadata": {"text": chunk, "source": filename}
        })

    index.upsert(vectors=vectors)
    return {"ingested": filename, "chunks": len(chunks)}