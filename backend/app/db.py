# app/db.py
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, JSON, Text
from sqlalchemy.sql import select
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cv_recommender.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata = MetaData()

cvs = Table(
    "cvs", metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String, nullable=False),
    Column("raw_text", Text),
    Column("parsed_json", JSON),
    Column("embedding_id", Integer)  # map to vector index id
)

metadata.create_all(engine)

def insert_cv(conn, filename, raw_text, parsed_json, embedding_id):
    ins = cvs.insert().values(filename=filename, raw_text=raw_text, parsed_json=parsed_json, embedding_id=embedding_id)
    result = conn.execute(ins)
    conn.commit()
    return result.inserted_primary_key[0]
