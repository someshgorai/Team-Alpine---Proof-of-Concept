import requests, io, os, logging
from datetime import datetime
from urllib.parse import urlparse
from pypdf import PdfReader
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class PDFExtractorInput(BaseModel):
    pdf_url: str
    save_path: str = Field(default="data/raw")

def extract_pdf(pdf_url: str, save_path: str = "data/raw"):
    """Download PDF, extract text, and metadata."""
    os.makedirs(save_path, exist_ok=True)
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(pdf_url, headers=headers, timeout=30)
    response.raise_for_status()

    pdf_file = io.BytesIO(response.content)
    reader = PdfReader(pdf_file)
    text = "".join([page.extract_text() or "" for page in reader.pages])
    metadata = reader.metadata or {}

    filename = os.path.basename(urlparse(pdf_url).path)
    filepath = os.path.join(save_path, filename)
    with open(filepath, 'wb') as f:
        f.write(response.content)

    return {
        "url": pdf_url,
        "filename": filename,
        "page_count": len(reader.pages),
        "title": metadata.get('/Title', 'Unknown'),
        "author": metadata.get('/Author', 'Unknown'),
        "downloaded_at": datetime.now().isoformat(),
        "text": text,
    }

PDFExtractorTool = BaseTool.from_function(
    func=extract_pdf,
    name="PDFExtractor",
    description="Download and extract text and metadata from a PDF file.",
    args_schema=PDFExtractorInput,
)
