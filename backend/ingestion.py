# ingestion.py (full file)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vectorstore import get_vectorstore
import chromadb

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)


def ingest_text(name: str, text: str):
    """Kept for backwards compatibility (plain text, no page info)."""
    chunks = text_splitter.split_text(text)
    metadatas = [{"source": name, "chunk_index": i} for i in range(len(chunks))]

    vs = get_vectorstore()
    vs.add_texts(chunks, metadatas=metadatas)

    return len(chunks)


def ingest_pages(name: str, pages: list[str]):
    """
    Ingest a document page-by-page so each chunk keeps track of which
    page it came from. `pages` is a list of strings, one per PDF page
    (pages[0] = page 1, etc).

    Idempotent: if a document with this `name` was already ingested,
    its old chunks are deleted first so re-uploading doesn't create
    duplicate entries in the vector store.
    """
    vs = get_vectorstore()
    existing = vs.get()
    if existing["ids"]:
        vs.delete(ids=existing["ids"])
  
    existing = vs._collection.get(where={"source": name})
    if existing and existing.get("ids"):
        print(f"[ingestion] Found {len(existing['ids'])} existing chunks for '{name}', removing before re-ingest.")
        vs._collection.delete(ids=existing["ids"])

    all_chunks = []
    all_metadatas = []

    for page_num, page_text in enumerate(pages, start=1):
        if not page_text or not page_text.strip():
            continue  

        page_chunks = text_splitter.split_text(page_text)
        for i, chunk in enumerate(page_chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": name,
                "page": page_num,
                "chunk_index": len(all_chunks) - 1,
            })

    if not all_chunks:
        print("[ingestion] No text extracted from any page — nothing to add.")
        return 0

    print(f"[ingestion] Adding {len(all_chunks)} chunks from '{name}' to vectorstore...")
    ids = vs.add_texts(all_chunks, metadatas=all_metadatas)
    print(f"[ingestion] add_texts returned {len(ids) if ids else 0} ids: {ids[:3] if ids else ids}")

    
    try:
        count = vs._collection.count()
        print(f"[ingestion] Collection total count after add: {count}")
    except Exception as e:
        print(f"[ingestion] Could not read collection count: {e}")

    return len(all_chunks)