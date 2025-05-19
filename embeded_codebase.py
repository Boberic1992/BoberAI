import json
import openai
import chromadb
import os
import time
import shutil
from config import OPENAI_API_KEY

openai.api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)

# Remove old ChromaDB database if it exists
db_path = "./chroma_db"
if os.path.exists(db_path):
    shutil.rmtree(db_path)
    print("Old ChromaDB vector database deleted.")

def get_openai_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

# Load code chunks
with open("code_chunks_manifest.json", "r") as f:
    code_chunks = json.load(f)

client = chromadb.PersistentClient(path=db_path)
collection = client.get_or_create_collection("code_chunks_openai")

documents = []
metadatas = []
ids = []
embeddings = []

for idx, chunk in enumerate(code_chunks):
    doc_id = f"{chunk['file']}:{chunk['chunk_id']}"
    content = f"Filename: {chunk['file']}\n{chunk['content']}"
    documents.append(content)
    # Store all relevant metadata for later retrieval
    metadatas.append({
        "file": chunk.get("file"),
        "chunk_id": chunk.get("chunk_id"),
        "ext": chunk.get("ext"),
        "start_line": chunk.get("start_line"),
        "end_line": chunk.get("end_line"),
    })
    ids.append(doc_id)
    emb = get_openai_embedding(content)
    embeddings.append(emb)
    print(f"Embedded chunk {idx+1}/{len(code_chunks)}")
    time.sleep(0.5)  # To avoid rate limits

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids,
    embeddings=embeddings
)

print(f"Embedded {len(documents)} code chunks into ChromaDB (OpenAI embeddings).")