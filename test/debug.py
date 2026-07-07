# debug_check.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = os.getenv("CHROMA_DIR")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vs = Chroma(collection_name="vectors", embedding_function=embeddings, persist_directory=CHROMA_DIR)

collection = vs._collection
print("Total chunks in DB:", collection.count())

# Pull a sample to see what's actually stored
sample = collection.peek(limit=3)
for doc, meta in zip(sample["documents"], sample["metadatas"]):
    print("---")
    print("metadata:", meta)
    print("text:", doc[:150])