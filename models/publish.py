"""
Publish models for Phase 7: Publish / Distribution Gate.

Defines data structures for publish requests, decisions, records, and audit logs.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from pathlib import Path


class Channel(str, Enum):
    """Publish channel types."""

    WEBSITE = "website"
    CMS = "cms"
    CRM = "crm"
    SLACK = "slack"
    EMAIL = "email"
    OBSIDIAN = "obsidian"
    FILESYSTEM = "filesystem"


class VisibilityLevel(str, Enum):
    """Visibility levels for published content."""

    PUBLIC = "public"  # Publicly accessible
    EXTERNAL = "external"  # External customers/partners
    INTERNAL = "internal"  # Internal team only
    RESTRICTED = "restricted"  # Restricted access (e.g., leadership only)


class ApprovalStatus(str, Enum):
    """Approval status for publish requests."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"


@dataclass
class PublishRequest:
    """Request to publish a Phase 6 output artifact.

    Phase 7 receives publish requests and makes decisions about eligibility,
    routing, and approval requirements.
    """

    # Artifact identification
    artifact_id: str  # Unique identifier for the artifact (e.g., story ID)
    artifact_type: str  # Type of artifact (e.g., "executive_output", "marketing_output", "obsidian_note")
    source_file: Path  # Path to the Phase 6 output file

    # Publish destination
    channel: Channel  # Target channel
    visibility: VisibilityLevel  # Visibility level for the published content

    # Approval control
    human_approved: bool = False  # Whether human has explicitly approved this request
    approved_by: str = ""  # Identifier for human approver (if human_approved=True)
    approved_at: str = ""  # ISO-8601 timestamp of approval (if human_approved=True)

    # Scheduling
    scheduled_for: Optional[str] = None  # ISO-8601 timestamp for delayed publishing (None = immediate)

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context for the publish request
    requested_by: str = "system"  # Who requested the publish (human or system)
    requested_at: str = ""  # ISO-8601 timestamp of request (filled by system if empty)


@dataclass
class PublishRecord:
    """Immutable record of a publish action (audit log entry).

    Every publish action creates a PublishRecord for auditability.
    Records are immutable and never modified after creation.
    """

    # Record identification
    record_id: str  # Unique identifier for this record
    published_at: str  # ISO-8601 timestamp when publish was executed

    # Artifact information
    artifact_id: str  # ID of the published artifact
    artifact_type: str  # Type of artifact
    source_file: str  # Path to source file (string for serialization)

    # Publish destination
    channel: str  # Channel name
    visibility: str  # Visibility level
    destination: str  # Actual destination (URL, file path, email address, etc.)

    # Approval information
    approved_by: str  # Who approved (human identifier or "system")
    approval_status: str  # "approved", "auto_approved", etc.

    # Outcome
    status: str  # "published", "scheduled", "failed"
    error_message: str = ""  # Error details if status="failed"

    # Rollback capability
    can_rollback: bool = False  # Whether this publish can be rolled back
    rolled_back: bool = False  # Whether rollback has been performed
    rolled_back_at: str = ""  # ISO-8601 timestamp of rollback (if rolled_back=True)
    rolled_back_by: str = ""  # Who performed the rollback

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishDecision:
    """Decision made by Phase 7 publish gate agent.

    The agent evaluates PublishRequest and produces a PublishDecision
    indicating whether to publish, deny, or schedule the request.
    """

    # Decision outcome
    approved: bool  # Whether the request is approved for publishing
    route_to_channel: Channel  # Which channel to route to (may differ from request)
    destination: str  # Specific destination within the channel (URL, path, etc.)

    # Denial reason (if approved=False)
    denial_reason: str = ""  # Human-readable explanation if denied

    # Scheduling (if not publishing immediately)
    scheduled_for: Optional[str] = None  # ISO-8601 timestamp if scheduled for later

    # Conditions
    requires_human_approval: bool = False  # Whether human approval is required
    approval_status: ApprovalStatus = ApprovalStatus.PENDING  # Current approval status

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context from the decision


@dataclass
class RollbackResult:
    """Result of a rollback operation."""

    success: bool  # Whether rollback was successful
    record_id: str  # Record ID that was rolled back
    channel: str  # Channel that was rolled back
    destination: str  # Destination that was rolled back
    rolled_back_at: str  # ISO-8601 timestamp of rollback
    rolled_back_by: str  # Who performed the rollback
    error_message: str = ""  # Error details if success=False
