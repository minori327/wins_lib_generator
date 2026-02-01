"""
Configuration validation utilities for Wins Library System v1.0.

Validates all YAML configuration files at startup.
"""

import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def validate_config_file(config_path: Path) -> List[str]:
    """Validate a single YAML configuration file.

    Args:
        config_path: Path to YAML file

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not config_path.exists():
        return [f"File not found: {config_path}"]

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML syntax error: {e}"]

    # Validate structure based on file type
    filename = config_path.name

    if filename == "config.yaml":
        errors.extend(_validate_main_config(config))
    elif filename == "business_rules.yaml":
        errors.extend(_validate_business_rules(config))
    elif filename == "output_config.yaml":
        errors.extend(_validate_output_config(config))
    elif filename == "publish_config.yaml":
        errors.extend(_validate_publish_config(config))

    return errors


def _validate_main_config(config: Dict[str, Any]) -> List[str]:
    """Validate main config.yaml structure."""
    errors = []

    # Check required top-level keys
    required_sections = ["paths", "llm", "processing"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    # Validate paths section
    if "paths" in config:
        required_paths = ["vault_root", "sources_dir", "library_dir", "outputs_dir"]
        for path_key in required_paths:
            if path_key not in config["paths"]:
                errors.append(f"Missing path: paths.{path_key}")

    # Validate LLM section
    if "llm" in config:
        required_llm = ["backend", "base_url", "model"]
        for llm_key in required_llm:
            if llm_key not in config["llm"]:
                errors.append(f"Missing LLM setting: llm.{llm_key}")

    return errors


def _validate_business_rules(config: Dict[str, Any]) -> List[str]:
    """Validate business_rules.yaml structure."""
    errors = []

    # Check required sections
    required_sections = ["success_evaluation", "ranking", "merge_policy", "deletion_policy"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    return errors


def _validate_output_config(config: Dict[str, Any]) -> List[str]:
    """Validate output_config.yaml structure."""
    errors = []

    # Check required sections
    required_sections = ["templates", "output_destinations", "generation"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    return errors


def _validate_publish_config(config: Dict[str, Any]) -> List[str]:
    """Validate publish_config.yaml structure."""
    errors = []

    # Check required sections
    required_sections = ["audit", "channels"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    return errors


def validate_all_configs(config_dir: Path) -> bool:
    """Validate all configuration files in directory.

    Args:
        config_dir: Directory containing config files

    Returns:
        True if all configs are valid, False otherwise
    """
    configs = [
        "config.yaml",
        "business_rules.yaml",
        "output_config.yaml",
        "publish_config.yaml"
    ]

    all_valid = True

    for config_name in configs:
        config_path = config_dir / config_name
        errors = validate_config_file(config_path)

        if errors:
            print(f"❌ {config_name}")
            for error in errors:
                print(f"   - {error}")
            all_valid = False
        else:
            print(f"✅ {config_name}")

    return all_valid


def check_directories(config: Dict[str, Any]) -> List[str]:
    """Check if required directories exist or can be created.

    Args:
        config: Configuration dictionary

    Returns:
        List of warnings (empty if all OK)
    """
    warnings = []

    if "paths" not in config:
        return warnings

    paths = config["paths"]

    # Check source directory
    if "sources_dir" in paths:
        source_dir = Path(paths["sources_dir"])
        if not source_dir.exists():
            warnings.append(f"Source directory will be created: {source_dir}")

    # Check library directory
    if "library_dir" in paths:
        library_dir = Path(paths["library_dir"])
        if not library_dir.exists():
            warnings.append(f"Library directory will be created: {library_dir}")

    # Check output directory
    if "outputs_dir" in paths:
        output_dir = Path(paths["outputs_dir"])
        if not output_dir.exists():
            warnings.append(f"Output directory will be created: {output_dir}")

    return warnings


def check_llm_connectivity(config: Dict[str, Any]) -> bool:
    """Check if LLM server is reachable.

    Args:
        config: Configuration dictionary

    Returns:
        True if LLM is reachable, False otherwise
    """
    if "llm" not in config:
        return False

    llm_config = config["llm"]

    if llm_config.get("backend") != "ollama":
        logger.warning(f"LLM backend {llm_config.get('backend')} not supported yet")
        return False

    # Try to connect to Ollama
    import urllib.request
    import json

    base_url = llm_config.get("base_url", "http://localhost:11434")
    model = llm_config.get("model", "glm-4:9b")

    try:
        # Check if Ollama is running
        url = f"{base_url}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())

        # Check if model is available
        models = [m["name"] for m in data.get("models", [])]
        if model not in models:
            logger.warning(f"Model {model} not found. Available models: {models}")
            return False

        logger.info(f"✅ LLM connectivity OK: {base_url}, model: {model}")
        return True

    except Exception as e:
        logger.error(f"❌ LLM connectivity failed: {e}")
        return False
