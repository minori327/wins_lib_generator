"""
Define RawItem data schema for standardized raw data representation.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class RawItem:
    """Standardized raw data representation."""
    id: str  # UUID v4 format
    text: str  # Extracted English text content
    source_type: str  # "pdf" | "email" | "teams" | "image"
    filename: str  # Original filename with extension
    country: str  # ISO 3166-1 alpha-2 code
    month: str  # YYYY-MM format
    created_at: str  # ISO-8601 datetime
    metadata: Dict  # Optional metadata (file_path, file_size, etc.)
