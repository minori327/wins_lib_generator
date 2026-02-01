"""
Publish Gate Agent for Phase 7: Publish / Distribution Gate.

Evaluates publish requests for Phase 6 outputs and makes decisions about:
- Publish eligibility
- Channel routing
- Visibility enforcement
- Approval requirements

Phase 7 does NOT modify content or apply business logic (Phase 5 responsibility).
"""

import logging
import hashlib
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

from models.publish import (
    PublishRequest,
    PublishDecision,
    PublishRecord,
    Channel,
    VisibilityLevel,
    ApprovalStatus,
    RollbackResult
)
from utils.publish_config_loader import (
    load_publish_config,
    get_channel_config,
    get_approval_matrix,
    get_visibility_rules,
    get_file_routing_config
)

logger = logging.getLogger(__name__)


def generate_publish_record_id() -> str:
    """Generate unique publish record ID.

    Returns:
        Unique record identifier (format: pub-{timestamp}-{hash})
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rand_hash = hashlib.sha256(timestamp.encode()).digest()[:4].hex()
    return f"pub-{timestamp}-{rand_hash}"


def validate_publish_request(request: PublishRequest) -> None:
    """Validate publish request for required fields and constraints.

    Args:
        request: PublishRequest to validate

    Raises:
        ValueError: If request is invalid
    """
    if not request.artifact_id:
        raise ValueError("artifact_id is required")

    if not request.artifact_type:
        raise ValueError("artifact_type is required")

    if not request.source_file:
        raise ValueError("source_file is required")

    if not request.source_file.exists():
        raise ValueError(f"Source file does not exist: {request.source_file}")

    if not request.channel:
        raise ValueError("channel is required")

    if not request.visibility:
        raise ValueError("visibility is required")


def check_visibility_rules(
    channel: Channel,
    visibility: VisibilityLevel
) -> bool:
    """Check if visibility level is allowed for the channel.

    Args:
        channel: Target channel
        visibility: Visibility level

    Returns:
        True if visibility is allowed for this channel, False otherwise
    """
    rules = get_visibility_rules()

    # Get rules for this visibility level
    visibility_key = visibility.value
    if visibility_key not in rules:
        logger.warning(f"No visibility rules defined for {visibility_key}, allowing by default")
        return True

    visibility_rules = rules[visibility_key]

    # Check disallowed channels first (deny takes precedence)
    disallowed = visibility_rules.get("disallowed_channels", [])
    if channel.value in disallowed:
        logger.debug(f"Channel {channel.value} is disallowed for visibility {visibility.value}")
        return False

    # Check allowed channels
    allowed = visibility_rules.get("allowed_channels", [])
    if "*" in allowed or channel.value in allowed:
        return True

    logger.debug(f"Channel {channel.value} not in allowed list for visibility {visibility.value}")
    return False


def determine_approval_required(
    channel: Channel,
    visibility: VisibilityLevel,
    human_approved: bool = None
) -> bool:
    """Determine if human approval is required for this (channel, visibility) combination.

    Args:
        channel: Target channel
        visibility: Visibility level
        human_approved: Whether human has already approved (overrides matrix)

    Returns:
        True if human approval is required, False if system can auto-approve
    """
    # If human has already explicitly approved, no additional approval needed
    if human_approved is True:
        return False

    # Check approval matrix
    matrix = get_approval_matrix()
    key = f"{channel.value}:{visibility.value}"

    # Look up in matrix
    if key in matrix:
        return matrix[key]

    # Fall back to global default
    config = load_publish_config()
    return config.get("defaults", {}).get("human_approval_required", True)


def determine_routing_destination(
    request: PublishRequest,
    channel_config: Dict[str, Any]
) -> str:
    """Determine the specific destination within a channel.

    Args:
        request: PublishRequest
        channel_config: Channel configuration dictionary

    Returns:
        Destination string (URL, file path, email address, etc.)
    """
    channel = request.channel.value

    # File routing configuration (for filesystem adapters)
    if channel_config.get("adapter") == "filesystem":
        file_routing = get_file_routing_config()

        # Check if this artifact type has specific routing
        if request.artifact_type in file_routing:
            routing = file_routing[request.artifact_type]
            base_path = routing.get("base_path", "vault")
            subdirectory = routing.get("subdirectory", "")
            return str(Path(base_path) / subdirectory)

        # Use channel's default file routing
        if "file_routing" in channel_config:
            file_routing_config = channel_config["file_routing"]
            base_path = file_routing_config.get("base_path", "vault")
            subdirectory = file_routing_config.get("subdirectory", "")
            return str(Path(base_path) / subdirectory)

        # Fallback
        return f"vault/{channel}"

    # API-based channels (website, CMS, CRM, Slack)
    if "destinations" in channel_config:
        destinations = channel_config["destinations"]

        # Use production destination by default
        if "production" in destinations:
            return destinations["production"]["url"]
        elif "staging" in destinations:
            return destinations["staging"]["url"]
        else:
            # Use first available destination
            first_key = list(destinations.keys())[0]
            return destinations[first_key]["url"]

    # Email channel
    if channel == Channel.EMAIL:
        destinations = channel_config.get("destinations", {})
        visibility_key = request.visibility.value

        if visibility_key in destinations:
            return destinations[visibility_key]["to"]
        elif "internal" in destinations:
            return destinations["internal"]["to"]

    # Fallback
    logger.warning(f"Could not determine destination for {channel}, using default")
    return f"{channel}://default"


def evaluate_publish_request(request: PublishRequest) -> PublishDecision:
    """Evaluate publish request and make publish decision.

    This is the main Phase 7 decision function. It evaluates the request
    against visibility rules, approval requirements, and routing configuration.

    Args:
        request: PublishRequest to evaluate

    Returns:
        PublishDecision with approval status and routing information

    Raises:
        ValueError: If request is invalid or violates visibility rules
    """
    # Validate request
    validate_publish_request(request)

    # Get channel configuration
    channel_config = get_channel_config(request.channel.value)
    if not channel_config:
        raise ValueError(f"Channel not configured: {request.channel.value}")

    # Check if channel is enabled
    if not channel_config.get("enabled", False):
        return PublishDecision(
            approved=False,
            route_to_channel=request.channel,
            destination="",
            denial_reason=f"Channel {request.channel.value} is disabled in configuration"
        )

    # Check visibility rules
    if not check_visibility_rules(request.channel, request.visibility):
        return PublishDecision(
            approved=False,
            route_to_channel=request.channel,
            destination="",
            denial_reason=f"Visibility level {request.visibility.value} is not allowed for channel {request.channel.value}"
        )

    # Determine if human approval is required
    requires_approval = determine_approval_required(
        request.channel,
        request.visibility,
        request.human_approved
    )

    # Check if human has already approved
    approval_status = ApprovalStatus.APPROVED if request.human_approved else ApprovalStatus.PENDING

    # If human approval required but not granted, deny
    if requires_approval and not request.human_approved:
        return PublishDecision(
            approved=False,
            route_to_channel=request.channel,
            destination="",
            denial_reason=f"Human approval required for {request.channel.value}/{request.visibility.value} but not granted",
            requires_human_approval=True,
            approval_status=ApprovalStatus.PENDING
        )

    # Determine routing destination
    destination = determine_routing_destination(request, channel_config)

    # Check if scheduled for later
    scheduled_for = request.scheduled_for
    if scheduled_for:
        # Scheduled publish
        return PublishDecision(
            approved=True,
            route_to_channel=request.channel,
            destination=destination,
            scheduled_for=scheduled_for,
            requires_human_approval=requires_approval,
            approval_status=approval_status
        )

    # Immediate publish
    return PublishDecision(
        approved=True,
        route_to_channel=request.channel,
        destination=destination,
        requires_human_approval=requires_approval,
        approval_status=approval_status
    )


def create_publish_record(
    request: PublishRequest,
    decision: PublishDecision,
    status: str = "published",
    error_message: str = ""
) -> PublishRecord:
    """Create publish record for audit log.

    Args:
        request: Original PublishRequest
        decision: PublishDecision from evaluate_publish_request()
        status: Publish status ("published", "scheduled", "failed")
        error_message: Error message if status="failed"

    Returns:
        PublishRecord for audit logging
    """
    record_id = generate_publish_record_id()
    published_at = datetime.utcnow().isoformat() + "Z"

    # Determine approval status
    if request.human_approved:
        approval_status = "approved"
        approved_by = request.approved_by or "human"
    elif decision.requires_human_approval:
        approval_status = "auto_approved"
        approved_by = "system"
    else:
        approval_status = "system_approved"
        approved_by = "system"

    # Determine rollback capability
    can_rollback = status == "published" and decision.route_to_channel in [
        Channel.WEBSITE,
        Channel.CMS,
        Channel.OBSIDIAN,
        Channel.FILESYSTEM
    ]

    return PublishRecord(
        record_id=record_id,
        published_at=published_at,
        artifact_id=request.artifact_id,
        artifact_type=request.artifact_type,
        source_file=str(request.source_file),
        channel=decision.route_to_channel.value,
        visibility=request.visibility.value,
        destination=decision.destination,
        approved_by=approved_by,
        approval_status=approval_status,
        status=status,
        error_message=error_message,
        can_rollback=can_rollback,
        metadata=request.metadata
    )


def approve_publish_request(
    request: PublishRequest,
    approved_by: str
) -> PublishRequest:
    """Add human approval to a publish request.

    Args:
        request: PublishRequest to approve
        approved_by: Identifier for human approver

    Returns:
        New PublishRequest with approval fields set
    """
    return PublishRequest(
        artifact_id=request.artifact_id,
        artifact_type=request.artifact_type,
        source_file=request.source_file,
        channel=request.channel,
        visibility=request.visibility,
        human_approved=True,
        approved_by=approved_by,
        approved_at=datetime.utcnow().isoformat() + "Z",
        scheduled_for=request.scheduled_for,
        metadata=request.metadata,
        requested_by=request.requested_by,
        requested_at=request.requested_at
    )


def schedule_publish_request(
    request: PublishRequest,
    publish_at: str
) -> PublishRequest:
    """Schedule a publish request for future execution.

    Args:
        request: PublishRequest to schedule
        publish_at: ISO-8601 timestamp for scheduled publish

    Returns:
        New PublishRequest with scheduled_for set
    """
    # Validate timestamp format and constraints
    try:
        scheduled_time = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"Invalid ISO-8601 timestamp: {publish_at}")

    now = datetime.utcnow()
    if scheduled_time < now:
        raise ValueError(f"Scheduled time must be in the future: {publish_at}")

    return PublishRequest(
        artifact_id=request.artifact_id,
        artifact_type=request.artifact_type,
        source_file=request.source_file,
        channel=request.channel,
        visibility=request.visibility,
        human_approved=request.human_approved,
        approved_by=request.approved_by,
        approved_at=request.approved_at,
        scheduled_for=publish_at,
        metadata=request.metadata,
        requested_by=request.requested_by,
        requested_at=request.requested_at
    )
