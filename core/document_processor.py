import PyPDF2
from typing import List

def extract_text_from_pdfs(pdf_files) -> str:
    """Extracts text from a list of uploaded Streamlit PDF files."""
    text = ""
    for f in pdf_files:
        reader = PyPDF2.PdfReader(f)
        for p in reader.pages:
            text += f"\n<source_doc name='{f.name}'>\n{p.extract_text()}\n</source_doc>"
    return text

def chunk_pdf_document(pdf_file, chunk_size: int = 5) -> List[str]:
    """Reads a PDF file and returns a list of text chunks (based on page count)."""
    reader = PyPDF2.PdfReader(pdf_file)
    pages = reader.pages
    chunks = []
    
    for i in range(0, len(pages), chunk_size):
        chunk_text = ""
        for p in pages[i:i + chunk_size]:
            chunk_text += p.extract_text() + "\n"
        chunks.append(chunk_text)
        
    return chunks
