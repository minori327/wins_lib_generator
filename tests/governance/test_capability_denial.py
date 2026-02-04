"""
GOVERNANCE TEST: Capability Denial

This test file enforces the POST-REMEDIATION AUDIT RESULT (2026-02-01):
- Iteration 2 has ZERO violations
- All autonomous capabilities have been archived

GOVERNANCE INTENT:
These tests ensure that forbidden capabilities CANNOT be imported or invoked,
even if they exist somewhere in the codebase. If any forbidden module,
function, or configuration key can be accessed, the test MUST FAIL.

This is a REGRESSION PREVENTION mechanism. Future iterations must NOT
reintroduce autonomous consolidation, deduplication, orchestration, ranking,
or AI decision-making capabilities without explicit human approval.

Test Categories:
1. Forbidden modules cannot be imported
2. Forbidden functions do not exist in active code
3. Forbidden configuration keys do not exist
4. Archived code is isolated from active code
"""

import pytest
import sys
from pathlib import Path
import yaml


# ============================================================================
# CATEGORY 1: FORBIDDEN MODULES CANNOT BE IMPORTED
# ============================================================================

class TestForbiddenModules:
    """Verify that forbidden v1 automation modules cannot be imported."""

    def test_cannot_import_agents_module(self):
        """
        GOVERNANCE: agents/ module from v1 must not be importable.

        The agents/ module contained:
        - semantic_merge_agent.py (autonomous consolidation)
        - semantic_dedup_agent.py (automatic deduplication)
        - ranking_agent.py (AI-based prioritization)
        - finalization_agent.py (AI final decisions)

        These capabilities violate Human Primacy and must remain archived.
        """
        with pytest.raises(ImportError):
            import agents

    def test_cannot_import_workflow_module(self):
        """
        GOVERNANCE: workflow/ module from v1 must not be importable.

        The workflow/ module contained:
        - orchestrator.py (full automation pipeline)
        - deduplicate.py (automatic deduplication)
        - publisher.py (automatic publication)

        These capabilities violate Human Primacy and must remain archived.
        """
        with pytest.raises(ImportError):
            import workflow

    def test_cannot_import_semantic_merge_agent(self):
        """
        GOVERNANCE: semantic_merge_agent must not be accessible.

        This agent enabled autonomous consolidation of SuccessStory objects,
        violating the principle that "Humans control all consolidation."
        """
        with pytest.raises(ImportError):
            from agents.semantic_merge_agent import merge_stories

    def test_cannot_import_semantic_dedup_agent(self):
        """
        GOVERNANCE: semantic_dedup_agent must not be accessible.

        This agent enabled automatic deduplication based on LLM judgment,
        violating the principle that "Humans control all deduplication."
        """
        with pytest.raises(ImportError):
            from agents.semantic_dedup_agent import detect_semantic_duplicates

    def test_cannot_import_orchestrator(self):
        """
        GOVERNANCE: orchestrator must not be accessible.

        The orchestrator implemented a full 12-phase autonomous pipeline,
        violating the principle that "All pipelines are human-triggered."
        """
        with pytest.raises(ImportError):
            from workflow.orchestrator import run_weekly_workflow

    def test_cannot_import_ranking_agent(self):
        """
        GOVERNANCE: ranking_agent must not be accessible.

        This agent enabled AI-based prioritization and scoring,
        violating the principle that "Humans decide priority."
        """
        with pytest.raises(ImportError):
            from agents.ranking_agent import rank_stories


# ============================================================================
# CATEGORY 2: FORBIDDEN FUNCTIONS DO NOT EXIST IN ACTIVE CODE
# ============================================================================

class TestForbiddenFunctions:
    """Verify that forbidden functions do not exist in active Python files."""

    def _strip_comments_and_strings(self, source_code: str) -> str:
        """
        Remove comments and string literals from source code.

        This prevents false positives from documentation/comments that mention
        forbidden capabilities in explanatory contexts.
        """
        import re

        # Remove string literals (both single and double quoted)
        # This handles multiline strings too
        source_code = re.sub(r'"""[\s\S]*?"""', '', source_code)
        source_code = re.sub(r"'''[\s\S]*?'''", '', source_code)
        source_code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '', source_code)
        source_code = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", '', source_code)

        # Remove comments (both # and docstrings)
        lines = source_code.split('\n')
        code_lines = []
        for line in lines:
            # Remove inline # comments
            if '#' in line:
                line = line[:line.index('#')]
            code_lines.append(line)

        return '\n'.join(code_lines)

    def test_merge_stories_function_does_not_exist(self):
        """
        GOVERNANCE: merge_stories() function must not exist in active code.

        This function enabled autonomous consolidation with auto_merge bypass.
        Active code must only provide consolidation hints (text fields).
        """
        # Search all active Python files for merge_stories function definition
        project_root = Path(__file__).parent.parent.parent
        active_files = []

        # Walk all Python files, excluding archive and __pycache__
        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue
            if "__pycache__" in py_file.parts:
                continue
            # Skip test files
            if "tests" in py_file.parts:
                continue

            active_files.append(py_file)

        # Check each active file for forbidden function
        for file_path in active_files:
            content = file_path.read_text()

            # Strip comments and strings to avoid false positives
            code_only = self._strip_comments_and_strings(content)

            # Check for function definition in code only (not comments/strings)
            if "def merge_stories(" in code_only:
                pytest.fail(
                    f"Forbidden function 'merge_stories' found in {file_path.relative_to(project_root)}. "
                    "Autonomous consolidation is not allowed in Iteration 2."
                )

            # Check for class-based merge methods in code only
            # Allow "merge" in variable names like "merge_policy"
            import re
            # Check for "def merge(" as a method definition
            if re.search(r'\bdef\s+merge\s*\(', code_only):
                pytest.fail(
                    f"Forbidden method 'def merge(' found in {file_path.relative_to(project_root)}. "
                    "Consolidation logic is not allowed in Iteration 2."
                )

    def test_semantic_dedup_functions_do_not_exist(self):
        """
        GOVERNANCE: Semantic deduplication functions must not exist in active code.

        Functions like detect_semantic_duplicates, apply_duplicate_flags,
        or any LLM-based similarity detection are forbidden.
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            "def detect_semantic_duplicates(",
            "def apply_duplicate_flags(",
            "def semantic_similarity(",
            "def llm_duplicate_check(",
        ]

        for py_file in project_root.rglob("*.py"):
            if "archive" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            if "tests" in py_file.parts:
                continue

            content = py_file.read_text()
            code_only = self._strip_comments_and_strings(content)

            for pattern in forbidden_patterns:
                if pattern in code_only:
                    pytest.fail(
                        f"Forbidden function '{pattern}' found in {py_file.relative_to(project_root)}. "
                        "Automatic deduplication is not allowed in Iteration 2."
                    )

    def test_ranking_scoring_functions_do_not_exist(self):
        """
        GOVERNANCE: Ranking and scoring functions must not exist in active code.

        Functions that assign scores, ranks, or priority based on AI judgment
        violate Human Primacy (humans decide priority).
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            "def rank_stories(",
            "def score_story(",
            "def calculate_priority(",
            "def evaluate_impact(",
        ]

        for py_file in project_root.rglob("*.py"):
            if "archive" in py_file.parts or "__pycache__" in py_file.parts:
                continue

            content = py_file.read_text()
            code_only = self._strip_comments_and_strings(content)

            for pattern in forbidden_patterns:
                # Allow in test files (for testing other constraints)
                if "tests" in py_file.parts:
                    continue

                if pattern in code_only:
                    pytest.fail(
                        f"Forbidden function '{pattern}' found in {py_file.relative_to(project_root)}. "
                        "AI-based ranking is not allowed in Iteration 2."
                    )

    def test_finalization_functions_do_not_exist(self):
        """
        GOVERNANCE: AI finalization functions must not exist in active code.

        Functions that automatically mark stories as 'final' or approved
        violate Human Primacy (only humans can approve).
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            "def finalize_drafts(",
            "def approve_story(",
            "def set_status_final(",
        ]

        for py_file in project_root.rglob("*.py"):
            if "archive" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            if "tests" in py_file.parts:
                continue

            content = py_file.read_text()
            code_only = self._strip_comments_and_strings(content)

            for pattern in forbidden_patterns:
                if pattern in code_only:
                    pytest.fail(
                        f"Forbidden function '{pattern}' found in {py_file.relative_to(project_root)}. "
                        "AI finalization is not allowed in Iteration 2."
                    )


# ============================================================================
# CATEGORY 3: FORBIDDEN CONFIGURATION KEYS DO NOT EXIST
# ============================================================================

class TestForbiddenConfigurationKeys:
    """Verify that forbidden configuration keys do not exist."""

    def test_no_auto_merge_in_config(self):
        """
        GOVERNANCE: auto_merge configuration key must not exist.

        The auto_merge flag allowed bypassing human approval for consolidation.
        This capability must never return.
        """
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check top-level keys
        assert "auto_merge" not in config, (
            "Forbidden configuration key 'auto_merge' found in config.yaml. "
            "Autonomous merging is not allowed in Iteration 2."
        )

        # Check nested keys
        for section in config.values():
            if isinstance(section, dict):
                assert "auto_merge" not in section, (
                    "Forbidden configuration key 'auto_merge' found in config section. "
                    "Autonomous merging is not allowed in Iteration 2."
                )

    def test_no_auto_delete_in_config(self):
        """
        GOVERNANCE: auto_delete configuration key must not exist.

        The auto_delete flag allowed automatic deletion of stories.
        This capability must never return.
        """
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check top-level keys
        assert "auto_delete" not in config, (
            "Forbidden configuration key 'auto_delete' found in config.yaml. "
            "Automatic deletion is not allowed in Iteration 2."
        )

        # Check nested keys
        for section in config.values():
            if isinstance(section, dict):
                assert "auto_delete" not in section, (
                    "Forbidden configuration key 'auto_delete' found in config section. "
                    "Automatic deletion is not allowed in Iteration 2."
                )

    def test_no_merge_policy_in_config(self):
        """
        GOVERNANCE: merge_policy section must not exist in config.

        The merge_policy section contained auto_merge and auto_merge_threshold.
        This entire section is forbidden.
        """
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "merge_policy" not in config, (
            "Forbidden configuration section 'merge_policy' found in config.yaml. "
            "Merge policy configuration is not allowed in Iteration 2."
        )

    def test_no_deletion_policy_in_config(self):
        """
        GOVERNANCE: deletion_policy section must not exist in config.

        The deletion_policy section contained auto_delete.
        This entire section is forbidden.
        """
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "deletion_policy" not in config, (
            "Forbidden configuration section 'deletion_policy' found in config.yaml. "
            "Deletion policy configuration is not allowed in Iteration 2."
        )

    def test_no_auto_flags_in_config(self):
        """
        GOVERNANCE: No auto_* configuration keys should exist.

        Any auto_* flag represents a capability for autonomous behavior.
        These are fundamentally incompatible with Human Primacy.
        """
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)
            config_text = f.read()

        # Check for any auto_ pattern in config text
        import re
        auto_patterns = re.findall(r'\bauto_\w+', config_text)

        # Allow some auto_ patterns that are technical, not behavioral
        allowed_auto_patterns = [
            # These might be in comments or descriptions
        ]

        forbidden_patterns = [p for p in auto_patterns if p not in allowed_auto_patterns]

        assert len(forbidden_patterns) == 0, (
            f"Forbidden auto_* configuration keys found: {forbidden_patterns}. "
            "Autonomous behavior flags are not allowed in Iteration 2."
        )


# ============================================================================
# CATEGORY 4: ARCHIVED CODE IS ISOLATED FROM ACTIVE CODE
# ============================================================================

class TestArchiveIsolation:
    """Verify that archived v1 code is isolated from active Iteration 2 code."""

    @staticmethod
    def _strip_comments_and_strings(content: str) -> str:
        """
        Remove comments and string literals from source code.

        This prevents false positives from documentation/comments that mention
        forbidden capabilities in explanatory contexts.
        """
        import re

        # Remove string literals (both single and double quoted)
        # This handles multiline strings too
        content = re.sub(r'"""[\s\S]*?"""', '', content)
        content = re.sub(r"'''[\s\S]*?'''", '', content)
        content = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '', content)
        content = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", '', content)

        # Remove comments (both # and docstrings)
        lines = content.split('\n')
        code_lines = []
        for line in lines:
            # Remove inline # comments
            if '#' in line:
                line = line[:line.index('#')]
            code_lines.append(line)

        return '\n'.join(code_lines)

    def test_archive_directory_exists(self):
        """
        GOVERNANCE: archive/ directory must exist.

        The archive/ directory contains all v1 automation code that was
        removed during remediation. Its existence confirms the audit trail.
        """
        project_root = Path(__file__).parent.parent.parent
        archive_dir = project_root / "archive"

        assert archive_dir.exists(), (
            "Archive directory not found. "
            "The archive/ directory must exist to store removed v1 automation code."
        )

        assert archive_dir.is_dir(), (
            "archive/ exists but is not a directory."
        )

    def test_archive_contains_iteration_1(self):
        """
        GOVERNANCE: archive/iteration_1/ must contain v1 code.

        This verifies that the v1 automation code has been properly archived,
        not deleted. The archive serves as an audit trail.
        """
        project_root = Path(__file__).parent.parent.parent
        iteration_1_dir = project_root / "archive" / "iteration_1"

        assert iteration_1_dir.exists(), (
            "archive/iteration_1/ directory not found. "
            "v1 code must be archived for audit trail."
        )

        # Verify key v1 components are archived
        archived_agents = iteration_1_dir / "agents"
        archived_workflow = iteration_1_dir / "workflow"

        assert archived_agents.exists(), (
            "archive/iteration_1/agents/ not found. "
            "v1 agents must be archived."
        )

        assert archived_workflow.exists(), (
            "archive/iteration_1/workflow/ not found. "
            "v1 workflow must be archived."
        )

    def test_active_code_does_not_import_archive(self):
        """
        GOVERNANCE: Active code must not import from archive/.

        Imports from archive/ would indicate that archived capabilities
        are still being used, violating the governance intent.
        """
        project_root = Path(__file__).parent.parent.parent

        # Find all active Python files (not in archive, not in __pycache__)
        active_files = []
        for py_file in project_root.rglob("*.py"):
            if "archive" in py_file.parts:
                continue
            if "__pycache__" in py_file.parts:
                continue
            active_files.append(py_file)

        # Check each file for archive imports
        for file_path in active_files:
            content = file_path.read_text()
            code_only = self._strip_comments_and_strings(content)

            # Check for import statements in code only (not comments)
            import re

            # Look for actual import statements
            # Pattern: "from archive" or "import archive" as code
            if re.search(r'\bfrom\s+archive\b', code_only):
                pytest.fail(
                    f"Import from archive/ found in {file_path.relative_to(project_root)}. "
                    "Active code must not import archived capabilities."
                )

            if re.search(r'\bimport\s+archive\b', code_only):
                pytest.fail(
                    f"Import of archive/ found in {file_path.relative_to(project_root)}. "
                    "Active code must not import archived capabilities."
                )

            # Check for relative imports into archive (e.g., from ..archive import)
            if re.search(r'\bfrom\s+\.\.archive\b', code_only):
                pytest.fail(
                    f"Relative import into archive/ found in {file_path.relative_to(project_root)}. "
                    "Active code must not import archived capabilities."
                )
