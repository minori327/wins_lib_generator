"""
Output Preparation Agent for filtering, formatting, and preparing final outputs.

Transforms SuccessStory objects into user-facing output formats with
appropriate filtering and business logic.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.library import SuccessStory
from utils.config_loader import get_output_filter_rules

logger = logging.getLogger(__name__)


class OutputFilterConfig:
    """Configurable output filtering rules.

    All values loaded from config/business_rules.yaml.
    """

    def __init__(
        self,
        exclude_internal: bool = None,  # Loaded from config if None
        min_confidence: Optional[str] = None,  # Loaded from config if None
        require_metrics: bool = None,  # Loaded from config if None
        allowed_countries: Optional[List[str]] = None,  # Loaded from config if None
        allowed_months: Optional[List[str]] = None,  # Loaded from config if None
    ):
        # Load from config if not provided
        if exclude_internal is None or min_confidence is None or require_metrics is None:
            rules = get_output_filter_rules()
            if exclude_internal is None:
                exclude_internal = rules["exclude_internal"]
            if min_confidence is None:
                min_confidence = rules["min_confidence"]
            if require_metrics is None:
                require_metrics = rules["require_metrics"]
            if allowed_countries is None:
                allowed_countries = rules.get("allowed_countries")
            if allowed_months is None:
                allowed_months = rules.get("allowed_months")

        self.exclude_internal = exclude_internal
        self.min_confidence = min_confidence
        self.require_metrics = require_metrics
        self.allowed_countries = allowed_countries
        self.allowed_months = allowed_months


def create_output_filter_config_from_rules(rules: Dict[str, Any] = None) -> OutputFilterConfig:
    """Create OutputFilterConfig from business_rules.yaml.

    Args:
        rules: Business rules dict (if None, loads from config file)

    Returns:
        OutputFilterConfig with values from YAML
    """
    if rules is None:
        rules = get_output_filter_rules()

    return OutputFilterConfig(
        exclude_internal=rules["exclude_internal"],
        min_confidence=rules.get("min_confidence"),
        require_metrics=rules["require_metrics"],
        allowed_countries=rules.get("allowed_countries"),
        allowed_months=rules.get("allowed_months")
    )


def filter_stories(
    stories: List[SuccessStory],
    config: OutputFilterConfig
) -> List[SuccessStory]:
    """Filter SuccessStory objects based on business rules.

    Args:
        stories: List of SuccessStory objects
        config: OutputFilterConfig with filtering rules

    Returns:
        Filtered list of SuccessStory objects
    """
    if not stories:
        return []

    filtered = []
    rejection_reasons = []

    for story in stories:
        # Rule 1: Exclude internal-only stories
        if config.exclude_internal and story.internal_only:
            rejection_reasons.append(f"{story.id}: internal-only")
            continue

        # Rule 2: Minimum confidence threshold
        if config.min_confidence:
            confidence_order = {"low": 1, "medium": 2, "high": 3}
            story_level = confidence_order.get(story.confidence.lower(), 0)
            required_level = confidence_order.get(config.min_confidence, 0)

            if story_level < required_level:
                rejection_reasons.append(
                    f"{story.id}: confidence {story.confidence} < {config.min_confidence}"
                )
                continue

        # Rule 3: Require metrics
        if config.require_metrics and (not story.metrics or len(story.metrics) == 0):
            rejection_reasons.append(f"{story.id}: no metrics")
            continue

        # Rule 4: Allowed countries
        if config.allowed_countries and story.country not in config.allowed_countries:
            rejection_reasons.append(f"{story.id}: country {story.country} not allowed")
            continue

        # Rule 5: Allowed months
        if config.allowed_months and story.month not in config.allowed_months:
            rejection_reasons.append(f"{story.id}: month {story.month} not allowed")
            continue

        # Story passed all filters
        filtered.append(story)

    logger.info(
        f"Filtered {len(stories)} stories -> {len(filtered)} stories "
        f"using {len(rejection_reasons)} rejections"
    )

    if rejection_reasons:
        logger.debug(f"Rejections: {rejection_reasons[:5]}...")  # Log first 5

    return filtered


def generate_executive_format(story: SuccessStory) -> str:
    """Generate executive version output from SuccessStory.

    Business Rule: Executive format focuses on business impact and metrics.
    - Concise, professional tone
    - Highlights quantifiable results
    - Suitable for leadership review

    Args:
        story: SuccessStory to format

    Returns:
        Formatted executive output string
    """
    lines = []
    lines.append(f"# Success Story: {story.customer}")
    lines.append(f"**Country:** {story.country}  |  **Month:** {story.month}")
    lines.append(f"**Confidence:** {story.confidence.upper()}")
    lines.append("")

    # Business Problem
    lines.append("## Business Challenge")
    lines.append(story.context)
    lines.append("")

    # Solution
    lines.append("## What We Did")
    lines.append(story.action)
    lines.append("")

    # Results (highlighted)
    lines.append("## Impact & Results")
    if story.metrics:
        for metric in story.metrics:
            lines.append(f"- {metric}")
    else:
        lines.append(story.outcome)
    lines.append("")

    # Metadata
    lines.append("---")
    lines.append(f"*Story ID: {story.id}*")
    lines.append(f"*Last Updated: {story.last_updated}*")
    if story.internal_only:
        lines.append("*INTERNAL USE ONLY*")

    return "\n".join(lines)


def generate_marketing_format(story: SuccessStory) -> str:
    """Generate marketing version output from SuccessStory.

    Business Rule: Marketing format focuses on customer success and testimonials.
    - Customer-centric language
    - Emphasizes positive outcomes
    - Suitable for external communication (if not internal-only)

    Args:
        story: SuccessStory to format

    Returns:
        Formatted marketing output string
    """
    lines = []
    lines.append(f"### {story.customer}")
    lines.append("")

    # Customer success story narrative
    lines.append("#### The Challenge")
    lines.append(story.context)
    lines.append("")

    lines.append("#### The Solution")
    lines.append(story.action)
    lines.append("")

    lines.append("#### The Results")
    if story.metrics:
        lines.append("**Key Results:**")
        for metric in story.metrics:
            lines.append(f"- {metric}")
    lines.append("")
    lines.append(story.outcome)
    lines.append("")

    # Call-to-action or industry tag
    if story.industry:
        lines.append(f"*Industry: {story.industry}*")

    return "\n".join(lines)


def prepare_outputs(
    stories: List[SuccessStory],
    output_format: str = "executive",
    filter_config: Optional[OutputFilterConfig] = None
) -> List[str]:
    """Prepare formatted outputs from SuccessStory objects.

    Args:
        stories: List of SuccessStory objects
        output_format: "executive" or "marketing"
        filter_config: Optional OutputFilterConfig for filtering

    Returns:
        List of formatted output strings
    """
    # Apply filters if config provided
    if filter_config:
        stories = filter_stories(stories, filter_config)

    if not stories:
        return []

    # Generate formatted outputs
    outputs = []
    for story in stories:
        if output_format == "executive":
            output = generate_executive_format(story)
        elif output_format == "marketing":
            # Skip internal-only stories for marketing
            if story.internal_only:
                logger.debug(f"Skipped internal-only story {story.id} for marketing output")
                continue
            output = generate_marketing_format(story)
        else:
            logger.warning(f"Unknown output format: {output_format}, using executive")
            output = generate_executive_format(story)

        outputs.append(output)

    logger.info(
        f"Prepared {len(outputs)} {output_format} outputs "
        f"from {len(stories)} stories"
    )

    return outputs


def generate_summary_statistics(stories: List[SuccessStory]) -> Dict[str, Any]:
    """Generate summary statistics for a set of stories.

    Business Rule: Aggregate metrics for reporting and dashboarding.

    Args:
        stories: List of SuccessStory objects

    Returns:
        Dictionary with summary statistics
    """
    if not stories:
        return {
            "total_stories": 0,
            "by_country": {},
            "by_month": {},
            "by_confidence": {},
            "internal_only_count": 0,
            "avg_metrics_per_story": 0.0,
        }

    # Count by country
    by_country: Dict[str, int] = {}
    for story in stories:
        by_country[story.country] = by_country.get(story.country, 0) + 1

    # Count by month
    by_month: Dict[str, int] = {}
    for story in stories:
        by_month[story.month] = by_month.get(story.month, 0) + 1

    # Count by confidence
    by_confidence: Dict[str, int] = {}
    for story in stories:
        by_confidence[story.confidence] = by_confidence.get(story.confidence, 0) + 1

    # Internal-only count
    internal_count = sum(1 for s in stories if s.internal_only)

    # Average metrics per story
    total_metrics = sum(len(s.metrics) if s.metrics else 0 for s in stories)
    avg_metrics = total_metrics / len(stories) if stories else 0.0

    stats = {
        "total_stories": len(stories),
        "by_country": by_country,
        "by_month": by_month,
        "by_confidence": by_confidence,
        "internal_only_count": internal_count,
        "avg_metrics_per_story": round(avg_metrics, 2),
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    logger.info(f"Generated summary statistics for {len(stories)} stories")

    return stats
