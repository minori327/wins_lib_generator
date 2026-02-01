"""
Generate executive version outputs from SuccessStory objects.

Uses Jinja2 templates for flexible, configurable output formatting.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, Template
from models.library import SuccessStory
from utils.output_config_loader import (
    load_output_config,
    get_template_settings,
    get_output_destinations
)

logger = logging.getLogger(__name__)


def _get_template_env() -> Environment:
    """Get Jinja2 template environment.

    Returns:
        Configured Jinja2 Environment

    Raises:
        FileNotFoundError: If templates directory doesn't exist
    """
    config = get_template_settings()
    template_base_dir = Path(config["base_dir"])

    if not template_base_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_base_dir}")

    # Create Jinja2 environment with template loader
    env = Environment(
        loader=FileSystemLoader(template_base_dir),
        autoescape=False,  # No auto-escaping for Markdown
        trim_blocks=True,
        lstrip_blocks=True
    )

    logger.debug(f"Loaded Jinja2 environment from {template_base_dir}")

    return env


def generate_executive_output(story: SuccessStory) -> str:
    """Generate executive version output from SuccessStory.

    Uses Jinja2 template (config/executive.md.jinja) for rendering.
    Template-driven formatting ensures all output is configurable.

    Args:
        story: SuccessStory to format

    Returns:
        Formatted executive output (Markdown string)

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    env = _get_template_env()
    config = get_template_settings()

    # Load executive template
    template_name = config["executive_markdown"]
    template = env.get_template(template_name)

    # Render template
    try:
        output = template.render(story=story)
        logger.debug(f"Generated executive output for {story.id}")
        return output
    except Exception as e:
        logger.error(f"Failed to render executive template for {story.id}: {e}")
        raise
