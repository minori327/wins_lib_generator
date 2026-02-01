"""
Signal ingestion agent for Phase 8: Feedback / Signal Loop.

Collects post-publish signals from various sources and normalizes them
into structured Signal objects.
"""

import logging
import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from models.signal import (
    Signal,
    EngagementSignal,
    FeedbackSignal,
    UsageSignal,
    OutcomeSignal,
    SignalType,
    SignalSource,
    FeedbackSentiment
)

logger = logging.getLogger(__name__)


def generate_signal_id() -> str:
    """Generate unique signal ID.

    Returns:
        Unique signal identifier
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rand_hash = hashlib.sha256(timestamp.encode()).digest()[:4].hex()
    return f"sig-{timestamp}-{rand_hash}"


def ingest_engagement_signal(
    artifact_id: str,
    artifact_type: str,
    source: SignalSource,
    raw_data: Dict[str, Any]
) -> EngagementSignal:
    """Ingest engagement signal from raw analytics data.

    Args:
        artifact_id: Published artifact ID
        artifact_type: Type of artifact
        source: Signal source
        raw_data: Raw analytics data (e.g., from Google Analytics, CMS)

    Returns:
        EngagementSignal instance
    """
    # Extract engagement metrics from raw data
    # Support multiple common analytics formats
    views = raw_data.get("views", raw_data.get("page_views", raw_data.get("views_count", 0)))
    clicks = raw_data.get("clicks", raw_data.get("link_clicks", 0))
    downloads = raw_data.get("downloads", raw_data.get("file_downloads", 0))
    time_spent = raw_data.get("time_spent_seconds", raw_data.get("avg_time_on_page", 0))
    unique_visitors = raw_data.get("unique_visitors", raw_data.get("unique_users", 0))

    # Create signal
    signal = EngagementSignal.create(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        source=source,
        views=int(views),
        clicks=int(clicks),
        downloads=int(downloads),
        time_spent_seconds=int(time_spent),
        unique_visitors=int(unique_visitors)
    )

    logger.debug(f"Ingested engagement signal for {artifact_id}: {views} views")
    return signal


def ingest_feedback_signal(
    artifact_id: str,
    artifact_type: str,
    source: SignalSource,
    raw_data: Dict[str, Any]
) -> FeedbackSignal:
    """Ingest feedback signal from raw feedback data.

    Args:
        artifact_id: Published artifact ID
        artifact_type: Type of artifact
        source: Signal source
        raw_data: Raw feedback data (e.g., survey, comment, rating)

    Returns:
        FeedbackSignal instance
    """
    # Extract feedback fields
    rating = raw_data.get("rating", raw_data.get("score", raw_data.get("stars")))
    if rating is not None:
        rating = int(rating)

    sentiment_str = raw_data.get("sentiment")
    sentiment = None
    if sentiment_str:
        try:
            sentiment = FeedbackSentiment(sentiment_str.lower())
        except ValueError:
            logger.warning(f"Invalid sentiment value: {sentiment_str}")

    comment = raw_data.get("comment", raw_data.get("short_comment", ""))
    feedback_text = raw_data.get("feedback_text", raw_data.get("message", raw_data.get("text", "")))

    # Create signal
    signal = FeedbackSignal.create(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        source=source,
        rating=rating,
        sentiment=sentiment,
        comment=comment,
        feedback_text=feedback_text
    )

    logger.debug(f"Ingested feedback signal for {artifact_id}: rating={rating}, sentiment={sentiment}")
    return signal


def ingest_usage_signal(
    artifact_id: str,
    artifact_type: str,
    source: SignalSource,
    raw_data: Dict[str, Any]
) -> UsageSignal:
    """Ingest usage signal from raw usage data.

    Args:
        artifact_id: Published artifact ID
        artifact_type: Type of artifact
        source: Signal source
        raw_data: Raw usage data (e.g., access logs, usage tracking)

    Returns:
        UsageSignal instance
    """
    access_count = raw_data.get("access_count", raw_data.get("hits", raw_data.get("visits", 0)))
    last_accessed = raw_data.get("last_accessed_at", raw_data.get("last_access", ""))
    used_in_contexts = raw_data.get("used_in_contexts", raw_data.get("contexts", []))
    referrers = raw_data.get("referrers", raw_data.get("sources", []))

    signal = UsageSignal.create(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        source=source,
        access_count=int(access_count),
        last_accessed_at=last_accessed,
        used_in_contexts=used_in_contexts if isinstance(used_in_contexts, list) else [used_in_contexts],
        referrers=referrers if isinstance(referrers, list) else [referrers]
    )

    logger.debug(f"Ingested usage signal for {artifact_id}: {access_count} accesses")
    return signal


def ingest_outcome_signal(
    artifact_id: str,
    artifact_type: str,
    source: SignalSource,
    raw_data: Dict[str, Any]
) -> OutcomeSignal:
    """Ingest outcome signal from raw outcome data.

    Args:
        artifact_id: Published artifact ID
        artifact_type: Type of artifact
        source: Signal source
        raw_data: Raw outcome data (e.g., CRM deal data, manual report)

    Returns:
        OutcomeSignal instance
    """
    outcome_type = raw_data.get("outcome_type", raw_data.get("type", "unknown"))
    outcome_description = raw_data.get("outcome_description", raw_data.get("description", ""))
    attributed_revenue = raw_data.get("attributed_revenue", raw_data.get("revenue", raw_data.get("deal_value")))
    attributed_deals = raw_data.get("attributed_deals", raw_data.get("deals", raw_data.get("deal_count", 0)))
    customer_reference = raw_data.get("customer_reference", raw_data.get("is_reference", False))

    signal = OutcomeSignal.create(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        source=source,
        outcome_type=str(outcome_type),
        outcome_description=str(outcome_description),
        attributed_revenue=float(attributed_revenue) if attributed_revenue else None,
        attributed_deals=int(attributed_deals),
        customer_reference=bool(customer_reference)
    )

    logger.debug(f"Ingested outcome signal for {artifact_id}: {outcome_type}")
    return signal


def ingest_signal_from_dict(raw_data: Dict[str, Any]) -> Signal:
    """Ingest signal from dictionary (generic entry point).

    Detects signal type from raw_data and routes to appropriate ingest function.

    Args:
        raw_data: Dictionary containing signal data with required fields:
                  - signal_type: Type of signal (string)
                  - artifact_id: Artifact ID
                  - artifact_type: Artifact type
                  - source: Signal source (string)
                  - ... other signal-specific fields

    Returns:
        Signal instance (appropriate subclass)

    Raises:
        ValueError: If signal_type is unknown or required fields are missing
    """
    signal_type_str = raw_data.get("signal_type")
    if not signal_type_str:
        raise ValueError("signal_type is required")

    artifact_id = raw_data.get("artifact_id")
    if not artifact_id:
        raise ValueError("artifact_id is required")

    artifact_type = raw_data.get("artifact_type", "unknown")

    source_str = raw_data.get("source", "manual")
    try:
        source = SignalSource(source_str)
    except ValueError:
        logger.warning(f"Unknown source: {source_str}, defaulting to MANUAL")
        source = SignalSource.MANUAL

    # Route to appropriate ingest function
    try:
        signal_type = SignalType(signal_type_str)

        if signal_type == SignalType.ENGAGEMENT:
            return ingest_engagement_signal(artifact_id, artifact_type, source, raw_data)
        elif signal_type == SignalType.FEEDBACK:
            return ingest_feedback_signal(artifact_id, artifact_type, source, raw_data)
        elif signal_type == SignalType.USAGE:
            return ingest_usage_signal(artifact_id, artifact_type, source, raw_data)
        elif signal_type == SignalType.OUTCOME:
            return ingest_outcome_signal(artifact_id, artifact_type, source, raw_data)
        else:
            raise ValueError(f"Unsupported signal type: {signal_type}")

    except ValueError as e:
        raise ValueError(f"Invalid signal type: {signal_type_str}") from e


def ingest_signals_from_file(file_path: Path) -> List[Signal]:
    """Ingest signals from JSON file.

    File format: JSON array of signal dictionaries, or JSONL (one JSON object per line).

    Args:
        file_path: Path to JSON or JSONL file

    Returns:
        List of Signal instances

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Signal file not found: {file_path}")

    signals = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

            # Try JSONL first (one object per line)
            if content.startswith('{'):
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw_data = json.loads(line)
                        signal = ingest_signal_from_dict(raw_data)
                        signals.append(signal)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON line: {e}")
                        continue

            # Try JSON array
            elif content.startswith('['):
                raw_signals = json.loads(content)
                for raw_data in raw_signals:
                    signal = ingest_signal_from_dict(raw_data)
                    signals.append(signal)

            else:
                raise ValueError("File must be JSON array or JSONL format")

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}") from e

    logger.info(f"Ingested {len(signals)} signals from {file_path}")
    return signals


def ingest_signals_from_api(
    artifact_id: str,
    source: SignalSource,
    api_data: Dict[str, Any]
) -> List[Signal]:
    """Ingest signals from API response (stub implementation).

    Args:
        artifact_id: Artifact ID
        source: Signal source
        api_data: API response data

    Returns:
        List of Signal instances
    """
    # STUB IMPLEMENTATION
    # In production, this would:
    # 1. Parse API response format
    # 2. Extract relevant metrics
    # 3. Create appropriate signal types

    logger.info(f"[STUB] Ingesting signals from API for {artifact_id}")
    logger.warning("API signal ingestion is a stub - implement for production")

    # Return empty list for now
    return []


def create_manual_signal(
    artifact_id: str,
    artifact_type: str,
    signal_type: SignalType,
    data: Dict[str, Any]
) -> Signal:
    """Create a manual signal from human input.

    Convenience function for creating signals via manual input (e.g., CLI, form).

    Args:
        artifact_id: Artifact ID
        artifact_type: Artifact type
        signal_type: Type of signal to create
        data: Signal-specific data

    Returns:
        Signal instance
    """
    raw_data = {
        "signal_type": signal_type.value,
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "source": SignalSource.MANUAL.value,
        **data
    }

    return ingest_signal_from_dict(raw_data)
