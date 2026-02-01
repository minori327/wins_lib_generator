"""
Semantic Deduplication Agent for detecting potential duplicate stories.

Performs LLM-based semantic similarity detection and flags duplicates.
Does NOT merge or delete - flagging only.
"""

import logging
from typing import List, Optional
from models.draft_story import DraftSuccessStory
from utils.llm_utils import call_ollama_json

logger = logging.getLogger(__name__)


class DuplicateFlag:
    """Represents a detected potential duplicate relationship."""

    def __init__(
        self,
        primary_index: int,
        duplicate_index: int,
        llm_judgment: str,
        similarity_score: float
    ):
        self.primary_index = primary_index  # Index of primary story
        self.duplicate_index = duplicate_index  # Index of potential duplicate
        self.llm_judgment = llm_judgment  # LLM's explanation
        self.similarity_score = similarity_score  # 0.0 to 1.0 from LLM

    def __repr__(self):
        return (
            f"DuplicateFlag(story[{self.duplicate_index}] -> story[{self.primary_index}], "
            f"similarity={self.similarity_score:.2f}, judgment={self.llm_judgment[:50]}...)"
        )


def llm_duplicate_check(
    story_a: DraftSuccessStory,
    story_b: DraftSuccessStory,
    model: str = "glm-4:9b",
    ollama_base_url: str = "http://localhost:11434"
) -> Optional[DuplicateFlag]:
    """Use LLM to determine if two stories are semantically duplicate.

    Args:
        story_a: First DraftSuccessStory
        story_b: Second DraftSuccessStory
        model: LLM model name
        ollama_base_url: Ollama server URL

    Returns:
        DuplicateFlag if LLM identifies them as duplicates, None otherwise
    """
    prompt = f"""You are analyzing two success stories to determine if they are duplicates.

Story A:
- Customer: {story_a.customer}
- Context: {story_a.context}
- Action: {story_a.action}
- Outcome: {story_a.outcome}
- Metrics: {story_a.metrics}

Story B:
- Customer: {story_b.customer}
- Context: {story_b.context}
- Action: {story_b.action}
- Outcome: {story_b.outcome}
- Metrics: {story_b.metrics}

Task: Determine if these stories describe the same success story.

Criteria for duplicates:
1. Same customer (or very similar customer names)
2. Same business problem (context)
3. Same actions taken
4. Same outcomes achieved

Return a JSON object with exactly these fields:
- is_duplicate: boolean (true if they describe the same story, false otherwise)
- similarity_score: float from 0.0 to 1.0 representing overall similarity
- reasoning: string explaining your judgment (1-2 sentences)

Return ONLY the JSON object, no other text."""

    try:
        response = call_ollama_json(prompt, model, ollama_base_url)

        # Validate response structure
        if not all(key in response for key in ["is_duplicate", "similarity_score", "reasoning"]):
            logger.warning(f"LLM returned invalid response structure: {response}")
            return None

        # Check if LLM identified them as duplicates
        if response.get("is_duplicate") is True:
            similarity = float(response.get("similarity_score", 0.0))
            reasoning = str(response.get("reasoning", ""))

            return DuplicateFlag(
                primary_index=-1,  # Will be set by caller
                duplicate_index=-1,  # Will be set by caller
                llm_judgment=reasoning,
                similarity_score=similarity
            )

        return None

    except Exception as e:
        logger.error(f"LLM duplicate check failed: {e}")
        return None


def detect_semantic_duplicates(
    drafts: List[DraftSuccessStory],
    model: str = "glm-4:9b",
    ollama_base_url: str = "http://localhost:11434"
) -> List[DuplicateFlag]:
    """Detect potential duplicate DraftSuccessStory objects using LLM-based semantic analysis.

    This function FLAGS duplicates only. It does NOT merge or delete.
    Similarity judgment is performed by LLM, not heuristic algorithms.

    Args:
        drafts: List of DraftSuccessStory objects
        model: LLM model name
        ollama_base_url: Ollama server URL

    Returns:
        List of DuplicateFlag objects representing detected duplicate relationships
    """
    if not drafts:
        return []

    flags = []
    checked_pairs = set()

    for i, draft_i in enumerate(drafts):
        for j, draft_j in enumerate(drafts):
            if i >= j:
                continue  # Avoid self-comparison and duplicate pairs

            pair_key = (i, j)
            if pair_key in checked_pairs:
                continue

            # Use LLM to check if they're duplicates
            flag = llm_duplicate_check(draft_i, draft_j, model, ollama_base_url)

            if flag:
                # Set indices in the flag
                flag.primary_index = i
                flag.duplicate_index = j
                flags.append(flag)

                logger.info(
                    f"LLM-flagged duplicate: story[{j}] -> story[{i}] "
                    f"(similarity={flag.similarity_score:.2f}, "
                    f"reasoning: {flag.llm_judgment})"
                )

            checked_pairs.add(pair_key)

    logger.info(
        f"LLM-based semantic deduplication flagged {len(flags)} potential duplicates "
        f"from {len(drafts)} DraftStory objects"
    )

    return flags


def apply_duplicate_flags(
    drafts: List[DraftSuccessStory],
    flags: List[DuplicateFlag]
):
    """Apply duplicate flags to filter out flagged duplicates.

    Returns primary stories and indices of removed duplicates.
    NOTE: This is a helper for orchestration. Phase 4 only flags.

    Args:
        drafts: List of DraftSuccessStory objects
        flags: List of DuplicateFlag objects

    Returns:
        Tuple of (filtered_drafts, removed_indices)
        - filtered_drafts: List of DraftStory objects with duplicates removed
        - removed_indices: List of indices that were removed
    """
    if not flags:
        return drafts, []

    # Collect indices to remove (duplicates only, not primaries)
    indices_to_remove = set(flag.duplicate_index for flag in flags)

    # Filter out duplicates
    filtered = [
        draft for i, draft in enumerate(drafts)
        if i not in indices_to_remove
    ]

    removed = sorted(indices_to_remove)

    logger.info(
        f"Applied duplicate flags: removed {len(removed)} stories, "
        f"kept {len(filtered)} from {len(drafts)} total"
    )

    return filtered, removed
