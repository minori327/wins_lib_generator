"""
Workflow orchestrator for Wins Library System v1.0.

Coordinates phase execution in correct order.
Enforces phase boundaries and error semantics.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path

from workflow.ingest import discover_files
from workflow.normalize import (
    normalize_pdf,
    normalize_email,
    normalize_teams_text,
    normalize_image
)
from models.library import save_success_story
from agents.extraction_agent import extract_from_raw_item
from agents.draft_normalization_agent import normalize_draft
from agents.semantic_dedup_agent import detect_semantic_duplicates
from agents.finalization_agent import finalize_drafts
from agents.success_evaluation_agent import evaluate_story
from agents.ranking_agent import rank_stories
from agents.output_preparation_agent import prepare_outputs
from workflow.writer import (
    write_executive_outputs,
    write_marketing_outputs
)

logger = logging.getLogger(__name__)


@dataclass
class WorkflowResult:
    """Result from running weekly workflow."""
    stories_processed: int
    stories_succeeded: int
    stories_failed: int
    errors: List[str] = field(default_factory=list)
    output_paths: List[Path] = field(default_factory=list)
    duration_seconds: float = 0.0


def run_weekly_workflow(
    countries: List[str],
    month: str,
    source_dir: Path,
    library_dir: Path,
    output_dir: Path,
    config: Dict[str, Any]
) -> WorkflowResult:
    """Execute end-to-end weekly workflow.

    Phases execute in order:
      1. Discovery (Phase 3)
      2. Normalization (Phase 3)
      3. Extraction (Phase 4)
      4. Draft Normalization (Phase 4)
      5. Semantic Deduplication (Phase 4)
      6. Finalization (Phase 4)
      7. Mechanical Deduplication (Phase 3)
      8. Save (Phase 4)
      9. Evaluation (Phase 5)
      10. Ranking (Phase 5)
      11. Output Preparation (Phase 5)
      12. Write Outputs (Phase 6)

    Error semantics:
      - Phase 3-4: Continue on error, log failures
      - Phase 5-6: Continue on error, log failures
      - Partial results acceptable

    Args:
        countries: List of country codes
        month: Month in YYYY-MM format
        source_dir: Source files directory
        library_dir: Library output directory
        output_dir: Output files directory
        config: System configuration

    Returns:
        WorkflowResult with statistics
    """
    start_time = time.time()
    errors = []

    # Ensure directories exist
    orchestrator_config = config.get("orchestrator", {})
    if orchestrator_config.get("create_missing_dirs", True):
        library_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Phase 3: File Discovery
    # ========================================================================
    logger.info("Phase 3: Starting file discovery...")
    all_files = []

    for country in countries:
        try:
            files = discover_files(source_dir, country, month)
            all_files.extend(files)
            logger.info(f"  Found {len(files)} files for {country}")
        except Exception as e:
            error_msg = f"Discovery failed for {country}: {e}"
            logger.error(f"  {error_msg}")
            errors.append(error_msg)
            continue

    logger.info(f"Phase 3 complete: {len(all_files)} total files discovered")

    # ========================================================================
    # Phase 3: Normalization
    # ========================================================================
    logger.info("Phase 3: Starting normalization...")
    raw_items = []

    for file_path in all_files:
        try:
            # Route to appropriate normalizer based on file type
            if file_path.suffix == ".pdf":
                raw_item = normalize_pdf(file_path, file_path.parent.parent.name, month)
            elif file_path.suffix == ".eml":
                raw_item = normalize_email(file_path, file_path.parent.parent.name, month)
            elif file_path.suffix in [".txt", ".text"]:
                raw_item = normalize_teams_text(file_path, file_path.parent.parent.name, month)
            elif file_path.suffix in [".png", ".jpg", ".jpeg"]:
                raw_item = normalize_image(file_path, file_path.parent.parent.name, month)
            else:
                logger.warning(f"  Unknown file type: {file_path.suffix}")
                continue

            # Set created_at timestamp
            from datetime import datetime
            raw_item.created_at = datetime.utcnow().isoformat() + "Z"

            raw_items.append(raw_item)
            logger.debug(f"  Normalized: {file_path.name} -> {raw_item.id}")

        except Exception as e:
            error_msg = f"Normalization failed for {file_path.name}: {e}"
            logger.error(f"  {error_msg}")
            errors.append(error_msg)
            continue

    logger.info(f"Phase 3 complete: {len(raw_items)} RawItems created")

    # ========================================================================
    # Phase 3: Mechanical Deduplication
    # ========================================================================
    logger.info("Phase 3: Starting mechanical deduplication of RawItems...")
    try:
        from workflow.deduplicate import deduplicate_raw_items
        raw_items = deduplicate_raw_items(raw_items)
        logger.info(f"Phase 3 complete: {len(raw_items)} RawItems after deduplication")
    except Exception as e:
        logger.warning(f"  Mechanical deduplication failed: {e}")
        logger.warning(f"  Continuing with all {len(raw_items)} RawItems")

    # ========================================================================
    # Phase 4: Extraction
    # ========================================================================
    logger.info("Phase 4: Starting extraction...")
    draft_stories = []
    llm_config = config.get("llm", {})

    for raw_item in raw_items:
        try:
            draft_story, failure_record = extract_from_raw_item(
                raw_item,
                model=llm_config.get("model", "glm-4:9b"),
                ollama_base_url=llm_config.get("base_url", "http://localhost:11434")
            )

            if draft_story:
                draft_stories.append(draft_story)
                logger.debug(f"  Extracted: {raw_item.id} -> DraftStory")
            else:
                error_msg = f"Extraction failed for {raw_item.id}: {failure_record.reason if failure_record else 'Unknown'}"
                logger.error(f"  {error_msg}")
                errors.append(error_msg)
                continue

        except Exception as e:
            error_msg = f"Extraction error for {raw_item.id}: {e}"
            logger.error(f"  {error_msg}")
            errors.append(error_msg)
            continue

    logger.info(f"Phase 4 complete: {len(draft_stories)} DraftStories created")

    # ========================================================================
    # Phase 4: Draft Normalization
    # ========================================================================
    logger.info("Phase 4: Starting draft normalization...")
    normalized_drafts = []

    for draft in draft_stories:
        try:
            normalized = normalize_draft(draft)
            normalized_drafts.append(normalized)
            logger.debug(f"  Normalized draft: {draft.source_raw_item_id}")
        except Exception as e:
            error_msg = f"Draft normalization failed for {draft.source_raw_item_id}: {e}"
            logger.error(f"  {error_msg}")
            errors.append(error_msg)
            continue

    logger.info(f"Phase 4 complete: {len(normalized_drafts)} drafts normalized")

    # ========================================================================
    # Phase 4: Semantic Deduplication
    # ========================================================================
    logger.info("Phase 4: Starting semantic deduplication...")
    llm_config = config.get("llm", {})

    try:
        duplicate_flags = detect_semantic_duplicates(
            normalized_drafts,
            model=llm_config.get("model", "glm-4:9b"),
            ollama_base_url=llm_config.get("base_url", "http://localhost:11434")
        )

        # Filter out duplicates (keep primary stories)
        seen_indices = set()
        unique_drafts = []
        for i, draft in enumerate(normalized_drafts):
            if i in seen_indices:
                continue
            unique_drafts.append(draft)
            # Mark all indices involved in duplicate flags
            for flag in duplicate_flags:
                if flag.primary_index == i:
                    seen_indices.add(flag.primary_index)
                if flag.duplicate_index == i:
                    seen_indices.add(flag.duplicate_index)

        logger.info(f"  Found {len(duplicate_flags)} potential duplicates")
        logger.info(f"Phase 4 complete: {len(unique_drafts)} unique stories after deduplication")

    except Exception as e:
        logger.warning(f"  Semantic deduplication failed: {e}")
        logger.warning(f"  Continuing with all {len(normalized_drafts)} drafts")
        unique_drafts = normalized_drafts

    # ========================================================================
    # Phase 4: Finalization
    # ========================================================================
    logger.info("Phase 4: Starting finalization...")

    try:
        # Extract country from first draft (all should be same country per batch)
        country = unique_drafts[0].country if unique_drafts else countries[0]

        # Prepare raw source filenames for each draft
        raw_source_filenames = [
            [draft.source_raw_item_id] if draft.source_raw_item_id else []
            for draft in unique_drafts
        ]

        success_stories = finalize_drafts(unique_drafts, country, month, raw_source_filenames)
        logger.debug(f"  Finalized {len(success_stories)} DraftStories to SuccessStories")

    except Exception as e:
        error_msg = f"Finalization failed: {e}"
        logger.error(f"  {error_msg}")
        errors.append(error_msg)
        success_stories = []

    logger.info(f"Phase 4 complete: {len(success_stories)} SuccessStories created")

    # ========================================================================
    # Phase 4: Save to Library
    # ========================================================================
    logger.info("Phase 4: Saving to library...")
    for story in success_stories:
        try:
            save_success_story(story, library_dir)
            logger.debug(f"  Saved: {story.id}")
        except Exception as e:
            error_msg = f"Save failed for {story.id}: {e}"
            logger.error(f"  {error_msg}")
            errors.append(error_msg)
            continue

    logger.info(f"Phase 4 complete: {len(success_stories)} stories saved to library")

    # ========================================================================
    # Phase 5: Success Evaluation
    # ========================================================================
    logger.info("Phase 5: Starting success evaluation...")
    evaluated_stories = []

    for story in success_stories:
        try:
            result = evaluate_story(story)
            # TODO: Store evaluation result
            evaluated_stories.append(story)
            logger.debug(f"  Evaluated: {story.id} -> {result.approved}")
        except Exception as e:
            error_msg = f"Evaluation failed for {story.id}: {e}"
            logger.error(f"  {error_msg}")
            errors.append(error_msg)
            # Continue with story even if evaluation fails
            evaluated_stories.append(story)
            continue

    logger.info(f"Phase 5 complete: {len(evaluated_stories)} stories evaluated")

    # ========================================================================
    # Phase 5: Ranking
    # ========================================================================
    logger.info("Phase 5: Starting ranking...")
    try:
        ranked_stories = rank_stories(evaluated_stories)
        logger.info(f"Phase 5 complete: Stories ranked")
    except Exception as e:
        logger.warning(f"  Ranking failed: {e}")
        logger.warning(f"  Continuing with original order")
        ranked_stories = evaluated_stories

    # ========================================================================
    # Phase 5: Output Preparation
    # ========================================================================
    logger.info("Phase 5: Starting output preparation...")
    # TODO: Integrate output_preparation_agent
    # For v1.0, we'll use stories directly
    prepared_stories = ranked_stories

    logger.info(f"Phase 5 complete: {len(prepared_stories)} stories prepared for output")

    # ========================================================================
    # Phase 6: Write Outputs
    # ========================================================================
    logger.info("Phase 6: Writing outputs...")

    try:
        # Executive outputs
        exec_paths = write_executive_outputs(prepared_stories, output_dir)
        logger.info(f"  Wrote {len(exec_paths)} executive outputs")
    except Exception as e:
        error_msg = f"Executive output generation failed: {e}"
        logger.error(f"  {error_msg}")
        errors.append(error_msg)

    try:
        # Marketing outputs
        mkt_paths = write_marketing_outputs(prepared_stories, output_dir)
        logger.info(f"  Wrote {len(mkt_paths)} marketing outputs")
    except Exception as e:
        error_msg = f"Marketing output generation failed: {e}"
        logger.error(f"  {error_msg}")
        errors.append(error_msg)

    logger.info(f"Phase 6 complete: Outputs written to {output_dir}")

    # ========================================================================
    # Summary
    # ========================================================================
    duration = time.time() - start_time

    result = WorkflowResult(
        stories_processed=len(raw_items),
        stories_succeeded=len(success_stories),
        stories_failed=len(raw_items) - len(success_stories),
        errors=errors,
        duration_seconds=duration
    )

    logger.info("=" * 60)
    logger.info("WEEKLY WORKFLOW COMPLETE")
    logger.info(f"Processed: {result.stories_processed}")
    logger.info(f"Succeeded: {result.stories_succeeded}")
    logger.info(f"Failed: {result.stories_failed}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Duration: {result.duration_seconds:.1f}s")
    logger.info("=" * 60)

    return result
