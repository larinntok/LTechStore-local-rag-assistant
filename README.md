# LTechStore Local RAG Assistant

An offline Retrieval-Augmented Generation (RAG) AI assistant built with Microsoft Foundry Local. The assistant answers user questions using information retrieved from local documents instead of relying on internet access.

## Features

- Offline AI assistant
- Microsoft Foundry Local
- Phi-3.5 Mini language model
- Qwen3 Embedding model
- SQLite knowledge base
- Cosine similarity search
- Retrieval-Augmented Generation (RAG)
- Source citation
- Command Line Interface (CLI)

---

## Technologies

- Python
- Microsoft Foundry Local
- Phi-3.5 Mini
- Qwen3 Embedding
- SQLite
- NumPy

---

## Project Structure

```
LTechStore-Local-RAG-Assistant/
│
├── documents/
│   ├── company_info.txt
│   ├── faq.txt
│   ├── inventory.txt
│   ├── manual.txt
│   ├── products.txt
│   └── sales.txt
│
├── app.py
├── ingest.py
├── ltechstore_rag.db
├── requirements.txt
└── README.md
```

---

## How It Works

1. Read documents from the `documents/` folder.
2. Split documents into chunks.
3. Generate embeddings using the Qwen3 Embedding model.
4. Store document chunks and embeddings in SQLite.
5. Convert the user question into an embedding.
6. Retrieve the most relevant document chunks using cosine similarity.
7. Send the retrieved context to the Phi-3.5 Mini model.
8. Display the generated answer together with its source.

If the requested information is not available, the assistant responds with:

```
I don't know based on the available documents.
```

---

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## Run the Project

Create the knowledge base:

```bash
python ingest.py
```

Start the assistant:

```bash
python app.py
```

---

## Example Questions

- Who is the company owner?
- What products do you sell?
- What are your working hours?
- Is the Laptop in stock?
- What is your warranty and return policy?
- How can I contact customer support?

---

## Sample Output

**Question**

```
Who is the company owner?
```

**Answer**

```
Larin TOK

Source:
company_info.txt
```

---

**Question**

```
Who is the president of France?
```

**Answer**

```
I don't know based on the available documents.
```

---

## Author

Microsoft Foundry Local Summer School Project
