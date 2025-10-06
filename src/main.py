from fastapi import FastAPI
from pydantic import BaseModel
from .ingestion import ingest_text

app = FastAPI()

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
