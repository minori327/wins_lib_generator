"""
Extract text from images using OCR.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# OCR library import
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None  # type: ignore
    Image = None  # type: ignore


def extract_text_from_image(file_path: Path) -> str:
    """Extract text from image using OCR.

    Args:
        file_path: Path to image file (.png, .jpg, .jpeg, etc.)

    Returns:
        Extracted text string

    Raises:
        FileNotFoundError: If image file does not exist
        ValueError: If OCR fails or returns empty text
        ImportError: If pytesseract or Pillow library is not installed
    """
    if pytesseract is None or Image is None:
        raise ImportError(
            "pytesseract and Pillow libraries are required for OCR text extraction. "
            "Install them with: pip install pytesseract Pillow"
        )

    if not file_path.exists():
        logger.error(f"Image file does not exist: {file_path}")
        raise FileNotFoundError(f"Image file does not exist: {file_path}")

    try:
        # Open image file
        with Image.open(file_path) as img:
            # Perform OCR using pytesseract
            text = pytesseract.image_to_string(img)

        if not text or text.strip() == '':
            logger.error(f"No text extracted from image: {file_path}")
            raise ValueError(f"No text could be extracted from image: {file_path}")

        # Clean up the extracted text
        cleaned_text = text.strip()

        logger.info(f"Extracted {len(cleaned_text)} characters from image {file_path}")

        return cleaned_text

    except Exception as e:
        logger.error(f"Failed to extract text from image {file_path}: {e}")
        raise ValueError(f"Failed to extract text from image: {e}")
