import os
from dotenv import load_dotenv
from .vectorstore import get_vectorstore
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub  

load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# --- Option 1: Free local HuggingFace model ---
# (uses HuggingFace Hub, requires a HF token if model is gated)
# Replace with "google/flan-t5-small" or "google/flan-t5-base"
def get_qa_chain():
    vs = get_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": 3})
    llm = HuggingFaceHub(    repo_id="google/flan-t5-large",
    model_kwargs={"temperature": 0.7, "max_length": 512},
    task="text2text-generation",
    huggingfacehub_api_token=HUGGINGFACE_API_KEY)
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
