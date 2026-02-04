"""
GOVERNANCE TEST: CLI Authority

This test file enforces the ITERATION 2 DESIGN REQUIREMENT:
- All pipelines are human-triggered via explicit CLI commands
- No alternative entry points exist
- No hidden workflows or background processes

GOVERNANCE INTENT:
These tests ensure that run.py is the SINGLE authoritative entry point,
providing exactly three mutually exclusive CLI commands. Any additional
entry points, commands, or invocation methods represent a governance violation.

Reference: DEVELOPMENT_PLAN_v2_FINAL.md, WS5 (Work Stream 5)
"""

import pytest
import sys
from pathlib import Path
import subprocess
import argparse


# ============================================================================
# CATEGORY 1: VERIFY RUN.PY IS THE ONLY ENTRY POINT
# ============================================================================

class TestCLIEntryPoints:
    """Verify that run.py is the only authoritative entry point."""

    def test_run_py_exists_at_project_root(self):
        """
        GOVERNANCE: run.py must exist at project root.

        run.py is the ONLY authorized entry point for Iteration 2.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py = project_root / "run.py"

        assert run_py.exists(), (
            "run.py not found at project root. "
            "run.py is the ONLY authorized entry point for Iteration 2."
        )

        assert run_py.is_file(), (
            "run.py exists but is not a file."
        )

    def test_run_py_is_executable(self):
        """
        GOVERNANCE: run.py must be executable.

        The entry point must be directly executable by users.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py = project_root / "run.py"

        # Check if file has executable content (shebang)
        with open(run_py) as f:
            first_line = f.readline().strip()

        assert first_line.startswith("#!"), (
            "run.py does not have a shebang (#!/usr/bin/env python3). "
            "Entry point must be executable."
        )

        assert "python" in first_line.lower(), (
            "run.py shebang does not reference python."
        )

    def test_no_main_py_entry_point(self):
        """
        GOVERNANCE: main.py must not exist as an alternative entry point.

        Only run.py is authorized. main.py would represent an alternative.
        """
        project_root = Path(__file__).parent.parent.parent
        main_py = project_root / "main.py"

        assert not main_py.exists(), (
            "main.py found at project root. "
            "Only run.py is authorized as the entry point. "
            "Alternative entry points violate CLI authority."
        )

    def test_no_cli_py_entry_point(self):
        """
        GOVERNANCE: cli.py must not exist as an alternative entry point.
        """
        project_root = Path(__file__).parent.parent.parent
        cli_py = project_root / "cli.py"

        assert not cli_py.exists(), (
            "cli.py found at project root. "
            "Only run.py is authorized as the entry point."
        )

    def test_no_app_py_entry_point(self):
        """
        GOVERNANCE: app.py must not exist as an alternative entry point.
        """
        project_root = Path(__file__).parent.parent.parent
        app_py = project_root / "app.py"

        assert not app_py.exists(), (
            "app.py found at project root. "
            "Only run.py is authorized as the entry point."
        )

    def test_no_if__name__block_in_active_modules(self):
        """
        GOVERNANCE: Active modules must not have __main__ blocks.

        __main__ blocks in modules create alternative entry points,
        violating single-entry-point governance.
        """
        project_root = Path(__file__).parent.parent.parent

        for py_file in project_root.rglob("*.py"):
            # Skip run.py itself (allowed to have __main__)
            if py_file.name == "run.py":
                continue

            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip test files (allowed to have __main__ for direct execution)
            if "tests" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            content = py_file.read_text()

            # Check for __main__ block
            assert 'if __name__ == "__main__"' not in content, (
                f"__main__ block found in {py_file.relative_to(project_root)}. "
                "This creates an alternative entry point. "
                "Only run.py is authorized as the entry point."
            )


# ============================================================================
# CATEGORY 2: VERIFY EXACTLY THREE CLI COMMANDS EXIST
# ============================================================================

class TestCLICommandCount:
    """Verify that exactly three CLI commands exist."""

    def test_cli_has_exactly_three_commands(self):
        """
        GOVERNANCE: run.py must have exactly three commands.

        Iteration 2 defines exactly three commands:
        1. --extract-markdown (WS1: Markdown extraction)
        2. --identify-stories (WS2: Candidate generation)
        3. --summary (WS4: Summary generation)

        Any additional command represents a governance violation.
        """
        # Import run.py to inspect argparse setup
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        # Read the file and count mode_group.add_argument calls
        with open(run_py_path) as f:
            content = f.read()

        # Count add_argument calls within mode_group context
        # Look for mode_group.add_argument pattern
        mode_group_args = []
        for line in content.split('\n'):
            if 'mode_group.add_argument' in line and 'def add_argument' not in line:
                mode_group_args.append(line.strip())

        assert len(mode_group_args) == 3, (
            f"Expected exactly 3 CLI commands, found {len(mode_group_args)}. "
            f"Iteration 2 only allows: --extract-markdown, --identify-stories, --summary. "
            f"Additional commands: {mode_group_args}"
        )

    def test_command_1_is_extract_markdown(self):
        """
        GOVERNANCE: First command must be --extract-markdown.

        This command implements Work Stream 1: Markdown extraction.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        with open(run_py_path) as f:
            content = f.read()

        assert '--extract-markdown' in content, (
            "--extract-markdown command not found. "
            "This is a required command for Work Stream 1."
        )

    def test_command_2_is_identify_stories(self):
        """
        GOVERNANCE: Second command must be --identify-stories.

        This command implements Work Stream 2: Candidate generation.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        with open(run_py_path) as f:
            content = f.read()

        assert '--identify-stories' in content, (
            "--identify-stories command not found. "
            "This is a required command for Work Stream 2."
        )

    def test_command_3_is_summary(self):
        """
        GOVERNANCE: Third command must be --summary.

        This command implements Work Stream 4: Summary generation.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        with open(run_py_path) as f:
            content = f.read()

        assert '--summary' in content, (
            "--summary command not found. "
            "This is a required command for Work Stream 4."
        )

    def test_no_additional_commands_exist(self):
        """
        GOVERNANCE: No additional commands beyond the three specified.

        Commands like --run, --execute, --process, --workflow, --orchestrate,
        --merge, --dedup, --rank, --finalize are strictly forbidden.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        with open(run_py_path) as f:
            content = f.read()

        forbidden_commands = [
            '--run',
            '--execute',
            '--process',
            '--workflow',
            '--orchestrate',
            '--orchestrator',
            '--merge',
            '--dedup',
            '--deduplicate',
            '--rank',
            '--finalize',
            '--publish',
            '--auto',
        ]

        for cmd in forbidden_commands:
            # Check for argument definitions (not in comments)
            for line in content.split('\n'):
                if cmd in line and 'add_argument' in line and not line.strip().startswith('#'):
                    pytest.fail(
                        f"Forbidden command '{cmd}' found in run.py. "
                        f"Iteration 2 only allows: --extract-markdown, --identify-stories, --summary."
                    )


# ============================================================================
# CATEGORY 3: VERIFY COMMANDS ARE MUTUALLY EXCLUSIVE
# ============================================================================

class TestCLIMutualExclusivity:
    """Verify that CLI commands are mutually exclusive."""

    def test_commands_use_mutually_exclusive_group(self):
        """
        GOVERNANCE: Commands must be in a mutually exclusive group.

        This ensures only one command can be executed per invocation,
        preventing hidden multi-command workflows.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        with open(run_py_path) as f:
            content = f.read()

        assert 'add_mutually_exclusive_group' in content, (
            "Commands not in mutually exclusive group. "
            "Users must only be able to run one command at a time."
        )

        assert 'required=True' in content, (
            "Mutually exclusive group does not require one command. "
            "Users must explicitly choose a command."
        )

    def test_only_one_mutually_exclusive_group_exists(self):
        """
        GOVERNANCE: Only one mutually exclusive group should exist.

        Multiple groups would allow multiple command selection paths,
        violating the single-command-per-invocation rule.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        with open(run_py_path) as f:
            content = f.read()

        # Count occurrences of add_mutually_exclusive_group
        group_count = content.count('add_mutually_exclusive_group')

        assert group_count == 1, (
            f"Found {group_count} mutually exclusive groups. "
            "Only one group should exist for the three mode commands."
        )


# ============================================================================
# CATEGORY 4: VERIFY CLI ENFORCES HUMAN TRIGGERING
# ============================================================================

class TestCLIHumanTriggering:
    """Verify that CLI enforces human triggering of all operations."""

    def test_no_cron_or_scheduler_in_codebase(self):
        """
        GOVERNANCE: No cron jobs or schedulers in active code.

        Automatic scheduling violates "All pipelines are human-triggered."
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            'schedule',
            'scheduler',
            'cron',
            'APScheduler',
            'celery beat',
            'periodic',
            'background_task',
        ]

        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            content = py_file.read_text()

            for pattern in forbidden_patterns:
                # Allow in comments
                if f'#{pattern}' in content or f'"{pattern}"' in content or f"'{pattern}'" in content:
                    continue

                # Check for actual usage (imports, function calls)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and not line.strip().startswith('#'):
                        if 'import' in line or 'from' in line or '=' in line:
                            pytest.fail(
                                f"Scheduler pattern '{pattern}' found in {py_file.relative_to(project_root)}:{i+1}. "
                                "Automatic scheduling is not allowed in Iteration 2."
                            )

    def test_no_file_watchers_in_codebase(self):
        """
        GOVERNANCE: No file watchers in active code.

        File watchers trigger automatic processing when files change,
        violating "All pipelines are human-triggered."
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            'watchdog',
            'watch_file',
            'file_observer',
            'on_file_changed',
            'inotify',
        ]

        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            content = py_file.read_text()

            for pattern in forbidden_patterns:
                # Check for actual usage (imports, function calls)
                if f'import {pattern}' in content or f'from {pattern}' in content:
                    pytest.fail(
                        f"File watcher pattern '{pattern}' found in {py_file.relative_to(project_root)}. "
                        "Automatic file watching is not allowed in Iteration 2."
                    )

    def test_no_background_daemons_or_processes(self):
        """
        GOVERNANCE: No background daemons or processes in active code.

        Background processes run autonomously, violating human control.
        """
        project_root = Path(__file__).parent.parent.parent

        forbidden_patterns = [
            'Process(target=',
            'Thread(target=',
            'daemon=True',
            'start()',
            'multiprocessing.Process',
            'threading.Thread',
        ]

        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            # Skip test files (may use threading for test execution)
            if "tests" in py_file.parts:
                continue

            content = py_file.read_text()

            for pattern in forbidden_patterns:
                # Check for actual usage (not in comments or strings)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and not line.strip().startswith('#'):
                        if 'import' in line or 'from' in line or ('=' in line and 'def' not in line):
                            pytest.fail(
                                f"Background process pattern '{pattern}' found in {py_file.relative_to(project_root)}:{i+1}. "
                                "Background processes are not allowed in Iteration 2."
                            )


# ============================================================================
# CATEGORY 5: VERIFY CLI DOCUMENTATION DECLARES AUTHORITY
# ============================================================================

class TestCLIDocumentation:
    """Verify that CLI documentation declares it as the only entry point."""

    def test_run_py_declares_authority(self):
        """
        GOVERNANCE: run.py must declare itself as the ONLY entry point.

        The module docstring should explicitly state this authority.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        with open(run_py_path) as f:
            content = f.read()

        # Check for module docstring
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

        # Check for authoritative declarations
        assert 'only entry point' in docstring or 'sole entry point' in docstring, (
            "run.py does not declare itself as the ONLY entry point in its docstring. "
            "The module must explicitly state: 'This is the ONLY entry point for the system.'"
        )

        assert 'three explicit commands' in docstring or 'three commands' in docstring, (
            "run.py does not declare the three-command structure in its docstring."
        )

    def test_cli_help_shows_only_three_commands(self):
        """
        GOVERNANCE: CLI --help must show only the three authorized commands.

        This ensures the user-facing documentation matches governance intent.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        # Run the CLI with --help
        result = subprocess.run(
            [sys.executable, str(run_py_path), '--help'],
            capture_output=True,
            text=True,
            cwd=project_root
        )

        help_text = result.stdout.lower()

        # Verify three commands are shown
        assert '--extract-markdown' in help_text, "--extract-markdown not shown in --help"
        assert '--identify-stories' in help_text, "--identify-stories not shown in --help"
        assert '--summary' in help_text, "--summary not shown in --help"

        # Verify forbidden commands are NOT shown
        forbidden_in_help = [
            '--merge',
            '--dedup',
            '--rank',
            '--finalize',
            '--orchestrat',
        ]

        for cmd in forbidden_in_help:
            assert cmd not in help_text, (
                f"Forbidden command '{cmd}' appears in --help output. "
                "This violates CLI authority governance."
            )
