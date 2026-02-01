"""
Semantic Merge Agent for merging duplicate or related SuccessStory objects.

Combines multiple SuccessStory objects that describe the same or related events,
preserving provenance of all merged inputs.
"""

import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, replace
from datetime import datetime
from models.library import SuccessStory
from utils.config_loader import get_merge_policy

logger = logging.getLogger(__name__)


@dataclass
class MergeRecord:
    """Audit record of a merge operation."""
    merged_story_id: str  # ID of the merged story
    source_story_ids: List[str]  # IDs of stories that were merged
    merge_strategy: str  # Description of merge strategy used
    merge_timestamp: str  # When merge occurred (ISO-8601)
    field_sources: Dict[str, str]  # Which source contributed each field


@dataclass
class MergeResult:
    """Result of merging SuccessStory objects."""
    merged_story: SuccessStory
    merge_record: MergeRecord
    rejected_story_ids: List[str]  # Stories that could not be merged


def merge_text_fields(texts: List[str]) -> str:
    """Merge multiple text fields by concatenation with separators.

    Business Rule: Concatenate with " | " separator.
    Deduplicate identical text segments.

    Args:
        texts: List of text strings to merge

    Returns:
        Merged text string
    """
    if not texts:
        return ""

    # Filter out empty strings
    non_empty = [t for t in texts if t and t.strip()]

    if not non_empty:
        return ""

    # Deduplicate while preserving order
    seen = set()
    unique_texts = []
    for text in non_empty:
        text_lower = text.lower().strip()
        if text_lower not in seen:
            seen.add(text_lower)
            unique_texts.append(text.strip())

    # Join with separator
    return " | ".join(unique_texts)


def merge_metrics_lists(metrics_lists: List[List[str]]) -> List[str]:
    """Merge multiple metrics lists.

    Business Rule: Union of all metrics, deduplicated case-insensitively.

    Args:
        metrics_lists: List of metrics lists to merge

    Returns:
        Merged, deduplicated list of metrics
    """
    if not metrics_lists:
        return []

    # Collect all metrics
    all_metrics = []
    for metrics in metrics_lists:
        if metrics:
            all_metrics.extend(metrics)

    # Deduplicate case-insensitively while preserving first occurrence
    seen = set()
    unique_metrics = []
    for metric in all_metrics:
        metric_lower = metric.lower().strip()
        if metric_lower and metric_lower not in seen:
            seen.add(metric_lower)
            unique_metrics.append(metric.strip())

    return unique_metrics


def merge_stories(
    stories: List[SuccessStory],
    primary_index: int = 0,
    auto_merge: bool = None,
    human_approval: bool = None
) -> MergeResult:
    """Merge multiple SuccessStory objects into one.

    MERGE GATE: Requires either human approval OR auto_merge flag in config.
    When both are False/None, raises PermissionError.

    Merge Strategy (Documented):
    1. ID: Use primary story's ID
    2. Country/Month: Use primary story's values
    3. Customer: Use most frequent customer (or primary's)
    4. Context/Action/Outcome: Concatenate with " | " separator
    5. Metrics: Union of all metrics, deduplicated
    6. Confidence: Use highest confidence level
    7. Internal-only: True if ANY story is internal-only
    8. Raw sources: Concatenate all source lists
    9. Tags/Industry/Team size: Use primary story's values
    10. Last updated: Current timestamp

    Args:
        stories: List of SuccessStory objects to merge
        primary_index: Index of primary story (default: 0)
        auto_merge: If True, skip approval check. If None, loads from config.
        human_approval: If True, skip auto_merge check. If None, requires explicit approval.

    Returns:
        MergeResult with merged story and audit record

    Raises:
        ValueError: If story list is empty
        PermissionError: If merge gate check fails (no approval and no auto_merge)
    """
    if not stories:
        raise ValueError("Cannot merge empty story list")

    # MERGE GATE: Check auto_merge policy
    if auto_merge is None:
        policy = get_merge_policy()
        auto_merge = policy.get("auto_merge", False)

    # If no human approval and no auto_merge flag, deny merge
    if not human_approval and not auto_merge:
        raise PermissionError(
            f"Merge operation requires human approval or auto_merge=true in config. "
            f"Attempting to merge {len(stories)} stories: {[s.id for s in stories]}"
        )

    # Log merge authorization
    if human_approval:
        logger.info(f"Merge authorized by human approval: {len(stories)} stories")
    elif auto_merge:
        logger.warning(f"Merge authorized by auto_merge flag: {len(stories)} stories")

    if len(stories) == 1:
        # Single story: no merge needed, return as-is
        record = MergeRecord(
            merged_story_id=stories[0].id,
            source_story_ids=[stories[0].id],
            merge_strategy="single_story_no_merge",
            merge_timestamp=datetime.utcnow().isoformat() + "Z",
            field_sources={}
        )
        return MergeResult(
            merged_story=stories[0],
            merge_record=record,
            rejected_story_ids=[]
        )

    primary = stories[primary_index]
    field_sources = {}

    # Rule 1-2: ID, Country, Month from primary
    merged_id = primary.id
    merged_country = primary.country
    merged_month = primary.month
    field_sources["id"] = primary.id
    field_sources["country"] = primary.id
    field_sources["month"] = primary.id

    # Rule 3: Customer (most frequent or primary's)
    customer_counts: Dict[str, int] = {}
    for story in stories:
        customer = story.customer.lower().strip()
        customer_counts[customer] = customer_counts.get(customer, 0) + 1

    most_frequent_customer = max(customer_counts, key=customer_counts.get)
    merged_customer = most_frequent_customer
    field_sources["customer"] = "most_frequent"

    # Rule 4: Context, Action, Outcome (concatenate)
    merged_context = merge_text_fields([s.context for s in stories])
    merged_action = merge_text_fields([s.action for s in stories])
    merged_outcome = merge_text_fields([s.outcome for s in stories])
    field_sources["context"] = "concatenated"
    field_sources["action"] = "concatenated"
    field_sources["outcome"] = "concatenated"

    # Rule 5: Metrics (union, deduplicated)
    merged_metrics = merge_metrics_lists([s.metrics for s in stories])
    field_sources["metrics"] = "union_deduplicated"

    # Rule 6: Confidence (highest)
    confidence_order = {"low": 1, "medium": 2, "high": 3}
    max_confidence_level = 0
    merged_confidence = primary.confidence

    for story in stories:
        level = confidence_order.get(story.confidence.lower(), 0)
        if level > max_confidence_level:
            max_confidence_level = level
            merged_confidence = story.confidence

    field_sources["confidence"] = "highest"

    # Rule 7: Internal-only (True if any is True)
    merged_internal_only = any(s.internal_only for s in stories)
    field_sources["internal_only"] = "any_true"

    # Rule 8: Raw sources (concatenate all)
    all_sources = []
    for story in stories:
        if story.raw_sources:
            all_sources.extend(story.raw_sources)

    # Deduplicate sources
    seen = set()
    unique_sources = []
    for source in all_sources:
        if source not in seen:
            seen.add(source)
            unique_sources.append(source)

    merged_raw_sources = unique_sources
    field_sources["raw_sources"] = "concatenated_deduplicated"

    # Rule 9: Tags, Industry, Team size from primary
    merged_tags = primary.tags if primary.tags else []
    merged_industry = primary.industry
    merged_team_size = primary.team_size
    field_sources["tags"] = primary.id
    field_sources["industry"] = primary.id
    field_sources["team_size"] = primary.id

    # Rule 10: Last updated = current timestamp
    merged_last_updated = datetime.utcnow().isoformat() + "Z"
    field_sources["last_updated"] = "current_timestamp"

    # Create merged story
    merged_story = SuccessStory(
        id=merged_id,
        country=merged_country,
        month=merged_month,
        customer=merged_customer,
        context=merged_context,
        action=merged_action,
        outcome=merged_outcome,
        metrics=merged_metrics,
        confidence=merged_confidence,
        internal_only=merged_internal_only,
        raw_sources=merged_raw_sources,
        last_updated=merged_last_updated,
        tags=merged_tags,
        industry=merged_industry,
        team_size=merged_team_size
    )

    # Create audit record
    source_ids = [s.id for s in stories]
    merge_record = MergeRecord(
        merged_story_id=merged_id,
        source_story_ids=source_ids,
        merge_strategy=f"merged_{len(stories)}_stories",
        merge_timestamp=merged_last_updated,
        field_sources=field_sources
    )

    logger.info(
        f"Merged {len(stories)} stories into {merged_id} "
        f"(sources: {source_ids})"
    )

    return MergeResult(
        merged_story=merged_story,
        merge_record=merge_record,
        rejected_story_ids=[]
    )


def merge_duplicate_groups(
    stories: List[SuccessStory],
    duplicate_groups: List[List[int]],  # Each group is list of indices
    auto_merge: bool = None,
    human_approval: bool = None
) -> Tuple[List[SuccessStory], List[MergeRecord]]:
    """Merge multiple groups of duplicate stories.

    MERGE GATE: Requires either human approval OR auto_merge flag in config.
    When both are False/None, raises PermissionError for ALL merge operations.

    Args:
        stories: List of all SuccessStory objects
        duplicate_groups: List of groups, where each group is a list of indices
                          pointing to stories in the stories list
        auto_merge: If True, skip approval check. If None, loads from config.
        human_approval: If True, skip auto_merge check. If None, requires explicit approval.

    Returns:
        Tuple of (merged_stories, merge_records)
        - merged_stories: List with duplicates merged (non-merged stories preserved)
        - merge_records: Audit records for all merge operations

    Raises:
        PermissionError: If merge gate check fails
    """
    if not stories:
        return [], []

    if not duplicate_groups:
        return stories, []

    # Load auto_merge policy if not specified
    if auto_merge is None:
        policy = get_merge_policy()
        auto_merge = policy.get("auto_merge", False)

    # Check merge gate once for all groups
    if not human_approval and not auto_merge:
        raise PermissionError(
            f"Batch merge operation requires human approval or auto_merge=true in config. "
            f"Attempting to merge {len(duplicate_groups)} groups."
        )

    # Track which indices have been merged
    merged_indices: Set[int] = set()
    merge_records = []
    result_stories = []

    # Process each duplicate group
    for group in duplicate_groups:
        if not group:
            continue

        # Extract stories for this group
        group_stories = [stories[i] for i in group]

        # Merge them (auto_merge and human_approval already checked above)
        merge_result = merge_stories(
            group_stories,
            auto_merge=True,  # Already checked gate above
            human_approval=human_approval or auto_merge
        )
        result_stories.append(merge_result.merged_story)
        merge_records.append(merge_result.merge_record)

        # Mark indices as merged
        merged_indices.update(group)

        logger.info(
            f"Merged group of {len(group)} stories: {group} -> {merge_result.merged_story.id}"
        )

    # Add non-merged stories
    for i, story in enumerate(stories):
        if i not in merged_indices:
            result_stories.append(story)

    logger.info(
        f"Merged {len(duplicate_groups)} groups "
        f"({len(merged_indices)} stories -> {len(merge_records)} merged stories), "
        f"{len(stories) - len(merged_indices)} stories unchanged"
    )

    return result_stories, merge_records
