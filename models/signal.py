"""
Signal models for Phase 8: Feedback / Signal Loop.

Defines data structures for post-publish signals, signal aggregation,
and feedback reports.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime
from pathlib import Path


class SignalType(str, Enum):
    """Types of signals that can be collected."""

    ENGAGEMENT = "engagement"  # Views, clicks, downloads, time spent
    FEEDBACK = "feedback"  # Ratings, comments, surveys, reactions
    USAGE = "usage"  # How often/where content is used
    OUTCOME = "outcome"  # Business impact attributed to the story
    ERROR = "error"  # Errors, broken links, complaints


class SignalSource(str, Enum):
    """Sources where signals originate."""

    WEBSITE = "website"  # Web analytics
    CMS = "cms"  # CMS analytics
    SLACK = "slack"  # Slack reactions/replies
    EMAIL = "email"  # Email responses, click tracking
    MANUAL = "manual"  # Direct human input
    API = "api"  # External system feedback via API
    SURVEY = "survey"  # Survey responses


class FeedbackSentiment(str, Enum):
    """Sentiment of feedback signals."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


@dataclass
class Signal:
    """Raw signal collected from post-publish activity.

    Signals are immutable once created and preserved in their raw form.
    """

    # Signal identification
    signal_id: str  # Unique identifier for this signal
    signal_type: SignalType  # Type of signal
    source: SignalSource  # Where the signal came from

    # Artifact reference
    artifact_id: str  # ID of the published artifact (e.g., publish record ID or story ID)
    artifact_type: str  # Type of artifact (e.g., "executive_output", "marketing_output")

    # Signal data
    collected_at: str  # ISO-8601 timestamp when signal was collected
    raw_payload: Dict[str, Any]  # Raw signal data from source (preserved as-is)

    # Normalized data (optional, extracted from raw_payload)
    normalized_data: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context
    version: str = "1.0"  # Signal schema version


@dataclass
class EngagementSignal(Signal):
    """Engagement signal (views, clicks, downloads, etc.)."""

    @staticmethod
    def create(
        artifact_id: str,
        artifact_type: str,
        source: SignalSource,
        views: int = 0,
        clicks: int = 0,
        downloads: int = 0,
        time_spent_seconds: int = 0,
        unique_visitors: int = 0,
        **kwargs
    ) -> 'EngagementSignal':
        """Create an engagement signal.

        Args:
            artifact_id: Published artifact ID
            artifact_type: Type of artifact
            source: Signal source
            views: Number of views
            clicks: Number of clicks
            downloads: Number of downloads
            time_spent_seconds: Average time spent on artifact
            unique_visitors: Number of unique visitors
            **kwargs: Additional metrics

        Returns:
            EngagementSignal instance
        """
        import hashlib

        timestamp = datetime.utcnow().isoformat() + "Z"
        payload_hash = hashlib.sha256(str(kwargs).encode()).digest()[:8].hex()
        signal_id = f"eng-{timestamp[:10].replace('-', '')}-{payload_hash}"

        raw_payload = {
            "views": views,
            "clicks": clicks,
            "downloads": downloads,
            "time_spent_seconds": time_spent_seconds,
            "unique_visitors": unique_visitors,
            **kwargs
        }

        normalized_data = {
            "total_interactions": views + clicks + downloads,
            "engagement_rate": round(clicks / views if views > 0 else 0, 4)
        }

        return EngagementSignal(
            signal_id=signal_id,
            signal_type=SignalType.ENGAGEMENT,
            source=source,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            collected_at=timestamp,
            raw_payload=raw_payload,
            normalized_data=normalized_data
        )


@dataclass
class FeedbackSignal(Signal):
    """Feedback signal (ratings, comments, reactions)."""

    @staticmethod
    def create(
        artifact_id: str,
        artifact_type: str,
        source: SignalSource,
        rating: Optional[int] = None,  # 1-5 scale
        sentiment: Optional[FeedbackSentiment] = None,
        comment: str = "",
        feedback_text: str = "",
        **kwargs
    ) -> 'FeedbackSignal':
        """Create a feedback signal.

        Args:
            artifact_id: Published artifact ID
            artifact_type: Type of artifact
            source: Signal source
            rating: Numeric rating (1-5)
            sentiment: Sentiment classification
            comment: Short comment
            feedback_text: Longer feedback text
            **kwargs: Additional feedback data

        Returns:
            FeedbackSignal instance
        """
        import hashlib

        timestamp = datetime.utcnow().isoformat() + "Z"
        payload_hash = hashlib.sha256((feedback_text + str(kwargs)).encode()).digest()[:8].hex()
        signal_id = f"fdb-{timestamp[:10].replace('-', '')}-{payload_hash}"

        raw_payload = {
            "rating": rating,
            "sentiment": sentiment.value if sentiment else None,
            "comment": comment,
            "feedback_text": feedback_text,
            **kwargs
        }

        normalized_data = {
            "has_rating": rating is not None,
            "rating_value": rating or 0,
            "sentiment_category": sentiment.value if sentiment else "neutral"
        }

        return FeedbackSignal(
            signal_id=signal_id,
            signal_type=SignalType.FEEDBACK,
            source=source,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            collected_at=timestamp,
            raw_payload=raw_payload,
            normalized_data=normalized_data
        )


@dataclass
class UsageSignal(Signal):
    """Usage signal (how often/where content is used)."""

    @staticmethod
    def create(
        artifact_id: str,
        artifact_type: str,
        source: SignalSource,
        access_count: int = 0,
        last_accessed_at: str = "",
        used_in_contexts: List[str] = None,
        referrers: List[str] = None,
        **kwargs
    ) -> 'UsageSignal':
        """Create a usage signal.

        Args:
            artifact_id: Published artifact ID
            artifact_type: Type of artifact
            source: Signal source
            access_count: Number of times artifact was accessed
            last_accessed_at: Last access timestamp
            used_in_contexts: Contexts where artifact was used (e.g., ["sales_call", "presentation"])
            referrers: Referrer sources
            **kwargs: Additional usage data

        Returns:
            UsageSignal instance
        """
        import hashlib

        timestamp = datetime.utcnow().isoformat() + "Z"
        payload_hash = hashlib.sha256(str(kwargs).encode()).digest()[:8].hex()
        signal_id = f"use-{timestamp[:10].replace('-', '')}-{payload_hash}"

        raw_payload = {
            "access_count": access_count,
            "last_accessed_at": last_accessed_at,
            "used_in_contexts": used_in_contexts or [],
            "referrers": referrers or [],
            **kwargs
        }

        normalized_data = {
            "total_usage_contexts": len(used_in_contexts or []),
            "has_recent_usage": bool(last_accessed_at)
        }

        return UsageSignal(
            signal_id=signal_id,
            signal_type=SignalType.USAGE,
            source=source,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            collected_at=timestamp,
            raw_payload=raw_payload,
            normalized_data=normalized_data
        )


@dataclass
class OutcomeSignal(Signal):
    """Outcome signal (business impact attributed to story)."""

    @staticmethod
    def create(
        artifact_id: str,
        artifact_type: str,
        source: SignalSource,
        outcome_type: str,
        outcome_description: str,
        attributed_revenue: Optional[float] = None,
        attributed_deals: int = 0,
        customer_reference: bool = False,
        **kwargs
    ) -> 'OutcomeSignal':
        """Create an outcome signal.

        Args:
            artifact_id: Published artifact ID
            artifact_type: Type of artifact
            source: Signal source
            outcome_type: Type of outcome (e.g., "deal_closed", "renewal", "expansion")
            outcome_description: Description of the outcome
            attributed_revenue: Revenue attributed to this story
            attributed_deals: Number of deals attributed
            customer_reference: Whether customer became a reference
            **kwargs: Additional outcome data

        Returns:
            OutcomeSignal instance
        """
        import hashlib

        timestamp = datetime.utcnow().isoformat() + "Z"
        payload_hash = hashlib.sha256((outcome_description + str(kwargs)).encode()).digest()[:8].hex()
        signal_id = f"out-{timestamp[:10].replace('-', '')}-{payload_hash}"

        raw_payload = {
            "outcome_type": outcome_type,
            "outcome_description": outcome_description,
            "attributed_revenue": attributed_revenue,
            "attributed_deals": attributed_deals,
            "customer_reference": customer_reference,
            **kwargs
        }

        normalized_data = {
            "has_revenue_impact": attributed_revenue is not None and attributed_revenue > 0,
            "revenue_value": attributed_revenue or 0,
            "deals_count": attributed_deals,
            "outcome_category": outcome_type
        }

        return OutcomeSignal(
            signal_id=signal_id,
            signal_type=SignalType.OUTCOME,
            source=source,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            collected_at=timestamp,
            raw_payload=raw_payload,
            normalized_data=normalized_data
        )


@dataclass
class AggregatedSignal:
    """Aggregated signals for an artifact over a time window.

    Aggregations are reproducible and include metadata about
    the aggregation process.
    """

    # Aggregation identification
    aggregation_id: str  # Unique identifier for this aggregation
    artifact_id: str  # Artifact ID that signals are aggregated for
    artifact_type: str  # Type of artifact

    # Aggregation window
    window_start: str  # ISO-8601 start timestamp
    window_end: str  # ISO-8601 end timestamp
    generated_at: str  # ISO-8601 timestamp when aggregation was created

    # Signal counts
    signal_count: int  # Total number of signals aggregated
    signal_type_counts: Dict[str, int]  # Count by signal type
    source_counts: Dict[str, int]  # Count by source

    # Aggregated metrics (computed from normalized_data)
    metrics: Dict[str, Any]  # Computed metrics (e.g., avg_rating, total_views)

    # Method metadata
    method_version: str  # Aggregation method version
    signal_ids: List[str]  # IDs of signals included in aggregation

    # Raw signal references
    raw_signals_file: str = ""  # Path to file containing raw signals

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackRecommendation:
    """Recommendation based on signal analysis.

    Recommendations are advisory only and do not automatically
    change Phase 5 decisions.
    """

    recommendation_id: str  # Unique identifier
    artifact_id: str  # Artifact this recommendation is for
    recommendation_type: str  # Type: "boost", "deprecate", "update", "investigate"
    confidence: str  # Confidence level: "high", "medium", "low"
    reason: str  # Human-readable explanation
    evidence: List[str]  # List of signal IDs providing evidence
    suggested_action: str  # Suggested action for Phase 5
    created_at: str  # ISO-8601 timestamp


@dataclass
class FeedbackReport:
    """Feedback report summarizing signals for an artifact or collection.

    Reports are the primary output of Phase 8 and provide structured
    feedback that may be used as evidence in Phase 5.
    """

    # Report identification
    report_id: str  # Unique identifier for this report
    report_type: Literal["artifact", "collection", "trend"]  # Type of report
    generated_at: str  # ISO-8601 timestamp

    # Report scope
    artifact_ids: List[str]  # Artifacts covered by this report
    window_start: str  # ISO-8601 start timestamp
    window_end: str  # ISO-8601 end timestamp

    # Signal summary
    total_signals: int  # Total number of signals
    signal_type_breakdown: Dict[str, int]  # Count by signal type
    source_breakdown: Dict[str, int]  # Count by source

    # Key insights
    insights: List[str]  # Human-readable insights extracted from signals
    trends: Dict[str, Any]  # Trend data (e.g., "engagement_up": true)

    # Recommendations (advisory only)
    recommendations: List[FeedbackRecommendation]

    # Method metadata
    method_version: str  # Report generation method version
    aggregation_ids: List[str]  # IDs of aggregations used

    # Additional data
    aggregated_signals_file: str = ""  # Path to aggregated signals file
    metadata: Dict[str, Any] = field(default_factory=dict)
