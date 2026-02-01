"""
Test data models - RawItem and SuccessStory.
"""

import pytest
from pathlib import Path
from datetime import datetime
from models.raw_item import RawItem
from models.library import SuccessStory, save_success_story, load_success_story


class TestRawItem:
    """Test RawItem dataclass."""

    def test_raw_item_creation(self):
        """Test RawItem dataclass instantiation."""
        item = RawItem(
            id="test-id-123",
            text="Test content",
            source_type="pdf",
            filename="test.pdf",
            country="US",
            month="2026-01",
            created_at="2026-01-01T00:00:00Z",
            metadata={}
        )

        assert item.id == "test-id-123"
        assert item.text == "Test content"
        assert item.source_type == "pdf"
        assert item.filename == "test.pdf"
        assert item.country == "US"
        assert item.month == "2026-01"
        assert item.metadata == {}

    def test_raw_item_required_fields(self):
        """Test RawItem has all required fields."""
        item = RawItem(
            id="test-id",
            text="Test",
            source_type="email",
            filename="test.eml",
            country="UK",
            month="2026-02",
            created_at="2026-02-01T00:00:00Z",
            metadata={}
        )

        assert hasattr(item, 'id')
        assert hasattr(item, 'text')
        assert hasattr(item, 'source_type')
        assert hasattr(item, 'filename')
        assert hasattr(item, 'country')
        assert hasattr(item, 'month')


class TestSuccessStory:
    """Test SuccessStory model and serialization."""

    def test_success_story_creation(self):
        """Test SuccessStory dataclass instantiation."""
        story = SuccessStory(
            id="win-2026-01-US-001",
            country="US",
            month="2026-01",
            customer="ACME Corporation",
            context="Test problem",
            action="Test solution",
            outcome="Test results",
            metrics=["+100% revenue"],
            confidence="high",
            internal_only=False,
            raw_sources=["test.pdf"],
            last_updated="2026-01-01T00:00:00Z",
            tags=["test"],
            industry="Tech",
            team_size="Enterprise"
        )

        assert story.id == "win-2026-01-US-001"
        assert story.customer == "ACME Corporation"
        assert story.confidence == "high"
        assert story.internal_only is False

    def test_success_story_save(self, tmp_path):
        """Test saving SuccessStory to JSON file."""
        story = SuccessStory(
            id="win-2026-01-US-001",
            country="US",
            month="2026-01",
            customer="Test Customer",
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
        )

        library_dir = tmp_path / "wins"
        library_dir.mkdir()

        saved_path = save_success_story(story, library_dir)

        assert saved_path.exists()
        assert saved_path.name == "win-2026-01-US-001.json"

        # Verify JSON content
        import json
        with open(saved_path, 'r') as f:
            data = json.load(f)

        assert data["customer"] == "Test Customer"
        assert data["confidence"] == "medium"

    def test_success_story_load(self, tmp_path):
        """Test loading SuccessStory from JSON file."""
        story = SuccessStory(
            id="win-2026-01-UK-002",
            country="UK",
            month="2026-01",
            customer="BBC Studios",
            context="Test context",
            action="Test action",
            outcome="Test outcome",
            metrics=[],
            confidence="high",
            internal_only=False,
            raw_sources=[],
            last_updated="2026-01-01T00:00:00Z",
            tags=[],
            industry="",
            team_size=""
        )

        library_dir = tmp_path / "wins"
        library_dir.mkdir()
        save_success_story(story, library_dir)

        # Load it back
        loaded_story = load_success_story("win-2026-01-UK-002", library_dir)

        assert loaded_story.id == story.id
        assert loaded_story.customer == story.customer
        assert loaded_story.context == story.context
        assert loaded_story.action == story.action
        assert loaded_story.outcome == story.outcome

    def test_success_story_round_trip(self, tmp_path):
        """Test save + load preserves data."""
        story = SuccessStory(
            id="win-2026-01-CN-003",
            country="CN",
            month="2026-01",
            customer="Alibaba",
            context="Challenge",
            action="Solution",
            outcome="Results",
            metrics=["+50% efficiency", "-30% costs"],
            confidence="medium",
            internal_only=True,
            raw_sources=["report.pdf"],
            last_updated="2026-01-15T10:30:00Z",
            tags=["china", "ecommerce"],
            industry="E-commerce",
            team_size="Enterprise"
        )

        library_dir = tmp_path / "wins"
        library_dir.mkdir()
        save_success_story(story, library_dir)

        loaded_story = load_success_story(story.id, library_dir)

        # Verify all fields preserved
        assert loaded_story.id == story.id
        assert loaded_story.customer == story.customer
        assert loaded_story.context == story.context
        assert loaded_story.action == story.action
        assert loaded_story.outcome == story.outcome
        assert loaded_story.metrics == story.metrics
        assert loaded_story.confidence == story.confidence
        assert loaded_story.internal_only == story.internal_only
        assert loaded_story.raw_sources == story.raw_sources
        assert loaded_story.tags == story.tags
        assert loaded_story.industry == story.industry
        assert loaded_story.team_size == story.team_size
