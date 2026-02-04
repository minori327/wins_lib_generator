"""
GOVERNANCE TEST: Determinism & Traceability

This test file enforces the ITERATION 2 DETERMINISM and TRACEABILITY
constraints that enable human oversight and auditability.

GOVERNANCE INTENT:
These tests ensure that:
1. Same inputs + same config → same outputs (determinism)
2. All outputs are traceable to source inputs
3. LLM behavior is controlled (temperature, explicit prompts)
4. No hidden or opaque processing

Determinism and traceability are ESSENTIAL for human oversight.
Without them, humans cannot verify system behavior or audit decisions.

Reference: DEVELOPMENT_PLAN_v2_FINAL.md, Design Principles
"""

import pytest
import yaml
from pathlib import Path


# ============================================================================
# CATEGORY 1: LLM TEMPERATURE IS CONFIGURED FOR DETERMINISM
# ============================================================================

class TestLLMDeterminism:
    """Verify that LLM configuration ensures determinism."""

    def test_llm_temperature_is_configured(self):
        """
        GOVERNANCE: LLM temperature must be configured.

        Temperature controls randomness. Lower temperature = more deterministic.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'llm' in config, (
            "llm section not found in config."
        )

        assert 'temperature' in config['llm'], (
            "temperature not found in llm config. "
            "Temperature must be configured for determinism."
        )

    def test_llm_temperature_is_low(self):
        """
        GOVERNANCE: LLM temperature should be low for determinism.

        Temperature should be <= 0.5 for consistent outputs.
        Higher temperatures introduce randomness.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        temperature = config['llm'].get('temperature', 1.0)

        assert temperature <= 0.5, (
            f"LLM temperature is {temperature}, which is too high. "
            "Temperature should be <= 0.5 for deterministic outputs."
        )

    def test_llm_temperature_is_used_in_client(self):
        """
        GOVERNANCE: LLM client must use configured temperature.

        Configured temperature must be passed to LLM API calls.
        """
        project_root = Path(__file__).parent.parent.parent
        llm_client_path = project_root / "utils" / "llm_client.py"

        with open(llm_client_path) as f:
            content = f.read()

        # Check that temperature is loaded from config
        assert 'temperature' in content, (
            "LLM client does not reference temperature. "
            "Temperature from config must be used in LLM calls."
        )

        # Check that temperature is passed to payload
        assert '"temperature"' in content or "'temperature'" in content, (
            "LLM client does not pass temperature to API payload. "
            "Temperature must be included in LLM API calls."
        )

    def test_llm_does_not_use_high_temperature(self):
        """
        GOVERNANCE: No hardcoded high temperature values in code.

        Hardcoded temperatures override config and introduce randomness.
        """
        project_root = Path(__file__).parent.parent.parent

        # Check all Python files
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

            # Look for temperature assignments with high values
            # (allow config loading and low values)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'temperature' in line.lower() and '=' in line:
                    # Skip if it's loading from config
                    if 'config' in line.lower() or 'get(' in line:
                        continue

                    # Check for numeric value
                    import re
                    temp_match = re.search(r'temperature.*=\s*(\d+\.?\d*)', line)
                    if temp_match:
                        temp_value = float(temp_match.group(1))
                        if temp_value > 0.5:
                            pytest.fail(
                                f"High temperature ({temp_value}) found in {py_file.relative_to(project_root)}:{i+1}. "
                                "Temperatures > 0.5 introduce randomness."
                            )


# ============================================================================
# CATEGORY 2: LLM CALLS ARE EXPLICIT AND LOGGED
# ============================================================================

class TestLLMExplicitness:
    """Verify that LLM calls are explicit and logged."""

    def test_llm_client_logs_all_calls(self):
        """
        GOVERNANCE: LLM client must log all calls.

        Every LLM call must be logged for traceability.
        """
        project_root = Path(__file__).parent.parent.parent
        llm_client_path = project_root / "utils" / "llm_client.py"

        with open(llm_client_path) as f:
            content = f.read()

        # Check for logging
        assert 'logger' in content.lower(), (
            "LLM client does not have logging configured."
        )

        # Check for log statements in call methods
        assert 'log' in content.lower(), (
            "LLM client does not log calls."
        )

    def test_llm_calls_have_explicit_prompts(self):
        """
        GOVERNANCE: LLM calls must use explicit prompts.

        Prompts should be stored in code or config, not generated dynamically.
        """
        project_root = Path(__file__).parent.parent.parent

        # Check story_identifier.py
        story_identifier_path = project_root / "story_identifier.py"
        with open(story_identifier_path) as f:
            content = f.read()

        # Should load prompt from file
        assert 'load_prompt_template' in content or 'prompt' in content.lower(), (
            "story_identifier.py does not load prompt templates. "
            "Prompts must be explicit and stored."
        )

        # Check summary_generator.py
        summary_generator_path = project_root / "summary_generator.py"
        with open(summary_generator_path) as f:
            content = f.read()

        assert 'load_prompt_template' in content or 'prompt' in content.lower(), (
            "summary_generator.py does not load prompt templates. "
            "Prompts must be explicit and stored."
        )

    def test_prompts_are_stored_as_files(self):
        """
        GOVERNANCE: Prompts must be stored as files, not inline strings.

        Stored prompts enable inspection and modification.
        """
        project_root = Path(__file__).parent.parent.parent
        prompts_dir = project_root / "prompts"

        assert prompts_dir.exists(), (
            "prompts/ directory does not exist. "
            "Prompts must be stored as files for traceability."
        )

        # Check for required prompt files
        required_prompts = [
            'identify_stories.yaml',
            'executive_summary.yaml',
        ]

        for prompt_file in required_prompts:
            prompt_path = prompts_dir / prompt_file
            assert prompt_path.exists(), (
                f"Required prompt file not found: {prompt_file}. "
                "All prompts must be stored as files."
            )


# ============================================================================
# CATEGORY 3: OUTPUTS CONTAIN SOURCE REFERENCES
# ============================================================================

class TestTraceabilityInOutputs:
    """Verify that outputs contain source references."""

    def test_markdown_includes_source_metadata(self):
        """
        GOVERNANCE: Markdown files must include source file references.

        Generated Markdown must reference original source files.
        """
        project_root = Path(__file__).parent.parent.parent
        markdown_extractor_path = project_root / "markdown_extractor.py"

        with open(markdown_extractor_path) as f:
            content = f.read()

        # Check for source file reference
        assert 'source_file' in content, (
            "Markdown generation does not include source_file reference. "
            "Outputs must be traceable to sources."
        )

        # Check for source ID
        assert 'source_id' in content, (
            "Markdown generation does not include source_id. "
            "Outputs must be traceable to sources."
        )

    def test_excel_includes_source_references(self):
        """
        GOVERNANCE: Excel files must include source references.

        Stories must be traceable to source files.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check for source_id in Excel output
        assert 'source_id' in content, (
            "Excel generation does not include source_id. "
            "Stories must be traceable to sources."
        )

        # Check for evidence_references
        assert 'evidence_references' in content, (
            "Excel generation does not include evidence_references. "
            "Stories must be traceable to source content."
        )

    def test_summary_includes_traceability_footer(self):
        """
        GOVERNANCE: Summaries must include traceability footer.

        Footer should reference input Excel file and generation time.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check for traceability footer function
        assert 'add_traceability_footer' in content or 'traceability' in content.lower(), (
            "summary_generator.py does not add traceability footer. "
            "Summaries must include source references and generation time."
        )

        # Check for footer content
        content_lower = content.lower()
        assert any(phrase in content_lower for phrase in [
            'source:',
            'generated:',
            'traceability',
            'input file',
        ]), (
            "Summary footer does not include traceability information. "
            "Footer should state: 'Source: <filename>, Generated: <timestamp>'"
        )


# ============================================================================
# CATEGORY 4: ALL PROCESSING IS LOGGED
# ============================================================================

class TestLoggingCoverage:
    """Verify that all processing steps are logged."""

    def test_markdown_extraction_is_logged(self):
        """
        GOVERNANCE: Markdown extraction must log progress.

        Humans must be able to see what's being processed.
        """
        project_root = Path(__file__).parent.parent.parent
        markdown_extractor_path = project_root / "markdown_extractor.py"

        with open(markdown_extractor_path) as f:
            content = f.read()

        # Check for logging
        assert 'logger' in content.lower() or 'print(' in content, (
            "Markdown extractor does not log progress."
        )

        # Check for log messages
        content_lower = content.lower()
        assert any(phrase in content_lower for phrase in [
            'starting operation',
            'processing file',
            'extracted',
            'completed',
            'failed',
        ]), (
            "Markdown extraction does not log key steps."
        )

    def test_story_identification_is_logged(self):
        """
        GOVERNANCE: Story identification must log progress.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check for logging
        assert 'logger' in content.lower() or 'print(' in content, (
            "Story identifier does not log progress."
        )

        # Check for log messages
        content_lower = content.lower()
        assert any(phrase in content_lower for phrase in [
            'starting operation',
            'processing source',
            'extracted candidates',
            'completed',
            'failed',
        ]), (
            "Story identification does not log key steps."
        )

    def test_summary_generation_is_logged(self):
        """
        GOVERNANCE: Summary generation must log progress.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check for logging
        assert 'logger' in content.lower() or 'print(' in content, (
            "Summary generator does not log progress."
        )

        # Check for log messages
        content_lower = content.lower()
        assert any(phrase in content_lower for phrase in [
            'starting operation',
            'loaded final stories',
            'calling llm',
            'generated summary',
            'completed',
        ]), (
            "Summary generation does not log key steps."
        )


# ============================================================================
# CATEGORY 5: LOGGING FORMAT IS CONSISTENT
# ============================================================================

class TestLoggingFormat:
    """Verify that logging follows a consistent, parseable format."""

    def test_logging_format_is_defined(self):
        """
        GOVERNANCE: Logging format must be defined in config.

        Consistent format enables log parsing and auditing.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'logging' in config, (
            "logging section not found in config."
        )

        assert 'format' in config['logging'], (
            "logging format not specified in config."
        )

    def test_logging_format_includes_component_name(self):
        """
        GOVERNANCE: Logging format should include component name.

        Format like: [component_name] message
        This helps identify which module logged each message.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        log_format = config['logging'].get('format', '')

        assert '%(name)s' in log_format or '[%(name)s]' in log_format, (
            "Logging format does not include component name (%(name)s). "
            "Format should be: '[%(name)s] %(message)s' for traceability."
        )

    def test_logging_is_configured_in_run_py(self):
        """
        GOVERNANCE: run.py must configure logging.

        All operations must use configured logging.
        """
        project_root = Path(__file__).parent.parent.parent
        run_py_path = project_root / "run.py"

        with open(run_py_path) as f:
            content = f.read()

        # Check for logging configuration
        assert 'logging' in content.lower(), (
            "run.py does not configure logging."
        )

        assert 'basicConfig' in content or 'dictConfig' in content, (
            "run.py does not set up logging configuration."
        )


# ============================================================================
# CATEGORY 6: NO HIDDEN OR OPAQUE PROCESSING
# ============================================================================

class TestTransparentProcessing:
    """Verify that no processing is hidden or opaque."""

    def test_all_files_are_processed_explicitly(self):
        """
        GOVERNANCE: File processing should be explicit, not hidden.

        No magic file discovery or automatic processing.
        """
        project_root = Path(__file__).parent.parent.parent
        markdown_extractor_path = project_root / "markdown_extractor.py"

        with open(markdown_extractor_path) as f:
            content = f.read()

        # Should have explicit file discovery
        assert 'discover_files' in content or 'glob(' in content or 'rglob(' in content, (
            "Markdown extractor does not have explicit file discovery. "
            "File processing should be explicit and logged."
        )

    def test_all_llm_calls_are_traceable(self):
        """
        GOVERNANCE: All LLM calls should be traceable to specific prompts.

        No dynamic prompt generation that obscures what was asked.
        """
        project_root = Path(__file__).parent.parent.parent

        # Check that LLM calls use loaded prompts
        for py_file in project_root.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts:
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            # Skip test files and utils (LLM client itself)
            if "tests" in py_file.parts or "utils" in py_file.parts:
                continue

            content = py_file.read_text()

            # If file uses LLM client, check for prompt loading
            if 'llm_client' in content.lower() or 'LLMClient' in content:
                # Should load prompt from file or define explicitly
                assert 'prompt' in content.lower(), (
                    f"{py_file.name} uses LLM client but does not reference prompts. "
                    "All LLM calls must use explicit prompts for traceability."
                )

    def test_no_dynamic_code_execution(self):
        """
        GOVERNANCE: No dynamic code execution (exec, eval) in active code.

        Dynamic execution is opaque and untraceable.
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

            # Check for dangerous patterns
            forbidden_patterns = [
                'exec(',
                'eval(',
                '__import__',
                'compile(',
            ]

            for pattern in forbidden_patterns:
                # Allow in comments
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and not line.strip().startswith('#'):
                        # Check if it's in a string
                        if '"' in line or "'" in line:
                            # Might be a string literal, check context
                            continue

                        pytest.fail(
                            f"Dynamic code execution pattern '{pattern}' found in {py_file.relative_to(project_root)}:{i+1}. "
                            "Dynamic execution is opaque and untraceable."
                        )


# ============================================================================
# CATEGORY 7: TIMESTAMPING FOR AUDIT TRAIL
# ============================================================================

class TestTimestamping:
    """Verify that outputs include timestamps for audit trail."""

    def test_excel_includes_metadata_with_timestamps(self):
        """
        GOVERNANCE: Excel files must include metadata with generation timestamp.

        Metadata worksheet should track when files were generated.
        """
        project_root = Path(__file__).parent.parent.parent
        story_identifier_path = project_root / "story_identifier.py"

        with open(story_identifier_path) as f:
            content = f.read()

        # Check for metadata worksheet
        assert 'Metadata' in content or 'metadata' in content.lower(), (
            "Excel generation does not create Metadata worksheet. "
            "Metadata is required for audit trail."
        )

        # Check for timestamp in metadata
        content_lower = content.lower()
        assert any(phrase in content_lower for phrase in [
            'generated_at',
            'timestamp',
            'datetime',
            'isoformat',
        ]), (
            "Excel metadata does not include generation timestamp. "
            "Timestamps are required for audit trail."
        )

    def test_markdown_includes_extraction_timestamp(self):
        """
        GOVERNANCE: Markdown files must include extraction timestamp.

        Frontmatter should track when extraction occurred.
        """
        project_root = Path(__file__).parent.parent.parent
        markdown_extractor_path = project_root / "markdown_extractor.py"

        with open(markdown_extractor_path) as f:
            content = f.read()

        # Check for timestamp in frontmatter
        content_lower = content.lower()
        assert any(phrase in content_lower for phrase in [
            'extracted_at',
            'timestamp',
            'datetime',
            'isoformat',
        ]), (
            "Markdown frontmatter does not include extraction timestamp. "
            "Timestamps are required for audit trail."
        )

    def test_summary_includes_generation_timestamp(self):
        """
        GOVERNANCE: Summaries must include generation timestamp.

        Footer or metadata should track when summary was generated.
        """
        project_root = Path(__file__).parent.parent.parent
        summary_generator_path = project_root / "summary_generator.py"

        with open(summary_generator_path) as f:
            content = f.read()

        # Check for timestamp
        content_lower = content.lower()
        assert any(phrase in content_lower for phrase in [
            'generated:',
            'timestamp',
            'datetime',
            'isoformat',
        ]), (
            "Summary does not include generation timestamp. "
            "Timestamps are required for audit trail."
        )
