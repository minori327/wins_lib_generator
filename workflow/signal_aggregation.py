"""
Signal aggregation and feedback generation for Phase 8: Feedback / Signal Loop.

Aggregates signals over time windows and generates structured feedback reports.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

from models.signal import (
    Signal,
    AggregatedSignal,
    FeedbackReport,
    FeedbackRecommendation,
    SignalType,
    SignalSource
)

logger = logging.getLogger(__name__)


def generate_aggregation_id() -> str:
    """Generate unique aggregation ID.

    Returns:
        Unique aggregation identifier
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"agg-{timestamp}"


def aggregate_signals_for_artifact(
    artifact_id: str,
    artifact_type: str,
    signals: List[Signal],
    window_start: str,
    window_end: str,
    method_version: str = "1.0"
) -> AggregatedSignal:
    """Aggregate signals for a single artifact over a time window.

    Args:
        artifact_id: Artifact ID to aggregate signals for
        artifact_type: Type of artifact
        signals: List of signals to aggregate (must all be for this artifact)
        window_start: ISO-8601 start timestamp
        window_end: ISO-8601 end timestamp
        method_version: Aggregation method version

    Returns:
        AggregatedSignal instance
    """
    # Filter signals by time window
    window_start_dt = datetime.fromisoformat(window_start.replace('Z', '+00:00'))
    window_end_dt = datetime.fromisoformat(window_end.replace('Z', '+00:00'))

    filtered_signals = []
    for signal in signals:
        signal_time = datetime.fromisoformat(signal.collected_at.replace('Z', '+00:00'))
        if window_start_dt <= signal_time <= window_end_dt:
            filtered_signals.append(signal)

    # Count by signal type and source
    signal_type_counts = defaultdict(int)
    source_counts = defaultdict(int)

    for signal in filtered_signals:
        signal_type_counts[signal.signal_type.value] += 1
        source_counts[signal.source.value] += 1

    # Compute aggregated metrics
    metrics = compute_aggregated_metrics(filtered_signals)

    # Create aggregation
    aggregation_id = generate_aggregation_id()
    signal_ids = [s.signal_id for s in filtered_signals]

    return AggregatedSignal(
        aggregation_id=aggregation_id,
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        window_start=window_start,
        window_end=window_end,
        generated_at=datetime.utcnow().isoformat() + "Z",
        signal_count=len(filtered_signals),
        signal_type_counts=dict(signal_type_counts),
        source_counts=dict(source_counts),
        metrics=metrics,
        method_version=method_version,
        signal_ids=signal_ids
    )


def compute_aggregated_metrics(signals: List[Signal]) -> Dict[str, Any]:
    """Compute aggregated metrics from list of signals.

    Args:
        signals: List of signals

    Returns:
        Dictionary of aggregated metrics
    """
    metrics = {}

    # Engagement metrics
    engagement_signals = [s for s in signals if s.signal_type == SignalType.ENGAGEMENT]
    if engagement_signals:
        total_views = sum(s.raw_payload.get("views", 0) for s in engagement_signals)
        total_clicks = sum(s.raw_payload.get("clicks", 0) for s in engagement_signals)
        total_downloads = sum(s.raw_payload.get("downloads", 0) for s in engagement_signals)
        avg_time = sum(s.raw_payload.get("time_spent_seconds", 0) for s in engagement_signals) / len(engagement_signals)

        metrics["engagement"] = {
            "total_views": total_views,
            "total_clicks": total_clicks,
            "total_downloads": total_downloads,
            "avg_time_spent_seconds": round(avg_time, 2),
            "engagement_rate": round(total_clicks / total_views if total_views > 0 else 0, 4)
        }

    # Feedback metrics
    feedback_signals = [s for s in signals if s.signal_type == SignalType.FEEDBACK]
    if feedback_signals:
        ratings = [s.raw_payload.get("rating") for s in feedback_signals if s.raw_payload.get("rating") is not None]
        if ratings:
            metrics["feedback"] = {
                "avg_rating": round(sum(ratings) / len(ratings), 2),
                "rating_count": len(ratings),
                "rating_distribution": {
                    "5": sum(1 for r in ratings if r == 5),
                    "4": sum(1 for r in ratings if r == 4),
                    "3": sum(1 for r in ratings if r == 3),
                    "2": sum(1 for r in ratings if r == 2),
                    "1": sum(1 for r in ratings if r == 1)
                }
            }

        # Sentiment breakdown
        sentiments = [s.raw_payload.get("sentiment") for s in feedback_signals if s.raw_payload.get("sentiment")]
        if sentiments:
            metrics["feedback"]["sentiment_distribution"] = {
                "positive": sum(1 for s in sentiments if s == "positive"),
                "neutral": sum(1 for s in sentiments if s == "neutral"),
                "negative": sum(1 for s in sentiments if s == "negative"),
                "mixed": sum(1 for s in sentiments if s == "mixed")
            }

    # Usage metrics
    usage_signals = [s for s in signals if s.signal_type == SignalType.USAGE]
    if usage_signals:
        total_accesses = sum(s.raw_payload.get("access_count", 0) for s in usage_signals)
        all_contexts = []
        for s in usage_signals:
            all_contexts.extend(s.raw_payload.get("used_in_contexts", []))

        metrics["usage"] = {
            "total_accesses": total_accesses,
            "unique_contexts": len(set(all_contexts)),
            "contexts_list": list(set(all_contexts))
        }

    # Outcome metrics
    outcome_signals = [s for s in signals if s.signal_type == SignalType.OUTCOME]
    if outcome_signals:
        total_revenue = sum(s.raw_payload.get("attributed_revenue", 0) for s in outcome_signals if s.raw_payload.get("attributed_revenue"))
        total_deals = sum(s.raw_payload.get("attributed_deals", 0) for s in outcome_signals)
        reference_count = sum(1 for s in outcome_signals if s.raw_payload.get("customer_reference", False))

        metrics["outcome"] = {
            "total_attributed_revenue": total_revenue,
            "total_attributed_deals": total_deals,
            "reference_count": reference_count
        }

    return metrics


def generate_recommendations(
    artifact_id: str,
    aggregated_signal: AggregatedSignal
) -> List[FeedbackRecommendation]:
    """Generate recommendations based on aggregated signal analysis.

    Recommendations are ADVISORY ONLY and do not automatically change Phase 5.

    Args:
        artifact_id: Artifact ID
        aggregated_signal: AggregatedSignal to analyze

    Returns:
        List of FeedbackRecommendation instances
    """
    recommendations = []
    metrics = aggregated_signal.metrics
    signal_count = aggregated_signal.signal_count

    # Low engagement signal
    if "engagement" in metrics:
        engagement = metrics["engagement"]
        if engagement["total_views"] < 10 and signal_count >= 3:
            recommendations.append(FeedbackRecommendation(
                recommendation_id=f"rec-{artifact_id}-low-engagement",
                artifact_id=artifact_id,
                recommendation_type="investigate",
                confidence="medium",
                reason=f"Low engagement ({engagement['total_views']} views) across {signal_count} signals",
                evidence=aggregated_signal.signal_ids[:3],
                suggested_action="Review if content is relevant and visible",
                created_at=datetime.utcnow().isoformat() + "Z"
            ))

    # High positive feedback signal
    if "feedback" in metrics:
        feedback = metrics["feedback"]
        if "avg_rating" in feedback and feedback["avg_rating"] >= 4.5:
            recommendations.append(FeedbackRecommendation(
                recommendation_id=f"rec-{artifact_id}-high-rating",
                artifact_id=artifact_id,
                recommendation_type="boost",
                confidence="high",
                reason=f"High average rating ({feedback['avg_rating']}/5) from {feedback['rating_count']} ratings",
                evidence=aggregated_signal.signal_ids[:3],
                suggested_action="Consider featuring this story more prominently",
                created_at=datetime.utcnow().isoformat() + "Z"
            ))

    # Negative feedback signal
    if "feedback" in metrics:
        feedback = metrics["feedback"]
        if "sentiment_distribution" in feedback:
            neg_count = feedback["sentiment_distribution"].get("negative", 0)
            pos_count = feedback["sentiment_distribution"].get("positive", 0)
            if neg_count > pos_count and neg_count >= 2:
                recommendations.append(FeedbackRecommendation(
                    recommendation_id=f"rec-{artifact_id}-negative-feedback",
                    artifact_id=artifact_id,
                    recommendation_type="investigate",
                    confidence="high",
                    reason=f"More negative feedback ({neg_count}) than positive ({pos_count})",
                    evidence=aggregated_signal.signal_ids[:3],
                    suggested_action="Review feedback and consider content updates",
                    created_at=datetime.utcnow().isoformat() + "Z"
                ))

    # High outcome signal
    if "outcome" in metrics:
        outcome = metrics["outcome"]
        if outcome["total_attributed_revenue"] > 10000 or outcome["total_attributed_deals"] >= 3:
            recommendations.append(FeedbackRecommendation(
                recommendation_id=f"rec-{artifact_id}-high-outcome",
                artifact_id=artifact_id,
                recommendation_type="boost",
                confidence="high",
                reason=f"Strong business outcomes (${outcome['total_attributed_revenue']:,}, {outcome['total_attributed_deals']} deals)",
                evidence=aggregated_signal.signal_ids[:3],
                suggested_action="Promote this story as a high-impact reference",
                created_at=datetime.utcnow().isoformat() + "Z"
            ))

    # Low usage signal
    if "usage" in metrics:
        usage = metrics["usage"]
        if usage["total_accesses"] < 5 and signal_count >= 3:
            recommendations.append(FeedbackRecommendation(
                recommendation_id=f"rec-{artifact_id}-low-usage",
                artifact_id=artifact_id,
                recommendation_type="deprecate",
                confidence="low",
                reason=f"Low usage ({usage['total_accesses']} accesses) across {signal_count} signals",
                evidence=aggregated_signal.signal_ids[:3],
                suggested_action="Consider archiving or updating content",
                created_at=datetime.utcnow().isoformat() + "Z"
            ))

    return recommendations


def generate_feedback_report_for_artifact(
    artifact_id: str,
    artifact_type: str,
    signals: List[Signal],
    window_start: str,
    window_end: str,
    method_version: str = "1.0"
) -> FeedbackReport:
    """Generate feedback report for a single artifact.

    Args:
        artifact_id: Artifact ID
        artifact_type: Type of artifact
        signals: List of signals for this artifact
        window_start: ISO-8601 start timestamp
        window_end: ISO-8601 end timestamp
        method_version: Report generation method version

    Returns:
        FeedbackReport instance
    """
    # Aggregate signals
    aggregated = aggregate_signals_for_artifact(
        artifact_id,
        artifact_type,
        signals,
        window_start,
        window_end,
        method_version
    )

    # Generate recommendations
    recommendations = generate_recommendations(artifact_id, aggregated)

    # Extract insights
    insights = extract_insights(aggregated)

    # Analyze trends
    trends = analyze_trends(signals)

    # Create report
    report_id = f"report-{artifact_id}-{window_start[:10].replace('-', '')}-{window_end[:10].replace('-', '')}"

    return FeedbackReport(
        report_id=report_id,
        report_type="artifact",
        generated_at=datetime.utcnow().isoformat() + "Z",
        artifact_ids=[artifact_id],
        window_start=window_start,
        window_end=window_end,
        total_signals=aggregated.signal_count,
        signal_type_breakdown=aggregated.signal_type_counts,
        source_breakdown=aggregated.source_counts,
        insights=insights,
        trends=trends,
        recommendations=recommendations,
        method_version=method_version,
        aggregation_ids=[aggregated.aggregation_id]
    )


def generate_collection_feedback_report(
    artifact_ids: List[str],
    all_signals: List[Signal],
    window_start: str,
    window_end: str,
    method_version: str = "1.0"
) -> FeedbackReport:
    """Generate feedback report for a collection of artifacts.

    Args:
        artifact_ids: List of artifact IDs to include in report
        all_signals: List of all signals (will be filtered by artifact IDs)
        window_start: ISO-8601 start timestamp
        window_end: ISO-8601 end timestamp
        method_version: Report generation method version

    Returns:
        FeedbackReport instance
    """
    # Filter signals by artifacts and time window
    window_start_dt = datetime.fromisoformat(window_start.replace('Z', '+00:00'))
    window_end_dt = datetime.fromisoformat(window_end.replace('Z', '+00:00'))

    filtered_signals = []
    for signal in all_signals:
        if signal.artifact_id not in artifact_ids:
            continue
        signal_time = datetime.fromisoformat(signal.collected_at.replace('Z', '+00:00'))
        if window_start_dt <= signal_time <= window_end_dt:
            filtered_signals.append(signal)

    # Count by signal type and source
    signal_type_counts = defaultdict(int)
    source_counts = defaultdict(int)

    for signal in filtered_signals:
        signal_type_counts[signal.signal_type.value] += 1
        source_counts[signal.source.value] += 1

    # Compute collection-level metrics
    metrics = compute_aggregated_metrics(filtered_signals)

    # Generate collection-level insights
    insights = extract_collection_insights(artifact_ids, metrics, filtered_signals)

    # Analyze trends
    trends = analyze_trends(filtered_signals)

    # Create report
    report_id = f"report-collection-{len(artifact_ids)}-{window_start[:10].replace('-', '')}"

    return FeedbackReport(
        report_id=report_id,
        report_type="collection",
        generated_at=datetime.utcnow().isoformat() + "Z",
        artifact_ids=artifact_ids,
        window_start=window_start,
        window_end=window_end,
        total_signals=len(filtered_signals),
        signal_type_breakdown=dict(signal_type_counts),
        source_breakdown=dict(source_counts),
        insights=insights,
        trends=trends,
        recommendations=[],  # No recommendations for collection reports
        method_version=method_version,
        aggregation_ids=[]
    )


def extract_insights(aggregated_signal: AggregatedSignal) -> List[str]:
    """Extract human-readable insights from aggregated signal.

    Args:
        aggregated_signal: AggregatedSignal to analyze

    Returns:
        List of insight strings
    """
    insights = []
    metrics = aggregated_signal.metrics

    # Engagement insights
    if "engagement" in metrics:
        eng = metrics["engagement"]
        if eng["total_views"] > 100:
            insights.append(f"High engagement with {eng['total_views']} total views")
        if eng["engagement_rate"] > 0.1:
            insights.append(f"Strong interaction rate ({eng['engagement_rate']:.1%})")

    # Feedback insights
    if "feedback" in metrics:
        fb = metrics["feedback"]
        if "avg_rating" in fb:
            if fb["avg_rating"] >= 4.0:
                insights.append(f"Positive feedback with average rating {fb['avg_rating']}/5")
            elif fb["avg_rating"] <= 2.5:
                insights.append(f"Concerning feedback with average rating {fb['avg_rating']}/5")

    # Usage insights
    if "usage" in metrics:
        usage = metrics["usage"]
        if usage["unique_contexts"] > 3:
            insights.append(f"Content used in {usage['unique_contexts']} different contexts")

    # Outcome insights
    if "outcome" in metrics:
        outcome = metrics["outcome"]
        if outcome["total_attributed_revenue"] > 0:
            insights.append(f"Attributed ${outcome['total_attributed_revenue']:,.0f} in revenue")
        if outcome["reference_count"] > 0:
            insights.append(f"Generated {outcome['reference_count']} customer reference(s)")

    return insights


def extract_collection_insights(
    artifact_ids: List[str],
    metrics: Dict[str, Any],
    signals: List[Signal]
) -> List[str]:
    """Extract collection-level insights.

    Args:
        artifact_ids: Artifact IDs in collection
        metrics: Computed metrics
        signals: Signals in collection

    Returns:
        List of insight strings
    """
    insights = []

    insights.append(f"Collection covers {len(artifact_ids)} artifacts with {len(signals)} total signals")

    # Engagement insight
    if "engagement" in metrics:
        eng = metrics["engagement"]
        insights.append(f"Collection generated {eng['total_views']} total views")

    # Outcome insight
    if "outcome" in metrics:
        outcome = metrics["outcome"]
        if outcome["total_attributed_revenue"] > 0:
            insights.append(f"Collection attributed ${outcome['total_attributed_revenue']:,.0f} in revenue")

    return insights


def analyze_trends(signals: List[Signal]) -> Dict[str, Any]:
    """Analyze trends in signals over time.

    Args:
        signals: List of signals

    Returns:
        Dictionary of trend indicators
    """
    if len(signals) < 2:
        return {"engagement_trend": "insufficient_data"}

    # Sort signals by time
    sorted_signals = sorted(signals, key=lambda s: s.collected_at)

    # Split into two halves for comparison
    mid = len(sorted_signals) // 2
    first_half = sorted_signals[:mid]
    second_half = sorted_signals[mid:]

    # Compare engagement
    first_views = sum(s.raw_payload.get("views", 0) for s in first_half if s.signal_type == SignalType.ENGAGEMENT)
    second_views = sum(s.raw_payload.get("views", 0) for s in second_half if s.signal_type == SignalType.ENGAGEMENT)

    if second_views > first_views * 1.2:
        engagement_trend = "up"
    elif second_views < first_views * 0.8:
        engagement_trend = "down"
    else:
        engagement_trend = "stable"

    return {
        "engagement_trend": engagement_trend,
        "first_half_views": first_views,
        "second_half_views": second_views
    }


def save_aggregated_signals(
    aggregated_signals: List[AggregatedSignal],
    output_path: Path
) -> None:
    """Save aggregated signals to JSON file.

    Args:
        aggregated_signals: List of AggregatedSignal objects
        output_path: Path to output file

    Raises:
        OSError: If file write fails
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = []
    for agg in aggregated_signals:
        data.append({
            "aggregation_id": agg.aggregation_id,
            "artifact_id": agg.artifact_id,
            "artifact_type": agg.artifact_type,
            "window_start": agg.window_start,
            "window_end": agg.window_end,
            "generated_at": agg.generated_at,
            "signal_count": agg.signal_count,
            "signal_type_counts": agg.signal_type_counts,
            "source_counts": agg.source_counts,
            "metrics": agg.metrics,
            "method_version": agg.method_version,
            "signal_ids": agg.signal_ids
        })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(aggregated_signals)} aggregated signals to {output_path}")


def load_aggregated_signals(input_path: Path) -> List[AggregatedSignal]:
    """Load aggregated signals from JSON file.

    Args:
        input_path: Path to input file

    Returns:
        List of AggregatedSignal objects
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    aggregated_signals = []
    for item in data:
        aggregated_signals.append(AggregatedSignal(
            aggregation_id=item["aggregation_id"],
            artifact_id=item["artifact_id"],
            artifact_type=item["artifact_type"],
            window_start=item["window_start"],
            window_end=item["window_end"],
            generated_at=item["generated_at"],
            signal_count=item["signal_count"],
            signal_type_counts=item["signal_type_counts"],
            source_counts=item["source_counts"],
            metrics=item["metrics"],
            method_version=item["method_version"],
            signal_ids=item["signal_ids"]
        ))

    return aggregated_signals
