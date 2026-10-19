
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain_community.document_compressors import FlashrankRerank
from langchain_core.prompts import ChatPromptTemplate

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

CHROMA_PATH = Path(
    os.getenv("CHROMA_PATH", "chroma_db")
).expanduser()

if not CHROMA_PATH.is_absolute():
    CHROMA_PATH = BASE_DIR / CHROMA_PATH

if not CHROMA_PATH.exists():
    raise RuntimeError(
        f"ChromaDB folder not found: {CHROMA_PATH}. "
        "Set CHROMA_PATH in .env to your existing database folder."
    )

api_key = os.getenv("API_KEY")
if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )

# --------------------------------------------------
# 2. Connect to existing ChromaDB
# --------------------------------------------------

embeddings_model = OllamaEmbeddings(
    model="nomic-embed-text"
)

db = Chroma(
    collection_name="cricket_matches",
    embedding_function=embeddings_model,
    persist_directory=str(CHROMA_PATH),
)

chunk_count = db._collection.count()

if chunk_count == 0:
    raise RuntimeError(
        "The ChromaDB collection is empty. "
        "Check the database path and collection name."
    )

print(f"Connected to ChromaDB: {chunk_count} chunks")

# --------------------------------------------------
# 3. LLM and reranker
# --------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=api_key,
)

reranker = FlashrankRerank(
    top_n=5,
    model="ms-marco-MiniLM-L-12-v2",
)

prompt = ChatPromptTemplate.from_template("""
You are a cricket data assistant.

Answer using only the supplied context.
Do not invent scores, players, results, or statistics.
If the context is insufficient, say so clearly.
Cite the relevant Match ID for factual claims.
Do not claim the context covers every match.

Context:
{context}

Question:
{question}

Give a clear answer with Match ID citations.
""")

# --------------------------------------------------
# 4. FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Cricket RAG Assistant",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    match_id: str | None = None


@app.get("/")
def home():
    return {
        "message": "Cricket RAG Assistant API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database_chunks": db._collection.count(),
    }


@app.post("/ask")
def ask_question(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    try:
        search_kwargs = {"k": 10}

        if request.match_id and request.match_id.strip():
            search_kwargs["filter"] = {
                "match_id": request.match_id.strip()
            }

        # Retrieve relevant documents
        retrieved_docs = db.similarity_search(
            question,
            **search_kwargs,
        )

        if not retrieved_docs:
            return {
                "answer": "No matching cricket documents were found.",
                "sources": [],
            }

        # Rerank retrieved documents
        reranked_docs = reranker.compress_documents(
            retrieved_docs,
            query=question,
        )

        if not reranked_docs:
            return {
                "answer": "No relevant evidence was found.",
                "sources": [],
            }

        # Prepare context
        context = "\n\n".join(
            f"[Match ID: {doc.metadata.get('match_id', 'Unknown')}]\n"
            f"{doc.page_content}"
            for doc in reranked_docs
        )

        # Generate answer
        response = (prompt | llm).invoke({
            "context": context,
            "question": question,
        })

        sources = list(dict.fromkeys(
            str(doc.metadata.get("match_id", "Unknown"))
            for doc in reranked_docs
        ))

        return {
            "answer": str(response.content),
            "sources": sources,
        }

    except Exception as exc:
        print(f"Question-answer error: {exc}")
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not answer the question. "
                "Check the backend terminal for the error."
            ),
        ) from exc
