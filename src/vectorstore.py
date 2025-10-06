import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

CHROMA_DIR = os.getenv("CHROMA_DIR")
embeddings = OpenAIEmbeddings()

def get_vectorstore():
    vectorstore = Chroma(
        collection_name="vectors",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    return vectorstore
