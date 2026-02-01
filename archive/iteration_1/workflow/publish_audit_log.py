"""
Publish audit logging for Phase 7: Publish / Distribution Gate.

Maintains an immutable audit log of all publish actions for accountability and traceability.
"""

import logging
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from models.publish import PublishRecord, RollbackResult
from utils.publish_config_loader import get_audit_config

logger = logging.getLogger(__name__)


def log_publish_action(record: PublishRecord) -> None:
    """Log a publish action to the audit log.

    Args:
        record: PublishRecord to log

    Raises:
        OSError: If log file cannot be written
    """
    config = get_audit_config()

    if not config.get("enabled", True):
        logger.debug("Audit logging is disabled, skipping log entry")
        return

    log_file = config.get("log_file", "vault/publish_audit.log.jsonl")
    log_path = Path(log_file)

    # Ensure log directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert record to dictionary (use dataclass.asdict for JSON serialization)
    record_dict = {
        "record_id": record.record_id,
        "published_at": record.published_at,
        "artifact_id": record.artifact_id,
        "artifact_type": record.artifact_type,
        "source_file": record.source_file,
        "channel": record.channel,
        "visibility": record.visibility,
        "destination": record.destination,
        "approved_by": record.approved_by,
        "approval_status": record.approval_status,
        "status": record.status,
        "error_message": record.error_message,
        "can_rollback": record.can_rollback,
        "rolled_back": record.rolled_back,
        "rolled_back_at": record.rolled_back_at,
        "rolled_back_by": record.rolled_back_by,
        "metadata": record.metadata
    }

    # Append to log file (JSONL format: one JSON object per line)
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record_dict, ensure_ascii=False) + '\n')

        logger.info(f"Logged publish action: {record.record_id} ({record.channel}/{record.visibility})")

    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")
        raise OSError(f"Failed to write audit log: {e}")


def load_audit_log(limit: int = 0, offset: int = 0) -> List[PublishRecord]:
    """Load publish records from audit log.

    Args:
        limit: Maximum number of records to load (0 = no limit)
        offset: Number of records to skip from the beginning

    Returns:
        List of PublishRecord objects
    """
    config = get_audit_config()
    log_file = config.get("log_file", "vault/publish_audit.log.jsonl")
    log_path = Path(log_file)

    if not log_path.exists():
        logger.warning(f"Audit log file not found: {log_path}")
        return []

    records = []

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    record_dict = json.loads(line)
                    record = PublishRecord(
                        record_id=record_dict["record_id"],
                        published_at=record_dict["published_at"],
                        artifact_id=record_dict["artifact_id"],
                        artifact_type=record_dict["artifact_type"],
                        source_file=record_dict["source_file"],
                        channel=record_dict["channel"],
                        visibility=record_dict["visibility"],
                        destination=record_dict["destination"],
                        approved_by=record_dict["approved_by"],
                        approval_status=record_dict["approval_status"],
                        status=record_dict["status"],
                        error_message=record_dict.get("error_message", ""),
                        can_rollback=record_dict.get("can_rollback", False),
                        rolled_back=record_dict.get("rolled_back", False),
                        rolled_back_at=record_dict.get("rolled_back_at", ""),
                        rolled_back_by=record_dict.get("rolled_back_by", ""),
                        metadata=record_dict.get("metadata", {})
                    )
                    records.append(record)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse audit log entry: {e}")
                    continue

    except Exception as e:
        logger.error(f"Failed to read audit log: {e}")
        return []

    # Apply offset and limit
    if offset > 0:
        records = records[offset:]
    if limit > 0:
        records = records[:limit]

    return records


def get_publish_record(record_id: str) -> Optional[PublishRecord]:
    """Get a specific publish record by ID.

    Args:
        record_id: Record identifier to look up

    Returns:
        PublishRecord if found, None otherwise
    """
    records = load_audit_log()
    for record in records:
        if record.record_id == record_id:
            return record
    return None


def get_records_by_channel(channel: str, limit: int = 0) -> List[PublishRecord]:
    """Get publish records for a specific channel.

    Args:
        channel: Channel name (e.g., "website", "slack")
        limit: Maximum number of records to return (0 = no limit)

    Returns:
        List of PublishRecord objects for the channel
    """
    records = load_audit_log()
    filtered = [r for r in records if r.channel == channel]
    return filtered[:limit] if limit > 0 else filtered


def get_records_by_artifact(artifact_id: str) -> List[PublishRecord]:
    """Get all publish records for a specific artifact.

    Args:
        artifact_id: Artifact identifier

    Returns:
        List of PublishRecord objects for the artifact
    """
    records = load_audit_log()
    return [r for r in records if r.artifact_id == artifact_id]


def log_rollback(rollback: RollbackResult, record_id: str) -> None:
    """Update audit log with rollback information.

    Args:
        rollback: RollbackResult containing rollback details
        record_id: Original publish record ID to update

    Raises:
        OSError: If log file cannot be written
    """
    # Update the original record in the log
    # Since JSONL is append-only, we add a new entry marking the rollback
    config = get_audit_config()
    log_file = config.get("log_file", "vault/publish_audit.log.jsonl")
    log_path = Path(log_file)

    # Ensure log directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create rollback log entry
    rollback_entry = {
        "record_id": f"{record_id}-rollback",
        "published_at": rollback.rolled_back_at,
        "artifact_id": record_id,
        "artifact_type": "rollback",
        "source_file": "",
        "channel": rollback.channel,
        "visibility": "rollback",
        "destination": rollback.destination,
        "approved_by": rollback.rolled_back_by,
        "approval_status": "rollback",
        "status": "rolled_back",
        "error_message": rollback.error_message,
        "can_rollback": False,
        "rolled_back": True,
        "rolled_back_at": rollback.rolled_back_at,
        "rolled_back_by": rollback.rolled_back_by,
        "metadata": {"original_record_id": record_id}
    }

    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rollback_entry, ensure_ascii=False) + '\n')

        logger.info(f"Logged rollback for record: {record_id}")

    except Exception as e:
        logger.error(f"Failed to write rollback log: {e}")
        raise OSError(f"Failed to write rollback log: {e}")


def generate_audit_report(output_path: Path = None) -> str:
    """Generate human-readable audit report.

    Args:
        output_path: Optional path to write report (if None, returns as string)

    Returns:
        Report content as string
    """
    records = load_audit_log()

    # Group records by channel and status
    by_channel = {}
    by_status = {}
    total = 0

    for record in records:
        # Count by channel
        if record.channel not in by_channel:
            by_channel[record.channel] = 0
        by_channel[record.channel] += 1

        # Count by status
        if record.status not in by_status:
            by_status[record.status] = 0
        by_status[record.status] += 1

        total += 1

    # Generate report
    lines = [
        "# Publish Audit Report",
        f"Generated: {datetime.utcnow().isoformat()}Z",
        "",
        "## Summary",
        f"Total publish actions: {total}",
        "",
        "## By Channel",
    ]

    for channel, count in sorted(by_channel.items()):
        lines.append(f"- {channel}: {count}")

    lines.extend([
        "",
        "## By Status",
    ])

    for status, count in sorted(by_status.items()):
        lines.append(f"- {status}: {count}")

    lines.extend([
        "",
        "## Recent Actions",
        ""
    ])

    # Show last 10 records
    recent_records = records[-10:] if len(records) > 10 else records
    for record in reversed(recent_records):
        lines.append(f"- {record.published_at}: {record.artifact_id} → {record.channel} ({record.status})")

    report = "\n".join(lines)

    # Write to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Wrote audit report to {output_path}")

    return report
