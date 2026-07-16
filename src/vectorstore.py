# vectorstore.py (full file)
from dotenv import load_dotenv
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()
CHROMA_DIR = os.getenv("CHROMA_DIR")

if not CHROMA_DIR:
    raise RuntimeError("CHROMA_DIR is not set — check your .env file")


print(f"[vectorstore] CHROMA_DIR (raw)      = {CHROMA_DIR}")
print(f"[vectorstore] CHROMA_DIR (resolved) = {os.path.abspath(CHROMA_DIR)}")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vectorstore():
    vectorstore = Chroma(
        collection_name="vectors",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    return vectorstore