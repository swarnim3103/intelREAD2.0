from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()
CHROMA_DIR = os.getenv("CHROMA_DIR")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vectorstore():
    vectorstore = Chroma(
        collection_name="vectors",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    return vectorstore
