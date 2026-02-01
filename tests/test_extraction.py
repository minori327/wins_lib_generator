"""
Test LLM extraction with mocks.
"""

import pytest
from pathlib import Path
from models.raw_item import RawItem
from agents.extraction_agent import extract_from_raw_item
from models.draft_story import DraftSuccessStory


class TestExtractionAgent:
    """Test LLM extraction with mocked Ollama."""

    def test_extract_with_mock_llm(self, monkeypatch):
        """Test extraction with mocked LLM response."""
        # Mock LLM response
        mock_response = {
            "customer": "ACME Corp",
            "context": "Test problem description",
            "action": "Test solution description",
            "outcome": "Test results description",
            "metrics": ["+10% revenue", "-5% costs"],
            "confidence": "high",
            "internal_only": False,
            "tags": ["technology", "growth"],
            "industry": "Manufacturing",
            "team_size": "Enterprise"
        }

        def mock_call_ollama_json(prompt, model, url):
            return mock_response

        monkeypatch.setattr("agents.extraction_agent.llm_utils", "call_ollama_json", mock_call_ollama_json)

        # Create test RawItem
        raw_item = RawItem(
            id="test-raw-001",
            text="Test content about ACME Corp success story",
            source_type="email",
            filename="test.eml",
            country="US",
            month="2026-01",
            created_at="2026-01-01T00:00:00Z"
        )

        # Extract
        draft_story, failure = extract_from_raw_item(raw_item)

        assert draft_story is not None
        assert failure is None
        assert draft_story.customer == "ACME Corp"
        assert draft_story.confidence == "high"
        assert draft_story.internal_only is False

    def test_extraction_failure_handling(self, monkeypatch):
        """Test graceful failure handling when LLM fails."""
        # Mock LLM to raise exception
        def mock_call_ollama_json(prompt, model, url):
            raise Exception("LLM timeout")

        monkeypatch.setattr("agents.extraction_agent.llm_utils", "call_ollama_json", mock_call_ollama_json)

        raw_item = RawItem(
            id="test-raw-002",
            text="Test content",
            source_type="pdf",
            filename="test.pdf",
            country="UK",
            month="2026-01",
            created_at="2026-01-01T00:00:00Z"
        )

        draft_story, failure = extract_from_raw_item(raw_item)

        assert draft_story is None
        assert failure is not None
        assert "LLM timeout" in failure.reason or "timeout" in failure.reason.lower()

    def test_extraction_retry_logic(self, monkeypatch):
        """Test retry logic with mock LLM."""
        call_count = {"count": 0}

        def mock_call_ollama_json(prompt, model, url):
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise Exception("Temporary failure")
            # Succeed on 3rd try
            return {
                "customer": "Test Customer",
                "context": "Test",
                "action": "Test",
                "outcome": "Test",
                "metrics": [],
                "confidence": "medium",
                "internal_only": False
            }

        monkeypatch.setattr("agents.extraction_agent.llm_utils", "call_ollama_json", mock_call_ollama_json)

        raw_item = RawItem(
            id="test-raw-003",
            text="Test content",
            source_type="teams",
            filename="test.txt",
            country="CN",
            month="2026-01",
            created_at="2026-01-01T00:00:00Z"
        )

        draft_story, failure = extract_from_raw_item(raw_item)

        # Should succeed after retries
        assert draft_story is not None
        assert failure is None
        assert call_count["count"] == 3  # Failed twice, succeeded on 3rd try
