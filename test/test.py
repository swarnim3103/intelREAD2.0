import os
from dotenv import load_dotenv

load_dotenv()

# Check if API keys exist
hf_token = os.getenv("GEMINI_API_KEY")
if not hf_token:
    print("Error: GEMINI_API_KEY not found in .env file")
    print("Please add your Gemini API key to the .env file")
    exit(1)


from src.query import run_llm
print(" Successfully imported run_llm")
print("Calling run_llm with simple query...")
result = run_llm("What is 2+2?")
print(f"Result: {result}")

