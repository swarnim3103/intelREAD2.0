# debug_duplicates.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = os.getenv("CHROMA_DIR")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vs = Chroma(collection_name="vectors", embedding_function=embeddings, persist_directory=CHROMA_DIR)

collection = vs._collection
data = collection.get(include=["documents", "metadatas"])

print(f"Total entries: {len(data['ids'])}")
print()

for doc_id, doc_text, meta in zip(data["ids"], data["documents"], data["metadatas"]):
    print(f"id={doc_id}")
    print(f"  metadata={meta}")
    print(f"  text={doc_text[:100]!r}")
    print()

# Check for exact duplicate text
from collections import Counter
text_counts = Counter(data["documents"])
dupes = {text: count for text, count in text_counts.items() if count > 1}
print("---")
print(f"Exact duplicate texts found: {len(dupes)}")
for text, count in dupes.items():
    print(f"  (x{count}) {text[:100]!r}")