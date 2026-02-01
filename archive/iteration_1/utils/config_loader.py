"""
Load business rules configuration from YAML file.

Centralized configuration loader for all Phase 5 business rules.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


# Global cache for config
_config_cache: Dict[str, Any] = None


def load_business_rules_config(config_path: Path = None) -> Dict[str, Any]:
    """Load business rules from YAML configuration file.

    Args:
        config_path: Path to business_rules.yaml. If None, uses default path.

    Returns:
        Dictionary with parsed business rules

    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If config file is invalid
    """
    global _config_cache

    # Use default path if not provided
    if config_path is None:
        # Default: config/business_rules.yaml relative to project root
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "business_rules.yaml"

    # Check cache first
    if _config_cache is not None:
        return _config_cache

    if not config_path.exists():
        logger.error(f"Business rules config not found: {config_path}")
        raise FileNotFoundError(f"Business rules config not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Validate required sections
        required_sections = [
            "success_evaluation",
            "ranking",
            "output_filters",
            "merge_policy",
            "deletion_policy",
            "human_override"
        ]

        missing = [s for s in required_sections if s not in config]
        if missing:
            raise ValueError(f"Missing required config sections: {missing}")

        # Cache the config
        _config_cache = config

        logger.info(f"Loaded business rules config from {config_path}")

        return config

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML config: {e}")
        raise ValueError(f"Invalid YAML config: {e}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise


def get_success_evaluation_rules(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get success evaluation rules from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with success evaluation rules
    """
    if config is None:
        config = load_business_rules_config()

    return config["success_evaluation"]


def get_ranking_rules(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get ranking rules from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with ranking rules
    """
    if config is None:
        config = load_business_rules_config()

    return config["ranking"]


def get_output_filter_rules(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get output filter rules from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with output filter rules
    """
    if config is None:
        config = load_business_rules_config()

    return config["output_filters"]


def get_merge_policy(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get merge policy from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with merge policy
    """
    if config is None:
        config = load_business_rules_config()

    return config["merge_policy"]


def get_deletion_policy(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get deletion policy from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with deletion policy
    """
    if config is None:
        config = load_business_rules_config()

    return config["deletion_policy"]


def get_human_override_settings(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get human override settings from config.

    Args:
        config: Config dict (if None, loads from file)

    Returns:
        Dictionary with human override settings
    """
    if config is None:
        config = load_business_rules_config()

    return config["human_override"]


def clear_config_cache():
    """Clear cached config (useful for testing or config reload)."""
    global _config_cache
    _config_cache = None
    logger.debug("Config cache cleared")
