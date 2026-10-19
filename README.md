# 🏏 Cricket RAG Assistant

An AI-powered Cricket RAG (Retrieval-Augmented Generation) Assistant that answers natural-language questions about cricket match documents.

## 🚀 Overview

This project combines document retrieval with a Large Language Model (LLM) to help users explore cricket match information through a simple web interface.

## ✨ Features

- Ask natural-language questions about cricket match documents
- Retrieve relevant document chunks using ChromaDB
- Generate context-based answers using a Groq-hosted LLM
- Generate embeddings locally using Ollama
- Serve the question-answering API using FastAPI
- Provide an interactive interface using Streamlit
- Filter retrieval by match ID when supported by the backend

## 🛠️ Tech Stack

- **Language:** Python
- **RAG framework:** LangChain
- **Vector database:** ChromaDB
- **Embeddings:** Ollama (`nomic-embed-text`)
- **LLM:** Groq API
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Data source:** Cricket match JSON documents

## 🏗️ Architecture

1. Cricket match data is converted into searchable text.
2. The text is split into chunks.
3. Ollama generates embeddings for the chunks.
4. ChromaDB stores the vectors for retrieval.
5. The user's question is sent to the FastAPI backend.
6. Relevant context is retrieved and passed to the LLM.
7. The generated answer is displayed in Streamlit.

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/cricket-rag-assistant.git
cd cricket-rag-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the packages used by the project. If a `requirements.txt` file is included:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
CHROMA_PATH=path_to_your_chroma_database
```

Never commit your real API key.

### 5. Install and start Ollama

Install Ollama from https://ollama.com/ and download the embedding model:

```bash
ollama pull nomic-embed-text
```

### 6. Start the FastAPI backend

```bash
python -m uvicorn backend:app --reload --port 8000
```

API documentation: http://127.0.0.1:8000/docs

### 7. Start the Streamlit frontend

Open another terminal in the project directory:

```bash
python -m streamlit run app.py --server.port 8502
```

Open http://localhost:8502 in your browser.

## 🔐 Security

- Store API keys in `.env`.
- Keep `.env`, virtual environments, and local database files out of Git.
- Configure your own database path and API key locally.

## 📌 Current Scope

The assistant answers questions using the cricket documents indexed in its vector database. Answer quality depends on document coverage and retrieval accuracy. Exact match statistics may require additional structured-data queries and validation.

## 👩‍💻 Author

Keerthana Sankar

## 📄 License

Add a license if you intend to make the project open source.
