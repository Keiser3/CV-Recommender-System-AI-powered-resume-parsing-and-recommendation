# app/main.py
import os, shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import sqlite3
from .extractor import extract_text_from_pdf
from .parser import parse_cv_with_llm
from .recommender import add_embedding, search
from .embeddings import embed_text
from .db import insert_cv
load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "../data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "changeme")

app = FastAPI(title="CV Recommender")

def check_api_key(key: str = Form(...)):
    if key != BACKEND_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/upload")
async def upload_cv(file: UploadFile = File(...), api_key: str = Form(...)):
    if api_key != BACKEND_API_KEY:
        raise HTTPException(status_code=401)
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDFs accepted")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    text = extract_text_from_pdf(file_path)
    parsed = await parse_cv_with_llm(text)
    # build a candidate text for embedding (resume summary + skills)
    candidate_text = " ".join([
        parsed.get("summary","") or "",
        " ".join(parsed.get("skills",[])) or "",
        parsed.get("location","") or ""
    ])
    embedding = embed_text(candidate_text or text[:2000])
    emb_id = add_embedding(embedding)
    # store in DB
    conn = sqlite3.connect(os.getenv("DATABASE_URL").replace("sqlite:///", ""))
    cv_id = insert_cv(conn, file.filename, text, parsed, emb_id)
    return {"status":"ok", "cv_id": cv_id}

@app.post("/recommend")
async def recommend(query: str = Form(...), api_key: str = Form(...), top_k: int = Form(5)):
    if api_key != BACKEND_API_KEY:
        raise HTTPException(status_code=401)
    ids, distances = search(query, top_k)
    # retrieve CV entries from DB
    conn = sqlite3.connect(os.getenv("DATABASE_URL").replace("sqlite:///", ""))
    cur = conn.cursor()
    results = []
    for idx, d in zip(ids, distances):
        # since we used position as id, map embedding idx -> DB row
        cur.execute("SELECT id, filename, parsed_json FROM cvs WHERE embedding_id = ?", (idx,))
        row = cur.fetchone()
        if row:
            results.append({"score": float(d), "cv": row[2], "filename": row[1], "db_id": row[0]})
    return JSONResponse({"results": results})
