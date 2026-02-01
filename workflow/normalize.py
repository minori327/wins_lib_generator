"""
Convert raw files into RawItem objects through mechanical text extraction.
"""

from pathlib import Path
from models.raw_item import RawItem


def normalize_pdf(file_path: Path, country: str, month: str) -> RawItem:
    """TODO: Extract text from PDF and create RawItem."""
    pass


def normalize_email(file_path: Path, country: str, month: str) -> RawItem:
    """TODO: Extract headers and body from email and create RawItem."""
    pass


def normalize_image(file_path: Path, country: str, month: str) -> RawItem:
    """TODO: Extract text from image using OCR and create RawItem."""
    pass


def normalize_teams_text(file_path: Path, country: str, month: str) -> RawItem:
    """TODO: Read and normalize Teams text message into RawItem."""
    pass
