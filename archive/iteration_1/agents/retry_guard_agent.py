"""
Retry & Guard Agent for LLM extraction with schema validation.

Handles JSON parsing, schema validation, and controlled retry logic.
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from models.draft_story import DraftSuccessStory, ExtractionFailureRecord
from utils.llm_utils import call_ollama_json

logger = logging.getLogger(__name__)


# Schema for DraftSuccessStory JSON validation
DRAFT_SCHEMA_REQUIRED = [
    "customer", "context", "action", "outcome",
    "metrics", "confidence", "internal_only"
]

DRAFT_SCHEMA_OPTIONAL = [
    "tags", "industry", "team_size"
]


def validate_draft_schema(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate dictionary against DraftSuccessStory schema.

    Args:
        data: Dictionary to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid, False otherwise
        - error_message: None if valid, error description otherwise
    """
    # Check required fields
    missing = [field for field in DRAFT_SCHEMA_REQUIRED if field not in data]
    if missing:
        return False, f"Missing required fields: {missing}"

    # Validate customer is non-empty string
    if not isinstance(data.get("customer"), str) or not data["customer"].strip():
        return False, "Field 'customer' must be a non-empty string"

    # Validate context is non-empty string
    if not isinstance(data.get("context"), str) or not data["context"].strip():
        return False, "Field 'context' must be a non-empty string"

    # Validate action is non-empty string
    if not isinstance(data.get("action"), str) or not data["action"].strip():
        return False, "Field 'action' must be a non-empty string"

    # Validate outcome is non-empty string
    if not isinstance(data.get("outcome"), str) or not data["outcome"].strip():
        return False, "Field 'outcome' must be a non-empty string"

    # Validate metrics is list
    if not isinstance(data.get("metrics"), list):
        return False, "Field 'metrics' must be a list"

    # Validate confidence is one of allowed values
    valid_confidence = ["high", "medium", "low"]
    if data.get("confidence") not in valid_confidence:
        return False, f"Field 'confidence' must be one of {valid_confidence}"

    # Validate internal_only is boolean
    if not isinstance(data.get("internal_only"), bool):
        return False, "Field 'internal_only' must be a boolean"

    # Validate optional fields if present
    if "tags" in data and not isinstance(data["tags"], list):
        return False, "Field 'tags' must be a list if present"

    if "industry" in data and not isinstance(data["industry"], str):
        return False, "Field 'industry' must be a string if present"

    if "team_size" in data and not isinstance(data["team_size"], str):
        return False, "Field 'team_size' must be a string if present"

    return True, None


def extract_with_retry(
    prompt: str,
    raw_item_id: str,
    raw_item_filename: str,
    model: str = "glm-4:9b",
    ollama_base_url: str = "http://localhost:11434",
    max_retries: int = 2
) -> Tuple[Optional[DraftSuccessStory], Optional[ExtractionFailureRecord]]:
    """Extract DraftSuccessStory using LLM with retry logic.

    Args:
        prompt: Extraction prompt (must request JSON output)
        raw_item_id: ID of RawItem being processed (for traceability)
        raw_item_filename: Filename for error records
        model: LLM model name
        ollama_base_url: Ollama server URL
        max_retries: Maximum retry attempts (default: 2)

    Returns:
        Tuple of (draft_story, failure_record)
        - draft_story: DraftSuccessStory if successful, None otherwise
        - failure_record: ExtractionFailureRecord if failed, None otherwise
    """
    retry_count = 0
    last_error = None
    last_raw_response = ""

    while retry_count <= max_retries:
        try:
            # Call LLM
            response_data = call_ollama_json(prompt, model, ollama_base_url)
            last_raw_response = json.dumps(response_data)

            # Validate schema
            is_valid, error_msg = validate_draft_schema(response_data)

            if not is_valid:
                last_error = f"Schema validation failed: {error_msg}"

                if retry_count < max_retries:
                    # Retry with format correction request
                    logger.warning(
                        f"Schema validation failed for {raw_item_id} "
                        f"(attempt {retry_count + 1}/{max_retries + 1}): {error_msg}"
                    )

                    # Create correction prompt
                    correction_prompt = f"""The previous JSON extraction had schema errors:

{error_msg}

Previous response:
{json.dumps(response_data, indent=2)}

Please correct the JSON to match the required schema. Ensure all required fields are present with correct types.
Return ONLY the corrected JSON, no other text."""

                    prompt = correction_prompt
                    retry_count += 1
                    continue
                else:
                    # All retries exhausted
                    logger.error(
                        f"Schema validation failed for {raw_item_id} after {max_retries + 1} attempts: {error_msg}"
                    )
                    failure_record = ExtractionFailureRecord(
                        raw_item_id=raw_item_id,
                        raw_item_filename=raw_item_filename,
                        error_type="schema_validation",
                        error_message=last_error,
                        raw_response=last_raw_response,
                        retry_count=retry_count,
                        timestamp=datetime.utcnow().isoformat() + "Z"
                    )
                    return None, failure_record

            # Schema validation passed - construct DraftSuccessStory
            draft = DraftSuccessStory(
                customer=response_data["customer"].strip(),
                context=response_data["context"].strip(),
                action=response_data["action"].strip(),
                outcome=response_data["outcome"].strip(),
                metrics=response_data["metrics"],
                confidence=response_data["confidence"],
                internal_only=response_data["internal_only"],
                tags=response_data.get("tags", []),
                industry=response_data.get("industry", ""),
                team_size=response_data.get("team_size", ""),
                source_raw_item_id=raw_item_id,
                extraction_model=model,
                extraction_timestamp=datetime.utcnow().isoformat() + "Z"
            )

            logger.info(f"Successfully extracted DraftSuccessStory from {raw_item_id}")

            return draft, None

        except ValueError as e:
            # JSON parsing or LLM call failed
            last_error = str(e)
            last_raw_response = getattr(e, 'response_text', '')

            if retry_count < max_retries:
                logger.warning(
                    f"LLM extraction failed for {raw_item_id} "
                    f"(attempt {retry_count + 1}/{max_retries + 1}): {e}"
                )
                retry_count += 1
                continue
            else:
                logger.error(
                    f"LLM extraction failed for {raw_item_id} after {max_retries + 1} attempts: {e}"
                )
                failure_record = ExtractionFailureRecord(
                    raw_item_id=raw_item_id,
                    raw_item_filename=raw_item_filename,
                    error_type="llm_failure",
                    error_message=last_error,
                    raw_response=last_raw_response,
                    retry_count=retry_count,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
                return None, failure_record

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error during extraction for {raw_item_id}: {e}")
            failure_record = ExtractionFailureRecord(
                raw_item_id=raw_item_id,
                raw_item_filename=raw_item_filename,
                error_type="llm_failure",
                error_message=f"Unexpected error: {str(e)}",
                raw_response="",
                retry_count=retry_count,
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            return None, failure_record

    # Should not reach here, but handle gracefully
    failure_record = ExtractionFailureRecord(
        raw_item_id=raw_item_id,
        raw_item_filename=raw_item_filename,
        error_type="retry_exhausted",
        error_message=last_error or "Retry exhausted without specific error",
        raw_response=last_raw_response,
        retry_count=retry_count,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    return None, failure_record
