"""
Load output configuration from YAML file.

Centralized configuration loader for all Phase 6 output settings.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


# Global cache for config
_config_cache: Dict[str, Any] = None


def load_output_config(config_path: Path = None) -> Dict[str, Any]:
    """Load output configuration from YAML file.

    Args:
        config_path: Path to output_config.yaml. If None, uses default path.

    Returns:
        Dictionary with parsed output configuration

    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If config file is invalid
    """
    global _config_cache

    # Use default path if not provided
    if config_path is None:
        # Default: config/output_config.yaml relative to project root
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "output_config.yaml"

    # Check cache first
    if _config_cache is not None:
        return _config_cache

    if not config_path.exists():
        logger.error(f"Output config not found: {config_path}")
        raise FileNotFoundError(f"Output config not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Validate required sections
        required_sections = [
            "templates",
            "output_destinations",
            "generation",
            "obsidian",
            "executive_format",
            "marketing_format"
        ]

        missing = [s for s in required_sections if s not in config]
        if missing:
            raise ValueError(f"Missing required config sections: {missing}")

        # Cache the config
        _config_cache = config

        logger.info(f"Loaded output config from {config_path}")

        return config

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML config: {e}")
        raise ValueError(f"Invalid YAML config: {e}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise


def get_template_settings(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get template settings from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with template settings
    """
    if config is None:
        config = load_output_config()

    return config["templates"]


def get_output_destinations(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get output destination settings from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with output destination settings
    """
    if config is None:
        config = load_output_config()

    return config["output_destinations"]


def get_generation_settings(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get generation settings from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with generation settings
    """
    if config is None:
        config = load_output_config()

    return config["generation"]


def get_obsidian_settings(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get Obsidian-specific settings from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with Obsidian settings
    """
    if config is None:
        config = load_output_config()

    return config["obsidian"]


def clear_config_cache():
    """Clear cached config (useful for testing or config reload)."""
    global _config_cache
    _config_cache = None
    logger.debug("Output config cache cleared")
