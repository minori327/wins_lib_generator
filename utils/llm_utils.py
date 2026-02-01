"""
Wrapper around Ollama API for LLM calls.
"""

from typing import Dict, Any


def call_ollama(prompt: str, model: str = "glm-4:9b", ollama_base_url: str = "http://localhost:11434") -> str:
    """TODO: Call Ollama API and get response."""
    pass


def call_ollama_json(prompt: str, model: str = "glm-4:9b", ollama_base_url: str = "http://localhost:11434") -> Dict[str, Any]:
    """TODO: Call Ollama API and parse JSON response."""
    pass
