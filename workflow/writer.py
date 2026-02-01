"""
Write Markdown files to Obsidian vault.
"""

from typing import List
from pathlib import Path
from models.library import SuccessStory


def write_success_story_note(story: SuccessStory, output_path: Path, template_path: Path) -> None:
    """TODO: Write SuccessStory as Markdown note to explicit output path."""
    pass


def write_weekly_summary(stories: List[SuccessStory], output_path: Path, template_path: Path, week_str: str) -> None:
    """TODO: Write weekly summary Markdown file to explicit output path."""
    pass
