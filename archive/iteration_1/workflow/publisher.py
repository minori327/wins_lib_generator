"""
Publisher workflow for Phase 7: Publish / Distribution Gate.

Orchestrates the publish flow: evaluate request, route to channel adapter,
execute publish, log to audit trail.

Phase 7 does NOT modify content - it only decides where and whether to publish.
"""

import logging
from pathlib import Path
from typing import Optional, List

from models.publish import (
    PublishRequest,
    PublishDecision,
    PublishRecord,
    RollbackResult,
    Channel
)
from agents.publish_gate_agent import (
    evaluate_publish_request,
    create_publish_record,
    approve_publish_request,
    schedule_publish_request
)
from workflow.publish_audit_log import (
    log_publish_action,
    get_publish_record,
    log_rollback
)
from workflow.channel_adapters import create_channel_adapter
from utils.publish_config_loader import (
    get_channel_config,
    is_channel_enabled,
    get_rollback_config
)

logger = logging.getLogger(__name__)


def publish_artifact(request: PublishRequest) -> PublishRecord:
    """Publish an artifact based on publish request.

    This is the main entry point for Phase 7 publishing.

    Args:
        request: PublishRequest describing what to publish

    Returns:
        PublishRecord documenting the publish action

    Raises:
        ValueError: If request is invalid
        OSError: If publish operation fails
    """
    # Step 1: Evaluate request (gate decision)
    decision = evaluate_publish_request(request)

    # Step 2: Create initial publish record
    if decision.approved:
        if decision.scheduled_for:
            # Scheduled publish
            record = create_publish_record(request, decision, status="scheduled")
            log_publish_action(record)
            logger.info(f"Scheduled publish for {request.artifact_id} at {decision.scheduled_for}")
            return record
        else:
            # Immediate publish - proceed to channel adapter
            return execute_publish(request, decision)
    else:
        # Denied - create failure record
        record = create_publish_record(
            request,
            decision,
            status="failed",
            error_message=decision.denial_reason
        )
        log_publish_action(record)
        logger.warning(f"Publish denied for {request.artifact_id}: {decision.denial_reason}")
        return record


def execute_publish(request: PublishRequest, decision: PublishDecision) -> PublishRecord:
    """Execute publish via channel adapter.

    Args:
        request: Original PublishRequest
        decision: PublishDecision from evaluate_publish_request()

    Returns:
        PublishRecord documenting the publish action

    Raises:
        OSError: If publish operation fails
    """
    channel = decision.route_to_channel.value
    destination = decision.destination

    logger.info(f"Publishing {request.artifact_id} to {channel} at {destination}")

    # Get channel configuration
    channel_config = get_channel_config(channel)
    if not channel_config:
        error = f"Channel configuration not found: {channel}"
        logger.error(error)
        record = create_publish_record(
            request,
            decision,
            status="failed",
            error_message=error
        )
        log_publish_action(record)
        return record

    # Create channel adapter
    try:
        adapter = create_channel_adapter(channel, channel_config)
    except ValueError as e:
        error = f"Failed to create channel adapter: {e}"
        logger.error(error)
        record = create_publish_record(
            request,
            decision,
            status="failed",
            error_message=error
        )
        log_publish_action(record)
        return record

    # Execute publish via adapter
    try:
        success = adapter.publish(
            source_file=request.source_file,
            destination=destination,
            metadata=request.metadata
        )

        if success:
            # Publish succeeded
            record = create_publish_record(request, decision, status="published")
            log_publish_action(record)
            logger.info(f"Successfully published {request.artifact_id} to {channel}")
            return record
        else:
            # Publish failed
            error = f"Channel adapter returned failure for {channel}"
            logger.error(error)
            record = create_publish_record(
                request,
                decision,
                status="failed",
                error_message=error
            )
            log_publish_action(record)
            return record

    except Exception as e:
        error = f"Exception during publish to {channel}: {e}"
        logger.error(error)
        record = create_publish_record(
            request,
            decision,
            status="failed",
            error_message=error
        )
        log_publish_action(record)
        return record


def approve_and_publish(
    base_request: PublishRequest,
    approved_by: str
) -> PublishRecord:
    """Approve a publish request and execute it.

    Convenience function that adds human approval and then publishes.

    Args:
        base_request: Base PublishRequest (without approval)
        approved_by: Identifier for human approver

    Returns:
        PublishRecord documenting the publish action
    """
    # Add approval to request
    approved_request = approve_publish_request(base_request, approved_by)

    # Publish
    return publish_artifact(approved_request)


def rollback_publish(
    record_id: str,
    rolled_back_by: str
) -> RollbackResult:
    """Rollback a previously published artifact.

    Args:
        record_id: Publish record ID to rollback
        rolled_back_by: Identifier for user performing rollback

    Returns:
        RollbackResult with rollback outcome

    Raises:
        ValueError: If record not found or rollback not supported
        OSError: If rollback operation fails
    """
    from datetime import datetime

    # Check if rollback is enabled
    rollback_config = get_rollback_config()
    if not rollback_config.get("enabled", True):
        raise ValueError("Rollback is disabled in configuration")

    # Find the publish record
    record = get_publish_record(record_id)
    if not record:
        raise ValueError(f"Publish record not found: {record_id}")

    # Check if rollback is supported for this channel
    if not record.can_rollback:
        return RollbackResult(
            success=False,
            record_id=record_id,
            channel=record.channel,
            destination=record.destination,
            rolled_back_at=datetime.utcnow().isoformat() + "Z",
            rolled_back_by=rolled_back_by,
            error_message=f"Rollback not supported for channel {record.channel}"
        )

    # Check if already rolled back
    if record.rolled_back:
        return RollbackResult(
            success=False,
            record_id=record_id,
            channel=record.channel,
            destination=record.destination,
            rolled_back_at=datetime.utcnow().isoformat() + "Z",
            rolled_back_by=rolled_back_by,
            error_message="Record already rolled back"
        )

    # Get channel adapter
    channel_config = get_channel_config(record.channel)
    if not channel_config:
        return RollbackResult(
            success=False,
            record_id=record_id,
            channel=record.channel,
            destination=record.destination,
            rolled_back_at=datetime.utcnow().isoformat() + "Z",
            rolled_back_by=rolled_back_by,
            error_message=f"Channel configuration not found: {record.channel}"
        )

    try:
        adapter = create_channel_adapter(record.channel, channel_config)
    except ValueError as e:
        return RollbackResult(
            success=False,
            record_id=record_id,
            channel=record.channel,
            destination=record.destination,
            rolled_back_at=datetime.utcnow().isoformat() + "Z",
            rolled_back_by=rolled_back_by,
            error_message=f"Failed to create channel adapter: {e}"
        )

    # Execute rollback
    try:
        success = adapter.rollback(
            destination=record.destination,
            metadata={"record_id": record_id}
        )

        if success:
            # Log rollback
            result = RollbackResult(
                success=True,
                record_id=record_id,
                channel=record.channel,
                destination=record.destination,
                rolled_back_at=datetime.utcnow().isoformat() + "Z",
                rolled_back_by=rolled_back_by
            )
            log_rollback(result, record_id)
            logger.info(f"Successfully rolled back {record_id}")
            return result
        else:
            # Rollback failed
            result = RollbackResult(
                success=False,
                record_id=record_id,
                channel=record.channel,
                destination=record.destination,
                rolled_back_at=datetime.utcnow().isoformat() + "Z",
                rolled_back_by=rolled_back_by,
                error_message="Channel adapter rollback returned failure"
            )
            return result

    except Exception as e:
        return RollbackResult(
            success=False,
            record_id=record_id,
            channel=record.channel,
            destination=record.destination,
            rolled_back_at=datetime.utcnow().isoformat() + "Z",
            rolled_back_by=rolled_back_by,
            error_message=f"Exception during rollback: {e}"
        )


def batch_publish(requests: List[PublishRequest]) -> List[PublishRecord]:
    """Publish multiple artifacts in batch.

    Args:
        requests: List of PublishRequest objects

    Returns:
        List of PublishRecord objects (one per request)
    """
    records = []

    for request in requests:
        try:
            record = publish_artifact(request)
            records.append(record)
        except Exception as e:
            logger.error(f"Failed to publish {request.artifact_id}: {e}")
            # Create failure record
            from models.publish import PublishDecision
            decision = PublishDecision(
                approved=False,
                route_to_channel=request.channel,
                destination="",
                denial_reason=f"Exception: {e}"
            )
            record = create_publish_record(
                request,
                decision,
                status="failed",
                error_message=str(e)
            )
            log_publish_action(record)
            records.append(record)

    return records


def can_publish_to_channel(
    channel: str,
    visibility: str
) -> bool:
    """Check if content with given visibility can be published to channel.

    Convenience function for pre-validation.

    Args:
        channel: Channel name
        visibility: Visibility level

    Returns:
        True if allowed, False otherwise
    """
    # Check channel is enabled
    if not is_channel_enabled(channel):
        return False

    # Check visibility rules via agent
    from models.publish import Channel, VisibilityLevel
    try:
        channel_enum = Channel(channel)
        visibility_enum = VisibilityLevel(visibility)
    except ValueError:
        return False

    from agents.publish_gate_agent import check_visibility_rules
    return check_visibility_rules(channel_enum, visibility_enum)
