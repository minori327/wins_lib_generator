"""
Draft data models for Phase 4 semantic extraction.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DraftSuccessStory:
    """Intermediate extraction result before finalization.

    This is a working draft created by LLM extraction.
    Must reference source RawItem for traceability.
    """
    # Extracted fields (may be incomplete or low confidence)
    customer: str  # Customer name
    context: str  # Business problem or situation
    action: str  # What was done
    outcome: str  # Results achieved
    metrics: List[str]  # Quantifiable impact metrics
    confidence: str  # "high" | "medium" | "low"
    internal_only: bool  # Whether restricted to internal use

    # Optional fields
    tags: List[str] = field(default_factory=list)  # Optional business tags
    industry: str = ""  # Optional industry classification
    team_size: str = ""  # Optional team size category

    # Traceability (REQUIRED)
    source_raw_item_id: str = ""  # ID of RawItem this was extracted from

    # Metadata for processing
    extraction_model: str = ""  # LLM model used for extraction
    extraction_timestamp: str = ""  # When extraction occurred


@dataclass
class ExtractionFailureRecord:
    """Record of failed extraction attempt.

    Used for audit trail and human review.
    """
    raw_item_id: str  # ID of RawItem that failed extraction
    raw_item_filename: str  # Original filename for context
    error_type: str  # "json_parse_error" | "schema_validation" | "llm_failure" | "retry_exhausted"
    error_message: str  # Detailed error message
    raw_response: str  # LLM raw response if applicable
    retry_count: int  # Number of retry attempts
    timestamp: str  # When failure occurred (ISO-8601)
