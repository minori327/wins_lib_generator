"""
Test end-to-end orchestration with mocks.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from workflow.orchestrator import run_weekly_workflow, WorkflowResult
from models.library import SuccessStory


class TestOrchestrator:
    """Test orchestrator control flow."""

    def test_orchestrator_happy_path(self, tmp_path, monkeypatch):
        """Test orchestrator with all phases mocked."""
        # Create test config
        config = {
            "paths": {
                "sources_dir": str(tmp_path),
                "library_dir": str(tmp_path / "wins"),
                "outputs_dir": str(tmp_path / "outputs")
            },
            "llm": {
                "backend": "ollama",
                "base_url": "http://localhost:11434",
                "model": "glm-4:9b"
            },
            "deduplication": {
                "similarity_threshold": 0.85
            },
            "orchestrator": {
                "create_missing_dirs": True
            }
        }

        # Create source directory structure
        (tmp_path / "US" / "2026-01").mkdir(parents=True)

        # Create a test PDF file (empty, just for discovery)
        (tmp_path / "US" / "2026-01" / "test.pdf").write_bytes(b"%PDF")

        # Mock all phase functions
        def mock_discover(*args):
            return [tmp_path / "US" / "2026-01" / "test.pdf"]

        def mock_normalize(*args):
            from models.raw_item import RawItem
            return RawItem(
                id="test-raw",
                text="Test",
                source_type="pdf",
                filename="test.pdf",
                country="US",
                month="2026-01",
                created_at="2026-01-01T00:00:00Z"
            )

        def mock_extract(*args):
            from models.draft_story import DraftSuccessStory
            draft = DraftSuccessStory(
                customer="Test",
                context="Test",
                action="Test",
                outcome="Test",
                metrics=[],
                confidence="medium",
                internal_only=False,
                tags=[],
                source_raw_item_id="test-raw"
            )
            return draft, None

        def mock_normalize_draft(draft):
            return draft

        def mock_detect_duplicates(drafts):
            return []

        def mock_finalize(drafts, month, source_ids):
            from models.library import SuccessStory
            return [SuccessStory(
                id="win-2026-01-US-test",
                country="US",
                month="2026-01",
                customer="Test",
                context="Test",
                action="Test",
                outcome="Test",
                metrics=[],
                confidence="medium",
                internal_only=False,
                raw_sources=[],
                last_updated="2026-01-01T00:00:00Z",
                tags=[],
                industry="",
                team_size=""
            )]

        def mock_deduplicate(stories):
            return stories

        def mock_save(story, library_dir):
            # Create empty JSON file
            (library_dir / f"{story.id}.json").write_text("{}")

        def mock_evaluate(story):
            from agents.success_evaluation_agent import EvaluationResult
            return EvaluationResult(
                story_id=story.id,
                approved=True,
                confidence="medium",
                reasons=["Test"]
            )

        def mock_rank(stories):
            return stories

        # Apply mocks
        monkeypatch.setattr("workflow.ingest", "discover_files", mock_discover)
        monkeypatch.setattr("workflow.normalize", "normalize_pdf", mock_normalize)
        monkeypatch.setattr("agents.extraction_agent", "extract_from_raw_item", mock_extract)
        monkeypatch.setattr("agents.draft_normalization_agent", "normalize_draft", mock_normalize_draft)
        monkeypatch.setattr("agents.semantic_dedup_agent", "detect_duplicates", mock_detect_duplicates)
        monkeypatch.setattr("agents.finalization_agent", "finalize_stories", mock_finalize)
        monkeypatch.setattr("workflow.deduplicate", "deduplicate_stories", mock_deduplicate)
        monkeypatch.setattr("models.library", "save_success_story", mock_save)
        monkeypatch.setattr("agents.success_evaluation_agent", "evaluate_story", mock_evaluate)
        monkeypatch.setattr("agents.ranking_agent", "rank_stories", mock_rank)

        # Run workflow
        result = run_weekly_workflow(
            countries=["US"],
            month="2026-01",
            source_dir=tmp_path,
            library_dir=tmp_path / "wins",
            output_dir=tmp_path / "outputs",
            config=config
        )

        # Verify results
        assert result.stories_processed == 1
        assert result.stories_succeeded == 1
        assert result.stories_failed == 0
        assert len(result.errors) == 0

    def test_orchestrator_continues_on_error(self, tmp_path, monkeypatch):
        """Test orchestrator continues after phase 3 failure."""
        config = {
            "paths": {
                "sources_dir": str(tmp_path),
                "library_dir": str(tmp_path / "wins"),
                "outputs_dir": str(tmp_path / "outputs")
            },
            "llm": {
                "backend": "ollama",
                "model": "glm-4:9b"
            },
            "deduplication": {},
            "orchestrator": {
                "continue_on_error": True,
                "create_missing_dirs": True
            }
        }

        # Create source directory but no files
        (tmp_path / "US" / "2026-01").mkdir(parents=True)

        # Mock extraction to fail
        def mock_extract(*args):
            from models.draft_story import ExtractionFailureRecord
            return None, ExtractionFailureRecord(
                raw_item_id="test",
                reason="LLM timeout",
                error="Timeout"
            )

        monkeypatch.setattr("workflow.ingest", "discover_files", lambda *args: [])
        monkeypatch.setattr("agents.extraction_agent", "extract_from_raw_item", mock_extract)

        # Run workflow
        result = run_weekly_workflow(
            countries=["US"],
            month="2026-01",
            source_dir=tmp_path,
            library_dir=tmp_path / "wins",
            output_dir=tmp_path / "outputs",
            config=config
        )

        # Should complete without crashing
        assert result.stories_processed == 0
        assert result.stories_succeeded == 0
        assert result.stories_failed == 0

    def test_orchestrator_phase_order(self, tmp_path, monkeypatch):
        """Test that phases execute in correct order."""
        phases_executed = []

        # Track phase execution order
        def mock_discover(*args):
            phases_executed.append("discovery")
            return []

        def mock_normalize(*args):
            phases_executed.append("normalization")
            return None

        def mock_extract(*args):
            phases_executed.append("extraction")
            return None, None

        def mock_normalize_draft(*args):
            phases_executed.append("draft_normalization")
            return None

        def mock_semantic_dedup(*args):
            phases_executed.append("semantic_dedup")
            return []

        def mock_finalize(*args):
            phases_executed.append("finalization")
            return []

        def mock_mechanical_dedup(*args):
            phases_executed.append("mechanical_dedup")
            return []

        def mock_save(*args):
            phases_executed.append("save")
            return None

        def mock_evaluate(*args):
            phases_executed.append("evaluation")
            return None

        def mock_rank(*args):
            phases_executed.append("ranking")
            return []

        def mock_prepare(*args):
            phases_executed.append("output_preparation")
            return None

        def mock_write(*args):
            phases_executed.append("write_outputs")
            return []

        # Apply mocks
        monkeypatch.setattr("workflow.ingest", "discover_files", mock_discover)
        monkeypatch.setattr("workflow.normalize", "normalize_pdf", mock_normalize)
        monkeypatch.setattr("agents.extraction_agent", "extract_from_raw_item", mock_extract)
        monkeypatch.setattr("agents.draft_normalization_agent", "normalize_draft", mock_normalize_draft)
        monkeypatch.setattr("agents.semantic_dedup_agent", "detect_duplicates", mock_semantic_dedup)
        monkeypatch.setattr("agents.finalization_agent", "finalize_stories", mock_finalize)
        monkeypatch.setattr("workflow.deduplicate", "deduplicate_stories", mock_mechanical_dedup)
        monkeypatch.setattr("models.library", "save_success_story", mock_save)
        monkeypatch.setattr("agents.success_evaluation_agent", "evaluate_story", mock_evaluate)
        monkeypatch.setattr("agents.ranking_agent", "rank_stories", mock_rank)
        monkeypatch.setattr("agents.output_preparation_agent", "prepare_outputs", mock_prepare)
        monkeypatch.setattr("workflow.writer", "write_executive_outputs", mock_write_outputs)

        config = {
            "paths": {
                "sources_dir": str(tmp_path),
                "library_dir": str(tmp_path / "wins"),
                "outputs_dir": str(tmp_path / "outputs")
            },
            "llm": {"model": "glm-4:9b"},
            "deduplication": {},
            "orchestrator": {"create_missing_dirs": True}
        }

        (tmp_path / "US" / "2026-01").mkdir(parents=True)

        # Run workflow
        run_weekly_workflow(
            countries=["US"],
            month="2026-01",
            source_dir=tmp_path,
            library_dir=tmp_path / "wins",
            output_dir=tmp_path / "outputs",
            config=config
        )

        # Verify phase order
        expected_order = [
            "discovery",
            "normalization",
            "extraction",
            "draft_normalization",
            "semantic_dedup",
            "finalization",
            "mechanical_dedup",
            "save",
            "evaluation",
            "ranking",
            "output_preparation",
            "write_outputs"
        ]

        assert phases_executed == expected_order
