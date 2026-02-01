"""
Extract SuccessStory objects from RawItem list using LLM.
"""

import logging
from typing import List, Tuple
from models.raw_item import RawItem
from models.draft_story import DraftSuccessStory, ExtractionFailureRecord
from agents.retry_guard_agent import extract_with_retry

logger = logging.getLogger(__name__)

# Extraction prompt template
EXTRACTION_PROMPT_TEMPLATE = """You are extracting a success story from raw text.

Analyze the following text and extract a success story in JSON format.

Source: {source_type}
Filename: {filename}
Country: {country}
Month: {month}

Text content:
{text}

Extract the following fields:
- customer: Customer name (string, required)
- context: Business problem or situation (string, required)
- action: What was done to address the problem (string, required)
- outcome: Results achieved (string, required)
- metrics: List of quantifiable impact metrics (array of strings, required)
- confidence: Your confidence in the extraction accuracy, either "high", "medium", or "low" (string, required)
- internal_only: Whether this story should be restricted to internal use only (boolean, required)
- tags: Optional business tags (array of strings, optional)
- industry: Optional industry classification (string, optional)
- team_size: Optional team size category (string, optional)

IMPORTANT:
1. Return ONLY valid JSON, no other text
2. All string fields must be non-empty
3. metrics must be an array (can be empty if no metrics found)
4. confidence must be exactly "high", "medium", or "low"
5. If insufficient information to extract a meaningful success story, set all fields to placeholder values and confidence to "low"
6. internal_only should be true only if the text explicitly mentions confidentiality or internal-only information

JSON response:
"""


def extract_from_raw_item(
    raw_item: RawItem,
    model: str = "glm-4:9b",
    ollama_base_url: str = "http://localhost:11434"
) -> Tuple[DraftSuccessStory, None] | Tuple[None, ExtractionFailureRecord]:
    """Extract single DraftSuccessStory from RawItem using LLM.

    Args:
        raw_item: RawItem to extract from
        model: LLM model name
        ollama_base_url: Ollama server URL

    Returns:
        Tuple of (draft_story, None) on success, or (None, failure_record) on failure
    """
    logger.info(f"Extracting from RawItem: {raw_item.id}")

    # Build extraction prompt
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        source_type=raw_item.source_type,
        filename=raw_item.filename,
        country=raw_item.country,
        month=raw_item.month,
        text=raw_item.text
    )

    # Use retry guard agent to extract with retry logic
    draft_story, failure_record = extract_with_retry(
        prompt=prompt,
        raw_item_id=raw_item.id,
        raw_item_filename=raw_item.filename,
        model=model,
        ollama_base_url=ollama_base_url,
        max_retries=2
    )

    return draft_story, failure_record


def extract_success_stories(
    raw_items: List[RawItem],
    model: str = "glm-4:9b",
    ollama_base_url: str = "http://localhost:11434"
) -> Tuple[List[DraftSuccessStory], List[ExtractionFailureRecord]]:
    """Extract DraftSuccessStory objects from RawItem list using LLM.

    Args:
        raw_items: List of RawItem objects
        model: LLM model name
        ollama_base_url: Ollama server URL

    Returns:
        Tuple of (draft_stories, failure_records)
        - draft_stories: List of successfully extracted DraftSuccessStory objects
        - failure_records: List of ExtractionFailureRecord objects for failed extractions
    """
    if not raw_items:
        logger.info("No RawItems to extract from")
        return [], []

    draft_stories = []
    failure_records = []

    for raw_item in raw_items:
        draft_story, failure_record = extract_from_raw_item(raw_item, model, ollama_base_url)

        if draft_story:
            draft_stories.append(draft_story)
        elif failure_record:
            failure_records.append(failure_record)

    logger.info(
        f"Extraction complete: {len(draft_stories)} successful, "
        f"{len(failure_records)} failed from {len(raw_items)} RawItems"
    )

    return draft_stories, failure_records
