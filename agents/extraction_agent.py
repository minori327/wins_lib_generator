"""
Extract SuccessStory objects from RawItem list using LLM.
"""

from typing import List
from models.raw_item import RawItem
from models.library import SuccessStory


def extract_success_stories(raw_items: List[RawItem], ollama_base_url: str = "http://localhost:11434", model: str = "glm-4:9b") -> List[SuccessStory]:
    """TODO: Extract SuccessStory objects from RawItem list using LLM."""
    pass
