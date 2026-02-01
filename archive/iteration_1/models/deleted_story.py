"""
DeletedStory model for safe deletion with persistence.
"""

from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class DeletedStory:
    """Record of a deleted SuccessStory with metadata.

    Ensures deletions are reversible and auditable.
    """
    # Original story data
    story_id: str  # Original SuccessStory ID
    original_data: dict  # Complete SuccessStory as dictionary

    # Deletion metadata
    deleted_at: str  # When story was deleted (ISO-8601)
    deleted_reason: str  # Why story was deleted
    deleted_by: str  # Who deleted the story (human or system)

    # Traceability
    source_raw_item_ids: List[str]  # Original RawItem IDs for traceability

    # Restoration flag
    restored: bool = False  # Whether story has been restored
    restored_at: str = ""  # When story was restored (ISO-8601), if applicable
    restored_by: str = ""  # Who restored the story, if applicable
