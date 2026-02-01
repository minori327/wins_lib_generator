#!/usr/bin/env python3
"""
LLM Client Wrapper v2.0 - Offline Only

This module provides a wrapper for local LLM calls via Ollama.
All LLM calls are offline, explicit, and logged.

Human Primacy: LLMs are tools, not decision-makers.
"""

import logging
import requests
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml


logger = logging.getLogger(__name__)


class LLMClient:
    """Offline LLM client using Ollama.

    Enforces offline-only operations. All calls are logged.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize LLM client from config.

        Args:
            config: Configuration dictionary with llm section

        Raises:
            ValueError: If config tries to use non-Ollama backend
        """
        self.backend = config["llm"]["backend"]

        # Enforce offline-only
        if self.backend != "ollama":
            raise ValueError(
                f"Iteration 2 REQUIRES offline-only LLM. "
                f"Backend '{self.backend}' is not allowed. "
                f"Only 'ollama' is supported."
            )

        self.base_url = config["llm"]["base_url"]
        self.model = config["llm"]["model"]
        self.temperature = config["llm"].get("temperature", 0.3)
        self.max_tokens = config["llm"].get("max_tokens", 2000)
        self.timeout = config["llm"].get("timeout_seconds", 120)

        logger.info(f"[LLMClient] Initialized with backend={self.backend}, model={self.model}")

    def call(
        self,
        prompt: str,
        output_format: str = "text",
        system_prompt: Optional[str] = None
    ) -> str:
        """Call LLM with a prompt.

        Args:
            prompt: The prompt to send
            output_format: Expected output format ("text", "json", "markdown")
            system_prompt: Optional system prompt

        Returns:
            LLM response as string

        Raises:
            RuntimeError: If LLM call fails
        """
        logger.info(f"[LLMClient] Calling LLM...")
        logger.info(f"[LLMClient] Prompt length: {len(prompt)} characters")
        logger.info(f"[LLMClient] Expected output format: {output_format}")

        # Build request
        url = f"{self.base_url}/api/generate"

        # Add system prompt if provided
        full_prompt = prompt
        if system_prompt:
            # Ollama uses a specific format for system prompts
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        # Call LLM
        try:
            logger.debug(f"[LLMClient] Sending request to {url}")
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

        except requests.exceptions.Timeout:
            error_msg = f"LLM call timeout after {self.timeout}s"
            logger.error(f"[LLMClient] {error_msg}")
            raise RuntimeError(error_msg)

        except requests.exceptions.ConnectionError:
            error_msg = (
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Ensure Ollama is running with: ollama serve"
            )
            logger.error(f"[LLMClient] {error_msg}")
            raise RuntimeError(error_msg)

        except requests.exceptions.HTTPError as e:
            error_msg = f"LLM HTTP error: {e}"
            logger.error(f"[LLMClient] {error_msg}")
            raise RuntimeError(error_msg)

        # Parse response
        try:
            data = response.json()
            result = data.get("response", "")

            if not result:
                raise RuntimeError("LLM returned empty response")

            logger.info(f"[LLMClient] Response length: {len(result)} characters")
            logger.debug(f"[LLMClient] Response preview: {result[:200]}...")

            return result

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse LLM response as JSON: {e}"
            logger.error(f"[LLMClient] {error_msg}")
            raise RuntimeError(error_msg)

    def call_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Call LLM expecting JSON output.

        Args:
            prompt: The prompt to send
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON dictionary

        Raises:
            RuntimeError: If LLM call fails or returns invalid JSON
        """
        # Add JSON instruction to prompt
        json_prompt = prompt + "\n\nOutput valid JSON only."

        response = self.call(json_prompt, output_format="json", system_prompt=system_prompt)

        # Try to parse JSON
        try:
            # Extract JSON from response (in case there's extra text)
            response = response.strip()

            # Find JSON object boundaries
            start_idx = response.find("{")
            end_idx = response.rfind("}")

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx + 1]
            else:
                # Try array
                start_idx = response.find("[")
                end_idx = response.rfind("]")
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx + 1]
                else:
                    json_str = response

            data = json.loads(json_str)
            logger.info(f"[LLMClient] Parsed JSON response with keys: {list(data.keys())}")
            return data

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON from LLM response: {e}\nResponse: {response[:500]}"
            logger.error(f"[LLMClient] {error_msg}")
            raise RuntimeError(error_msg)


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load system configuration.

    Args:
        config_path: Path to config.yaml

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def create_llm_client(config_path: str = "config/config.yaml") -> LLMClient:
    """Create LLM client from config file.

    Args:
        config_path: Path to config.yaml

    Returns:
        Initialized LLMClient
    """
    config = load_config(config_path)
    return LLMClient(config)
