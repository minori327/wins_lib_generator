"""
Generate marketing version outputs from SuccessStory objects.

Uses Jinja2 templates for flexible, configurable output formatting.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment
from models.library import SuccessStory
from workflow.outputs.executive import _get_template_env
from utils.output_config_loader import get_template_settings

logger = logging.getLogger(__name__)


def generate_marketing_output(story: SuccessStory) -> str:
    """Generate marketing version output from SuccessStory.

    Uses Jinja2 template (config/marketing.md.jinja) for rendering.
    Template-driven formatting ensures all output is configurable.

    Args:
        story: SuccessStory to format

    Returns:
        Formatted marketing output (Markdown string)

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    env = _get_template_env()
    config = get_template_settings()

    # Load marketing template
    template_name = config["marketing_markdown"]
    template = env.get_template(template_name)

    # Render template
    try:
        output = template.render(story=story)
        logger.debug(f"Generated marketing output for {story.id}")
        return output
    except Exception as e:
        logger.error(f"Failed to render marketing template for {story.id}: {e}")
        raise
