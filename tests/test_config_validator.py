"""
Test configuration validation.
"""

import pytest
import yaml
from pathlib import Path
from utils.config_validator import (
    validate_config_file,
    validate_all_configs,
    _validate_main_config
)


class TestConfigValidation:
    """Test configuration file validation."""

    def test_config_yaml_syntax(self, tmp_path):
        """Test YAML syntax validation."""
        # Create valid YAML file
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
paths:
  vault_root: "./vault"
  library_dir: "./wins"

llm:
  backend: "ollama"
  model: "glm-4:9b"
        """)

        errors = validate_config_file(config_file)
        assert len(errors) == 0

    def test_config_yaml_syntax_invalid(self, tmp_path):
        """Test YAML syntax validation with invalid YAML."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
paths:
  vault_root: "./vault"
  library_dir: ["wins"  # Invalid YAML - list instead of string
        """)

        errors = validate_config_file(config_file)
        assert len(errors) > 0

    def test_config_required_keys(self, tmp_path):
        """Test required top-level keys in main config."""
        # Missing required sections
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
paths:
  vault_root: "./vault"
        """)

        errors = validate_config_file(config_file)
        assert len(errors) > 0
        assert any("llm" in e for e in errors)

    def test_config_paths_exist(self, tmp_path):
        """Test path configuration validation."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
paths:
  library_dir: "./wins"
        """)

        errors = validate_config_file(config_file)
        # Should warn about missing vault_root and sources_dir
        assert len(errors) >= 1

    def test_validate_all_configs(self, tmp_path, monkeypatch):
        """Test validating all config files."""
        # Create test config files
        (tmp_path / "config.yaml").write_text("paths:\n  vault_root: ./vault")
        (tmp_path / "business_rules.yaml").write_text("success_evaluation:\n  enabled: true")
        (tmp_path / "output_config.yaml").write_text("templates:\n  base_dir: ./templates")
        (tmp_path / "publish_config.yaml").write_text("channels:\n  website:\n    enabled: false")

        # Patch Path.exists to return True
        def mock_exists(self):
            return True

        monkeypatch.setattr(Path, "exists", mock_exists)

        is_valid = validate_all_configs(tmp_path)
        assert is_valid is True

    def test_validate_main_config_complete(self):
        """Test complete main config validation."""
        config = {
            "paths": {
                "vault_root": "./vault",
                "sources_dir": "./vault/00_sources",
                "library_dir": "./wins",
                "outputs_dir": "./vault/outputs"
            },
            "llm": {
                "backend": "ollama",
                "base_url": "http://localhost:11434",
                "model": "glm-4:9b"
            },
            "processing": {
                "batch_size": 10
            }
        }

        errors = _validate_main_config(config)
        assert len(errors) == 0
