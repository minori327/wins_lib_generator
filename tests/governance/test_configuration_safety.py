"""
GOVERNANCE TEST: Configuration Safety

This test file enforces that NO CONFIGURATION can enable autonomous
behavior or violate Human Primacy constraints.

GOVERNANCE INTENT:
Configuration must NEVER provide a "backdoor" to enable forbidden
capabilities. Even if defaults are safe, the existence of config
flags that COULD enable autonomous behavior is a violation.

This is a CRITICAL security constraint. Any config option that allows:
- Autonomous merging
- Automatic deletion
- Auto-decision making
- Background processing
...represents a governance violation.

Reference: DEVELOPMENT_PLAN_v2_FINAL.md, Human Primacy MUST NOT
"""

import pytest
import yaml
from pathlib import Path


# ============================================================================
# CATEGORY 1: NO AUTO_* FLAGS IN CONFIGURATION
# ============================================================================

class TestNoAutoFlags:
    """Verify that no auto_* flags exist in configuration."""

    def test_no_auto_merge_flag(self):
        """
        GOVERNANCE: auto_merge flag must not exist in any config file.

        The auto_merge flag allowed bypassing human approval for consolidation.
        This capability must NEVER return via configuration.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check top-level
        assert 'auto_merge' not in config, (
            "auto_merge flag found in config.yaml. "
            "Autonomous merging is forbidden in Iteration 2."
        )

        # Check nested sections
        def check_dict(d, path=""):
            for key, value in d.items():
                full_path = f"{path}.{key}" if path else key
                if 'auto_merge' in key.lower():
                    pytest.fail(
                        f"auto_merge flag found in config at {full_path}. "
                        "Autonomous merging is forbidden."
                    )
                if isinstance(value, dict):
                    check_dict(value, full_path)

        check_dict(config)

    def test_no_auto_delete_flag(self):
        """
        GOVERNANCE: auto_delete flag must not exist in any config file.

        The auto_delete flag allowed automatic deletion of stories.
        This capability must NEVER return via configuration.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check top-level
        assert 'auto_delete' not in config, (
            "auto_delete flag found in config.yaml. "
            "Automatic deletion is forbidden in Iteration 2."
        )

        # Check nested sections
        def check_dict(d, path=""):
            for key, value in d.items():
                full_path = f"{path}.{key}" if path else key
                if 'auto_delete' in key.lower():
                    pytest.fail(
                        f"auto_delete flag found in config at {full_path}. "
                        "Automatic deletion is forbidden."
                    )
                if isinstance(value, dict):
                    check_dict(value, full_path)

        check_dict(config)

    def test_no_auto_dedup_flag(self):
        """
        GOVERNANCE: auto_dedup flag must not exist in any config file.

        Automatic deduplication is forbidden in all forms.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        def check_dict(d, path=""):
            for key, value in d.items():
                full_path = f"{path}.{key}" if path else key
                if 'auto_dedup' in key.lower() or 'dedup_auto' in key.lower():
                    pytest.fail(
                        f"auto_dedup flag found in config at {full_path}. "
                        "Automatic deduplication is forbidden."
                    )
                if isinstance(value, dict):
                    check_dict(value, full_path)

        check_dict(config)

    def test_no_auto_flags_of_any_kind(self):
        """
        GOVERNANCE: NO auto_* flags should exist in configuration.

        Any auto_* flag represents autonomous behavior capability.
        These are fundamentally incompatible with Human Primacy.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config_text = f.read()
            config = yaml.safe_load(f)

        # If config is empty or None, that's OK - just check the text
        # Strip YAML comments before checking text
        import re
        config_text_no_comments = re.sub(r'#.*$', '', config_text, flags=re.MULTILINE)

        # Check for auto_* patterns in YAML text (excluding comments)
        auto_patterns = re.findall(r'\bauto_\w+', config_text_no_comments)

        # Define explicitly allowed auto_ patterns (should be very few or none)
        allowed_auto_patterns = []

        # Filter out allowed patterns
        forbidden_patterns = [p for p in auto_patterns if p not in allowed_auto_patterns]

        assert len(forbidden_patterns) == 0, (
            f"Forbidden auto_* flags found: {forbidden_patterns}. "
            "Any auto_* configuration is forbidden in Iteration 2."
        )

        # Also check in nested structures (if config exists)
        if config is not None:
            def check_dict(d, path=""):
                for key, value in d.items():
                    if key.startswith('auto_') and key not in allowed_auto_patterns:
                        pytest.fail(
                            f"auto_* flag '{key}' found in config at {path}.{key}. "
                            "All autonomous behavior flags are forbidden."
                        )
                    if isinstance(value, dict):
                        check_dict(value, f"{path}.{key}" if path else key)

            check_dict(config)


# ============================================================================
# CATEGORY 2: NO AUTONOMOUS BEHAVIOR SECTIONS
# ============================================================================

class TestNoAutonomousSections:
    """Verify that no configuration sections enable autonomous behavior."""

    def test_no_merge_policy_section(self):
        """
        GOVERNANCE: merge_policy section must not exist.

        The merge_policy section contained auto_merge and threshold settings.
        This entire section is forbidden.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'merge_policy' not in config, (
            "merge_policy section found in config.yaml. "
            "Merge policy configuration is forbidden (autonomous merging)."
        )

    def test_no_deletion_policy_section(self):
        """
        GOVERNANCE: deletion_policy section must not exist.

        The deletion_policy section contained auto_delete settings.
        This entire section is forbidden.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'deletion_policy' not in config, (
            "deletion_policy section found in config.yaml. "
            "Deletion policy configuration is forbidden (automatic deletion)."
        )

    def test_no_deduplication_section(self):
        """
        GOVERNANCE: deduplication section must not exist.

        Any deduplication configuration would enable autonomous behavior.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'deduplication' not in config, (
            "deduplication section found in config.yaml. "
            "Deduplication configuration is forbidden."
        )

    def test_no_orchestration_section(self):
        """
        GOVERNANCE: orchestration section must not exist.

        Orchestration configuration would enable autonomous workflows.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'orchestration' not in config, (
            "orchestration section found in config.yaml. "
            "Orchestration configuration is forbidden."
        )

    def test_no_ranking_section(self):
        """
        GOVERNANCE: ranking section must not exist.

        Ranking configuration would enable AI-based prioritization.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'ranking' not in config, (
            "ranking section found in config.yaml. "
            "Ranking configuration is forbidden (AI-based prioritization)."
        )

    def test_no_scheduling_section(self):
        """
        GOVERNANCE: scheduling section must not exist.

        Scheduling configuration would enable automatic execution.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'scheduling' not in config, (
            "scheduling section found in config.yaml. "
            "Scheduling configuration is forbidden (automatic execution)."
        )


# ============================================================================
# CATEGORY 3: CONFIGURATION DOCUMENTS SAFETY
# ============================================================================

class TestConfigSafetyDocumentation:
    """Verify that configuration documents Human Primacy constraints."""

    def test_config_declares_human_primary_system(self):
        """
        GOVERNANCE: Config header should declare Human Primacy.

        Configuration should state: "Iteration 2: Human-Primary System"
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            content = f.read()

        # Check first few lines for declaration
        lines = content.split('\n')[:10]
        header_text = '\n'.join(lines).lower()

        assert 'iteration 2' in header_text or 'v2.0' in header_text, (
            "Config does not declare Iteration 2 version."
        )

        assert 'human' in header_text, (
            "Config does not declare Human Primacy in header. "
            "Should state: 'Iteration 2: Human-Primary System'"
        )

    def test_config_documents_read_only_human_owned_rows(self):
        """
        GOVERNANCE: Config should document that human-owned rows are read-only.

        Comments should explain the ownership model.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            content = f.read()

        # Check for ownership documentation
        assert 'read-only' in content.lower() or 'read only' in content.lower(), (
            "Config does not document human-owned rows as read-only. "
            "Comments should state: 'System MUST NOT modify rows with these statuses'"
        )

        # Check for human-owned statuses list
        assert 'human_owned_statuses' in content or 'human owned' in content.lower(), (
            "Config does not define human_owned_statuses. "
            "This list is required to document the ownership model."
        )


# ============================================================================
# CATEGORY 4: NO BEHAVIORAL CONFIGURATION BEYOND TECHNICAL SETTINGS
# ============================================================================

class TestTechnicalOnlyConfig:
    """Verify that configuration only contains technical settings."""

    def test_config_sections_are_technical_only(self):
        """
        GOVERNANCE: All config sections should be technical, not behavioral.

        ALLOWED: paths, llm settings (backend, model, temperature), logging
        FORBIDDEN: business rules, behavioral switches, autonomous behavior flags
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Expected sections (technical only)
        expected_sections = {
            'paths',      # Directory paths
            'llm',        # LLM connection settings
            'excel',      # Excel status definitions
            'processing', # Technical processing settings
            'logging',    # Logging configuration
        }

        # Actual sections
        actual_sections = set(config.keys())

        # Check that all sections are expected
        unexpected_sections = actual_sections - expected_sections

        assert len(unexpected_sections) == 0, (
            f"Unexpected config sections found: {unexpected_sections}. "
            f"Iteration 2 only allows: {expected_sections}. "
            "Additional sections may introduce autonomous behavior."
        )

    def test_llm_config_does_not_enable_behavior(self):
        """
        GOVERNANCE: LLM config should only have technical settings.

        ALLOWED: backend, model, temperature, max_tokens, timeout
        FORBIDDEN: behavior modifiers, decision thresholds, quality gates
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'llm' in config, (
            "llm section not found in config."
        )

        llm_config = config['llm']

        # Expected LLM settings (technical only)
        expected_llm_keys = {
            'backend',
            'base_url',
            'model',
            'temperature',
            'max_tokens',
            'timeout_seconds',
        }

        # Actual LLM settings
        actual_llm_keys = set(llm_config.keys())

        # Check for unexpected settings
        unexpected_keys = actual_llm_keys - expected_llm_keys

        assert len(unexpected_keys) == 0, (
            f"Unexpected LLM config keys found: {unexpected_keys}. "
            f"Iteration 2 only allows: {expected_llm_keys}. "
            "Additional LLM settings may enable autonomous behavior."
        )

    def test_no_threshold_or_quality_gates_in_config(self):
        """
        GOVERNANCE: No threshold or quality gate settings in config.

        Thresholds enable AI decision-making based on scores.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            content = f.read()
            config = yaml.safe_load(f)

        # Check for threshold patterns in text
        forbidden_patterns = [
            'threshold',
            'quality_gate',
            'minimum_quality',
            'score_cutoff',
            'confidence_threshold',
            'similarity_threshold',
        ]

        content_lower = content.lower()

        for pattern in forbidden_patterns:
            # Check in keys (only if config is not None)
            if config is not None:
                def check_keys(d, path=""):
                    for key in d.keys():
                        if pattern in key.lower():
                            pytest.fail(
                                f"Threshold/quality gate pattern '{pattern}' found in config at {path}.{key}. "
                                "Thresholds enable AI decision-making."
                            )
                        if isinstance(d[key], dict):
                            check_keys(d[key], f"{path}.{key}" if path else key)

                check_keys(config)

    def test_processing_config_is_technical_only(self):
        """
        GOVERNANCE: Processing config should only have technical settings.

        ALLOWED: batch_size, max_retries, retry_delay
        FORBIDDEN: behavior modifiers, decision logic
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        if 'processing' in config:
            processing_config = config['processing']

            # Expected processing settings (technical only)
            expected_keys = {
                'batch_size',
                'max_retries',
                'retry_delay_seconds',
            }

            # Actual processing settings
            actual_keys = set(processing_config.keys())

            # Check for unexpected settings
            unexpected_keys = actual_keys - expected_keys

            assert len(unexpected_keys) == 0, (
                f"Unexpected processing config keys found: {unexpected_keys}. "
                f"Iteration 2 only allows: {expected_keys}. "
                "Additional processing settings may enable autonomous behavior."
            )


# ============================================================================
# CATEGORY 5: EXCEL CONFIG ENFORCES OWNERSHIP MODEL
# ============================================================================

class TestExcelOwnershipConfig:
    """Verify that Excel configuration enforces ownership model."""

    def test_excel_config_defines_all_statuses(self):
        """
        GOVERNANCE: Excel config must define all valid statuses.

        This documents the ownership model explicitly.
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'excel' in config, (
            "excel section not found in config."
        )

        assert 'statuses' in config['excel'], (
            "statuses not found in excel section."
        )

        # Expected statuses
        expected_statuses = {'candidate', 'consolidated', 'final', 'archived'}
        actual_statuses = set(config['excel']['statuses'])

        assert actual_statuses == expected_statuses, (
            f"Excel statuses mismatch. Expected: {expected_statuses}, Found: {actual_statuses}. "
            "All four statuses must be defined."
        )

    def test_excel_config_declares_human_owned_statuses(self):
        """
        GOVERNANCE: Excel config must declare human-owned statuses.

        This documents which statuses are human-owned (read-only).
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert 'human_owned_statuses' in config['excel'], (
            "human_owned_statuses not found in excel section. "
            "System must document which statuses are human-owned."
        )

        # Check that the right statuses are marked as human-owned
        human_owned = set(config['excel']['human_owned_statuses'])
        expected_human_owned = {'consolidated', 'final', 'archived'}

        assert human_owned == expected_human_owned, (
            f"human_owned_statuses incorrect. Expected: {expected_human_owned}, Found: {human_owned}. "
            "Only 'consolidated', 'final', and 'archived' should be human-owned."
        )

    def test_candidate_not_marked_as_human_owned(self):
        """
        GOVERNANCE: 'candidate' status must NOT be in human_owned_statuses.

        Candidates are AI-generated and system-modifiable (until humans own them).
        """
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)

        human_owned = set(config['excel']['human_owned_statuses'])

        assert 'candidate' not in human_owned, (
            "'candidate' status marked as human-owned. "
            "Candidates are AI-generated and should be modifiable by the system."
        )


# ============================================================================
# CATEGORY 6: NO CONFIG FILES BEYOND CONFIG.YAML
# ============================================================================

class TestNoAdditionalConfigFiles:
    """Verify that no additional config files exist that could override safety."""

    def test_no_business_rules_yaml(self):
        """
        GOVERNANCE: business_rules.yaml must not exist in active config.

        The business_rules.yaml file from v1 contained auto_merge, auto_delete,
        and other forbidden settings.
        """
        project_root = Path(__file__).parent.parent.parent
        business_rules_path = project_root / "config" / "business_rules.yaml"

        assert not business_rules_path.exists(), (
            "business_rules.yaml found in config/ directory. "
            "This file from v1 contains forbidden autonomous behavior settings. "
            "It must remain archived."
        )

    def test_no_merge_policy_yaml(self):
        """
        GOVERNANCE: merge_policy.yaml must not exist in active config.
        """
        project_root = Path(__file__).parent.parent.parent
        merge_policy_path = project_root / "config" / "merge_policy.yaml"

        assert not merge_policy_path.exists(), (
            "merge_policy.yaml found in config/ directory. "
            "Merge policy configuration is forbidden."
        )

    def test_no_deletion_policy_yaml(self):
        """
        GOVERNANCE: deletion_policy.yaml must not exist in active config.
        """
        project_root = Path(__file__).parent.parent.parent
        deletion_policy_path = project_root / "config" / "deletion_policy.yaml"

        assert not deletion_policy_path.exists(), (
            "deletion_policy.yaml found in config/ directory. "
            "Deletion policy configuration is forbidden."
        )

    def test_only_config_yaml_exists(self):
        """
        GOVERNANCE: Only config.yaml should exist in active config directory.

        Additional config files could introduce autonomous behavior.
        """
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"

        # List all YAML files in config directory
        config_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml"))

        # Should only have config.yaml and __init__.py
        expected_files = {'config.yaml', '__init__.py'}
        actual_files = {f.name for f in config_files}

        # Remove expected files
        unexpected_files = actual_files - expected_files

        assert len(unexpected_files) == 0, (
            f"Unexpected config files found: {unexpected_files}. "
            f"Iteration 2 only allows: {expected_files}. "
            "Additional config files may introduce autonomous behavior."
        )
