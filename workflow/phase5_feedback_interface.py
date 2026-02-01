"""
Phase 5 Feedback Interface for Phase 8: Feedback / Signal Loop.

Provides READ-ONLY access to signal data for Phase 5 decision-making.

Phase 5 may use signal evidence as INPUT to future evaluations, but:
- Phase 8 does NOT automatically change Phase 5 scores
- Phase 8 does NOT retroactively alter past approvals
- Feedback is ADVISORY, not authoritative
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from models.signal import Signal, AggregatedSignal, FeedbackRecommendation
from workflow.signal_storage import SignalStore, AggregatedSignalStore, FeedbackReportStore
from workflow.signal_aggregation import (
    aggregate_signals_for_artifact,
    compute_aggregated_metrics,
    generate_recommendations
)

logger = logging.getLogger(__name__)


class FeedbackInterface:
    """Read-only interface for Phase 5 to access signal data.

    This interface allows Phase 5 agents to query signal evidence
    for use in future decision-making, but does not allow modifying
    the underlying signal data.
    """

    def __init__(
        self,
        signal_store: SignalStore = None,
        aggregation_store: AggregatedSignalStore = None,
        report_store: FeedbackReportStore = None
    ):
        """Initialize feedback interface.

        Args:
            signal_store: Signal storage instance
            aggregation_store: Aggregated signal storage instance
            report_store: Feedback report storage instance
        """
        self.signal_store = signal_store or SignalStore()
        self.aggregation_store = aggregation_store or AggregatedSignalStore()
        self.report_store = report_store or FeedbackReportStore()

    def get_signals_for_story(
        self,
        story_id: str,
        signal_types: List[str] = None
    ) -> List[Signal]:
        """Get all signals for a story (by any artifact ID).

        Args:
            story_id: SuccessStory ID
            signal_types: Optional filter by signal type (e.g., ["engagement", "feedback"])

        Returns:
            List of Signal objects (READ-ONLY)
        """
        # Get all artifacts with signals
        artifact_ids = self.signal_store.list_artifacts_with_signals()

        # Filter artifacts that belong to this story
        # (artifact IDs may be publish record IDs or story IDs)
        story_artifacts = [aid for aid in artifact_ids if story_id in aid]

        all_signals = []
        for artifact_id in story_artifacts:
            signals = self.signal_store.load_signals_for_artifact(artifact_id)

            # Filter by signal type if requested
            if signal_types:
                signals = [s for s in signals if s.signal_type.value in signal_types]

            all_signals.extend(signals)

        logger.debug(f"Retrieved {len(all_signals)} signals for story {story_id}")
        return all_signals

    def get_aggregated_signals_for_story(
        self,
        story_id: str
    ) -> List[AggregatedSignal]:
        """Get aggregated signals for a story.

        Args:
            story_id: SuccessStory ID

        Returns:
            List of AggregatedSignal objects (READ-ONLY)
        """
        # Get all artifacts with signals
        artifact_ids = self.signal_store.list_artifacts_with_signals()

        # Filter artifacts that belong to this story
        story_artifacts = [aid for aid in artifact_ids if story_id in aid]

        all_aggregations = []
        for artifact_id in story_artifacts:
            aggregations = self.aggregation_store.load_aggregations_for_artifact(artifact_id)
            all_aggregations.extend(aggregations)

        logger.debug(f"Retrieved {len(all_aggregations)} aggregations for story {story_id}")
        return all_aggregations

    def get_latest_aggregation_for_story(
        self,
        story_id: str
    ) -> Optional[AggregatedSignal]:
        """Get the latest aggregation for a story.

        Args:
            story_id: SuccessStory ID

        Returns:
            Latest AggregatedSignal, or None if no aggregations exist
        """
        aggregations = self.get_aggregated_signals_for_story(story_id)

        if not aggregations:
            return None

        # Sort by generated_at and return latest
        latest = max(aggregations, key=lambda a: a.generated_at)
        return latest

    def get_feedback_report_for_story(
        self,
        story_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the latest feedback report for a story.

        Args:
            story_id: SuccessStory ID

        Returns:
            Feedback report dictionary, or None if no report exists
        """
        # List all reports
        report_ids = self.report_store.list_reports()

        # Find reports for this story
        story_reports = [rid for rid in report_ids if story_id in rid]

        if not story_reports:
            return None

        # Load the latest report (by report ID which contains timestamp)
        # Report ID format: report-{story_id}-{start_date}-{end_date}
        latest_report_id = sorted(story_reports)[-1]
        report = self.report_store.load_report(latest_report_id)

        return report

    def get_recommendations_for_story(
        self,
        story_id: str
    ) -> List[FeedbackRecommendation]:
        """Get feedback recommendations for a story.

        Args:
            story_id: SuccessStory ID

        Returns:
            List of FeedbackRecommendation objects
        """
        report = self.get_feedback_report_for_story(story_id)

        if not report:
            return []

        # Extract recommendations from report
        recommendations_data = report.get("recommendations", [])

        recommendations = []
        for rec_data in recommendations_data:
            rec = FeedbackRecommendation(
                recommendation_id=rec_data["recommendation_id"],
                artifact_id=rec_data["artifact_id"],
                recommendation_type=rec_data["recommendation_type"],
                confidence=rec_data["confidence"],
                reason=rec_data["reason"],
                evidence=rec_data["evidence"],
                suggested_action=rec_data["suggested_action"],
                created_at=rec_data["created_at"]
            )
            recommendations.append(rec)

        return recommendations

    def get_signal_summary_for_story(self, story_id: str) -> Dict[str, Any]:
        """Get a summary of signals for a story.

        Provides high-level metrics that Phase 5 can use as evidence.

        Args:
            story_id: SuccessStory ID

        Returns:
            Dictionary with signal summary metrics
        """
        signals = self.get_signals_for_story(story_id)
        aggregations = self.get_aggregated_signals_for_story(story_id)

        # Count by signal type
        signal_type_counts = {}
        for signal in signals:
            st = signal.signal_type.value
            signal_type_counts[st] = signal_type_counts.get(st, 0) + 1

        # Get latest aggregation metrics
        latest_aggregation = self.get_latest_aggregation_for_story(story_id)
        aggregation_metrics = {}
        if latest_aggregation:
            aggregation_metrics = latest_aggregation.metrics

        # Get recommendations
        recommendations = self.get_recommendations_for_story(story_id)
        recommendation_types = [r.recommendation_type for r in recommendations]

        return {
            "story_id": story_id,
            "total_signals": len(signals),
            "signal_type_breakdown": signal_type_counts,
            "total_aggregations": len(aggregations),
            "latest_metrics": aggregation_metrics,
            "recommendation_count": len(recommendations),
            "recommendation_types": recommendation_types,
            "has_data": len(signals) > 0
        }

    def get_high_performing_stories(
        self,
        min_rating: float = 4.0,
        min_revenue: float = 0
    ) -> List[str]:
        """Get list of high-performing stories based on signals.

        Args:
            min_rating: Minimum average rating threshold
            min_revenue: Minimum attributed revenue threshold

        Returns:
            List of story IDs that meet criteria
        """
        all_artifacts = self.signal_store.list_artifacts_with_signals()
        high_performers = []

        for artifact_id in all_artifacts:
            aggregations = self.aggregation_store.load_aggregations_for_artifact(artifact_id)

            if not aggregations:
                continue

            # Get latest aggregation
            latest = max(aggregations, key=lambda a: a.generated_at)
            metrics = latest.metrics

            # Check criteria
            meets_rating = False
            if "feedback" in metrics and "avg_rating" in metrics["feedback"]:
                if metrics["feedback"]["avg_rating"] >= min_rating:
                    meets_rating = True

            meets_revenue = False
            if "outcome" in metrics and "total_attributed_revenue" in metrics["outcome"]:
                if metrics["outcome"]["total_attributed_revenue"] >= min_revenue:
                    meets_revenue = True

            if meets_rating or meets_revenue:
                high_performers.append(artifact_id)

        return high_performers

    def get_underperforming_stories(
        self,
        max_views: int = 10,
        max_rating: float = 2.5
    ) -> List[str]:
        """Get list of underperforming stories based on signals.

        Args:
            max_views: Maximum views threshold
            max_rating: Maximum average rating threshold

        Returns:
            List of story IDs that meet underperformance criteria
        """
        all_artifacts = self.signal_store.list_artifacts_with_signals()
        underperformers = []

        for artifact_id in all_artifacts:
            aggregations = self.aggregation_store.load_aggregations_for_artifact(artifact_id)

            if not aggregations:
                continue

            # Get latest aggregation
            latest = max(aggregations, key=lambda a: a.generated_at)
            metrics = latest.metrics

            # Check low engagement
            low_engagement = False
            if "engagement" in metrics:
                if metrics["engagement"]["total_views"] <= max_views:
                    low_engagement = True

            # Check low rating
            low_rating = False
            if "feedback" in metrics and "avg_rating" in metrics["feedback"]:
                if metrics["feedback"]["avg_rating"] <= max_rating:
                    low_rating = True

            if low_engagement or low_rating:
                underperformers.append(artifact_id)

        return underperformers


def get_feedback_interface(
    signal_storage_dir: Path = None,
    aggregation_storage_dir: Path = None,
    report_storage_dir: Path = None
) -> FeedbackInterface:
    """Get a FeedbackInterface instance.

    Convenience function for Phase 5 agents to access feedback data.

    Args:
        signal_storage_dir: Custom signal storage directory
        aggregation_storage_dir: Custom aggregation storage directory
        report_storage_dir: Custom report storage directory

    Returns:
        FeedbackInterface instance
    """
    signal_store = SignalStore(signal_storage_dir) if signal_storage_dir else None
    aggregation_store = AggregatedSignalStore(aggregation_storage_dir) if aggregation_storage_dir else None
    report_store = FeedbackReportStore(report_storage_dir) if report_storage_dir else None

    return FeedbackInterface(signal_store, aggregation_store, report_store)
