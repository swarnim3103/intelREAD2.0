import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from .vectorstore import get_vectorstore

load_dotenv()

# Configure Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

def run_llm(prompt: str) -> str:
    """Send prompt to Gemini model and return generated text"""
    try:
        if not gemini_api_key:
            return "Error: GEMINI_API_KEY not found in environment variables"
        
        # Initialize the Gemini model (using latest flash model)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Generate content
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

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
