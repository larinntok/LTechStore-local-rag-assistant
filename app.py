import sqlite3
import json
import numpy as np
import os

from foundry_local_sdk import Configuration, FoundryLocalManager

DB_NAME = "ltechstore_rag.db"

config = Configuration(app_name="FoundryLocalProject")
FoundryLocalManager.initialize(config)
foundry_manager = FoundryLocalManager.instance


print("Loading Phi-3.5...")

ai_model = foundry_manager.catalog.get_model("phi-3.5-mini")

if ai_model is None:
    print("[!] phi-3.5-mini not found.")
    exit()

ai_model.download()
ai_model.load()

chat_client = ai_model.get_chat_client()


print("Loading Embedding Model...")

embedding_model = foundry_manager.catalog.get_model("qwen3-embedding-0.6b")

if embedding_model is None:
    embedding_model = foundry_manager.catalog.get_model("all-minilm-l6-v2")

if embedding_model is not None:
    embedding_model.download()
    embedding_model.load()

    embedding_client = embedding_model.get_embedding_client()

TARGET_VECTOR_DIM = 1536


def get_embedding(text):

    try:
        result = embedding_client.generate_embeddings([text])

        vector = result.data[0].embedding

        return [float(x) for x in vector]

    except Exception as e:
        print("Embedding Error:", e)
        return None


def cosine_similarity(v1, v2):

    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)

    if len(a) != len(b):
        max_len = max(len(a), len(b))
        a = np.pad(a, (0, max_len - len(a)))
        b = np.pad(b, (0, max_len - len(b)))

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def retrieve_context_vector_search(query, top_k=3):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT content, source, embedding_json FROM knowledge_base"
    )

    rows = cursor.fetchall()
    conn.close()

    if len(rows) == 0:
        return None, None

    query_vector = get_embedding(query)
    if query_vector is None:
        return None, None

    scores = []

    for content, source, embedding_json in rows:

        doc_vector = json.loads(embedding_json)

        similarity = cosine_similarity(query_vector, doc_vector)

        scores.append((similarity, content, source))

    scores.sort(key=lambda x: x[0], reverse=True)

    top = scores[:top_k]

    context = "\n\n".join(
        [item[1] for item in top]
    )

    sources = ", ".join(
        list(set([item[2] for item in top]))
    )

    return context, sources


def query_ai_model(prompt):

    try:

        response = chat_client.complete_chat(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"Foundry Local Error: {e}"

def get_assistant_response(user_query):

    context, source = retrieve_context_vector_search(user_query)

    if context is None:
        return "No relevant documents found."

    prompt = f"""
You are a LTechStore AI RAG assistant.

Answer ONLY using the retrieved context.

If the context contains the answer, answer briefly and do NOT add any extra explanation.

If the answer is NOT present in the context, reply exactly:

I don't know based on the available documents.

Context:
{context}

Question:
{user_query}

Answer:
"""
    answer = query_ai_model(prompt)

    return f"{answer}\n\nSource: {source}"



if __name__ == "__main__":

    if not os.path.exists(DB_NAME):
        print("[!] Database not found.")
        print("Run: python ingest.py")
        exit()

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("LTechStore AI Support Assistantis Ready")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

print("You can ask questions such as:\n")

print("- Who is the company owner?")
print("- What products do you sell?")
print("- What are your working hours?")
print("- How can I contact customer support?")

print("\nType 'exit' to quit.\n")

while True:

        try:

            question = input("You: ").strip()

            if question == "":
                continue

            if question.lower() in ["exit", "quit", "q"]:
                print("Goodbye:), see you next time!")
                break

            print("\nAssistant is thinking...\n")

            answer = get_assistant_response(question)

        except KeyboardInterrupt:
            print("\nSession ended.")
            break

        except Exception as e:
            print(f"\nError: {e}\n")
