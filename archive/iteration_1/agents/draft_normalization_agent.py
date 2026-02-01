"""
Draft Normalization Agent for field normalization and metadata attachment.
"""

import logging
from typing import List
from models.draft_story import DraftSuccessStory
from models.raw_item import RawItem

logger = logging.getLogger(__name__)


def normalize_draft(draft: DraftSuccessStory, raw_item: RawItem) -> DraftSuccessStory:
    """Normalize DraftSuccessStory fields and attach metadata.

    Performs:
    - Field trimming and whitespace cleanup
    - Confidence value normalization
    - Empty list initialization for optional fields
    - Source traceability verification

    Args:
        draft: DraftSuccessStory to normalize
        raw_item: Source RawItem for metadata

    Returns:
        Normalized DraftSuccessStory (new object, original unchanged)
    """
    # Normalize string fields (trim whitespace)
    normalized_customer = draft.customer.strip()
    normalized_context = draft.context.strip()
    normalized_action = draft.action.strip()
    normalized_outcome = draft.outcome.strip()

    # Normalize confidence (ensure lowercase)
    normalized_confidence = draft.confidence.lower()
    if normalized_confidence not in ["high", "medium", "low"]:
        logger.warning(
            f"Invalid confidence value '{draft.confidence}', defaulting to 'low'"
        )
        normalized_confidence = "low"

    # Normalize metrics (ensure list, trim each metric)
    normalized_metrics = [
        str(metric).strip() for metric in draft.metrics
        if metric and str(metric).strip()
    ]

    # Normalize optional fields (ensure empty list instead of None)
    normalized_tags = [tag.strip() for tag in (draft.tags or []) if tag and tag.strip()]
    normalized_industry = draft.industry.strip() if draft.industry else ""
    normalized_team_size = draft.team_size.strip() if draft.team_size else ""

    # Verify traceability
    if draft.source_raw_item_id != raw_item.id:
        logger.warning(
            f"Draft source_raw_item_id '{draft.source_raw_item_id}' does not match "
            f"RawItem.id '{raw_item.id}', updating to match"
        )
        source_raw_item_id = raw_item.id
    else:
        source_raw_item_id = draft.source_raw_item_id

    # Create normalized DraftSuccessStory
    normalized = DraftSuccessStory(
        customer=normalized_customer,
        context=normalized_context,
        action=normalized_action,
        outcome=normalized_outcome,
        metrics=normalized_metrics,
        confidence=normalized_confidence,
        internal_only=draft.internal_only,
        tags=normalized_tags,
        industry=normalized_industry,
        team_size=normalized_team_size,
        source_raw_item_id=source_raw_item_id,
        extraction_model=draft.extraction_model,
        extraction_timestamp=draft.extraction_timestamp
    )

    logger.debug(f"Normalized draft for RawItem {raw_item.id}")

    return normalized


def normalize_drafts(
    drafts: List[DraftSuccessStory],
    raw_items: List[RawItem]
) -> List[DraftSuccessStory]:
    """Normalize list of DraftSuccessStory objects.

    Args:
        drafts: List of DraftSuccessStory objects
        raw_items: List of corresponding RawItem objects (by index)

    Returns:
        List of normalized DraftSuccessStory objects
    """
    if not drafts:
        return []

    if len(drafts) != len(raw_items):
        logger.error(
            f"Mismatch: {len(drafts)} drafts but {len(raw_items)} raw_items. "
            "Cannot normalize with 1:1 mapping."
        )
        raise ValueError(
            f"Drafts and RawItems must have same length for normalization: "
            f"{len(drafts)} != {len(raw_items)}"
        )

    normalized = []
    for draft, raw_item in zip(drafts, raw_items):
        normalized_draft = normalize_draft(draft, raw_item)
        normalized.append(normalized_draft)

    logger.info(f"Normalized {len(normalized)} DraftSuccessStory objects")

    return normalized
