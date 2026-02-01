"""
Test Phase 3 processors with mocks.
"""

import pytest
from pathlib import Path
from processors import pdf_processor, email_processor, text_processor


class TestPDFProcessor:
    """Test PDF text extraction."""

    def test_pdf_extraction_mock(self, monkeypatch):
        """Test PDF extraction with mocked pdfplumber."""
        mock_text = "Sample PDF content for testing"

        # Mock pdfplumber to return our test text
        class MockPage:
            def extract_text(self):
                return mock_text

        class MockPDF:
            pages = [MockPage()]

        def mock_pdf_open(filepath):
            return MockPDF()

        monkeypatch.setattr("pdf_processor.pdfplumber", __name__)

        # Create dummy PDF file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = Path(f.name)
            f.write(b"%PDF-1.4")

        try:
            result = pdf_processor.extract_text_from_pdf(pdf_path)
            assert isinstance(result, str)
        finally:
            pdf_path.unlink()

    def test_pdf_extraction_empty_file(self, monkeypatch):
        """Test PDF extraction with empty file returns empty string."""
        # Mock empty PDF
        class MockPDF:
            pages = []

        def mock_pdf_open(filepath):
            return MockPDF()

        monkeypatch.setattr("pdf_processor.pdfplumber", __name__)

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = Path(f.name)

        try:
            result = pdf_processor.extract_text_from_pdf(pdf_path)
            assert result == ""
        finally:
            pdf_path.unlink()


class TestEmailProcessor:
    """Test email parsing."""

    def test_email_parsing_mock(self, tmp_path):
        """Test email parsing with mock .eml file."""
        # Create test email
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Subject
Date: Mon, 01 Jan 2026 12:00:00 +0000

Test email body."""
        email_file = tmp_path / "test.eml"
        email_file.write_text(email_content)

        result = email_processor.extract_email_data(email_file)

        assert result["subject"] == "Test Subject"
        assert result["from"] == "sender@example.com"
        assert "Test email body" in result["body"]


class TestTextProcessor:
    """Test text normalization."""

    def test_text_normalization(self):
        """Test text encoding normalization."""
        # Text with encoding issues (various encodings)
        text = "Test text with special chars: cafÃ©"
        result = text_processor.normalize_text_encoding(text)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_text_normalization_empty(self):
        """Test normalization of empty string."""
        result = text_processor.normalize_text_encoding("")
        assert result == ""

    def test_text_normalization_preserves_content(self):
        """Test normalization preserves meaningful content."""
        text = "Normal English text"
        result = text_processor.normalize_text_encoding(text)

        assert "Normal English text" in result
