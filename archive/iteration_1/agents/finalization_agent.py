"""
Finalization Agent for converting DraftSuccessStory to SuccessStory.

Performs deterministic ID assignment and final field population.
No ranking, filtering, or business rules - mechanical conversion only.
"""

import logging
import hashlib
from typing import List
from datetime import datetime
from models.draft_story import DraftSuccessStory
from models.library import SuccessStory

logger = logging.getLogger(__name__)


def generate_story_id(
    customer: str,
    context: str,
    action: str,
    outcome: str,
    country: str,
    month: str
) -> str:
    """Generate deterministic SuccessStory ID based on content hash.

    ID Format: win-{month}-{country}-{hash}
    Where hash is first 16 hex characters of SHA-256 hash.

    The hash is derived from: customer + context + action + outcome
    This ensures same content always produces same ID, regardless of processing order.

    Args:
        customer: Customer name
        context: Business problem or situation
        action: What was done
        outcome: Results achieved
        country: ISO 3166-1 alpha-2 country code
        month: YYYY-MM format

    Returns:
        SuccessStory ID string (deterministic)
    """
    # Create content string for hashing
    content = f"{customer}|{context}|{action}|{outcome}"

    # Generate SHA-256 hash
    hash_bytes = hashlib.sha256(content.encode()).digest()

    # Use first 8 bytes (16 hex chars) for ID
    hash_hex = hash_bytes[:8].hex()

    # Format: win-YYYY-MM-CC-AAAAAAAAAAAAAAAA
    return f"win-{month}-{country}-{hash_hex}"


def finalize_draft(
    draft: DraftSuccessStory,
    country: str,
    month: str,
    raw_source_filenames: List[str]
) -> SuccessStory:
    """Convert DraftSuccessStory to SuccessStory with deterministic ID.

    ID is generated from content hash, ensuring:
    - Same content always produces same ID
    - IDs are deterministic across batches
    - No dependency on processing order

    Args:
        draft: DraftSuccessStory to finalize
        country: ISO 3166-1 alpha-2 country code
        month: YYYY-MM format
        raw_source_filenames: List of source filenames (traceability)

    Returns:
        SuccessStory object with deterministic ID and all fields populated
    """
    # Generate deterministic ID from content
    story_id = generate_story_id(
        customer=draft.customer,
        context=draft.context,
        action=draft.action,
        outcome=draft.outcome,
        country=country,
        month=month
    )

    # Generate timestamp (UTC, deterministic format)
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Create SuccessStory
    story = SuccessStory(
        id=story_id,
        country=country,
        month=month,
        customer=draft.customer,
        context=draft.context,
        action=draft.action,
        outcome=draft.outcome,
        metrics=draft.metrics,
        confidence=draft.confidence,
        internal_only=draft.internal_only,
        raw_sources=raw_source_filenames,
        last_updated=timestamp,
        tags=draft.tags,
        industry=draft.industry,
        team_size=draft.team_size
    )

    logger.debug(
        f"Finalized SuccessStory: {story_id} from DraftSuccessStory "
        f"(source_raw_item_id={draft.source_raw_item_id})"
    )

    return story


def finalize_drafts(
    drafts: List[DraftSuccessStory],
    country: str,
    month: str,
    raw_source_filenames: List[List[str]]
) -> List[SuccessStory]:
    """Convert list of DraftSuccessStory objects to SuccessStory objects.

    Each story receives a deterministic ID based on its content hash.
    IDs are not sequential - they are derived from content.

    Args:
        drafts: List of DraftSuccessStory objects
        country: ISO 3166-1 alpha-2 country code
        month: YYYY-MM format
        raw_source_filenames: List of source filename lists (one per draft)

    Returns:
        List of SuccessStory objects with deterministic IDs

    Raises:
        ValueError: If drafts and raw_source_filenames lengths don't match
    """
    if not drafts:
        return []

    if len(drafts) != len(raw_source_filenames):
        raise ValueError(
            f"Length mismatch: {len(drafts)} drafts but "
            f"{len(raw_source_filenames)} source filename lists"
        )

    stories = []
    for draft, sources in zip(drafts, raw_source_filenames):
        story = finalize_draft(draft, country, month, sources)
        stories.append(story)

    logger.info(
        f"Finalized {len(stories)} SuccessStory objects "
        f"with content-based deterministic IDs"
    )

    return stories
