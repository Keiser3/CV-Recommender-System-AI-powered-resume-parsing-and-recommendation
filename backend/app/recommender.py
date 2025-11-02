# app/recommender.py
from .embeddings import load_or_create_index, save_index, embed_text
import numpy as np

index = load_or_create_index()
next_id = index.ntotal  # starting id

def add_embedding(embedding: np.ndarray):
    global index, next_id
    # faiss IndexFlat doesn't manage IDs; use IndexIDMap for stable ids if needed
    # For simplicity, we'll just append and return index position
    index.add(np.array([embedding], dtype='float32'))
    idx = index.ntotal - 1
    save_index(index)
    return idx

def search(query_text: str, top_k=5):
    q_emb = embed_text(query_text)
    D, I = index.search(np.array([q_emb], dtype='float32'), top_k)
    # D: distances, I: indexes
    return I[0].tolist(), D[0].tolist()
