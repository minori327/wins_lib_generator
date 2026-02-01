"""
Convert raw files into RawItem objects through mechanical text extraction.
"""

import logging
import hashlib
from pathlib import Path
from models.raw_item import RawItem
from processors import pdf_processor
from processors import email_processor
from processors import image_processor
from processors import text_processor

logger = logging.getLogger(__name__)


def normalize_pdf(file_path: Path, country: str, month: str) -> RawItem:
    """Extract text from PDF and create RawItem.

    Args:
        file_path: Path to PDF file
        country: Country code
        month: Month in YYYY-MM format

    Returns:
        RawItem object with extracted PDF text

    Raises:
        FileNotFoundError: If PDF file does not exist
        ValueError: If PDF extraction fails
    """
    # Extract text using PDF processor
    text = pdf_processor.extract_text_from_pdf(file_path)

    # Generate deterministic ID from file path and metadata
    content = f"{file_path}:{country}:{month}"
    hash_bytes = hashlib.sha256(content.encode()).digest()
    hex_str = hash_bytes[:16].hex()
    item_id = f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"

    # Create RawItem with deterministic fields
    raw_item = RawItem(
        id=item_id,
        text=text,
        source_type="pdf",
        filename=file_path.name,
        country=country,
        month=month,
        created_at="",  # Populated by caller
        metadata={
            "file_path": str(file_path),
        }
    )

    logger.info(f"Normalized PDF to RawItem: {file_path.name} ({len(text)} characters)")

    return raw_item


def normalize_email(file_path: Path, country: str, month: str) -> RawItem:
    """Extract headers and body from email and create RawItem.

    Args:
        file_path: Path to .eml file
        country: Country code
        month: Month in YYYY-MM format

    Returns:
        RawItem object with extracted email content

    Raises:
        FileNotFoundError: If email file does not exist
        ValueError: If email parsing fails
    """
    # Extract email data using email processor
    email_data = email_processor.extract_email_data(file_path)

    # Format email content as text
    text_parts = [
        f"Subject: {email_data['subject']}",
        f"From: {email_data['from']}",
        f"To: {email_data['to']}",
        f"Date: {email_data['date']}",
        "",
        email_data['body']
    ]
    text = "\n".join(text_parts)

    # Generate deterministic ID from file path and metadata
    content = f"{file_path}:{country}:{month}"
    hash_bytes = hashlib.sha256(content.encode()).digest()
    hex_str = hash_bytes[:16].hex()
    item_id = f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"

    # Create RawItem with deterministic fields
    raw_item = RawItem(
        id=item_id,
        text=text,
        source_type="email",
        filename=file_path.name,
        country=country,
        month=month,
        created_at="",  # Populated by caller
        metadata={
            "file_path": str(file_path),
            "subject": email_data['subject'],
            "from": email_data['from'],
            "to": email_data['to'],
        }
    )

    logger.info(f"Normalized email to RawItem: {file_path.name} ({len(text)} characters)")

    return raw_item


def normalize_image(file_path: Path, country: str, month: str) -> RawItem:
    """Extract text from image using OCR and create RawItem.

    Args:
        file_path: Path to image file
        country: Country code
        month: Month in YYYY-MM format

    Returns:
        RawItem object with OCR-extracted text

    Raises:
        FileNotFoundError: If image file does not exist
        ValueError: If OCR fails
    """
    # Extract text using OCR processor
    text = image_processor.extract_text_from_image(file_path)

    # Generate deterministic ID from file path and metadata
    content = f"{file_path}:{country}:{month}"
    hash_bytes = hashlib.sha256(content.encode()).digest()
    hex_str = hash_bytes[:16].hex()
    item_id = f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"

    # Create RawItem with deterministic fields
    raw_item = RawItem(
        id=item_id,
        text=text,
        source_type="image",
        filename=file_path.name,
        country=country,
        month=month,
        created_at="",  # Populated by caller
        metadata={
            "file_path": str(file_path),
        }
    )

    logger.info(f"Normalized image to RawItem: {file_path.name} ({len(text)} characters)")

    return raw_item


def normalize_teams_text(file_path: Path, country: str, month: str) -> RawItem:
    """Read and normalize Teams text message into RawItem.

    Args:
        file_path: Path to .txt file
        country: Country code
        month: Month in YYYY-MM format

    Returns:
        RawItem object with normalized text content

    Raises:
        FileNotFoundError: If text file does not exist
        ValueError: If text reading fails
    """
    if not file_path.exists():
        logger.error(f"Text file does not exist: {file_path}")
        raise FileNotFoundError(f"Text file does not exist: {file_path}")

    try:
        # Read text content
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_text = file.read()

        # Normalize text encoding
        text = text_processor.normalize_text_encoding(raw_text)

    except UnicodeDecodeError:
        # Fallback: try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                raw_text = file.read()
            text = text_processor.normalize_text_encoding(raw_text)
        except Exception as e:
            logger.error(f"Failed to read text file {file_path}: {e}")
            raise ValueError(f"Failed to read text file: {e}")

    # Generate deterministic ID from file path and metadata
    content = f"{file_path}:{country}:{month}"
    hash_bytes = hashlib.sha256(content.encode()).digest()
    hex_str = hash_bytes[:16].hex()
    item_id = f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"

    # Create RawItem with deterministic fields
    raw_item = RawItem(
        id=item_id,
        text=text,
        source_type="teams",
        filename=file_path.name,
        country=country,
        month=month,
        created_at="",  # Populated by caller
        metadata={
            "file_path": str(file_path),
        }
    )

    logger.info(f"Normalized Teams text to RawItem: {file_path.name} ({len(text)} characters)")

    return raw_item
