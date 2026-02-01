"""
Success Evaluation Agent for applying explicit acceptance criteria.

Determines whether a SuccessStory meets the threshold for inclusion
in the final Wins Library based on documented business rules.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from models.library import SuccessStory
from utils.config_loader import get_success_evaluation_rules
from utils.deletion_store import DeletionStore

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of evaluating a SuccessStory against acceptance criteria."""
    story_id: str
    is_accepted: bool
    rejection_reason: str  # Empty if accepted
    score: float  # 0.0 to 1.0
    criteria_scores: Dict[str, float]  # Individual criterion scores


@dataclass
class SuccessCriteriaConfig:
    """Configurable success criteria for evaluating stories.

    All values loaded from config/business_rules.yaml.
    """
    min_confidence: str  # "low", "medium", or "high"
    min_metrics_count: int  # Minimum number of metrics
    require_outcome: bool  # Must have outcome text
    require_action: bool  # Must have action text
    min_text_length: int  # Minimum characters in key fields


def create_config_from_rules(rules: Dict[str, Any] = None) -> SuccessCriteriaConfig:
    """Create SuccessCriteriaConfig from business_rules.yaml.

    Args:
        rules: Business rules dict (if None, loads from config file)

    Returns:
        SuccessCriteriaConfig with values from YAML
    """
    if rules is None:
        rules = get_success_evaluation_rules()

    return SuccessCriteriaConfig(
        min_confidence=rules["min_confidence"],
        min_metrics_count=rules["min_metrics_count"],
        require_outcome=rules["require_outcome"],
        require_action=rules["require_action"],
        min_text_length=rules["min_text_length"]
    )


def evaluate_story(
    story: SuccessStory,
    config: SuccessCriteriaConfig
) -> EvaluationResult:
    """Evaluate a SuccessStory against explicit acceptance criteria.

    Business Rules (Loaded from config/business_rules.yaml):
    1. Confidence threshold: Story must meet minimum confidence level
    2. Metrics requirement: Story must have minimum number of quantifiable metrics
    3. Content completeness: Story must have action and outcome text
    4. Text substance: Key fields must meet minimum length requirements

    Args:
        story: SuccessStory to evaluate
        config: SuccessCriteriaConfig with business rules

    Returns:
        EvaluationResult with acceptance decision and detailed scoring
    """
    criteria_scores = {}
    rejection_reasons = []

    # Rule 1: Confidence threshold
    confidence_order = {"low": 1, "medium": 2, "high": 3}
    story_confidence_level = confidence_order.get(story.confidence, 0)
    required_confidence_level = confidence_order.get(config.min_confidence, 0)

    if story_confidence_level < required_confidence_level:
        rejection_reasons.append(
            f"Confidence too low: {story.confidence} < {config.min_confidence}"
        )
        confidence_score = 0.0
    else:
        confidence_score = 1.0

    criteria_scores["confidence"] = confidence_score

    # Rule 2: Metrics requirement
    metrics_count = len(story.metrics) if story.metrics else 0
    if metrics_count < config.min_metrics_count:
        rejection_reasons.append(
            f"Insufficient metrics: {metrics_count} < {config.min_metrics_count}"
        )
        metrics_score = 0.0
    else:
        # Score based on metrics count (cap at 3 for full score)
        metrics_score = min(metrics_count / 3.0, 1.0)

    criteria_scores["metrics"] = metrics_score

    # Rule 3: Content completeness
    if config.require_action and not story.action or len(story.action.strip()) == 0:
        rejection_reasons.append("Missing action field")
        action_score = 0.0
    else:
        action_score = 1.0 if len(story.action) >= config.min_text_length else 0.5

    if config.require_outcome and not story.outcome or len(story.outcome.strip()) == 0:
        rejection_reasons.append("Missing outcome field")
        outcome_score = 0.0
    else:
        outcome_score = 1.0 if len(story.outcome) >= config.min_text_length else 0.5

    criteria_scores["content_completeness"] = (action_score + outcome_score) / 2.0

    # Calculate overall score
    overall_score = sum(criteria_scores.values()) / len(criteria_scores)

    # Determine acceptance: ALL hard requirements must pass
    is_accepted = len(rejection_reasons) == 0

    rejection_reason = "; ".join(rejection_reasons) if rejection_reasons else ""

    result = EvaluationResult(
        story_id=story.id,
        is_accepted=is_accepted,
        rejection_reason=rejection_reason,
        score=overall_score,
        criteria_scores=criteria_scores
    )

    logger.info(
        f"Evaluated {story.id}: "
        f"{'ACCEPTED' if is_accepted else 'REJECTED'} "
        f"(score={overall_score:.2f})"
    )

    if not is_accepted:
        logger.debug(f"Rejection reasons: {rejection_reason}")

    return result


def evaluate_stories(
    stories: List[SuccessStory],
    config: SuccessCriteriaConfig
) -> List[EvaluationResult]:
    """Evaluate list of SuccessStory objects against acceptance criteria.

    Args:
        stories: List of SuccessStory objects
        config: SuccessCriteriaConfig with business rules

    Returns:
        List of EvaluationResult objects (same order as input)
    """
    if not stories:
        return []

    results = []
    for story in stories:
        result = evaluate_story(story, config)
        results.append(result)

    accepted_count = sum(1 for r in results if r.is_accepted)
    logger.info(
        f"Evaluation complete: {accepted_count}/{len(stories)} stories accepted "
        f"using criteria: min_confidence={config.min_confidence}, "
        f"min_metrics={config.min_metrics_count}"
    )

    return results


def filter_and_persist_rejected(
    stories: List[SuccessStory],
    evaluation_results: List[EvaluationResult],
    deletion_store: Optional[DeletionStore] = None
) -> List[SuccessStory]:
    """Filter stories to only include accepted ones, persist rejected stories.

    SAFE DELETION: Rejected stories are persisted to deletion store for
    audit trail and potential recovery. They are NOT silently discarded.

    Args:
        stories: List of SuccessStory objects
        evaluation_results: List of EvaluationResult objects (same length)
        deletion_store: DeletionStore for persisting rejected stories (if None, rejected stories are logged but not persisted)

    Returns:
        List of accepted SuccessStory objects

    Raises:
        ValueError: If lengths don't match
    """
    if len(stories) != len(evaluation_results):
        raise ValueError(
            f"Length mismatch: {len(stories)} stories but {len(evaluation_results)} results"
        )

    accepted_stories = []
    rejected_stories = []

    for story, result in zip(stories, evaluation_results):
        if result.is_accepted:
            accepted_stories.append(story)
        else:
            rejected_stories.append((story, result))
            logger.debug(f"Rejected {story.id}: {result.rejection_reason}")

    # Persist rejected stories if deletion store provided
    if deletion_store and rejected_stories:
        for story, result in rejected_stories:
            try:
                deletion_store.save_deleted_story(
                    story=story,
                    reason=f"Failed evaluation: {result.rejection_reason}",
                    deleted_by="success_evaluation_agent"
                )
                logger.info(f"Persisted rejected story {story.id} to deletion store")
            except Exception as e:
                logger.error(f"Failed to persist rejected story {story.id}: {e}")

    logger.info(
        f"Filtered to {len(accepted_stories)} accepted stories, "
        f"{len(rejected_stories)} rejected and persisted"
    )

    return accepted_stories


# Legacy function (deprecated: use filter_and_persist_rejected)
def filter_accepted_stories(
    stories: List[SuccessStory],
    evaluation_results: List[EvaluationResult]
) -> List[SuccessStory]:
    """Filter stories to only include accepted ones.

    WARNING: This function does NOT persist rejected stories.
    Use filter_and_persist_rejected() for safe deletion with persistence.

    Args:
        stories: List of SuccessStory objects
        evaluation_results: List of EvaluationResult objects (same length)

    Returns:
        List of accepted SuccessStory objects
    """
    logger.warning(
        "filter_accepted_stories() does not persist rejected stories. "
        "Use filter_and_persist_rejected() for safe deletion."
    )

    if len(stories) != len(evaluation_results):
        raise ValueError(
            f"Length mismatch: {len(stories)} stories but {len(evaluation_results)} results"
        )

    accepted_stories = []
    for story, result in zip(stories, evaluation_results):
        if result.is_accepted:
            accepted_stories.append(story)
        else:
            logger.debug(f"Filtered out {story.id}: {result.rejection_reason}")

    logger.info(
        f"Filtered to {len(accepted_stories)} accepted stories "
        f"from {len(stories)} total"
    )

    return accepted_stories
