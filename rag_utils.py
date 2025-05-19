import openai
import chromadb
import os
from config import OPENAI_API_KEY

openai.api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("code_chunks_openai")

def get_openai_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

def query_codebase(question, top_k=10):
    embedding = get_openai_embedding(question)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    # Return both code and metadata for context
    docs = results['documents'][0] if results['documents'] else []
    metas = results['metadatas'][0] if results['metadatas'] else []
    return list(zip(docs, metas))