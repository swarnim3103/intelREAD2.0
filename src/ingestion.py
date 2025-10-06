from langchain.text_splitter import RecursiveCharacterTextSplitter
from .vectorstore import get_vectorstore

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

def ingest_text(name: str, text: str):

    chunks = text_splitter.split_text(text)
    metadatas = [{"source": name} for _ in chunks]

   
    vs = get_vectorstore()
    vs.add_texts(chunks, metadatas=metadatas)
    vs.persist()

    return len(chunks)
