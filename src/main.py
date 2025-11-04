from fastapi import FastAPI,UploadFile, File
from pydantic import BaseModel
from .ingestion import ingest_text
from .query import get_qa_chain
from pydantic import BaseModel
from PyPDF2 import PdfReader
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
qa = get_qa_chain()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

class IngestRequest(BaseModel):
   file: UploadFile = File(...)

@app.post("/ingest_pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    pdf_reader = PdfReader(file.file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    count = ingest_text(file.filename, text)
    return {"status": "ok", "chunks_added": count}


class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(req: AskRequest):
    answer =qa(req.question)   
    return {"answer": answer}
