#!/usr/bin/env python3
"""
Wins Library System - CLI Entry Point v2.0
Iteration 2: Human-Primary System

This is the ONLY entry point for the system.
Three explicit commands only:
- --extract-markdown: Extract Markdown from source files
- --identify-stories: Generate candidate Success Stories
- --summary: Generate summaries from final Excel rows

Human Primacy: System extracts and suggests, humans decide.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional


# Configure logging per specification
logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load system configuration.

    Args:
        config_path: Path to config.yaml (default: config/config.yaml)

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    import yaml

    if config_path is None:
        config_path = "config/config.yaml"

    config_path = Path(config_path)

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded configuration from {config_path}")
    return config


def cmd_extract_markdown(sources_path: str, config: Dict[str, Any]):
    """Extract Markdown from source files.

    Work Stream 1: Transform original sources into navigable Markdown.

    Args:
        sources_path: Path to source files
        config: Configuration dictionary
    """
    from markdown_extractor import extract_markdown

    sources = Path(sources_path)
    output_dir = Path(config["paths"]["notes_sources_dir"])

    logger.info(f"[CMD_EXTRACT_MARKDOWN] Starting operation...")
    logger.info(f"[CMD_EXTRACT_MARKDOWN] Sources path: {sources}")
    logger.info(f"[CMD_EXTRACT_MARKDOWN] Output directory: {output_dir}")

    if not sources.exists():
        logger.error(f"[CMD_EXTRACT_MARKDOWN] Sources path not found: {sources}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract Markdown
    extract_markdown(
        sources_path=sources,
        output_dir=output_dir,
        config=config
    )

    logger.info(f"[CMD_EXTRACT_MARKDOWN] Completed in {output_dir}")


def cmd_identify_stories(sources_path: str, output_path: str, config: Dict[str, Any]):
    """Identify Success Story candidates from sources.

    Work Stream 2: Generate candidate rows for human review.
    NO consolidation, NO deduplication, NO final judgment.

    Args:
        sources_path: Path to Markdown sources
        output_path: Output Excel file path
        config: Configuration dictionary
    """
    from story_identifier import identify_stories

    sources = Path(sources_path)
    output = Path(output_path)

    logger.info(f"[CMD_IDENTIFY_STORIES] Starting operation...")
    logger.info(f"[CMD_IDENTIFY_STORIES] Sources path: {sources}")
    logger.info(f"[CMD_IDENTIFY_STORIES] Output path: {output}")

    if not sources.exists():
        logger.error(f"[CMD_IDENTIFY_STORIES] Sources path not found: {sources}")
        sys.exit(1)

    # Create output directory
    output.parent.mkdir(parents=True, exist_ok=True)

    # Identify stories (candidates only)
    identify_stories(
        sources_path=sources,
        output_path=output,
        config=config
    )

    logger.info(f"[CMD_IDENTIFY_STORIES] Completed: {output}")


def cmd_summary(input_path: str, output_path: str, prompt_template: str, config: Dict[str, Any]):
    """Generate executive summary from final Excel rows.

    Work Stream 4: Summary from final rows ONLY.

    Args:
        input_path: Input Excel file path
        output_path: Output Markdown file path
        prompt_template: Path to prompt template
        config: Configuration dictionary
    """
    from summary_generator import generate_summary

    input_file = Path(input_path)
    output = Path(output_path)

    logger.info(f"[CMD_SUMMARY] Starting operation...")
    logger.info(f"[CMD_SUMMARY] Input Excel: {input_file}")
    logger.info(f"[CMD_SUMMARY] Output path: {output}")
    logger.info(f"[CMD_SUMMARY] Prompt template: {prompt_template}")

    if not input_file.exists():
        logger.error(f"[CMD_SUMMARY] Input file not found: {input_file}")
        sys.exit(1)

    # Create output directory
    output.parent.mkdir(parents=True, exist_ok=True)

    # Generate summary
    generate_summary(
        input_path=input_file,
        output_path=output,
        prompt_template=prompt_template,
        config=config
    )

    logger.info(f"[CMD_SUMMARY] Completed: {output}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Wins Library System v2.0 - Human-Primary",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --extract-markdown --sources vault/00_sources/2026-01/
  %(prog)s --identify-stories --sources vault/20_notes/sources/ --output outputs/candidates_v1_20260201.xlsx
  %(prog)s --summary executive --input outputs/wins_library_v1_20260201.xlsx --output outputs/executive_summary.md
        """
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to config.yaml (default: config/config.yaml)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging"
    )

    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--extract-markdown",
        action="store_true",
        help="Extract Markdown from source files"
    )
    mode_group.add_argument(
        "--identify-stories",
        action="store_true",
        help="Identify Success Story candidates"
    )
    mode_group.add_argument(
        "--summary",
        action="store_true",
        help="Generate executive summary"
    )

    # Arguments for --extract-markdown
    parser.add_argument("--sources", type=str, help="Path to source files directory")

    # Arguments for --identify-stories
    parser.add_argument("--output", type=str, help="Output Excel file path")

    # Arguments for --summary
    parser.add_argument(
        "summary_type",
        nargs="?",
        choices=["executive"],
        help="Type of summary to generate (for --summary mode)"
    )
    parser.add_argument("--input", type=str, help="Input Excel file path")
    parser.add_argument(
        "--prompt",
        type=str,
        default="prompts/executive_summary.yaml",
        help="Prompt template path (default: prompts/executive_summary.yaml)"
    )

    args = parser.parse_args()

    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load config
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    # Route to command handler
    if args.extract_markdown:
        if not args.sources:
            logger.error("--extract-markdown requires --sources argument")
            sys.exit(1)
        cmd_extract_markdown(args.sources, config)

    elif args.identify_stories:
        if not args.sources:
            logger.error("--identify-stories requires --sources argument")
            sys.exit(1)
        if not args.output:
            logger.error("--identify-stories requires --output argument")
            sys.exit(1)
        cmd_identify_stories(args.sources, args.output, config)

    elif args.summary:
        if not args.input:
            logger.error("--summary requires --input argument")
            sys.exit(1)
        if not args.output:
            logger.error("--summary requires --output argument")
            sys.exit(1)
        if not args.summary_type:
            logger.error("--summary requires summary_type argument (executive)")
            sys.exit(1)
        cmd_summary(args.input, args.output, args.prompt, config)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
