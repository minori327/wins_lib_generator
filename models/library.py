"""
Persist and retrieve SuccessStory objects to/from JSON files.
"""

from dataclasses import dataclass
from typing import List
from pathlib import Path


@dataclass
class SuccessStory:
    """Core business object representing a success story."""
    id: str  # Format: win-YYYY-MM-{country}-{seq}
    country: str  # ISO 3166-1 alpha-2
    month: str  # YYYY-MM
    customer: str  # Customer name
    context: str  # Business problem or situation
    action: str  # What was done
    outcome: str  # Results achieved
    metrics: List[str]  # Quantifiable impact metrics
    confidence: str  # "high" | "medium" | "low"
    internal_only: bool  # Whether restricted to internal use
    raw_sources: List[str]  # Source filenames
    last_updated: str  # ISO-8601 timestamp
    tags: List[str]  # Optional business tags
    industry: str  # Optional industry classification
    team_size: str  # Optional team size category


def save_success_story(story: SuccessStory, library_dir: Path) -> Path:
    """TODO: Save SuccessStory to JSON file."""
    pass


def load_success_story(story_id: str, library_dir: Path) -> SuccessStory:
    """TODO: Load SuccessStory from JSON file."""
    pass


def load_all_stories(library_dir: Path) -> List[SuccessStory]:
    """TODO: Load all SuccessStory objects from library."""
    pass
