"""
Write Markdown files to Obsidian vault and other output locations.

Handles file writing with configurable output paths and templates.
"""

import logging
from typing import List
from pathlib import Path
from jinja2 import Environment
from models.library import SuccessStory
from workflow.outputs.executive import _get_template_env
from utils.output_config_loader import (
    get_output_destinations,
    get_generation_settings,
    get_template_settings,
    get_obsidian_settings
)

logger = logging.getLogger(__name__)


def write_success_story_note(
    story: SuccessStory,
    output_path: Path,
    template_path: Path = None
) -> None:
    """Write SuccessStory as Markdown note to explicit output path.

    Uses Jinja2 template for rendering. Output path is created if it doesn't exist
(based on generation.create_missing_dirs config).

    Args:
        story: SuccessStory to write
        output_path: Explicit output file path
        template_path: Optional path to template (if None, uses default)

    Raises:
        OSError: If file write fails
        FileNotFoundError: If template doesn't exist
    """
    config = get_generation_settings()

    # Ensure output directory exists
    if config["create_missing_dirs"]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if not output_path.parent.exists():
            raise OSError(f"Output directory does not exist: {output_path.parent}")

    # Get template environment
    env = _get_template_env()

    # Load template (default to obsidian_note template)
    template_settings = get_template_settings()
    template_name = template_path.name if template_path else template_settings["obsidian_note"]
    template = env.get_template(template_name)

    # Render template
    try:
        content = template.render(story=story)
    except Exception as e:
        logger.error(f"Failed to render template for {story.id}: {e}")
        raise

    # Write to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Wrote SuccessStory note to {output_path}")

    except Exception as e:
        logger.error(f"Failed to write file {output_path}: {e}")
        raise


def write_weekly_summary(
    stories: List[SuccessStory],
    output_path: Path,
    week_str: str,
    timestamp: str,
    template_path: Path = None
) -> None:
    """Write weekly summary Markdown file to explicit output path.

    Uses Jinja2 template for rendering. Generates summary statistics from
    the provided stories.

    Args:
        stories: List of SuccessStory objects to summarize
        output_path: Explicit output file path
        week_str: Week identifier (e.g., "2026-W05")
        timestamp: Generation timestamp (ISO-8601 format) - MUST be provided by caller
        template_path: Optional path to template (if None, uses default)

    Raises:
        OSError: If file write fails
        FileNotFoundError: If template doesn't exist
    """
    config = get_generation_settings()

    # Ensure output directory exists
    if config["create_missing_dirs"]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if not output_path.parent.exists():
            raise OSError(f"Output directory does not exist: {output_path.parent}")

    # Get template environment
    env = _get_template_env()

    # Load template (default to weekly_summary template)
    template_settings = get_template_settings()
    template_name = template_path.name if template_path else template_settings["weekly_summary"]
    template = env.get_template(template_name)

    # Calculate summary statistics
    by_country = {}
    by_confidence = {}
    for story in stories:
        by_country[story.country] = by_country.get(story.country, 0) + 1
        by_confidence[story.confidence] = by_confidence.get(story.confidence, 0) + 1

    # Render template
    try:
        content = template.render(
            stories=stories,
            week_str=week_str,
            total_stories=len(stories),
            by_country=by_country,
            by_confidence=by_confidence,
            timestamp=timestamp  # Provided by caller, not generated
        )
    except Exception as e:
        logger.error(f"Failed to render weekly summary template: {e}")
        raise

    # Write to file
    try:
        # Check overwrite behavior
        if not config["overwrite_existing"] and output_path.exists():
            logger.error(f"File already exists and overwrite_existing=False: {output_path}")
            raise OSError(f"File already exists: {output_path}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Wrote weekly summary to {output_path}")

    except Exception as e:
        logger.error(f"Failed to write file {output_path}: {e}")
        raise


def write_executive_outputs(
    stories: List[SuccessStory],
    output_dir: Path = None
) -> List[Path]:
    """Write executive version outputs for all stories.

    Uses generate_executive_output() and writes to output_dir/executive/.

    Args:
        stories: List of SuccessStory objects
        output_dir: Base output directory (if None, uses config default)

    Returns:
        List of written file paths

    Raises:
        OSError: If file write fails
    """
    from workflow.outputs.executive import generate_executive_output

    # Get output destination from config
    config = get_output_destinations()
    base_dir = Path(output_dir) if output_dir else Path(config["base_dir"])
    exec_dir = base_dir / config["executive"]

    # Create directory
    exec_dir.mkdir(parents=True, exist_ok=True)

    written_paths = []

    config = get_generation_settings()

    for story in stories:
        # Generate output
        content = generate_executive_output(story)

        # Determine filename using config format
        filename_format = config["story_filename_format"]
        filename = filename_format.format(id=story.id, customer=story.customer, country=story.country, month=story.month)
        file_path = exec_dir / filename

        # Write file
        try:
            # Check overwrite behavior
            if not config["overwrite_existing"] and file_path.exists():
                logger.error(f"File already exists and overwrite_existing=False: {file_path}")
                raise OSError(f"File already exists: {file_path}")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            written_paths.append(file_path)
            logger.info(f"Wrote executive output for {story.id} to {file_path}")

        except Exception as e:
            logger.error(f"Failed to write executive output for {story.id}: {e}")
            raise

    logger.info(f"Wrote {len(written_paths)} executive outputs to {exec_dir}")

    return written_paths


def write_marketing_outputs(
    stories: List[SuccessStory],
    output_dir: Path = None
) -> List[Path]:
    """Write marketing version outputs for all stories.

    Uses generate_marketing_output() and writes to output_dir/marketing/.
    Skips internal-only stories.

    Args:
        stories: List of SuccessStory objects
        output_dir: Base output directory (if None, uses config default)

    Returns:
        List of written file paths

    Raises:
        OSError: If file write fails
    """
    from workflow.outputs.marketing import generate_marketing_output

    # Get output destination from config
    config = get_output_destinations()
    base_dir = Path(output_dir) if output_dir else Path(config["base_dir"])
    marketing_dir = base_dir / config["marketing"]

    # Create directory
    marketing_dir.mkdir(parents=True, exist_ok=True)

    written_paths = []

    for story in stories:
        # Generate output
        content = generate_marketing_output(story)

        # Determine filename using config format
        config = get_generation_settings()
        filename_format = config["story_filename_format"]
        filename = filename_format.format(id=story.id, customer=story.customer, country=story.country, month=story.month)
        file_path = marketing_dir / filename

        # Write file
        try:
            # Check overwrite behavior
            if not config["overwrite_existing"] and file_path.exists():
                logger.error(f"File already exists and overwrite_existing=False: {file_path}")
                raise OSError(f"File already exists: {file_path}")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            written_paths.append(file_path)
            logger.info(f"Wrote marketing output for {story.id} to {file_path}")

        except Exception as e:
            logger.error(f"Failed to write marketing output for {story.id}: {e}")
            raise

    logger.info(f"Wrote {len(written_paths)} marketing outputs to {marketing_dir}")

    return written_paths
