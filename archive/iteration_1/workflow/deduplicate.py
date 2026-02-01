"""
Remove duplicate RawItem objects using mechanical equality checks.
"""

import logging
from typing import List
from models.raw_item import RawItem

logger = logging.getLogger(__name__)


def is_duplicate_raw_item(item: RawItem, existing_items: List[RawItem]) -> bool:
    """Check if RawItem is duplicate of an existing RawItem using mechanical equality.

    Duplicate definition (mechanical only):
    - Same RawItem.id (exact string match)
    - OR same (filename + country + month) combination

    Args:
        item: RawItem to check
        existing_items: List of existing RawItem objects

    Returns:
        True if duplicate found, False otherwise
    """
    for existing in existing_items:
        # Check 1: Same ID (exact string match)
        if item.id == existing.id:
            logger.debug(
                f"Duplicate found by ID: {item.id} matches {existing.id}"
            )
            return True

        # Check 2: Same (filename + country + month) combination
        if (item.filename == existing.filename and
            item.country == existing.country and
            item.month == existing.month):
            logger.debug(
                f"Duplicate found by (filename, country, month): "
                f"{item.filename}|{item.country}|{item.month} matches "
                f"{existing.filename}|{existing.country}|{existing.month}"
            )
            return True

    return False


def deduplicate_raw_items(items: List[RawItem]) -> List[RawItem]:
    """Remove duplicate RawItem objects from list.

    Mechanical deduplication only:
    - Keep first occurrence
    - Drop subsequent duplicates
    - No merging
    - No similarity metrics

    Args:
        items: List of RawItem objects

    Returns:
        Deduplicated list of RawItem objects
    """
    if not items:
        return []

    deduplicated = []
    seen_ids = set()
    seen_signatures = set()

    for item in items:
        # Check if we've seen this ID before
        if item.id in seen_ids:
            logger.debug(f"Skipping duplicate by ID: {item.id}")
            continue

        # Check if we've seen this (filename, country, month) signature before
        signature = f"{item.filename}|{item.country}|{item.month}"
        if signature in seen_signatures:
            logger.debug(
                f"Skipping duplicate by signature: {signature} (ID: {item.id})"
            )
            continue

        # Not seen before, add to deduplicated list
        seen_ids.add(item.id)
        seen_signatures.add(signature)
        deduplicated.append(item)

    logger.info(
        f"Deduplication complete: {len(items)} items -> {len(deduplicated)} unique items"
    )

    return deduplicated
