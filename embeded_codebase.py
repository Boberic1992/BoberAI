import json
import os
import shutil
import time

import chromadb
import openai

from config import OPENAI_API_KEY

openai.api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)

DB_PATH = "./chroma_db"


def get_openai_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


def embed_codebase(manifest_path="code_chunks_manifest.json"):
    """Embed code chunks from manifest into ChromaDB."""
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print("Old ChromaDB vector database deleted.")

    with open(manifest_path, "r") as f:
        code_chunks = json.load(f)

    db_client = chromadb.PersistentClient(path=DB_PATH)
    collection = db_client.get_or_create_collection("code_chunks_openai")

    documents = []
    metadatas = []
    ids = []
    embeddings = []

    for idx, chunk in enumerate(code_chunks):
        doc_id = f"{chunk['file']}:{chunk['chunk_id']}"
        content = f"Filename: {chunk['file']}\n{chunk['content']}"

        documents.append(content)
        metadatas.append({
            "file": chunk.get("file"),
            "chunk_id": chunk.get("chunk_id"),
            "ext": chunk.get("ext"),
            "start_line": chunk.get("start_line"),
            "end_line": chunk.get("end_line"),
        })
        ids.append(doc_id)
        embeddings.append(get_openai_embedding(content))
        print(f"Embedded chunk {idx + 1}/{len(code_chunks)}")
        time.sleep(0.5)

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )

    print(f"Embedded {len(documents)} code chunks into ChromaDB.")


if __name__ == "__main__":
    embed_codebase()
