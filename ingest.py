import os
import json
import sqlite3
import numpy as np

from foundry_local_sdk import Configuration, FoundryLocalManager


DB_NAME = "supermarket_rag.db"
DOCUMENTS_DIR = "documents"
TARGET_VECTOR_DIM = 1536

config = Configuration(app_name="FoundryLocalProject")
FoundryLocalManager.initialize(config)
foundry_manager = FoundryLocalManager.instance

print("Embedding modeli yükleniyor...")

embedding_model = foundry_manager.catalog.get_model("qwen3-embedding-0.6b")

if embedding_model is None:
    embedding_model = foundry_manager.catalog.get_model("all-minilm-l6-v2")

if embedding_model:
    embedding_model.download()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()
else:
    embedding_client = None

def get_embedding(text):

    if embedding_client is None:
        raise Exception("Embedding client yüklenemedi.")

    result = embedding_client.generate_embeddings([text])

    vector = result.data[0].embedding

    return [float(x) for x in vector]


def chunk_text(text, chunk_size=500, overlap=100):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks


def create_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_base(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        content TEXT,

        source TEXT,

        embedding_json TEXT

    )
    """)

    cursor.execute("DELETE FROM knowledge_base")

    conn.commit()

    conn.close()


def ingest_documents():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    files = [f for f in os.listdir(DOCUMENTS_DIR) if f.endswith(".txt")]

    print(f"[+] {len(files)} document(s) found.\n")

    for filename in files:

        filepath = os.path.join(DOCUMENTS_DIR, filename)

        print(f"Reading {filename}...")

        with open(filepath, "r", encoding="utf-8") as file:

            text = file.read()

        chunks = chunk_text(text)

        print(f"  -> {len(chunks)} chunk(s)")

        for i, chunk in enumerate(chunks):

            embedding = get_embedding(chunk)

            cursor.execute(
                """
                INSERT INTO knowledge_base
                (content, source, embedding_json)
                VALUES (?, ?, ?)
                """,
                (
                    chunk,
                    f"{filename} (Chunk {i+1})",
                    json.dumps(embedding)
                )
            )

            print(f"     Chunk {i+1} indexed.")

        print()

    conn.commit()
    conn.close()

print("***********************************************")
print("LTechStore Knowledge Base Successfully Created ")    
print("***********************************************")


if __name__ == "__main__":

    if not os.path.exists(DOCUMENTS_DIR):
        print(f"[!] '{DOCUMENTS_DIR}' klasörü bulunamadı.")
        exit()

    create_database()

    ingest_documents()

    print("\nDone!")