from fastapi import FastAPI
from pydantic import BaseModel
from .ingestion import ingest_text
from .query import get_qa_chain
from pydantic import BaseModel


app = FastAPI()
qa = get_qa_chain()

@app.get("/health")
def health():
    return {"status": "ok"}

class IngestRequest(BaseModel):
    name: str
    text: str

@app.post("/ingest_text")
def ingest(req: IngestRequest):
    count = ingest_text(req.name, req.text)
    return {"status": "ok", "chunks_added": count}


class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(req: AskRequest):
    answer = qa(req.question)   
    return {"answer": answer}
