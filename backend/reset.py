import os
from pathlib import Path
from dotenv import load_dotenv
import chromadb

load_dotenv(Path(__file__).resolve().parent / ".env")

CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")

client = chromadb.CloudClient(
    tenant=CHROMA_TENANT,
    database=CHROMA_DATABASE,
    api_key=CHROMA_API_KEY,
)

print("Existing collections:")
for c in client.list_collections():
    print(f"  - {c.name}")

client.delete_collection(name="vectors")
print("Deleted 'vectors' collection.")