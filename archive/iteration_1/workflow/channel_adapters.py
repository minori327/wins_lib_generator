"""
Channel adapters for Phase 7: Publish / Distribution Gate.

Channel adapters handle the actual delivery of published content to various destinations.
Each adapter encapsulates the protocol-specific logic for publishing.

This is an abstract interface - concrete implementations are provided for common channels.
"""

import logging
import os
import shutil
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ChannelAdapter(ABC):
    """Abstract base class for channel adapters.

    Channel adapters encapsulate the protocol-specific logic for delivering
    content to various distribution channels (APIs, file systems, email, etc.).
    """

    def __init__(self, channel_config: Dict[str, Any]):
        """Initialize adapter with channel configuration.

        Args:
            channel_config: Channel configuration dictionary
        """
        self.config = channel_config
        self.channel_name = channel_config.get("name", "unknown")

    @abstractmethod
    def publish(self, source_file: Path, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Publish content from source file to destination.

        Args:
            source_file: Path to source file (Phase 6 output)
            destination: Destination string (URL, file path, email address, etc.)
            metadata: Additional metadata for the publish operation

        Returns:
            True if publish succeeded, False otherwise
        """
        pass

    @abstractmethod
    def rollback(self, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Rollback a published artifact.

        Args:
            destination: Destination that was published to
            metadata: Additional metadata for the rollback operation

        Returns:
            True if rollback succeeded, False otherwise
        """
        pass

    def validate(self) -> bool:
        """Validate adapter configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        return True


class LocalFileAdapter(ChannelAdapter):
    """Adapter for publishing to local file system.

    Used for channels like Obsidian vault where files are copied to a local directory.
    """

    def publish(self, source_file: Path, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Publish file to local file system.

        Args:
            source_file: Path to source file
            destination: Destination directory path (as string)
            metadata: Optional metadata (not used for filesystem adapter)

        Returns:
            True if publish succeeded, False otherwise
        """
        try:
            source_path = Path(source_file)
            dest_path = Path(destination)

            # Validate source exists
            if not source_path.exists():
                logger.error(f"Source file does not exist: {source_path}")
                return False

            # Create destination directory if needed
            dest_path.mkdir(parents=True, exist_ok=True)

            # Determine target file path
            target_file = dest_path / source_path.name

            # Check overwrite behavior
            overwrite = self.config.get("overwrite_existing", True)
            if not overwrite and target_file.exists():
                logger.error(f"Target file exists and overwrite=False: {target_file}")
                return False

            # Copy file
            shutil.copy2(source_path, target_file)

            logger.info(f"Published {source_path} to {target_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish to local file system: {e}")
            return False

    def rollback(self, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Rollback published file by deleting it.

        Args:
            destination: File path that was published
            metadata: Optional metadata

        Returns:
            True if rollback succeeded, False otherwise
        """
        try:
            file_path = Path(destination)

            if not file_path.exists():
                logger.warning(f"File to rollback does not exist: {file_path}")
                return True  # Already rolled back

            # Delete file
            file_path.unlink()

            logger.info(f"Rolled back file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback file: {e}")
            return False


class APIAdapter(ChannelAdapter):
    """Adapter for publishing to API-based channels.

    Used for channels like website, CMS, CRM that expose REST APIs.
    This is a stub implementation - real API integration requires protocol-specific code.
    """

    def __init__(self, channel_config: Dict[str, Any]):
        super().__init__(channel_config)
        self.headers = channel_config.get("headers", {})

    def publish(self, source_file: Path, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Publish content via API (stub implementation).

        Args:
            source_file: Path to source file
            destination: API URL
            metadata: Optional metadata

        Returns:
            True if publish succeeded, False otherwise
        """
        # STUB IMPLEMENTATION
        # In production, this would:
        # 1. Read source file content
        # 2. Format according to channel's format (JSON, XML, etc.)
        # 3. Make HTTP request to destination URL
        # 4. Handle authentication via env_var or credentials
        # 5. Parse response and return success/failure

        logger.info(f"[STUB] API publish to {destination} from {source_file}")
        logger.warning("APIAdapter is a stub - implement actual HTTP requests for production")

        # Simulate success
        return True

    def rollback(self, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Rollback API publish (stub implementation).

        Args:
            destination: API URL for rollback
            metadata: Optional metadata

        Returns:
            True if rollback succeeded, False otherwise
        """
        # STUB IMPLEMENTATION
        # In production, this would make DELETE or PATCH request to the API

        logger.info(f"[STUB] API rollback at {destination}")
        logger.warning("APIAdapter rollback is a stub - implement actual HTTP requests for production")

        # Simulate success
        return True


class SlackAdapter(ChannelAdapter):
    """Adapter for publishing to Slack via webhooks."""

    def publish(self, source_file: Path, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Publish message to Slack webhook (stub implementation).

        Args:
            source_file: Path to source file (used to generate message content)
            destination: Slack webhook URL
            metadata: Optional metadata

        Returns:
            True if publish succeeded, False otherwise
        """
        # STUB IMPLEMENTATION
        # In production, this would:
        # 1. Read source file or extract key info
        # 2. Format Slack message payload
        # 3. POST to webhook URL
        # 4. Handle response

        logger.info(f"[STUB] Slack publish to webhook {destination}")
        logger.warning("SlackAdapter is a stub - implement actual webhook calls for production")

        return True

    def rollback(self, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Rollback not supported for Slack.

        Args:
            destination: Webhook URL
            metadata: Optional metadata

        Returns:
            False (rollback not supported)
        """
        logger.warning("Rollback not supported for Slack messages")
        return False


class EmailAdapter(ChannelAdapter):
    """Adapter for publishing via email (SMTP)."""

    def publish(self, source_file: Path, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Send email with file attachment (stub implementation).

        Args:
            source_file: Path to file to attach
            destination: Email recipient address
            metadata: Optional metadata (subject, from, etc.)

        Returns:
            True if email sent successfully, False otherwise
        """
        # STUB IMPLEMENTATION
        # In production, this would:
        # 1. Connect to SMTP server
        # 2. Compose email with attachment
        # 3. Send to recipient
        # 4. Handle retries

        logger.info(f"[STUB] Email to {destination} with attachment {source_file}")
        logger.warning("EmailAdapter is a stub - implement actual SMTP calls for production")

        return True

    def rollback(self, destination: str, metadata: Dict[str, Any] = None) -> bool:
        """Rollback not supported for email.

        Args:
            destination: Email address
            metadata: Optional metadata

        Returns:
            False (rollback not supported)
        """
        logger.warning("Rollback not supported for email")
        return False


def create_channel_adapter(channel_name: str, channel_config: Dict[str, Any]) -> ChannelAdapter:
    """Factory function to create channel adapter based on configuration.

    Args:
        channel_name: Name of the channel
        channel_config: Channel configuration dictionary

    Returns:
        ChannelAdapter instance

    Raises:
        ValueError: If adapter type is unknown
    """
    adapter_type = channel_config.get("adapter", "filesystem")

    # Set channel name in config for adapter use
    channel_config["name"] = channel_name

    if adapter_type == "filesystem":
        return LocalFileAdapter(channel_config)
    elif adapter_type == "api":
        return APIAdapter(channel_config)
    elif adapter_type == "slack":
        return SlackAdapter(channel_config)
    elif adapter_type == "smtp":
        return EmailAdapter(channel_config)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type} for channel {channel_name}")
