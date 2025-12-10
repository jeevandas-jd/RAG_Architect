# src/api/main.py
import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path

from ingest import ingest_pdf_to_weaviate
from query import retrieve_and_answer

app = FastAPI(title="RAG Architect API")

BASE_DATA = Path(os.getenv("DATA_DIR", "/data"))
BASE_DATA.mkdir(parents=True, exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...), source: str = Form(None)):
    # save uploaded file
    dest = BASE_DATA / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        ingest_pdf_to_weaviate(str(dest), source_name=source)
        return {"status":"ok", "file": file.filename}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/query")
async def query(question: str = Form(...)):
    try:
        result = retrieve_and_answer(question)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
