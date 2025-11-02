# app/extractor.py
import fitz  # PyMuPDF

def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    text_parts = []
    for page in doc:
        text = page.get_text("text")
        if text:
            text_parts.append(text)
    doc.close()
    return "\n".join(text_parts)
