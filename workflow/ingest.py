"""
Scan source directories and discover new raw input files for processing.
"""

import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def discover_files(source_dir: Path, country: str, month: str) -> List[Path]:
    """Discover files matching country/month in source directory.

    Args:
        source_dir: Root source directory (e.g., vault/00_sources)
        country: Country code (e.g., 'US')
        month: Month in YYYY-MM format

    Returns:
        List of discovered file paths

    Raises:
        FileNotFoundError: If source_dir does not exist
        ValueError: If country or month format is invalid
    """
    if not source_dir.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    # Validate country code (basic format check)
    if len(country) != 2 or not country.isalpha():
        logger.error(f"Invalid country code format: {country}")
        raise ValueError(f"Invalid country code format: {country} (expected 2-letter code)")

    # Validate month format (basic format check)
    if len(month) != 7 or month[4] != '-':
        logger.error(f"Invalid month format: {month}")
        raise ValueError(f"Invalid month format: {month} (expected YYYY-MM)")

    # Construct pattern: {country}/{month}/*
    pattern = f"{country}/{month}/*"
    matching_paths = list(source_dir.glob(pattern))

    # Filter to files only (not directories)
    matching_files = [p for p in matching_paths if p.is_file()]

    logger.info(f"Discovered {len(matching_files)} files matching pattern '{pattern}' in {source_dir}")

    return matching_files


def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract metadata from file path.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with metadata keys:
        - filename: str - Original filename with extension
        - file_type: str - File extension (pdf, eml, txt, png, jpg, etc.)
        - file_size: int - File size in bytes
        - country: str - Country code extracted from path (if available)
        - month: str - Month extracted from path (if available)
    """
    metadata = {
        "filename": file_path.name,
        "file_type": file_path.suffix.lstrip('.').lower() if file_path.suffix else "unknown",
        "file_size": file_path.stat().st_size if file_path.exists() else 0,
    }

    # Attempt to extract country and month from path structure
    # Expected structure: .../country/month/filename.ext
    path_parts = file_path.parent.parts

    if len(path_parts) >= 2:
        # Check if second-to-last part looks like month (YYYY-MM)
        potential_month = path_parts[-1]
        if len(potential_month) == 7 and potential_month[4] == '-':
            metadata["month"] = potential_month

            # Check if third-to-last part looks like country code (2 letters)
            potential_country = path_parts[-2]
            if len(potential_country) == 2 and potential_country.isalpha():
                metadata["country"] = potential_country.upper()

    return metadata


def is_new_file(file_path: Path, processed_files: List[str]) -> bool:
    """Check if file has been processed before.

    Args:
        file_path: Path to check
        processed_files: List of previously processed file paths (as strings)

    Returns:
        True if file is new (not in processed list), False otherwise
    """
    file_path_str = str(file_path)

    # Deterministic check: is this file's string representation in the list?
    is_new = file_path_str not in processed_files

    if is_new:
        logger.debug(f"File is new: {file_path_str}")
    else:
        logger.debug(f"File already processed: {file_path_str}")

    return is_new
