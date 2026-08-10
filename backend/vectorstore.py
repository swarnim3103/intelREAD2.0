import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
import chromadb

load_dotenv(Path(__file__).resolve().parent / ".env")

CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")

if not all([CHROMA_TENANT, CHROMA_DATABASE, CHROMA_API_KEY]):
    raise RuntimeError(
        "CHROMA_TENANT, CHROMA_DATABASE, and CHROMA_API_KEY must all be set — check your .env file"
    )

print(f"[vectorstore] Connecting to Chroma Cloud — tenant={CHROMA_TENANT}, database={CHROMA_DATABASE}")

# vectorstore.py
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Cloud client — replaces PersistentClient, no local disk involved
chroma_client = chromadb.CloudClient(
    tenant=CHROMA_TENANT,
    database=CHROMA_DATABASE,
    api_key=CHROMA_API_KEY,
)

def get_vectorstore():
    vectorstore = Chroma(
        client=chroma_client,
        collection_name="vectors",
        embedding_function=embeddings,
    )
    return vectorstore