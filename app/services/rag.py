from openai import OpenAI
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

def get_embedding(text: str):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def query_rag(question: str, top_k: int = 5):
    embedding = get_embedding(question)

    results = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )

    context_chunks = [match.metadata["text"] for match in results.matches]
    context = "\n\n".join(context_chunks)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a financial research assistant. Answer questions using only the provided context. Always cite which document your answer comes from."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [match.metadata.get("source", "unknown") for match in results.matches]
    }