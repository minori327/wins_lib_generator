# Wins Library System - Phase 7: Publish / Distribution Gate

This document describes Phase 7 of the Wins Library System: the Publish / Distribution Gate.

---

## Overview

Phase 7 controls **WHEN**, **WHERE**, and **WHETHER** Phase 6 outputs are published or distributed. It acts as the final gate before content reaches external channels.

### Key Responsibilities

- ✅ **Publish Eligibility**: Decide if outputs are ready for publishing
- ✅ **Visibility Rules**: Enforce internal/external/restricted access controls
- ✅ **Channel Routing**: Route outputs to appropriate distribution channels
- ✅ **Approval Gates**: Require human approval for sensitive publishes
- ✅ **Audit Trail**: Log all publish actions for accountability
- ✅ **Rollback**: Support unpublishing published artifacts

### What Phase 7 Does NOT Do

- ❌ Modify SuccessStory content (content is final from Phase 6)
- ❌ Re-render templates or change formats
- ❌ Apply business evaluation logic (Phase 5 responsibility)
- ❌ Merge or split outputs
- ❌ Bypass human overrides

---

## Architecture

### Components

1. **Publish Gate Agent** ([agents/publish_gate_agent.py](../agents/publish_gate_agent.py))
   - Evaluates publish requests
   - Checks visibility rules
   - Determines approval requirements
   - Makes publish/deny/schedule decisions

2. **Publisher Workflow** ([workflow/publisher.py](../workflow/publisher.py))
   - Orchestrates publish flow
   - Routes to channel adapters
   - Logs to audit trail
   - Handles rollback

3. **Channel Adapters** ([workflow/channel_adapters.py](../workflow/channel_adapters.py))
   - Abstract interface for distribution protocols
   - Concrete implementations: filesystem, API, Slack, email
   - Protocol-specific publish/rollback logic

4. **Audit Logger** ([workflow/publish_audit_log.py](../workflow/publish_audit_log.py))
   - Immutable JSONL log of all publish actions
   - Query by record ID, channel, or artifact
   - Generate human-readable reports

5. **Publish Configuration** ([config/publish_config.yaml](../config/publish_config.yaml))
   - Channel definitions and settings
   - Visibility rules
   - Approval matrix
   - Destinations and credentials

---

## Publish Flow

### 1. Create Publish Request

```python
from models.publish import PublishRequest, Channel, VisibilityLevel
from pathlib import Path

request = PublishRequest(
    artifact_id="win-2026-01-US-1234abcd",
    artifact_type="executive_output",
    source_file=Path("vault/outputs/executive/win-2026-01-US-1234abcd.md"),
    channel=Channel.OBSIDIAN,
    visibility=VisibilityLevel.INTERNAL,
    requested_by="user@example.com"
)
```

### 2. Evaluate Request (Gate Decision)

```python
from agents.publish_gate_agent import evaluate_publish_request

decision = evaluate_publish_request(request)

if decision.approved:
    print(f"Approved for {decision.route_to_channel} → {decision.destination}")
else:
    print(f"Denied: {decision.denial_reason}")
```

### 3. Publish (with optional approval)

```python
from workflow.publisher import publish_artifact, approve_and_publish

# Option A: Direct publish (if no approval required)
record = publish_artifact(request)

# Option B: Approve and publish (if human approval required)
record = approve_and_publish(request, approved_by="manager@example.com")
```

### 4. Audit Log Entry

Every publish creates a `PublishRecord` in the audit log:

```json
{
  "record_id": "pub-20260201153045-a1b2c3d4",
  "published_at": "2026-02-01T15:30:45Z",
  "artifact_id": "win-2026-01-US-1234abcd",
  "channel": "obsidian",
  "visibility": "internal",
  "destination": "vault/obsidian/success_stories",
  "approved_by": "manager@example.com",
  "status": "published"
}
```

---

## Channels

### Supported Channels

| Channel | Adapter | Visibility | Approval Required |
|---------|---------|------------|-------------------|
| **Website** | API | public, external | Yes (human) |
| **CMS** | API | public, external | Yes (human) |
| **CRM** | API | internal, external | Yes (human) |
| **Slack** | Webhook | internal, restricted | No (auto) |
| **Email** | SMTP | internal, external | No (auto) |
| **Obsidian** | Filesystem | internal, restricted | No (auto) |

### Adding New Channels

To add a new channel:

1. **Update config** in `config/publish_config.yaml`:
```yaml
channels:
  my_new_channel:
    enabled: true
    adapter: "api"  # or "filesystem", "slack", "smtp"
    format: "json"
    visibility_levels:
      - "internal"
    approval_required: false
    destinations:
      production:
        url: "https://example.com/api/publish"
```

2. **Create adapter** in `workflow/channel_adapters.py` (if new protocol needed)

3. **Update visibility rules** in `config/publish_config.yaml`:
```yaml
visibility_rules:
  internal:
    allowed_channels:
      - "my_new_channel"
```

---

## Visibility Levels

### Level Definitions

- **PUBLIC**: Publicly accessible (website, CMS)
- **EXTERNAL**: External customers/partners (email, website)
- **INTERNAL**: Internal team only (Slack, Obsidian, email)
- **RESTRICTED**: Restricted access (leadership, Obsidian only)

### Enforcement

Phase 7 enforces visibility rules through:
1. **Channel whitelist**: Each channel defines allowed visibility levels
2. **Visibility blacklist**: Certain visibility cannot go to certain channels
3. **Approval matrix**: (channel, visibility) combinations requiring human approval

Example from config:
```yaml
visibility_rules:
  public:
    allowed_channels: ["website", "cms"]
    disallowed_channels: ["slack", "email", "obsidian"]

  restricted:
    allowed_channels: ["obsidian", "slack"]
    disallowed_channels: ["website", "cms", "email"]
```

---

## Approval Workflow

### Approval Matrix

The approval matrix defines which (channel, visibility) combinations require human approval:

```yaml
approval_matrix:
  "website:public": true  # Requires human approval
  "slack:internal": false  # Auto-approve
  "obsidian:internal": false  # Auto-approve
```

### Human Approval Flow

1. **System evaluates request** → determines approval needed
2. **Request marked as PENDING** if approval required
3. **Human approves** (via separate UI/workflow):
```python
from agents.publish_gate_agent import approve_publish_request

approved_request = approve_publish_request(
    request,
    approved_by="manager@example.com"
)
```

4. **Publish executes** with approval credentials

### Auto-Approval

Certain combinations are auto-approved by the system:
- Internal → Obsidian (no approval needed)
- Internal → Slack (no approval needed)
- All channels with `approval_required: false` in config

---

## Rollback

### Rollback Support

Not all channels support rollback:
- ✅ **Supported**: Filesystem (Obsidian), API (website, CMS)
- ❌ **Not Supported**: Slack, Email (already delivered)

### Rollback Flow

```python
from workflow.publisher import rollback_publish

result = rollback_publish(
    record_id="pub-20260201153045-a1b2c3d4",
    rolled_back_by="admin@example.com"
)

if result.success:
    print(f"Rolled back {result.record_id}")
else:
    print(f"Rollback failed: {result.error_message}")
```

### Rollback Configuration

```yaml
rollback:
  enabled: true
  auto_rollback_on_error: false  # Require manual rollback
  retention_days: 30  # Keep rollback records for 30 days
  backup_destinations:
    website: "vault/backups/website"
    obsidian: "vault/backups/obsidian"
```

---

## Audit Trail

### Audit Log Format

JSONL (JSON Lines) format - one JSON object per line:

```
vault/publish_audit.log.jsonl
```

Example entries:
```json
{"record_id":"pub-20260201153045-a1b2c3d4","published_at":"2026-02-01T15:30:45Z","artifact_id":"win-2026-01-US-1234abcd",...}
{"record_id":"pub-20260201153122-b2c3d4e5","published_at":"2026-02-01T15:31:22Z","artifact_id":"win-2026-01-UK-5678efgh",...}
```

### Querying Audit Log

```python
from workflow.publish_audit_log import (
    load_audit_log,
    get_publish_record,
    get_records_by_channel
)

# Get all records
all_records = load_audit_log()

# Get specific record
record = get_publish_record("pub-20260201153045-a1b2c3d4")

# Get records for a channel
website_records = get_records_by_channel("website")

# Generate report
report = workflow.publish_audit_log.generate_audit_report(
    output_path=Path("vault/audit_report.md")
)
```

### Audit Report

Generate human-readable audit report:

```python
from workflow.publish_audit_log import generate_audit_report

report = generate_audit_report(output_path=Path("vault/audit_report.md"))
```

Report includes:
- Total publish actions
- Breakdown by channel
- Breakdown by status
- Recent actions

---

## Configuration

### Channel Configuration

Each channel in `config/publish_config.yaml` defines:

```yaml
channels:
  website:
    enabled: true
    adapter: "api"
    format: "json"
    visibility_levels: ["public", "external"]
    approval_required: true
    overwrite_existing: true
    destinations:
      production:
        url: "https://example.com/api/stories"
        auth_method: "bearer_token"
        env_var: "WEBSITE_PROD_TOKEN"
    headers:
      Content-Type: "application/json"
```

### File Routing

Map artifact types to channels:

```yaml
file_routing:
  executive_outputs:
    channel: "obsidian"
    subdirectory: "outputs/executive"
  marketing_outputs:
    channel: "obsidian"
    subdirectory: "outputs/marketing"
  weekly_summaries:
    channel: "slack"
    destination: "wins"
```

---

## Usage Examples

### Example 1: Publish to Obsidian

```python
from models.publish import PublishRequest, Channel, VisibilityLevel
from workflow.publisher import publish_artifact
from pathlib import Path

request = PublishRequest(
    artifact_id="win-2026-01-US-1234abcd",
    artifact_type="obsidian_note",
    source_file=Path("vault/notes/win-2026-01-US-1234abcd.md"),
    channel=Channel.OBSIDIAN,
    visibility=VisibilityLevel.INTERNAL
)

record = publish_artifact(request)
print(f"Published: {record.record_id}")
```

### Example 2: Publish to Website (with approval)

```python
from models.publish import PublishRequest, Channel, VisibilityLevel
from workflow.publisher import approve_and_publish
from pathlib import Path

request = PublishRequest(
    artifact_id="win-2026-01-US-1234abcd",
    artifact_type="marketing_output",
    source_file=Path("vault/outputs/marketing/win-2026-01-US-1234abcd.md"),
    channel=Channel.WEBSITE,
    visibility=VisibilityLevel.PUBLIC
)

# Requires human approval
record = approve_and_publish(request, approved_by="marketing-director@example.com")
print(f"Published to website: {record.destination}")
```

### Example 3: Batch Publish

```python
from workflow.publisher import batch_publish
from models.publish import PublishRequest, Channel, VisibilityLevel

requests = [
    PublishRequest(
        artifact_id="win-2026-01-US-1234abcd",
        artifact_type="executive_output",
        source_file=Path("vault/outputs/executive/win-2026-01-US-1234abcd.md"),
        channel=Channel.OBSIDIAN,
        visibility=VisibilityLevel.INTERNAL
    ),
    # ... more requests
]

records = batch_publish(requests)
print(f"Published {len(records)} artifacts")
```

### Example 4: Rollback

```python
from workflow.publisher import rollback_publish

result = rollback_publish(
    record_id="pub-20260201153045-a1b2c3d4",
    rolled_back_by="admin@example.com"
)

if result.success:
    print("Rollback successful")
```

---

## Determinism & Idempotency

Phase 7 guarantees:
- **Deterministic decisions**: Same request → same decision (based on config)
- **Idempotent publishes**: Publishing same artifact twice = 2 records, last one wins
- **Immutable audit log**: Records never modified, only appended
- **Reversible**: Rollback supported for filesystem and API channels

---

## Security Considerations

### Credentials Management

- Credentials stored in environment variables (not in config)
- Config references env_var names (e.g., `WEBSITE_PROD_TOKEN`)
- No hardcoded secrets in code or config

### Access Control

- Human approval required for external-facing channels
- Visibility rules prevent internal content from going public
- Audit trail provides accountability for all publish actions

### Channel Security

- API channels use authentication (bearer tokens, API keys, OAuth2)
- Filesystem channels respect local file permissions
- Email channels use SMTP with TLS

---

## Error Handling

### Publish Failures

All publish failures are logged to audit trail with `status="failed"` and `error_message` field.

```python
record = publish_artifact(request)

if record.status == "failed":
    print(f"Publish failed: {record.error_message}")
```

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `Channel not configured` | Channel missing from config | Add channel to `publish_config.yaml` |
| `Visibility not allowed` | Visibility level blocked for channel | Check `visibility_rules` in config |
| `Human approval required` | Request needs approval | Use `approve_and_publish()` |
| `Source file does not exist` | Phase 6 output missing | Generate Phase 6 output first |
| `Destination unreachable` | Network/API error | Check destination URL, credentials |

---

## Testing

### Unit Tests

Test publish gate agent logic:

```python
from agents.publish_gate_agent import evaluate_publish_request
from models.publish import PublishRequest, Channel, VisibilityLevel

request = PublishRequest(
    artifact_id="test-1",
    artifact_type="executive_output",
    source_file=Path("test.md"),
    channel=Channel.OBSIDIAN,
    visibility=VisibilityLevel.INTERNAL
)

decision = evaluate_publish_request(request)
assert decision.approved == True
```

### Integration Tests

Test full publish flow with mock adapters:

```python
from workflow.publisher import publish_artifact
from models.publish import PublishRequest, Channel, VisibilityLevel

request = PublishRequest(...)
record = publish_artifact(request)

assert record.status == "published"
assert "pub-" in record.record_id
```

---

## Future Enhancements

Potential future features for Phase 7:

1. **Scheduled Publishing Queue**: Background worker to execute scheduled publishes
2. **Webhook Notifications**: Notify external systems on publish events
3. **Publish Dashboard**: UI for viewing audit log and triggering rollbacks
4. **A/B Testing**: Publish multiple variants and track performance
5. **CDN Integration**: Push published content to CDN for caching
6. **Multi-Region Publishing**: Publish to multiple regions simultaneously

---

*Phase 7: Publish / Distribution Gate*
*Last Updated: 2026-02-01*
