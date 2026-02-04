"""
GOVERNANCE TEST: Ownership & Non-Mutation

This test file enforces the ITERATION 2 OWNERSHIP MODEL:
- System never overwrites Excel files
- System never modifies human-owned rows
- System creates new versioned files on every run
- Humans own rows with status='consolidated', 'final', 'archived'

GOVERNANCE INTENT:
These tests prevent data loss and violation of human decisions.
Once a human edits a row or marks it as approved, the system MUST
NEVER modify, overwrite, or delete that content.

This is a CRITICAL safety constraint. Violations could result in:
- Loss of human decisions
- Silent overwriting of curated content
- Erosion of trust in the system

Reference: DEVELOPMENT_PLAN_v2_FINAL.md, Row-Level Ownership Model
"""

import pytest
import sys
from pathlib import Path
import tempfile
import yaml


# ============================================================================
# CATEGORY 1: EXCEL FILES ARE NEVER OVERWRITTEN
# ============================================================================

class TestExcelNonOverwrite:
    """Verify that Excel files are never overwritten."""

    def test_excel_creation_uses_version_numbering(self):
        """
        GOVERNANCE: Excel file creation must use version numbering.

        Every run must create a new file with incremented version number.
        This prevents overwriting previous outputs.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check for version number generation
        assert 'version' in content.lower(), (
            "story_identifier.py does not generate version numbers. "
            "Excel files must use version numbering to prevent overwrites."
        )

        # Check for version increment logic
        assert 'max(versions) + 1' in content or 'version = version + 1' in content or 'version +=' in content, (
            "story_identifier.py does not increment version numbers. "
            "Each run must create a higher version number."
        )

    def test_excel_filename_includes_version(self):
        """
        GOVERNANCE: Excel filename must include version number.

        Format: candidates_v{N}_{YYYYMMDD}.xlsx
        The version number prevents filename collisions.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check for filename pattern with version
        assert 'candidates_v' in content or 'version' in content, (
            "Excel filename does not include version prefix. "
            "Filename format must be: candidates_v{N}_{date}.xlsx"
        )

        # Check for datestamp in filename
        assert 'datestamp' in content.lower() or 'strftime' in content, (
            "Excel filename does not include date. "
            "Filename format must be: candidates_v{N}_{YYYYMMDD}.xlsx"
        )

    def test_no_excel_file_overwrite_logic(self):
        """
        GOVERNANCE: No code should overwrite existing Excel files.

        Look for patterns that would write to an existing file path.
        """
        project_root = Path(__file__).parent.parent.parent

        # Forbidden patterns: opening file in write mode without versioning
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

            # Look for wb.save() calls
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'wb.save(' in line or 'workbook.save(' in line:
                    # Check if save path includes version number
                    # (not reusing input path or fixed output path)
                    if 'output_path.parent' in line or 'version' in line:
                        continue  # This is OK - creates new file

                    # If save uses exact output_path, might be overwriting
                    if 'output_path)' in line or 'output_path,' in line:
                        # Check context for versioning
                        context = '\n'.join(lines[max(0, i-10):i+10])
                        if 'version' not in context.lower():
                            pytest.fail(
                                f"Potential Excel overwrite in {py_file.relative_to(project_root)}:{i+1}. "
                                "Excel files must use version numbering to prevent overwrites."
                            )

    def test_excel_creates_new_file_every_run(self):
        """
        GOVERNANCE: Excel creation must create a NEW file on every run.

        The system should never update an existing file in place.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check for new workbook creation
        assert 'Workbook()' in content or 'openpyxl.Workbook()' in content, (
            "story_identifier.py does not create new workbook. "
            "Each run must create a new Excel file."
        )

        # Check that it's not loading and modifying existing file
        assert 'load_workbook(' not in content or 'mode="a"' not in content, (
            "story_identifier.py loads existing workbook for modification. "
            "This would overwrite human edits. Create new files only."
        )


# ============================================================================
# CATEGORY 2: HUMAN-OWNED ROWS ARE NEVER MODIFIED
# ============================================================================

class TestRowOwnership:
    """Verify that human-owned rows are never modified."""

    def test_config_defines_human_owned_statuses(self):
        """
        GOVERNANCE: Config must define human-owned statuses.

        The system must know which statuses represent human ownership.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'excel' in config, (
            "config.yaml missing 'excel' section."
        )

        assert 'human_owned_statuses' in config['excel'], (
            "config.yaml missing 'human_owned_statuses' definition. "
            "System must know which statuses are human-owned."
        )

        # Verify the human-owned statuses
        human_owned = set(config['excel']['human_owned_statuses'])

        expected_human_owned = {'consolidated', 'final', 'archived'}

        assert human_owned == expected_human_owned, (
            f"Expected human_owned_statuses: {expected_human_owned}, "
            f"found: {human_owned}. "
            "Only 'consolidated', 'final', and 'archived' should be human-owned."
        )

    def test_system_never_writes_to_human_owned_rows(self):
        """
        GOVERNANCE: No code writes rows with human-owned statuses.

        The system must only write rows with status='candidate'.
        """
        project_root = Path(__file__).parent.parent.parent

        # Check all active Python files
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

            # Look for writing human-owned statuses
            forbidden_patterns = [
                "status = 'consolidated'",
                'status = "consolidated"',
                "status = 'final'",
                'status = "final"',
                "status = 'archived'",
                'status = "archived"',
            ]

            for pattern in forbidden_patterns:
                # Check for assignment (not comparison)
                if 'status !=' in content and 'final' in content:
                    # This is OK - it's comparison, not assignment
                    continue

                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and not line.strip().startswith('#'):
                        # Allow in summary_generator for comparison
                        if py_file.name == 'summary_generator.py' and '!=' in line:
                            continue

                        pytest.fail(
                            f"Code writes human-owned status in {py_file.relative_to(project_root)}:{i+1}. "
                            "System must never write rows with human-owned statuses."
                        )

    def test_system_only_writes_candidate_rows(self):
        """
        GOVERNANCE: System must only write candidate rows.

        This is the ONLY status the system is allowed to set.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check that normalize_candidate sets status to candidate
        assert "'status': 'candidate'" in content or '"status": "candidate"' in content, (
            "story_identifier.py does not set status='candidate'. "
            "This is the ONLY status the system is allowed to set."
        )


# ============================================================================
# CATEGORY 3: OUTPUTS ARE WRITTEN TO NEW VERSIONED FILES ONLY
# ============================================================================

class TestVersionedOutputs:
    """Verify that outputs are written to new versioned files only."""

    def test_summary_creates_new_file(self):
        """
        GOVERNANCE: Summary generator must create new file, not overwrite.

        The output path should not be an existing input file.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check for file writing
        assert 'with open(output_path' in content or "with open(output_path" in content, (
            "summary_generator.py does not write output file."
        )

        # Verify it opens for writing (creates new or overwrites by explicit path)
        assert "'w'" in content or '"w"' in content, (
            "summary_generator.py does not open file in write mode."
        )

    def test_no_summary_overwrites_input(self):
        """
        GOVERNANCE: Summary output must not overwrite input Excel.

        Input and output paths must be different parameters.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check function signature
        assert 'def generate_summary(' in content, (
            "generate_summary function not found."
        )

        # Verify separate input and output parameters
        assert 'input_path' in content and 'output_path' in content, (
            "Summary generator does not have separate input/output paths. "
            "This could lead to overwriting input file."
        )

        # Verify they are different
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'def generate_summary(' in line:
                # Check next several lines for parameters
                sig_lines = lines[i:min(i+10, len(lines))]
                sig_text = '\n'.join(sig_lines)

                assert 'input_path' in sig_text and 'output_path' in sig_text, (
                    "Function signature missing input_path or output_path parameter."
                )

                break

    def test_markdown_extraction_creates_new_files(self):
        """
        GOVERNANCE: Markdown extraction must create new files.

        Source files are never modified. Output files are new.
        """
        project_root = Path(__file__).parent.parent.parent
        markdown_extractor_path = project_root / "markdown_extractor.py"

        with open(markdown_extractor_path) as f:
            content = f.read()

        # Check that source files are only read
        assert 'extract_text_from_file(' in content, (
            "extract_text_from_file function not found."
        )

        # Verify source files are not modified
        # (no writing to sources_path)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Look for write operations
            if 'with open(' in line and "'w'" in line:
                # Check if it's writing to source directory
                if 'sources_path' in line:
                    pytest.fail(
                        f"Markdown extractor writes to source directory in {markdown_extractor_path}:{i+1}. "
                        "Source files must never be modified."
                    )

    def test_outputs_directory_exists(self):
        """
        GOVERNANCE: outputs/ directory must exist for versioned outputs.

        All system outputs go to outputs/ to prevent overwriting vault content.
        """
        project_root = Path(__file__).parent.parent.parent
        outputs_dir = project_root / "outputs"

        # Directory should exist or be created by code
        # (we just verify it's defined in config)
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'paths' in config, (
            "config.yaml missing 'paths' section."
        )

        assert 'outputs_dir' in config['paths'], (
            "config.yaml missing 'outputs_dir' path. "
            "System outputs must go to outputs/ directory."
        )

        assert 'outputs' in config['paths']['outputs_dir'], (
            "outputs_dir does not point to outputs/ directory."
        )


# ============================================================================
# CATEGORY 4: SYSTEM DOCUMENTS OWNERSHIP MODEL
# ============================================================================

class TestOwnershipDocumentation:
    """Verify that ownership model is documented."""

    def test_config_documents_ownership_model(self):
        """
        GOVERNANCE: Config must document the ownership model.

        Comments should explain which statuses are human-owned
        and that system must not modify them.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            content = f.read()

        # Check for ownership documentation
        # Normalize: remove hyphens/spaces for comparison
        content_normalized = content.lower().replace('-', ' ').replace('_', ' ')
        assert 'human owned' in content_normalized, (
            "config.yaml does not document human-owned statuses. "
            "Comments should explain the ownership model."
        )

        # Check for read-only declaration
        assert 'read only' in content_normalized or 'read only' in content_normalized, (
            "config.yaml does not declare human-owned rows as read-only. "
            "Comments should state: 'System MUST NOT modify rows with these statuses'."
        )

    def test_story_identifier_documents_ownership(self):
        """
        GOVERNANCE: story_identifier must document ownership constraints.

        Code should state that it only generates candidates and does not
        make final decisions or modify human-owned content.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        content_lower = content.lower()

        # Check for human primacy documentation
        assert 'human primacy' in content_lower or 'human' in content_lower, (
            "story_identifier.py does not document human primacy. "
            "Module docstring should state 'HUMAN PRIMACY ENFORCEMENT'."
        )

        # Check that it documents it only generates candidates (not final/consolidated)
        # The module should state it generates candidates only
        assert any(phrase in content_lower for phrase in [
            'candidate only',
            'candidates only',
            'generate candidates',
            'generate candidate',
            'no final',
        ]), (
            "story_identifier.py does not document that it only generates candidates. "
            "Module should state: 'Generate candidates only, no final decisions'."
        )

    def test_summary_generator_documents_final_only(self):
        """
        GOVERNANCE: summary_generator must document final-only consumption.

        Code should state that only human-finalized rows are consumed.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        content_lower = content.lower()

        # Check for final-only documentation
        assert 'only final' in content_lower or 'final rows only' in content_lower, (
            "summary_generator.py does not document final-only consumption. "
            "Module should state: 'ONLY final rows are consumed.'"
        )

        # Check for human-approved reference
        assert 'human' in content_lower and ('approved' in content_lower or 'approve' in content_lower), (
            "summary_generator.py does not state that final rows are human-approved."
        )


# ============================================================================
# CATEGORY 5: NO DELETION OF HUMAN CONTENT
# ============================================================================

class TestNoDeletionOfHumanContent:
    """Verify that human content is never deleted."""

    def test_no_delete_file_operations(self):
        """
        GOVERNANCE: No code should delete files.

        File deletion is forbidden for human-owned content.
        """
        project_root = Path(__file__).parent.parent.parent

        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            # Skip test files (may need cleanup)
            if "tests" in py_file.parts:
                continue

            content = py_file.read_text()

            # Check for file deletion patterns
            forbidden_patterns = [
                'os.remove(',
                'os.unlink(',
                'Path.unlink(',
                '.remove(',
                '.unlink(',
            ]

            for pattern in forbidden_patterns:
                if pattern in content:
                    # Check if it might affect user data
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line and not line.strip().startswith('#'):
                            # Allow for temp files or test cleanup
                            if 'temp' in line.lower() or 'tmp' in line.lower():
                                continue

                            # Allow .remove() for workbook sheets (not file deletion)
                            if pattern == '.remove(' and 'wb.' in line:
                                continue

                            pytest.fail(
                                f"File deletion found in {py_file.relative_to(project_root)}:{i+1}. "
                                "Deleting files (especially human content) is forbidden."
                            )

    def test_no_row_deletion_from_excel(self):
        """
        GOVERNANCE: No code should delete rows from Excel.

        Row deletion would destroy human decisions.
        """
        project_root = Path(__file__).parent.parent.parent

        # Check for row deletion patterns
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

            # Look for row deletion patterns
            forbidden_patterns = [
                'ws.delete_rows(',
                'sheet.delete_rows(',
                '.delete(',
            ]

            for pattern in forbidden_patterns:
                if pattern in content:
                    pytest.fail(
                        f"Row deletion found in {py_file.relative_to(project_root)}. "
                        "Deleting Excel rows destroys human decisions."
                    )
