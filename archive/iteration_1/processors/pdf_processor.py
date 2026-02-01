"""
Extract text from PDF files mechanically.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# PDF processing library import
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract all text from PDF file.

    Args:
        file_path: Path to PDF file

    Returns:
        Extracted text string

    Raises:
        FileNotFoundError: If PDF file does not exist
        ValueError: If PDF extraction fails or returns empty text
        ImportError: If pypdf library is not installed
    """
    if PdfReader is None:
        raise ImportError(
            "pypdf library is required for PDF text extraction. "
            "Install it with: pip install pypdf"
        )

    if not file_path.exists():
        logger.error(f"PDF file does not exist: {file_path}")
        raise FileNotFoundError(f"PDF file does not exist: {file_path}")

    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text_parts = []

            # Extract text from each page
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num} in {file_path}: {e}")
                    continue

            if not text_parts:
                logger.error(f"No text extracted from PDF: {file_path}")
                raise ValueError(f"No text could be extracted from PDF: {file_path}")

            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from {len(reader.pages)} pages in {file_path}")

            return full_text

    except Exception as e:
        logger.error(f"Failed to read PDF file {file_path}: {e}")
        raise ValueError(f"Failed to extract text from PDF {file_path}: {e}")
