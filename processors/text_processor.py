"""
Clean and normalize text encoding.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def normalize_text_encoding(text: str) -> str:
    """Clean and normalize text encoding.

    Args:
        text: Input text string

    Returns:
        Cleaned text string with normalized encoding

    Raises:
        ValueError: If text is not a string
        UnicodeDecodeError: If text cannot be decoded
    """
    if not isinstance(text, str):
        logger.error(f"Input must be string, got {type(text)}")
        raise ValueError(f"Input must be string, got {type(text)}")

    try:
        # If text is already a string, normalize it
        # First, handle any problematic characters
        normalized = text

        # Replace common problematic characters
        replacements = {
            '\u00a0': ' ',  # Non-breaking space
            '\u201c': '"',  # Left smart quote
            '\u201d': '"',  # Right smart quote
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u2013': '-',  # En dash
            '\u2014': '--',  # Em dash
            '\u2026': '...',  # Ellipsis
        }

        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        # Normalize Unicode to NFC form (canonical composition)
        import unicodedata
        normalized = unicodedata.normalize('NFC', normalized)

        # Remove any remaining null bytes or control characters (except newlines and tabs)
        cleaned = ''.join(
            char for char in normalized
            if char == '\n' or char == '\t' or unicodedata.category(char)[0] != 'C'
        )

        logger.debug(f"Normalized text encoding: {len(text)} -> {len(cleaned)} characters")

        return cleaned

    except Exception as e:
        logger.error(f"Failed to normalize text encoding: {e}")
        raise ValueError(f"Failed to normalize text encoding: {e}")
