"""
Wrapper around Ollama API for LLM calls.
"""

import json
import logging
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)


def call_ollama(
    prompt: str,
    model: str = "glm-4:9b",
    ollama_base_url: str = "http://localhost:11434"
) -> str:
    """Call Ollama API and get text response.

    Args:
        prompt: Prompt string to send to LLM
        model: Model name (default: "glm-4:9b")
        ollama_base_url: Ollama server URL

    Returns:
        LLM response text

    Raises:
        ValueError: If API call fails or returns empty response
        requests.ConnectionError: If cannot connect to Ollama server
    """
    url = f"{ollama_base_url}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        result = data.get("response", "")

        if not result:
            logger.error(f"Empty response from Ollama for model {model}")
            raise ValueError(f"Empty response from Ollama model {model}")

        logger.debug(f"Ollama call successful: {len(result)} characters returned")

        return result

    except requests.ConnectionError as e:
        logger.error(f"Failed to connect to Ollama at {ollama_base_url}: {e}")
        raise
    except requests.Timeout as e:
        logger.error(f"Ollama request timed out: {e}")
        raise ValueError(f"Ollama request timed out: {e}")
    except requests.HTTPError as e:
        logger.error(f"Ollama HTTP error: {e}")
        raise ValueError(f"Ollama HTTP error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error calling Ollama: {e}")
        raise ValueError(f"Failed to call Ollama: {e}")


def call_ollama_json(
    prompt: str,
    model: str = "glm-4:9b",
    ollama_base_url: str = "http://localhost:11434"
) -> Dict[str, Any]:
    """Call Ollama API and parse JSON response.

    Args:
        prompt: Prompt string to send to LLM (must request JSON output)
        model: Model name (default: "glm-4:9b")
        ollama_base_url: Ollama server URL

    Returns:
        Parsed JSON dictionary

    Raises:
        ValueError: If API call fails, returns non-JSON, or JSON is invalid
        requests.ConnectionError: If cannot connect to Ollama server
    """
    try:
        response_text = call_ollama(prompt, model, ollama_base_url)

        # Attempt to parse JSON from response
        try:
            parsed = json.loads(response_text)
            logger.debug("Successfully parsed JSON response from Ollama")
            return parsed

        except json.JSONDecodeError as e:
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                # Extract content between ```json and ```
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    json_str = response_text[start:end].strip()
                    parsed = json.loads(json_str)
                    logger.debug("Extracted and parsed JSON from markdown code block")
                    return parsed

            # Try extracting from ``` without json label
            if "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                if end != -1:
                    # Check if next word is "json"
                    block_content = response_text[start:end].strip()
                    if block_content.startswith("json"):
                        block_content = block_content[4:].strip()
                    json_str = block_content
                    parsed = json.loads(json_str)
                    logger.debug("Extracted and parsed JSON from generic code block")
                    return parsed

            # All parsing attempts failed
            logger.error(f"Failed to parse JSON from Ollama response: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            raise ValueError(f"Failed to parse JSON from Ollama response: {e}")

    except ValueError:
        # Re-raise ValueError from call_ollama or JSON parsing
        raise
    except Exception as e:
        logger.error(f"Unexpected error in call_ollama_json: {e}")
        raise ValueError(f"Failed to get JSON response from Ollama: {e}")
