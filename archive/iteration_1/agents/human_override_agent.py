"""
Human Override Agent for manual approval, rejection, and editing.

Allows human decisions to override automated Phase 5 logic.
All human decisions are persisted and take precedence.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from models.library import SuccessStory
from utils.deletion_store import DeletionStore

logger = logging.getLogger(__name__)


@dataclass
class HumanDecision:
    """Record of a human decision overriding automated logic."""
    story_id: str  # Story ID this decision applies to
    decision_type: str  # "approve", "reject", "edit", "merge"
    automated_action: str  # What the automated logic wanted to do
    human_action: str  # What the human decided instead
    reason: str  # Human's explanation for the decision
    decision_timestamp: str  # When decision was made (ISO-8601)
    decision_author: str  # Who made the decision (e.g., username)

    # For "edit" decisions
    edited_fields: Optional[Dict[str, Any]] = None  # Fields that were changed

    # For "merge" decisions
    merge_story_ids: Optional[List[str]] = None  # Stories to merge


class HumanOverrideStore:
    """Persist human decisions to JSON file for audit trail."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.decisions: Dict[str, HumanDecision] = {}  # story_id -> decision

    def load(self):
        """Load decisions from JSON file."""
        if not self.storage_path.exists():
            logger.info(f"No existing decisions file at {self.storage_path}")
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Reconstruct HumanDecision objects
            for story_id, decision_dict in data.items():
                self.decisions[story_id] = HumanDecision(**decision_dict)

            logger.info(f"Loaded {len(self.decisions)} human decisions from {self.storage_path}")

        except Exception as e:
            logger.error(f"Failed to load decisions from {self.storage_path}: {e}")
            raise

    def save(self):
        """Save decisions to JSON file."""
        try:
            # Convert to dict for JSON serialization
            data = {
                story_id: asdict(decision)
                for story_id, decision in self.decisions.items()
            }

            # Ensure parent directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.decisions)} human decisions to {self.storage_path}")

        except Exception as e:
            logger.error(f"Failed to save decisions to {self.storage_path}: {e}")
            raise

    def record_decision(self, decision: HumanDecision):
        """Record a human decision.

        Args:
            decision: HumanDecision to record
        """
        self.decisions[decision.story_id] = decision
        logger.info(
            f"Recorded human decision for {decision.story_id}: "
            f"{decision.decision_type} (overrode {decision.automated_action})"
        )

    def get_decision(self, story_id: str) -> Optional[HumanDecision]:
        """Get human decision for a story, if exists.

        Args:
            story_id: Story ID to look up

        Returns:
            HumanDecision if exists, None otherwise
        """
        return self.decisions.get(story_id)

    def has_decision(self, story_id: str) -> bool:
        """Check if a human decision exists for a story.

        Args:
            story_id: Story ID to check

        Returns:
            True if decision exists, False otherwise
        """
        return story_id in self.decisions

    def clear_decision(self, story_id: str):
        """Clear a human decision (revert to automated logic).

        Args:
            story_id: Story ID to clear decision for
        """
        if story_id in self.decisions:
            del self.decisions[story_id]
            logger.info(f"Cleared human decision for {story_id}")


def apply_human_override(
    story: SuccessStory,
    decision: HumanDecision,
    deletion_store: Optional[DeletionStore] = None
) -> Optional[SuccessStory]:
    """Apply human decision to a SuccessStory.

    SAFE DELETION: If decision is "reject", story is persisted to deletion store
    instead of being silently discarded.

    Args:
        story: Original SuccessStory
        decision: HumanDecision to apply
        deletion_store: DeletionStore for persisting rejected stories

    Returns:
        Modified SuccessStory based on human decision, or None if rejected

    Raises:
        ValueError: If decision type is unknown
    """
    # Work with a copy
    from dataclasses import replace
    modified_story = story

    if decision.decision_type == "approve":
        # No changes needed, just approve
        logger.info(f"Human approved story {story.id}")
        return modified_story

    elif decision.decision_type == "reject":
        # SAFE DELETION: Persist to deletion store
        logger.info(f"Human rejected story {story.id}: {decision.reason}")

        if deletion_store:
            try:
                deletion_store.save_deleted_story(
                    story=story,
                    reason=f"Human rejected: {decision.reason}",
                    deleted_by=decision.decision_author
                )
                logger.info(f"Persisted human-rejected story {story.id} to deletion store")
            except Exception as e:
                logger.error(f"Failed to persist rejected story {story.id}: {e}")
                # Still return None to indicate rejection, but log error

        # Return None to indicate rejection
        return None

    elif decision.decision_type == "edit":
        # Apply edited fields
        if decision.edited_fields:
            logger.info(f"Human edited story {story.id}: {list(decision.edited_fields.keys())}")

            # Apply each edited field
            for field, value in decision.edited_fields.items():
                if hasattr(modified_story, field):
                    setattr(modified_story, field, value)
                else:
                    logger.warning(f"Story has no field '{field}', skipping edit")

        return modified_story

    else:
        raise ValueError(f"Unknown decision type: {decision.decision_type}")


def apply_human_overrides(
    stories: List[SuccessStory],
    store: HumanOverrideStore,
    deletion_store: Optional[DeletionStore] = None
) -> Tuple[List[SuccessStory], List[HumanDecision]]:
    """Apply all human decisions to a list of stories.

    Human decisions ALWAYS override automated logic.
    If a story has a human decision, it is applied regardless of automated evaluation.

    SAFE DELETION: Rejected stories are persisted to deletion store if provided.

    Args:
        stories: List of SuccessStory objects
        store: HumanOverrideStore with loaded decisions
        deletion_store: Optional DeletionStore for persisting rejected stories

    Returns:
        Tuple of (modified_stories, applied_decisions)
        - modified_stories: List of stories with human decisions applied
                          (rejected stories are filtered out)
        - applied_decisions: List of HumanDecision objects that were applied
    """
    if not stories:
        return [], []

    modified_stories = []
    applied_decisions = []

    for story in stories:
        # Check if human decision exists
        if store.has_decision(story.id):
            decision = store.get_decision(story.id)
            if decision:
                result_story = apply_human_override(story, decision, deletion_store)

                # If rejected, result_story will be None
                if result_story is not None:
                    modified_stories.append(result_story)
                    applied_decisions.append(decision)
                else:
                    # Story was rejected, don't include in output
                    logger.info(f"Story {story.id} rejected by human decision")
                    applied_decisions.append(decision)
        else:
            # No human decision, use story as-is
            modified_stories.append(story)

    logger.info(
        f"Applied {len(applied_decisions)} human decisions "
        f"({len(stories)} -> {len(modified_stories)} stories)"
    )

    return modified_stories, applied_decisions


def create_edit_decision(
    story_id: str,
    automated_action: str,
    edited_fields: Dict[str, Any],
    reason: str,
    author: str = "human"
) -> HumanDecision:
    """Create a human decision for editing a story.

    Args:
        story_id: Story ID to edit
        automated_action: What automated logic wanted to do
        edited_fields: Dictionary of field changes
        reason: Explanation for the edit
        author: Who is making the decision

    Returns:
        HumanDecision for edit
    """
    return HumanDecision(
        story_id=story_id,
        decision_type="edit",
        automated_action=automated_action,
        human_action="edit",
        reason=reason,
        decision_timestamp=datetime.utcnow().isoformat() + "Z",
        decision_author=author,
        edited_fields=edited_fields
    )


def create_rejection_decision(
    story_id: str,
    automated_action: str,
    reason: str,
    author: str = "human"
) -> HumanDecision:
    """Create a human decision for rejecting a story.

    Args:
        story_id: Story ID to reject
        automated_action: What automated logic wanted to do
        reason: Explanation for the rejection
        author: Who is making the decision

    Returns:
        HumanDecision for rejection
    """
    return HumanDecision(
        story_id=story_id,
        decision_type="reject",
        automated_action=automated_action,
        human_action="reject",
        reason=reason,
        decision_timestamp=datetime.utcnow().isoformat() + "Z",
        decision_author=author
    )


def create_approval_decision(
    story_id: str,
    automated_action: str,
    reason: str,
    author: str = "human"
) -> HumanDecision:
    """Create a human decision for approving a story.

    Args:
        story_id: Story ID to approve
        automated_action: What automated logic wanted to do
        reason: Explanation for the approval
        author: Who is making the decision

    Returns:
        HumanDecision for approval
    """
    return HumanDecision(
        story_id=story_id,
        decision_type="approve",
        automated_action=automated_action,
        human_action="approve",
        reason=reason,
        decision_timestamp=datetime.utcnow().isoformat() + "Z",
        decision_author=author
    )
