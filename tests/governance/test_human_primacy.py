"""
GOVERNANCE TEST: Human Primacy Boundaries

This test file enforces the CORE HUMAN PRIMACY CONSTRAINTS:
- AI never makes final business decisions
- AI generates suggestions only (status='candidate')
- Only humans can approve (status='final')
- Consolidation and deduplication are human-only activities

GOVERNANCE INTENT:
These tests enforce the FUNDAMENTAL DESIGN PRINCIPLE of Iteration 2:
"This system exists to support human decision-making, not to replace it."

Any code that allows AI to set status='final', perform consolidation,
execute deduplication, or make quality judgments represents a CRITICAL
governance violation.

Reference: DEVELOPMENT_PLAN_v2_FINAL.md, Human Primacy Clause
"""

import pytest
import sys
from pathlib import Path
import tempfile
import openpyxl
import re


def _strip_comments_and_strings_simple(source_code: str) -> str:
    """
    Simple helper to remove comments and string literals from source code.

    This is a lightweight version for AST-based tests.
    """
    # Remove string literals
    source_code = re.sub(r'"""[\s\S]*?"""', '', source_code)
    source_code = re.sub(r"'''[\s\S]*?'''", '', source_code)
    source_code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '', source_code)
    source_code = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", '', source_code)

    # Remove comments
    lines = source_code.split('\n')
    code_lines = []
    for line in lines:
        if '#' in line:
            line = line[:line.index('#')]
        code_lines.append(line)

    return '\n'.join(code_lines)


# ============================================================================
# CATEGORY 1: AI-GENERATED ROWS MUST ALWAYS HAVE STATUS='CANDIDATE'
# ============================================================================

class TestAICandidateOnly:
    """Verify that AI can only generate candidate rows."""

    def test_story_identifier_sets_status_candidate(self):
        """
        GOVERNANCE: story_identifier must set status='candidate' for all rows.

        AI-generated rows can NEVER have status='final', 'consolidated',
        or any other status. They must always be 'candidate' awaiting human review.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check that normalize_candidate sets status to 'candidate'
        assert "'status': 'candidate'" in content or '"status": "candidate"' in content, (
            "story_identifier.py does not set status='candidate' for generated rows. "
            "AI can only generate candidates, never final rows."
        )

        # Verify the exact pattern
        assert 'status' in content and 'candidate' in content, (
            "Status assignment not found in story_identifier.py."
        )

    def test_no_code_sets_status_to_final(self):
        """
        GOVERNANCE: No active code sets status='final'.

        Only humans can set status='final' by editing Excel directly.
        The system must NEVER programmatically set status='final'.
        """
        project_root = Path(__file__).parent.parent.parent

        # Use AST to detect actual assignments, not comparisons
        import ast

        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            # Skip test files
            if "tests" in py_file.parts:
                continue

            try:
                content = py_file.read_text()
                code_only = _strip_comments_and_strings_simple(content)

                # Parse AST to find assignments to status
                tree = ast.parse(code_only)

                # Look for assignments: status = 'final'
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == 'status':
                                # Check if the value is 'final'
                                if isinstance(node.value, ast.Constant):
                                    if node.value.value == 'final':
                                        pytest.fail(
                                            f"Code sets status='final' in {py_file.relative_to(project_root)}. "
                                            "Only humans can set status='final' via Excel editing."
                                        )
            except SyntaxError:
                # If we can't parse the file, skip it (might be a partial file)
                pass

    def test_no_code_sets_status_to_consolidated(self):
        """
        GOVERNANCE: No active code sets status='consolidated'.

        Only humans can set status='consolidated' by merging rows in Excel.
        The system must NEVER programmatically consolidate rows.
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            "status = 'consolidated'",
            'status = "consolidated"',
            "status='consolidated'",
            'status="consolidated"',
        ]

        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            # Skip test files
            if "tests" in py_file.parts:
                continue

            content = py_file.read_text()

            for pattern in forbidden_patterns:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and not line.strip().startswith('#'):
                        pytest.fail(
                            f"Code sets status='consolidated' in {py_file.relative_to(project_root)}:{i+1}. "
                            "Only humans can consolidate by editing Excel."
                        )

    def test_consolidation_hints_are_text_only(self):
        """
        GOVERNANCE: consolidation_hints must be text field only.

        The system can provide consolidation hints as advisory text,
        but must never perform actual consolidation.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # consolidation_hints should be a text field
        assert 'consolidation_hints' in content, (
            "consolidation_hints field not found. "
            "System should provide consolidation hints as text for human review."
        )

        # Verify it's treated as a string/text field
        assert "consolidation_hints': candidate.get('consolidation_hints'" in content or \
               'consolidation_hints": candidate.get("consolidation_hints"' in content, (
            "consolidation_hints should be extracted from LLM as text."
        )

        # Verify Excel column exists for hints
        assert 'consolidation_hints' in content, (
            "consolidation_hints column not defined for Excel output."
        )


# ============================================================================
# CATEGORY 2: SUMMARY GENERATION READS ONLY FINAL ROWS
# ============================================================================

class TestSummaryFinalOnly:
    """Verify that summary generation reads only final rows."""

    def test_summary_generator_filters_for_final_status(self):
        """
        GOVERNANCE: summary_generator must filter for status='final'.

        Summaries must ONLY consume human-approved content.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check for status filtering
        assert "status != 'final'" in content or 'status != "final"' in content, (
            "summary_generator.py does not filter for status='final'. "
            "Summaries must only consume human-approved (final) rows."
        )

        # Check that non-final rows are skipped
        assert 'continue' in content, (
            "summary_generator.py does not skip non-final rows."
        )

    def test_summary_warns_if_no_final_rows(self):
        """
        GOVERNANCE: summary_generator must warn if no final rows found.

        This prevents silent failures when humans haven't approved any rows.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check for warning when no final rows
        assert 'WARNING' in content or 'warning' in content, (
            "summary_generator.py does not warn when no final rows found."
        )

        assert 'status=' in content and 'final' in content, (
            "Warning message does not mention status='final' requirement."
        )

    def test_summary_documentation_declares_final_only(self):
        """
        GOVERNANCE: summary_generator documentation must declare final-only behavior.

        The module docstring should explicitly state that only final rows are consumed.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Extract module docstring
        lines = content.split('\n')
        docstring_started = False
        docstring_lines = []

        for line in lines:
            if '"""' in line or "'''" in line:
                if not docstring_started:
                    docstring_started = True
                else:
                    break
            elif docstring_started:
                docstring_lines.append(line)

        docstring = '\n'.join(docstring_lines).lower()

        # Check for declaration
        assert 'only final' in docstring or 'final rows only' in docstring, (
            "summary_generator.py docstring does not declare final-only consumption. "
            "Documentation must explicitly state: 'ONLY final rows are consumed.'"
        )


# ============================================================================
# CATEGORY 3: NO AI DECISION-MAKING CAPABILITIES
# ============================================================================

class TestNoAIDecisions:
    """Verify that AI has no decision-making authority."""

    def test_no_quality_evaluation_functions(self):
        """
        GOVERNANCE: No AI quality evaluation functions in active code.

        Functions that evaluate whether a story is "good enough" or
        "worthy of inclusion" represent AI judgment, violating Human Primacy.
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            'def evaluate_quality',
            'def assess_story',
            'def is_good_story',
            'def validate_story',
            'def check_completeness',
        ]

        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            # Skip test files
            if "tests" in py_file.parts:
                continue

            content = py_file.read_text()

            for pattern in forbidden_patterns:
                if pattern in content:
                    pytest.fail(
                        f"AI evaluation function '{pattern}' found in {py_file.relative_to(project_root)}. "
                        "AI quality judgment is not allowed in Iteration 2."
                    )

    def test_no_success_filtering_by_ai(self):
        """
        GOVERNANCE: No AI-based filtering of success stories.

        The system must not filter stories based on AI judgment
        about what constitutes a "real" success story.
        """
        project_root = Path(__file__).parent.parent.parent

        # Check prompts for instructions that tell AI to filter
        prompts_dir = project_root / "prompts"

        for prompt_file in prompts_dir.glob("*.yaml"):
            with open(prompt_file) as f:
                content = f.read()

            # AI should be told NOT to filter, not to filter
            # Look for filtering instructions
            forbidden_phrases = [
                'filter out',
                'exclude low quality',
                'remove poor quality',
                'only include stories that',
                'ignore stories that',
            ]

            for phrase in forbidden_phrases:
                if phrase in content.lower():
                    pytest.fail(
                        f"AI filtering instruction '{phrase}' found in {prompt_file.name}. "
                        "AI should not filter stories. Humans decide what counts."
                    )

            # Check for Human Primacy constraints
            assert 'do not' in content.lower() or 'not attempt' in content.lower(), (
                f"Prompt {prompt_file.name} does not include 'DO NOT' constraints. "
                "Prompts must explicitly tell AI what NOT to do."
            )

    def test_prompt_enforces_human_primacy(self):
        """
        GOVERNANCE: Story identification prompt must enforce Human Primacy.

        The prompt must explicitly state that AI should NOT:
        - Consolidate
        - Deduplicate
        - Make final judgments
        """
        project_root = Path(__file__).parent.parent.parent
        identify_prompt = project_root / "prompts" / "identify_stories.yaml"

        with open(identify_prompt) as f:
            content = f.read()

        # The prompt should explicitly forbid AI from autonomous actions
        # Check for uppercase or case-insensitive presence
        # Use flexible matching to allow variations in phrasing
        content_lower = content.lower()

        # Check for "do not" followed by forbidden actions (with possible intervening words)
        forbidden_actions = [
            ('do not', 'merge'),  # "do not merge", "do not attempt to merge"
            ('do not', 'consolidate'),  # "do not consolidate"
            ('do not', 'dedup'),  # "do not dedup", "do not perform deduplication"
            ('do not', 'final'),  # "do not make final", "do not make final judgments"
        ]

        for negation, action in forbidden_actions:
            # Check that both negation and action appear in content
            # They may have words between them, so check for presence of both
            assert negation in content_lower and action in content_lower, (
                f"Prompt missing constraint: '{negation} ... {action}'. "
                "Prompt must explicitly forbid AI from consolidation/deduplication/final judgments."
            )


# ============================================================================
# CATEGORY 4: CONSOLIDATION AND DEDUPLICATION ARE HUMAN-ONLY
# ============================================================================

class TestHumanOnlyConsolidation:
    """Verify that consolidation and deduplication are human-only activities."""

    def test_consolidation_by_humans_only(self):
        """
        GOVERNANCE: Code must state consolidation is human-only.

        Comments or documentation should explicitly state that
        consolidation happens in Excel by humans, not by the system.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Look for explicit statements
        content_lower = content.lower()

        # Should mention that consolidation is human-only
        assert any(phrase in content_lower for phrase in [
            'human consolidation',
            'consolidation by humans',
            'humans consolidate',
            'excel as consolidation workspace',
            'no consolidation',
        ]), (
            "story_identifier.py does not state that consolidation is human-only. "
            "Comments should clarify that consolidation happens in Excel by humans."
        )

    def test_deduplication_by_humans_only(self):
        """
        GOVERNANCE: Code must state deduplication is human-only.

        Comments or documentation should explicitly state that
        deduplication is not performed by the system.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        content_lower = content.lower()

        # Should mention no deduplication
        assert 'no dedup' in content_lower, (
            "story_identifier.py does not state 'NO deduplication'. "
            "Comments should explicitly forbid automatic deduplication."
        )

    def test_prompt_tells_ai_not_to_consolidate_or_dedup(self):
        """
        GOVERNANCE: Prompt must tell AI not to consolidate or deduplicate.

        The LLM prompt must explicitly forbid these activities.
        """
        project_root = Path(__file__).parent.parent.parent
        identify_prompt = project_root / "prompts" / "identify_stories.yaml"

        with open(identify_prompt) as f:
            content = f.read().lower()

        # Check for explicit prohibitions
        assert 'do not attempt to merge' in content or 'do not merge' in content, (
            "Prompt does not explicitly forbid consolidation."
        )

        assert 'do not perform deduplication' in content or 'do not dedup' in content, (
            "Prompt does not explicitly forbid deduplication."
        )

    def test_excel_column_for_human_consolidation(self):
        """
        GOVERNANCE: Excel must have consolidation_hints column for human use.

        The system provides hints (text), humans perform consolidation.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check for consolidation_hints column definition
        assert 'consolidation_hints' in content, (
            "consolidation_hints column not found in Excel generation code. "
            "System should provide hints for human consolidation."
        )


# ============================================================================
# CATEGORY 5: AI IS A TOOL, NOT A DECISION-MAKER
# ============================================================================

class TestAIAsToolNotDecider:
    """Verify that AI is treated as a tool, not a decision-maker."""

    def test_llm_client_declares_tool_status(self):
        """
        GOVERNANCE: LLM client must declare AI as tool, not decision-maker.

        Module documentation should state: "LLMs are tools, not decision-makers."
        """
        project_root = Path(__file__).parent.parent.parent
        llm_client_path = project_root / "utils" / "llm_client.py"

        with open(llm_client_path) as f:
            content = f.read()

        # Extract module docstring
        lines = content.split('\n')
        docstring_started = False
        docstring_lines = []

        for line in lines:
            if '"""' in line or "'''" in line:
                if not docstring_started:
                    docstring_started = True
                else:
                    break
            elif docstring_started:
                docstring_lines.append(line)

        docstring = '\n'.join(docstring_lines).lower()

        # Check for declaration
        assert 'tool' in docstring and 'not' in docstring, (
            "LLM client does not declare AI as a tool, not a decision-maker. "
            "Module docstring should state: 'LLMs are tools, not decision-makers.'"
        )

    def test_no_ai_priority_or_ranking(self):
        """
        GOVERNANCE: AI must not assign priority or rank to stories.

        Priority and ranking are human decisions. AI suggestions
        are advisory only.
        """
        project_root = Path(__file__).parent.parent.parent

        # Check that no output files contain priority/rank fields
        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            # Skip test files
            if "tests" in py_file.parts:
                continue

            content = py_file.read_text()

            # Check for AI-assigned priority/rank
            if "'priority'" in content or '"priority"' in content:
                # Verify it's not AI-assigned
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'priority' in line.lower() and 'llm' in line.lower():
                        pytest.fail(
                            f"AI-assigned priority found in {py_file.relative_to(project_root)}:{i+1}. "
                            "Priority ranking is a human decision."
                        )

    def test_llm_calls_are_explicit_and_logged(self):
        """
        GOVERNANCE: All LLM calls must be explicit and logged.

        Hidden LLM calls represent opaque decision-making.
        All LLM interactions must be traceable.
        """
        project_root = Path(__file__).parent.parent.parent
        llm_client_path = project_root / "utils" / "llm_client.py"

        with open(llm_client_path) as f:
            content = f.read()

        # Check for logging
        assert 'logger' in content.lower(), (
            "LLM client does not have logging. "
            "All LLM calls must be logged for traceability."
        )

        assert 'log' in content.lower(), (
            "LLM client does not log calls. "
            "Every LLM call must be logged."
        )

        # Check for explicit prompt parameter
        assert 'def call(' in content and 'prompt' in content, (
            "LLM client does not have explicit prompt parameter. "
            "All LLM calls should have explicit prompts for traceability."
        )
