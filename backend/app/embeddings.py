# app/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
from dotenv import load_dotenv
load_dotenv()
MODEL_NAME = os.getenv("SENTENCE_MODEL", "all-MiniLM-L6-v2")
INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "../data/faiss_index.bin")

model = SentenceTransformer(MODEL_NAME)
dim = model.get_sentence_embedding_dimension()

# if index exists, load, else create flat index
def load_or_create_index():
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        # store metadata separately in DB (embedding_id linking)
    else:
        index = faiss.IndexFlatL2(dim)
    return index

def save_index(index):
    faiss.write_index(index, INDEX_PATH)

def embed_text(text: str):
    emb = model.encode([text], convert_to_numpy=True, show_progress_bar=False)
    return emb[0].astype('float32')
