"""
PDF Extractor Tool for downloading and extracting text from PDF files
"""
from crewai.tools import BaseTool
import requests
import io
from typing import Type, Dict
from pydantic import BaseModel, Field
from pypdf import PdfReader
import logging
from datetime import datetime
import os
from urllib.parse import urlparse


class PDFExtractorToolInput(BaseModel):
    """Input schema for PDFExtractorTool"""
    pdf_url: str = Field(..., description="The URL of the PDF file to download and extract")
    save_path: str = Field(default="data/raw", description="Directory to save downloaded PDFs")


class PDFExtractorTool(BaseTool):
    name: str = "PDF Extractor"
    description: str = (
        "Downloads a PDF from a URL, extracts its text content, and saves the PDF file. "
        "Returns extracted text and metadata about the PDF."
    )
    args_schema: Type[BaseModel] = PDFExtractorToolInput

    def _run(self, pdf_url: str, save_path: str = "data/raw") -> Dict:
        """
        Download and extract text from PDF

        Args:
            pdf_url: URL of the PDF to download
            save_path: Directory to save the PDF

        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Download PDF
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(pdf_url, headers=headers, timeout=30)
            response.raise_for_status()

            # Read PDF content
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)

            # Extract text from all pages
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() or ""

            # Extract metadata
            metadata = reader.metadata

            # Save PDF to disk
            os.makedirs(save_path, exist_ok=True)
            filename = os.path.basename(urlparse(pdf_url).path)
            filepath = os.path.join(save_path, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            result = {
                'url': pdf_url,
                'filename': filename,
                'filepath': filepath,
                'text': full_text,
                'page_count': len(reader.pages),
                'title': metadata.get('/Title', 'Unknown') if metadata else 'Unknown',
                'author': metadata.get('/Author', 'Unknown') if metadata else 'Unknown',
                'downloaded_at': datetime.now().isoformat(),
                'success': True
            }

            logging.info(f"Successfully extracted PDF: {filename}")
            return result

        except Exception as e:
            logging.error(f"Error extracting PDF from {pdf_url}: {str(e)}")
            return {
                'url': pdf_url,
                'error': str(e),
                'success': False
            }
