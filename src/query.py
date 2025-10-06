import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from .ingestion import get_vectorstore

load_dotenv()

# Initialize HF Inference Client
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
client = InferenceClient(model="google/flan-t5-large", token=hf_token)

def run_llm(prompt: str) -> str:
    """Send prompt to Hugging Face model and return generated text"""
    response = client.text_generation(prompt, max_new_tokens=200)
    return response

def get_qa_chain():
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever()

    # Simple QA pipeline: retrieve docs, then call HF model
    def qa_function(query: str):
        docs = retriever.get_relevant_documents(query)
        context = "\n".join([d.page_content for d in docs])
        prompt = f"Answer the question based on context:\n\n{context}\n\nQuestion: {query}\nAnswer:"
        return run_llm(prompt)

    return qa_function
