"""
Scan source directories and discover new raw input files for processing.
"""

from typing import List, Dict, Any
from pathlib import Path


def discover_files(source_dir: Path, country: str, month: str) -> List[Path]:
    """TODO: Discover files matching country/month in source directory."""
    pass


def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """TODO: Extract metadata from file path."""
    pass


def is_new_file(file_path: Path, processed_files: List[str]) -> bool:
    """TODO: Check if file has been processed before."""
    pass
