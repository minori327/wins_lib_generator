"""
Configuration loader for Phase 7: Publish / Distribution Gate.

Loads and provides access to publish configuration from config/publish_config.yaml.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)

# Cached configuration
_publish_config: Optional[Dict[str, Any]] = None


def load_publish_config() -> Dict[str, Any]:
    """Load publish configuration from config/publish_config.yaml.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    global _publish_config

    if _publish_config is not None:
        return _publish_config

    config_path = Path("config/publish_config.yaml")

    if not config_path.exists():
        raise FileNotFoundError(f"Publish config not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        _publish_config = yaml.safe_load(f)

    logger.debug(f"Loaded publish configuration from {config_path}")

    return _publish_config


def get_audit_config() -> Dict[str, Any]:
    """Get audit logging configuration.

    Returns:
        Audit configuration dictionary
    """
    config = load_publish_config()
    return config.get("audit", {})


def get_defaults() -> Dict[str, Any]:
    """Get global default settings.

    Returns:
        Default settings dictionary
    """
    config = load_publish_config()
    return config.get("defaults", {})


def get_approval_matrix() -> Dict[str, bool]:
    """Get approval matrix for (channel, visibility) combinations.

    Returns:
        Dictionary mapping "channel:visibility" to approval_required boolean
    """
    config = load_publish_config()
    return config.get("approval_matrix", {})


def get_channel_config(channel_name: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific channel.

    Args:
        channel_name: Channel name (e.g., "website", "slack", "obsidian")

    Returns:
        Channel configuration dictionary, or None if channel not found
    """
    config = load_publish_config()
    channels = config.get("channels", {})
    return channels.get(channel_name)


def get_all_channel_configs() -> Dict[str, Dict[str, Any]]:
    """Get all channel configurations.

    Returns:
        Dictionary mapping channel names to their configurations
    """
    config = load_publish_config()
    return config.get("channels", {})


def get_visibility_rules() -> Dict[str, Dict[str, Any]]:
    """Get visibility rules for channels.

    Returns:
        Dictionary mapping visibility levels to allowed/disallowed channels
    """
    config = load_publish_config()
    return config.get("visibility_rules", {})


def get_file_routing_config() -> Dict[str, Dict[str, Any]]:
    """Get file routing configuration.

    Returns:
        Dictionary mapping artifact types to routing destinations
    """
    config = load_publish_config()
    return config.get("file_routing", {})


def get_scheduled_publishing_config() -> Dict[str, Any]:
    """Get scheduled publishing configuration.

    Returns:
        Scheduled publishing settings dictionary
    """
    config = load_publish_config()
    return config.get("scheduled_publishing", {})


def get_rollback_config() -> Dict[str, Any]:
    """Get rollback configuration.

    Returns:
        Rollback settings dictionary
    """
    config = load_publish_config()
    return config.get("rollback", {})


def is_channel_enabled(channel_name: str) -> bool:
    """Check if a channel is enabled.

    Args:
        channel_name: Channel name to check

    Returns:
        True if channel is enabled, False otherwise
    """
    channel_config = get_channel_config(channel_name)
    if not channel_config:
        return False
    return channel_config.get("enabled", False)


def get_channel_adapter(channel_name: str) -> Optional[str]:
    """Get adapter type for a channel.

    Args:
        channel_name: Channel name

    Returns:
        Adapter type string (e.g., "api", "filesystem", "smtp"), or None
    """
    channel_config = get_channel_config(channel_name)
    if not channel_config:
        return None
    return channel_config.get("adapter")


def get_channel_destinations(channel_name: str) -> Dict[str, Any]:
    """Get destinations for a channel.

    Args:
        channel_name: Channel name

    Returns:
        Dictionary of destinations (e.g., {"production": {...}, "staging": {...}})
    """
    channel_config = get_channel_config(channel_name)
    if not channel_config:
        return {}
    return channel_config.get("destinations", {})


def reload_publish_config() -> Dict[str, Any]:
    """Reload publish configuration from file.

    Clears the cache and reloads configuration.

    Returns:
        Reloaded configuration dictionary
    """
    global _publish_config
    _publish_config = None
    return load_publish_config()
