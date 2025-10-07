# intellRead

#### Completing an old project


- #### How rag (retrival augmented generation works) :


  1. Query Input
   - A user provides a question or prompt.
 
     

  2. Retriever (Knowledge Search)
   - The query is converted into a vector embedding.
   - This embedding is used to search a vector database (Chroma).
   - Relevant documents/passages are retrieved based on similarity to the query.
 
     

  3. Augmentation (Context Injection)
   - The retrieved documents are appended to the original query.
   - This enriched prompt gives the LLM external knowledge to work with.



  4. Generator (LLM Response)
  - The LLM processes the augmented input.
  - It generates a response that is grounded in the retrieved documents.
    


  5. Final Output
  - The user receives a contextual, fact-based response.


 
  
- Steps that i followed :
  - 1. Made .env(for hugging face api key and chroma dir) and requirements.txt 
  - 2. Added src/main.py for exposing endpoints
  - 3. Added src/vectorstore.py for create/load a Chroma vector DB, add texts and similarity search.
  - 4. Added src/ingestion.py for functions to read .txt or .pdf, clean text, split into chunks (with overlap).
  - 5. Used Chroma for vector database 
  - 6. Hugging face for free open api
  - 7. Basic frontend inspired from NotebookLM 

> ```bash
> pip install -r requirements.txt
> ```
