from fastapi import FastAPI,UploadFile, File
from pydantic import BaseModel
from .ingestion import ingest_text
from .query import get_qa_chain
from pydantic import BaseModel
from PyPDF2 import PdfReader

app = FastAPI()
qa = get_qa_chain()

@app.get("/health")
def health():
    return {"status": "ok"}

class IngestRequest(BaseModel):
   file: UploadFile = File(...)

@app.post("/ingest_text")
def ingest(req: IngestRequest):
    pdf_reader = PdfReader(req.file.file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    count = ingest_text(req.file.filename, text)
    return {"status": "ok", "chunks_added": count}


class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(req: AskRequest):
    answer = qa(req.question)   
    return {"answer": answer}
