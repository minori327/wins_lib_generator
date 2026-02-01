"""
Deletion Store for safe persistence of deleted SuccessStory objects.

Ensures deletions are reversible and auditable.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import asdict

from models.deleted_story import DeletedStory
from models.library import SuccessStory

logger = logging.getLogger(__name__)


class DeletionStore:
    """Persist and manage deleted SuccessStory objects."""

    def __init__(self, store_dir: Path):
        """Initialize deletion store.

        Args:
            store_dir: Directory where deleted stories are stored
        """
        self.store_dir = store_dir
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def _get_story_path(self, story_id: str) -> Path:
        """Get file path for a deleted story.

        Args:
            story_id: Story ID

        Returns:
            Path to deleted story JSON file
        """
        return self.store_dir / f"{story_id}.deleted.json"

    def save_deleted_story(
        self,
        story: SuccessStory,
        reason: str,
        deleted_by: str = "system"
    ) -> DeletedStory:
        """Persist a deleted SuccessStory with metadata.

        Args:
            story: SuccessStory to delete
            reason: Reason for deletion
            deleted_by: Who is deleting the story

        Returns:
            DeletedStory record
        """
        from dataclasses import asdict

        # Create DeletedStory record
        deleted_story = DeletedStory(
            story_id=story.id,
            original_data=asdict(story),
            deleted_at=datetime.utcnow().isoformat() + "Z",
            deleted_reason=reason,
            deleted_by=deleted_by,
            source_raw_item_ids=story.raw_sources,
            restored=False,
            restored_at="",
            restored_by=""
        )

        # Save to file
        file_path = self._get_story_path(story.id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(deleted_story), f, indent=2, ensure_ascii=False)

        logger.info(
            f"Persisted deleted story {story.id} to {file_path} "
            f"(reason: {reason}, by: {deleted_by})"
        )

        return deleted_story

    def load_deleted_story(self, story_id: str) -> Optional[DeletedStory]:
        """Load a deleted story record.

        Args:
            story_id: Story ID to load

        Returns:
            DeletedStory if found, None otherwise
        """
        file_path = self._get_story_path(story_id)

        if not file_path.exists():
            logger.warning(f"Deleted story not found: {story_id}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            deleted_story = DeletedStory(**data)

            logger.debug(f"Loaded deleted story {story_id} from {file_path}")

            return deleted_story

        except Exception as e:
            logger.error(f"Failed to load deleted story {story_id}: {e}")
            return None

    def restore_story(self, story_id: str, restored_by: str = "system") -> Optional[SuccessStory]:
        """Restore a deleted story.

        Args:
            story_id: Story ID to restore
            restored_by: Who is restoring the story

        Returns:
            Restored SuccessStory if found, None otherwise
        """
        # Load deleted story
        deleted_story = self.load_deleted_story(story_id)
        if deleted_story is None:
            return None

        # Check if already restored
        if deleted_story.restored:
            logger.warning(f"Story {story_id} already restored")
            return None

        # Reconstruct SuccessStory
        story = SuccessStory(**deleted_story.original_data)

        # Update deleted story record
        deleted_story.restored = True
        deleted_story.restored_at = datetime.utcnow().isoformat() + "Z"
        deleted_story.restored_by = restored_by

        # Save updated record
        file_path = self._get_story_path(story_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(deleted_story), f, indent=2, ensure_ascii=False)

        logger.info(f"Restored story {story_id} (by: {restored_by})")

        return story

    def list_deleted_stories(self) -> List[DeletedStory]:
        """List all deleted stories in the store.

        Returns:
            List of DeletedStory objects
        """
        deleted_stories = []

        for file_path in self.store_dir.glob("*.deleted.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                deleted_story = DeletedStory(**data)
                deleted_stories.append(deleted_story)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue

        logger.info(f"Listed {len(deleted_stories)} deleted stories from {self.store_dir}")

        return deleted_stories

    def permanently_delete(self, story_id: str) -> bool:
        """Permanently remove a deleted story record (cannot be undone).

        Args:
            story_id: Story ID to permanently delete

        Returns:
            True if deleted, False if not found
        """
        file_path = self._get_story_path(story_id)

        if not file_path.exists():
            logger.warning(f"Cannot permanently delete {story_id}: not found")
            return False

        try:
            file_path.unlink()
            logger.warning(f"Permanently deleted story record: {story_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to permanently delete {story_id}: {e}")
            return False
