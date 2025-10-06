# intellRead

#### Completing an old project
- Steps that i followed :
  - 1. Made .env(for hugging face api key and chroma dir) and requirements.txt 
  - 2. Added src/main.py for exposing endpoints
  - 3. Added src/vectorstore.py for create/load a Chroma vector DB, add texts and similarity search.
  - 4. Added src/ingestion.py for functions to read .txt or .pdf, clean text, split into chunks (with overlap).
  - 5. Used Chroma for vector database 
  - 6. Hugging face for free open api 

> ```bash
> pip install -r requirements.txt
> ```
