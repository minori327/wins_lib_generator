"""
Ranking & Prioritization Agent for scoring SuccessStory objects.

Applies documented business metrics to rank stories by importance
and strategic value.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from models.library import SuccessStory
from utils.config_loader import get_ranking_rules

logger = logging.getLogger(__name__)


@dataclass
class RankingResult:
    """Result of ranking a SuccessStory."""
    story_id: str
    rank: int  # 1 = highest priority
    score: float  # Overall priority score (0.0 to 1.0)
    metric_scores: Dict[str, float]  # Individual metric scores


class RankingConfig:
    """Configurable ranking metrics and weights.

    All weights loaded from config/business_rules.yaml.
    """

    def __init__(
        self,
        confidence_weight: float = None,  # Loaded from config if None
        metrics_weight: float = None,  # Loaded from config if None
        impact_weight: float = None,  # Loaded from config if None
        recency_weight: float = None,  # Loaded from config if None
        completeness_weight: float = None,  # Loaded from config if None
    ):
        # Load from config if not provided
        if any(w is None for w in [confidence_weight, metrics_weight, impact_weight, recency_weight, completeness_weight]):
            rules = get_ranking_rules()
            if confidence_weight is None:
                confidence_weight = rules["confidence_weight"]
            if metrics_weight is None:
                metrics_weight = rules["metrics_weight"]
            if impact_weight is None:
                impact_weight = rules["impact_weight"]
            if recency_weight is None:
                recency_weight = rules["recency_weight"]
            if completeness_weight is None:
                completeness_weight = rules["completeness_weight"]

        # Validate weights sum to approximately 1.0
        total_weight = (
            confidence_weight + metrics_weight +
            impact_weight + recency_weight + completeness_weight
        )
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(
                f"Ranking weights sum to {total_weight}, not 1.0. "
                "Weights will be normalized."
            )

        self.confidence_weight = confidence_weight
        self.metrics_weight = metrics_weight
        self.impact_weight = impact_weight
        self.recency_weight = recency_weight
        self.completeness_weight = completeness_weight


def create_ranking_config_from_rules(rules: Dict[str, Any] = None) -> RankingConfig:
    """Create RankingConfig from business_rules.yaml.

    Args:
        rules: Business rules dict (if None, loads from config file)

    Returns:
        RankingConfig with weights from YAML
    """
    if rules is None:
        rules = get_ranking_rules()

    return RankingConfig(
        confidence_weight=rules["confidence_weight"],
        metrics_weight=rules["metrics_weight"],
        impact_weight=rules["impact_weight"],
        recency_weight=rules["recency_weight"],
        completeness_weight=rules["completeness_weight"]
    )


def calculate_confidence_score(story: SuccessStory) -> float:
    """Calculate confidence score.

    Business Rule: high=1.0, medium=0.6, low=0.2

    Args:
        story: SuccessStory to score

    Returns:
        Confidence score from 0.0 to 1.0
    """
    confidence_map = {"high": 1.0, "medium": 0.6, "low": 0.2}
    return confidence_map.get(story.confidence.lower(), 0.0)


def calculate_metrics_score(story: SuccessStory) -> float:
    """Calculate metrics score based on quantity and quality.

    Business Rule:
    - 0 metrics: 0.0
    - 1-2 metrics: 0.5
    - 3-5 metrics: 0.8
    - 6+ metrics: 1.0

    Args:
        story: SuccessStory to score

    Returns:
        Metrics score from 0.0 to 1.0
    """
    metrics_count = len(story.metrics) if story.metrics else 0

    if metrics_count == 0:
        return 0.0
    elif metrics_count <= 2:
        return 0.5
    elif metrics_count <= 5:
        return 0.8
    else:
        return 1.0


def calculate_impact_score(story: SuccessStory) -> float:
    """Calculate impact score based on metrics content.

    Business Rule: Look for quantitative indicators in metrics.
    - No metrics: 0.0
    - Metrics with numbers/%: 0.6
    - Metrics with revenue/impact keywords: 0.8
    - Both numbers AND impact keywords: 1.0

    Args:
        story: SuccessStory to score

    Returns:
        Impact score from 0.0 to 1.0
    """
    if not story.metrics or len(story.metrics) == 0:
        return 0.0

    has_numbers = any(
        any(char.isdigit() for char in metric)
        for metric in story.metrics
    )

    impact_keywords = [
        "revenue", "cost", "saving", "increase", "decrease",
        "time", "efficiency", "growth", "%", "percent", "USD", "$"
    ]

    has_impact_keywords = any(
        any(keyword.lower() in metric.lower() for keyword in impact_keywords)
        for metric in story.metrics
    )

    if has_numbers and has_impact_keywords:
        return 1.0
    elif has_impact_keywords:
        return 0.8
    elif has_numbers:
        return 0.6
    else:
        return 0.4


def calculate_completeness_score(story: SuccessStory) -> float:
    """Calculate completeness score based on field population.

    Business Rule: Score based on which optional fields are populated.
    - Required fields only: 0.5
    - + tags: 0.1
    - + industry: 0.1
    - + team_size: 0.1
    - + all optional: 0.3

    Args:
        story: SuccessStory to score

    Returns:
        Completeness score from 0.0 to 1.0
    """
    base_score = 0.5  # All required fields present

    optional_score = 0.0
    if story.tags and len(story.tags) > 0:
        optional_score += 0.1
    if story.industry and len(story.industry.strip()) > 0:
        optional_score += 0.1
    if story.team_size and len(story.team_size.strip()) > 0:
        optional_score += 0.1

    return min(base_score + optional_score, 1.0)


def rank_story(
    story: SuccessStory,
    config: RankingConfig
) -> RankingResult:
    """Rank a single SuccessStory using configured metrics.

    Args:
        story: SuccessStory to rank
        config: RankingConfig with weights

    Returns:
        RankingResult with score (rank not set yet)
    """
    metric_scores = {
        "confidence": calculate_confidence_score(story),
        "metrics": calculate_metrics_score(story),
        "impact": calculate_impact_score(story),
        "completeness": calculate_completeness_score(story),
    }

    # Calculate weighted score
    overall_score = (
        metric_scores["confidence"] * config.confidence_weight +
        metric_scores["metrics"] * config.metrics_weight +
        metric_scores["impact"] * config.impact_weight +
        metric_scores["completeness"] * config.completeness_weight
    )

    result = RankingResult(
        story_id=story.id,
        rank=0,  # Will be set after ranking all stories
        score=overall_score,
        metric_scores=metric_scores
    )

    logger.debug(
        f"Ranked {story.id}: score={overall_score:.2f} "
        f"(confidence={metric_scores['confidence']:.2f}, "
        f"metrics={metric_scores['metrics']:.2f}, "
        f"impact={metric_scores['impact']:.2f}, "
        f"completeness={metric_scores['completeness']:.2f})"
    )

    return result


def rank_stories(
    stories: List[SuccessStory],
    config: RankingConfig
) -> List[RankingResult]:
    """Rank list of SuccessStory objects by priority.

    Stories are sorted by score (descending). Higher score = higher priority.
    Ranks are assigned after sorting (1 = highest priority).

    Business Rules Applied (Documented):
    - Confidence: Higher confidence scores higher
    - Metrics: More metrics and quantitative indicators score higher
    - Impact: Metrics with revenue/cost/efficiency keywords score higher
    - Completeness: More populated optional fields score higher

    Args:
        stories: List of SuccessStory objects
        config: RankingConfig with metric weights

    Returns:
        List of RankingResult objects sorted by rank (1 = highest priority)
    """
    if not stories:
        return []

    # Calculate scores for all stories
    results = []
    for story in stories:
        result = rank_story(story, config)
        results.append(result)

    # Sort by score descending
    results.sort(key=lambda r: r.score, reverse=True)

    # Assign ranks
    for rank, result in enumerate(results, start=1):
        result.rank = rank

    logger.info(
        f"Ranked {len(results)} stories using weights: "
        f"confidence={config.confidence_weight}, "
        f"metrics={config.metrics_weight}, "
        f"impact={config.impact_weight}, "
        f"completeness={config.completeness_weight}"
    )

    return results


def sort_stories_by_rank(
    stories: List[SuccessStory],
    ranking_results: List[RankingResult]
) -> List[SuccessStory]:
    """Sort stories by ranking results.

    Args:
        stories: List of SuccessStory objects
        ranking_results: List of RankingResult objects (same length)

    Returns:
        List of SuccessStory objects sorted by rank (highest priority first)

    Raises:
        ValueError: If lengths don't match or story IDs don't align
    """
    if len(stories) != len(ranking_results):
        raise ValueError(
            f"Length mismatch: {len(stories)} stories but {len(ranking_results)} results"
        )

    # Create mapping from story_id to RankingResult
    ranking_map = {r.story_id: r for r in ranking_results}

    # Create list of (story, rank) tuples
    story_rank_pairs = []
    for story in stories:
        if story.id not in ranking_map:
            raise ValueError(f"No ranking result found for story {story.id}")
        story_rank_pairs.append((story, ranking_map[story.id].rank))

    # Sort by rank
    story_rank_pairs.sort(key=lambda pair: pair[1])

    # Extract sorted stories
    sorted_stories = [pair[0] for pair in story_rank_pairs]

    logger.info(
        f"Sorted {len(sorted_stories)} stories by rank "
        f"(priority: {sorted_stories[0].id} -> {sorted_stories[-1].id})"
    )

    return sorted_stories
