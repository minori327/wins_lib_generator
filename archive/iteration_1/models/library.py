"""
Persist and retrieve SuccessStory objects to/from JSON files.
"""

import json
import logging
from dataclasses import asdict
from dataclasses import dataclass
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)


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
    """Save SuccessStory to JSON file (mechanical serialization).

    Args:
        story: SuccessStory object to save
        library_dir: Directory where story files are stored

    Returns:
        Path to saved JSON file

    Raises:
        ValueError: If story serialization fails
        OSError: If file write fails
    """
    if not library_dir.exists():
        logger.error(f"Library directory does not exist: {library_dir}")
        raise OSError(f"Library directory does not exist: {library_dir}")

    try:
        # Convert dataclass to dictionary
        story_dict = asdict(story)

        # Serialize to JSON
        json_content = json.dumps(story_dict, indent=2, ensure_ascii=False)

        # Determine file path from story.id
        # Format: win-YYYY-MM-{country}-{seq} -> win-YYYY-MM-{country}-{seq}.json
        file_name = f"{story.id}.json"
        file_path = library_dir / file_name

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_content)

        logger.info(f"Saved SuccessStory to {file_path}")

        return file_path

    except Exception as e:
        logger.error(f"Failed to save SuccessStory {story.id}: {e}")
        raise ValueError(f"Failed to save SuccessStory: {e}")


def load_success_story(story_id: str, library_dir: Path) -> SuccessStory:
    """Load SuccessStory from JSON file (mechanical deserialization).

    Args:
        story_id: Story ID without .json extension
        library_dir: Directory where story files are stored

    Returns:
        SuccessStory object

    Raises:
        FileNotFoundError: If story file does not exist
        ValueError: If JSON deserialization fails
    """
    if not library_dir.exists():
        logger.error(f"Library directory does not exist: {library_dir}")
        raise FileNotFoundError(f"Library directory does not exist: {library_dir}")

    # Construct file path
    file_name = f"{story_id}.json"
    file_path = library_dir / file_name

    if not file_path.exists():
        logger.error(f"Story file does not exist: {file_path}")
        raise FileNotFoundError(f"Story file does not exist: {file_path}")

    try:
        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            story_dict = json.load(f)

        # Validate required fields
        required_fields = [
            'id', 'country', 'month', 'customer', 'context', 'action',
            'outcome', 'metrics', 'confidence', 'internal_only',
            'raw_sources', 'last_updated', 'tags', 'industry', 'team_size'
        ]

        missing_fields = [field for field in required_fields if field not in story_dict]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Construct SuccessStory from dictionary
        story = SuccessStory(**story_dict)

        logger.info(f"Loaded SuccessStory from {file_path}")

        return story

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {file_path}: {e}")
        raise ValueError(f"Failed to parse JSON: {e}")
    except Exception as e:
        logger.error(f"Failed to load SuccessStory from {file_path}: {e}")
        raise ValueError(f"Failed to load SuccessStory: {e}")


def load_all_stories(library_dir: Path) -> List[SuccessStory]:
    """Load all SuccessStory objects from library directory (mechanical file loading).

    Args:
        library_dir: Directory where story files are stored

    Returns:
        List of SuccessStory objects

    Raises:
        FileNotFoundError: If library directory does not exist
        ValueError: If any story file fails to load
    """
    if not library_dir.exists():
        logger.error(f"Library directory does not exist: {library_dir}")
        raise FileNotFoundError(f"Library directory does not exist: {library_dir}")

    try:
        # List all JSON files in library directory
        json_files = list(library_dir.glob("*.json"))

        if not json_files:
            logger.info(f"No story files found in {library_dir}")
            return []

        # Load each story file
        stories = []
        failed_files = []

        for file_path in json_files:
            try:
                # Extract story_id from filename (remove .json extension)
                story_id = file_path.stem
                story = load_success_story(story_id, library_dir)
                stories.append(story)

            except Exception as e:
                logger.warning(f"Failed to load story from {file_path}: {e}")
                failed_files.append(str(file_path))
                continue

        if failed_files:
            logger.warning(
                f"Failed to load {len(failed_files)} story files: {failed_files}"
            )

        logger.info(
            f"Loaded {len(stories)} stories from {library_dir} "
            f"({len(json_files)} total files, {len(failed_files)} failed)"
        )

        return stories

    except Exception as e:
        logger.error(f"Failed to load stories from {library_dir}: {e}")
        raise ValueError(f"Failed to load stories: {e}")
