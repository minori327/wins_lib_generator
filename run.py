#!/usr/bin/env python3
"""
Wins Library System - CLI Entry Point v1.0

This is the ONLY entry point for the system.
All commands route through the orchestrator.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config(config_path: Path = None) -> Dict[str, Any]:
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
        config_path = Path("config/config.yaml")

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded configuration from {config_path}")
    return config


def cmd_validate(args):
    """Validate configuration files.

    Args:
        args: Parsed arguments (expect no additional args)
    """
    from utils.config_validator import validate_all_configs

    config_dir = Path("config")
    if not config_dir.exists():
        print(f"❌ Config directory not found: {config_dir}")
        sys.exit(1)

    print("Validating configuration files...")
    print("-" * 50)

    is_valid = validate_all_configs(config_dir)

    print("-" * 50)
    if is_valid:
        print("✅ All configuration files are valid")
        sys.exit(0)
    else:
        print("❌ Configuration validation failed")
        sys.exit(1)


def cmd_status(args):
    """Show library statistics.

    Args:
        args: Parsed arguments
    """
    config = load_config(args.config)
    library_dir = Path(config["paths"]["library_dir"])

    if not library_dir.exists():
        print(f"Library directory not found: {library_dir}")
        print("Run 'python run.py weekly' to create the library.")
        sys.exit(1)

    # Load all stories
    from models.library import load_all_stories

    stories = load_all_stories(library_dir)

    if not stories:
        print(f"Library: {library_dir}")
        print("Total Stories: 0")
        print("\nNo stories found. Run 'python run.py weekly' to process source files.")
        return

    # Statistics
    from collections import Counter

    by_country = Counter(s.country for s in stories)
    by_month = Counter(s.month for s in stories)
    by_confidence = Counter(s.confidence for s in stories)

    print(f"Library: {library_dir}")
    print(f"Total Stories: {len(stories)}")
    print()
    print("By Country:")
    for country, count in sorted(by_country.items()):
        print(f"  {country}: {count}")
    print()
    print("By Month:")
    for month, count in sorted(by_month.items()):
        print(f"  {month}: {count}")
    print()
    print("By Confidence:")
    for confidence, count in sorted(by_confidence.items()):
        print(f"  {confidence}: {count}")


def cmd_weekly(args):
    """Run weekly update workflow.

    Args:
        args: Parsed arguments with country, month, and optional flags
    """
    from workflow.orchestrator import run_weekly_workflow

    # Load configuration
    config = load_config(args.config)

    # Validate config first
    from utils.config_validator import validate_all_configs
    config_dir = Path("config")
    if not validate_all_configs(config_dir):
        print("❌ Configuration validation failed. Run 'python run.py validate' first.")
        sys.exit(1)

    # Dry run mode
    if args.dry_run:
        print("Dry run mode - validating configuration and inputs...")
        print(f"Countries: {args.country}")
        print(f"Month: {args.month}")
        print(f"Source directory: {config['paths']['sources_dir']}")
        print()
        print("✅ Dry run complete. Remove --dry-run to execute.")
        return

    # Extract paths from config
    source_dir = Path(config["paths"]["sources_dir"])
    library_dir = Path(config["paths"]["library_dir"])
    output_dir = Path(config["paths"]["outputs_dir"])

    # Run workflow
    print(f"Starting weekly update workflow for {args.month}...")
    print(f"Countries: {', '.join(args.country)}")
    print("-" * 50)

    result = run_weekly_workflow(
        countries=args.country,
        month=args.month,
        source_dir=source_dir,
        library_dir=library_dir,
        output_dir=output_dir,
        config=config
    )

    # Print results
    print()
    print("=" * 50)
    print("WEEKLY WORKFLOW COMPLETE")
    print("=" * 50)
    print(f"Stories Processed: {result.stories_processed}")
    print(f"Succeeded: {result.stories_succeeded}")
    print(f"Failed: {result.stories_failed}")
    print(f"Duration: {result.duration_seconds:.1f} seconds")

    if result.errors:
        print()
        print("Errors encountered:")
        for i, error in enumerate(result.errors[:10], 1):
            print(f"  {i}. {error}")
        if len(result.errors) > 10:
            print(f"  ... and {len(result.errors) - 10} more errors")

    if result.stories_failed > 0:
        print()
        print(f"⚠️  Warning: {result.stories_failed} stories failed to process")
        print("   Check logs for details: logs/wins_library.log")
        sys.exit(1)
    else:
        print()
        print("✅ All stories processed successfully")


def cmd_review(args):
    """Review a story for approval (Phase 5 human checkpoint).

    Args:
        args: Parsed arguments with story_id
    """
    config = load_config(args.config)
    library_dir = Path(config["paths"]["library_dir"])

    # Load story
    from models.library import load_success_story

    try:
        story = load_success_story(args.story_id, library_dir)
    except FileNotFoundError:
        print(f"❌ Story not found: {args.story_id}")
        print(f"Library directory: {library_dir}")
        sys.exit(1)

    # Display story details
    print()
    print("=" * 60)
    print(f"STORY REVIEW: {args.story_id}")
    print("=" * 60)
    print()
    print(f"Customer: {story.customer}")
    print(f"Country: {story.country}")
    print(f"Month: {story.month}")
    print(f"Confidence: {story.confidence}")
    print(f"Internal Only: {story.internal_only}")
    print()
    print("Context:")
    print(f"  {story.context}")
    print()
    print("Action:")
    print(f"  {story.action}")
    print()
    print("Outcome:")
    print(f"  {story.outcome}")
    print()
    print("Metrics:")
    for metric in story.metrics:
        print(f"  - {metric}")
    print()
    print(f"Sources: {', '.join(story.raw_sources)}")
    print()
    print("=" * 60)

    # TODO: Integrate with Phase 5 evaluation agent
    # For now, this is a manual review checkpoint
    print()
    print("⚠️  Full Phase 5 integration pending")
    print("   This is a manual review checkpoint for v1.0")
    print()
    print("To approve this story for publishing, use:")
    print(f"  python run.py publish --story-id {args.story_id} --approve")


def cmd_publish(args):
    """Publish a story artifact (Phase 7 publish checkpoint).

    Args:
        args: Parsed arguments with artifact_id and optional approve flag
    """
    if not args.approve:
        # Interactive approval checkpoint
        print(f"Publish approval required for: {args.artifact_id}")
        print()
        print("This requires explicit approval. Re-run with --approve flag:")
        print(f"  python run.py publish --artifact-id {args.artifact_id} --approve")
        sys.exit(1)

    # TODO: Integrate with Phase 7 publish gate agent
    print(f"✅ Publishing approved for: {args.artifact_id}")
    print()
    print("⚠️  Full Phase 7 integration pending for v1.0")
    print("   Publishing is logged but not yet executed to external channels")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Wins Library System v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s weekly --country US --month 2026-01
  %(prog)s weekly --country US --country UK --month 2026-01
  %(prog)s status
  %(prog)s validate
  %(prog)s review --story-id win-2026-01-US-1234
  %(prog)s publish --artifact-id pub-xxx --approve
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

    subparsers = parser.add_subparsers(
        dest="mode",
        required=True,
        help="Operation mode"
    )

    # Weekly mode
    weekly_parser = subparsers.add_parser(
        "weekly",
        help="Run weekly update workflow"
    )
    weekly_parser.add_argument(
        "--country",
        action="append",
        required=True,
        help="Country code (can specify multiple)"
    )
    weekly_parser.add_argument(
        "--month",
        required=True,
        help="Month in YYYY-MM format"
    )
    weekly_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without processing"
    )

    # Status mode
    status_parser = subparsers.add_parser(
        "status",
        help="Show library statistics"
    )

    # Validate mode
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate configuration files"
    )

    # Review mode
    review_parser = subparsers.add_parser(
        "review",
        help="Review a story (Phase 5 checkpoint)"
    )
    review_parser.add_argument(
        "--story-id",
        required=True,
        help="Story ID to review"
    )

    # Publish mode
    publish_parser = subparsers.add_parser(
        "publish",
        help="Publish an artifact (Phase 7 checkpoint)"
    )
    publish_parser.add_argument(
        "--artifact-id",
        required=True,
        help="Artifact ID to publish"
    )
    publish_parser.add_argument(
        "--approve",
        action="store_true",
        help="Approve publishing"
    )

    args = parser.parse_args()

    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Route to command handler
    if args.mode == "weekly":
        cmd_weekly(args)
    elif args.mode == "status":
        cmd_status(args)
    elif args.mode == "validate":
        cmd_validate(args)
    elif args.mode == "review":
        cmd_review(args)
    elif args.mode == "publish":
        cmd_publish(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
