from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from ingestion import ingest_pages
from query import get_qa_chain
from PyPDF2 import PdfReader
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
qa = get_qa_chain()

origins = [
    "https://intel-read.vercel.app/",
    "http://localhost:5173"
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


@app.post("/ingest_pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        pdf_reader = PdfReader(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read PDF — file may be corrupted or encrypted")

    if len(pdf_reader.pages) == 0:
        raise HTTPException(status_code=400, detail="PDF has no pages")

    pages = []
    for page in pdf_reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")  

    if not any(p.strip() for p in pages):
        raise HTTPException(
            status_code=422,
            detail="No extractable text found — this may be a scanned/image-only PDF",
        )

    count = ingest_pages(file.filename, pages)
    return {"status": "ok", "chunks_added": count, "pages_processed": len(pages)}

class AskRequest(BaseModel):
    question: str
    allow_outside_knowledge: bool = False  


@app.post("/ask")
async def ask(req: AskRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = qa(req.question, allow_outside_knowledge=req.allow_outside_knowledge)
    return result