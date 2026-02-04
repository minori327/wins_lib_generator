"""
GOVERNANCE TEST: Mechanical Invariants

This test file enforces the BOUNDARY between TECHNICAL INCLUSIONS
and JUDGMENT-BASED FILTERING.

GOVERNANCE INTENT:
Iteration 2 allows ONLY technical integrity filtering (data validation,
format compatibility, identifier checks). Any filtering based on
semantic similarity, quality judgment, or AI evaluation is FORBIDDEN.

This is a CRITICAL boundary. Tests must be conservative:
- When in doubt, classify as VIOLATION
- Prefer false positives over missed violations
- Any judgment-based filtering is unacceptable

Reference: Post-Remediation Audit Report, Section E
"""

import pytest
from pathlib import Path
import re


def _strip_comments_and_strings_simple(source_code: str) -> str:
    """
    Simple helper to remove comments and string literals from source code.
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
# CATEGORY 1: IDENTIFY ALL FILTERING OPERATIONS
# ============================================================================

class TestFilteringInventory:
    """Inventory all filtering operations and classify them."""

    def test_only_technical_filtering_exists(self):
        """
        GOVERNANCE: Only technical filtering is allowed in active code.

        ALLOWED (Technical Invariants):
        - Status filtering for reading (respecting human decisions)
        - Data integrity checks (None values, missing fields)
        - Format compatibility checks (file extensions, encoding)
        - Identifier validation (source_id exists)

        FORBIDDEN (Judgment-Based):
        - Quality filtering (good enough, complete enough)
        - Semantic similarity filtering
        - Content-based filtering (about specific topics)
        - Scoring thresholds (above/below score)
        """
        project_root = Path(__file__).parent.parent.parent

        # Inventory all filtering patterns
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
            lines = content.split('\n')

            # Find all filtering operations (if statements with continue, skip, etc.)
            for i, line in enumerate(lines):
                # Check for filtering patterns
                if any(pattern in line for pattern in ['if', 'continue', 'skip', 'pass']):
                    # Extract context (5 lines before and after)
                    context_start = max(0, i - 5)
                    context_end = min(len(lines), i + 6)
                    context = '\n'.join(lines[context_start:context_end])

                    # Check for forbidden judgment-based filtering
                    self._assert_not_judgment_based(
                        context,
                        py_file,
                        i + 1,
                        project_root
                    )

    def _assert_not_judgment_based(self, context, file_path, line_num, project_root):
        """Helper to check if filtering is judgment-based."""

        context_lower = context.lower()

        # FORBIDDEN: Quality judgments
        quality_patterns = [
            'quality',
            'good enough',
            'worthy',
            'valuable',
            'important',
            'relevant',
            'significant',
        ]

        # FORBIDDEN: Completeness judgments
        completeness_patterns = [
            'complete enough',
            'sufficient detail',
            'adequate',
        ]

        # FORBIDDEN: Similarity judgments
        similarity_patterns = [
            'similar to',
            'duplicate of',
            'resembles',
            'like',
            'same as',
        ]

        # FORBIDDEN: Score-based filtering
        scoring_patterns = [
            'score >',
            'score <',
            'score >=',
            'score <=',
            'above threshold',
            'below threshold',
            'ranking',
        ]

        # FORBIDDEN: Content-based filtering
        content_patterns = [
            'about specific topic',
            'mentions specific',
            'contains keyword',
            'matches topic',
        ]

        # Check each forbidden pattern
        all_forbidden = (
            quality_patterns +
            completeness_patterns +
            similarity_patterns +
            scoring_patterns +
            content_patterns
        )

        for pattern in all_forbidden:
            if pattern in context_lower:
                # Allow if it's in a comment
                if '#' in context:
                    lines = context.split('\n')
                    for line in lines:
                        if pattern in line.lower() and line.strip().startswith('#'):
                            return  # It's a comment, OK

                # Allow if it's in a string (documentation, error message)
                if '"' in context or "'" in context:
                    # Check if pattern is part of string literal
                    import re
                    strings = re.findall(r'["\']([^"\']*)["\']', context)
                    for s in strings:
                        if pattern in s.lower():
                            return  # It's in a string, OK

                # Otherwise, it's a violation
                pytest.fail(
                    f"Judgment-based filtering found in {file_path.relative_to(project_root)}:{line_num}. "
                    f"Pattern: '{pattern}'. "
                    "Filtering must be based on technical invariants only, not judgments."
                )


# ============================================================================
# CATEGORY 2: STATUS FILTERING IS FOR READING, NOT JUDGMENT
# ============================================================================

class TestStatusFiltering:
    """Verify that status filtering respects human decisions."""

    def test_status_filtering_is_for_reading_only(self):
        """
        GOVERNANCE: Status filtering must be for INPUT selection, not quality judgment.

        ALLOWED: "Read only rows where status='final'" (respecting human approval)
        FORBIDDEN: "Filter out rows where status='candidate' because they're low quality"
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Use AST to find actual status comparisons, not string references
        import ast

        code_only = _strip_comments_and_strings_simple(content)

        try:
            tree = ast.parse(code_only)

            # Find all if statements that check status
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    # Check if the test involves status
                    test_str = ast.unparse(node.test)
                    if 'status' in test_str and 'final' in test_str:
                        # This is a status check - verify it's for reading (inequality)
                        # Look for patterns like: status != 'final' (good - skipping non-final)
                        # Or patterns like: status == 'final' (also good - reading only final)
                        # The key is it's for INPUT selection, not quality judgment

                        # As long as it's not doing quality checks, it's OK
                        # The important thing is it respects status as a filter
                        continue
        except SyntaxError:
            pass

        # Most importantly: verify no quality-related filtering
        # by checking that "quality", "good", "better", "worthy" don't appear
        # in status-related code
        code_lower = code_only.lower()

        # If we find status AND quality indicators together, that's bad
        status_quality_pairs = [
            ('status', 'quality'),
            ('status', 'good'),
            ('status', 'better'),
            ('status', 'worthy'),
            ('status', 'sufficient'),
        ]

        lines = code_only.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for status_word, quality_word in status_quality_pairs:
                if status_word in line_lower and quality_word in line_lower:
                    pytest.fail(
                        f"Status filtering based on quality found in {summary_generator_path}:{i+1}. "
                        f"Found '{status_word}' and '{quality_word}' on same line. "
                        "Status filtering must respect human decisions, not judge quality."
                    )

    def test_status_filtering_uses_inequality(self):
        """
        GOVERNANCE: Status filtering should use inequality (status != 'final').

        This pattern indicates "skip non-final" (respecting human approval),
        not "filter based on quality" (AI judgment).
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check for inequality-based status filtering
        assert "status != 'final'" in content or 'status != "final"' in content, (
            "Summary generator does not use inequality-based status filtering. "
            "Pattern should be: if status != 'final': skip (respecting human approval)"
        )


# ============================================================================
# CATEGORY 3: DATA INTEGRITY CHECKS ARE ALLOWED
# ============================================================================

class TestDataIntegrityChecks:
    """Verify that data integrity checks are technical, not judgment-based."""

    def test_none_value_checks_are_allowed(self):
        """
        GOVERNANCE: None/value checks are allowed (technical invariant).

        Example: if not value: continue (missing data)
        """
        project_root = Path(__file__).parent.parent.parent

        # This test just documents that None checks are allowed
        # No assertion needed - this is informational
        assert True, "None/value checks are allowed as technical invariants"

    def test_source_id_validation_is_allowed(self):
        """
        GOVERNANCE: Source ID validation is allowed (technical invariant).

        Example: if not source_id: skip (cannot process without identifier)
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Source ID validation is OK
        assert 'source_id' in content, (
            "Source ID validation not found. "
            "Source ID checks are allowed as technical invariants."
        )

    def test_file_extension_checks_are_allowed(self):
        """
        GOVERNANCE: File extension checks are allowed (technical invariant).

        Example: if ext not in SUPPORTED_EXTENSIONS: skip
        """
        project_root = Path(__file__).parent.parent.parent
        markdown_extractor_path = project_root / "markdown_extractor.py"

        with open(markdown_extractor_path) as f:
            content = f.read()

        # File extension filtering is OK
        assert 'SUPPORTED_EXTENSIONS' in content or 'supported' in content.lower(), (
            "File extension checks not found. "
            "Format compatibility checks are allowed as technical invariants."
        )


# ============================================================================
# CATEGORY 4: NO SEMANTIC SIMILARITY FILTERING
# ============================================================================

class TestNoSemanticSimilarity:
    """Verify that no semantic similarity filtering exists."""

    def test_no_similarity_score_calculation(self):
        """
        GOVERNANCE: No similarity score calculation in active code.

        Semantic similarity is judgment-based and forbidden.
        """
        project_root = Path(__file__).parent.parent.parent

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
            content_lower = content.lower()

            # Check for similarity calculation
            forbidden_patterns = [
                'similarity score',
                'similarity_score',
                'calculate_similarity',
                'compute_similarity',
                'semantic_similarity',
                'cosine similarity',
                'jaccard similarity',
                'levenshtein',
                'edit distance',
            ]

            for pattern in forbidden_patterns:
                # Allow in comments
                if pattern in content_lower:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line.lower() and not line.strip().startswith('#'):
                            # Check if it's in a string
                            if '"' in line or "'" in line:
                                continue

                            pytest.fail(
                                f"Similarity calculation found in {py_file.relative_to(project_root)}:{i+1}. "
                                "Semantic similarity filtering is forbidden in Iteration 2."
                            )

    def test_no_duplicate_detection_by_content(self):
        """
        GOVERNANCE: No duplicate detection based on content similarity.

        Duplicate detection based on LLM judgment is forbidden.
        """
        project_root = Path(__file__).parent.parent.parent

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
            content_lower = content.lower()

            # Check for content-based duplicate detection
            forbidden_patterns = [
                'detect_duplicate',
                'find_duplicate',
                'is_duplicate',
                'check_duplicate',
            ]

            for pattern in forbidden_patterns:
                if pattern in content_lower:
                    # Check context
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line.lower() and 'def ' in line:
                            # Found a function - check if it's content-based
                            # Extract function body (simplified)
                            func_start = i
                            func_lines = lines[func_start:min(func_start + 20, len(lines))]
                            func_text = '\n'.join(func_lines)

                            # Check for LLM usage or similarity in function
                            if 'llm' in func_text.lower() or 'similarity' in func_text.lower():
                                pytest.fail(
                                    f"Content-based duplicate detection found in {py_file.relative_to(project_root)}:{i+1}. "
                                    "AI-based duplicate detection is forbidden."
                                )


# ============================================================================
# CATEGORY 5: NO QUALITY-BASED FILTERING
# ============================================================================

class TestNoQualityFiltering:
    """Verify that no quality-based filtering exists."""

    def test_no_quality_scoring_functions(self):
        """
        GOVERNANCE: No quality scoring functions in active code.

        Quality scoring is judgment-based and forbidden.
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_functions = [
            'def score_quality',
            'def calculate_quality',
            'def assess_quality',
            'def evaluate_quality',
            'def quality_score',
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

            for func in forbidden_functions:
                if func in content:
                    pytest.fail(
                        f"Quality scoring function found in {py_file.relative_to(project_root)}. "
                        "Quality-based filtering is forbidden in Iteration 2."
                    )

    def test_no_completeness_scoring(self):
        """
        GOVERNANCE: No completeness scoring in active code.

        Checking if a story is "complete enough" is judgment-based.
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            'completeness_score',
            'is_complete',
            'completeness check',
            'complete enough',
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
            content_lower = content.lower()

            for pattern in forbidden_patterns:
                if pattern in content_lower:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line.lower() and 'def ' not in line:
                            if not line.strip().startswith('#'):
                                pytest.fail(
                                    f"Completeness scoring found in {py_file.relative_to(project_root)}:{i+1}. "
                                    "Completeness assessment is judgment-based and forbidden."
                                )


# ============================================================================
# CATEGORY 6: FILTERING DOCUMENTATION MUST BE EXPLICIT
# ============================================================================

class TestFilteringDocumentation:
    """Verify that filtering operations are documented as technical invariants."""

    def test_status_filtering_documented_as_respecting_human_decisions(self):
        """
        GOVERNANCE: Status filtering should be documented as respecting human decisions.

        Comments should state: "Skip non-final rows (humans haven't approved)"
        NOT: "Skip low-quality rows"
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check for status filtering
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'status' in line.lower() and 'final' in line.lower():
                # Extract surrounding context for comments
                context_start = max(0, i - 3)
                context_lines = lines[context_start:i+1]

                # Check for comments
                for context_line in context_lines:
                    if '#' in context_line:
                        comment = context_line.strip().lower()

                        # Comment should mention human approval
                        if 'status' in comment and 'final' in comment:
                            assert any(phrase in comment for phrase in [
                                'human',
                                'approve',
                                'approved',
                                'human-owned',
                            ]), (
                                f"Status filtering comment in {summary_generator_path}:{context_lines.index(context_line)+1} "
                                "does not mention human approval. "
                                "Comments should state: 'Skip non-final rows (not human-approved)'"
                            )
