# Phase 7 Review Checklist

**Purpose**: Review checklist for Phase 7 (Publishing Gate & Distribution Layer)
**Version**: 1.0
**Date**: 2026-02-01

---

## Overview

This checklist is used to validate that the Phase 7 output (Publishing Gate & Distribution Layer) meets all requirements and follows the constraints defined in MASTER_EXECUTION_BLUEPRINT.md and DESIGN.md.

**Critical Context**: Phase 7 is the OPTIONAL final layer for publishing content to external channels. Phase 7 controls visibility and distribution but MUST NOT modify content. Phase 7 is a GATE, not a content processor.

**Review Method**: ✅ / ❌ / N/A
**Rule**: Any Hard Stop (🟥) failure → Phase 7 REJECTED

---

## Checklist Items

### 🟥 1️⃣ Phase Boundary Integrity (Hard Stop)

**Checks**:
- ⬜ Phase 7 does NOT modify Phase 6 output files
- ⬜ Phase 7 does NOT re-render or regenerate formatted outputs
- ⬜ Phase 7 does NOT touch SuccessStory content or fields
- ⬜ Phase 7 only consumes Phase 6 artifacts as immutable inputs
- ⬜ Phase 7 does NOT apply templates or formatting logic
- ⬜ Phase 7 does NOT alter timestamps or metadata from Phase 6

**Why this matters**: Phase 7 is a pure distribution gate. Any modification to Phase 6 outputs bypasses formatting validation and creates inconsistency.

**Failure Message**:
```
❌ Phase Boundary: Phase 7 modified Phase 6 outputs or content.
                  Phase 7 MUST:
                  - NOT modify Phase 6 output files
                  - NOT re-render or regenerate outputs
                  - NOT touch SuccessStory content
                  - Consume Phase 6 artifacts as immutable inputs
                  - NOT apply templates or formatting
                  - Preserve Phase 6 timestamps and metadata
```

**Verification**: Git diff against Phase 6, verify no output file modifications, check for template rendering in Phase 7

---

### 🟥 2️⃣ Publish Control & Visibility (Hard Stop)

**Checks**:
- ⬜ Explicit publish decision exists for each output (publish / hold / reject)
- ⬜ Visibility levels are enforced (internal / external / restricted)
- ⬜ Internal-only content cannot be published to external channels
- ⬜ Human approval decisions are respected (not overridden by automation)
- ⬜ Publish decisions are persisted and auditable
- ⬜ No content is published without explicit decision (default is "hold")

**Why this matters**: Publishing is irreversible. Without explicit control, sensitive content can leak externally. Human governance is essential.

**Failure Message**:
```
❌ Publish Control: Publishing lacks explicit control or visibility enforcement.
                   Phase 7 MUST:
                   - Require explicit decision (publish/hold/reject)
                   - Enforce visibility levels (internal/external/restricted)
                   - Prevent internal content from leaking externally
                   - Respect human approval (no auto-override)
                   - Persist publish decisions
                   - Default to "hold" (no auto-publish)
```

**Verification**: Test publish with missing decision (should fail), test visibility enforcement, check decision persistence

---

### 🟥 3️⃣ Channel-Driven Architecture (Hard Stop)

**Checks**:
- ⬜ Publishing logic is per-channel (web, CRM, Slack, email, etc.)
- ⬜ Channels are pluggable (add new channel without modifying core logic)
- ⬜ No channel-specific logic is hardcoded in core gate code
- ⬜ Each channel has isolated configuration (credentials, endpoints)
- ⬜ Channel failures do NOT affect other channels
- ⬜ Channels are registered/discovered, not hardcoded

**Why this matters**: Distribution requirements evolve. Channel-driven architecture enables adding new destinations without refactoring.

**Failure Message**:
```
❌ Channel Architecture: Publishing logic is monolithic or hardcoded.
                        Phase 7 MUST:
                        - Separate logic per channel
                        - Make channels pluggable
                        - NOT hardcode channel logic in core
                        - Isolate channel configuration
                        - Isolate channel failures
                        - Register/discover channels dynamically
```

**Verification**: Add new channel without modifying core code, test channel isolation, verify channel discovery

---

### 🟥 4️⃣ Auditability & Rollback (Hard Stop)

**Checks**:
- ⬜ Every publish action is logged with:
  - WHO (user or system that initiated publish)
  - WHEN (timestamp of publish)
  - WHERE (channel and destination)
  - WHAT (story IDs or file paths published)
- ⬜ Logs are stored in persistent, machine-readable format
- ⬜ Rollback or unpublish is supported for all channels
- ⬜ Failed publishes are recoverable (can retry without data loss)
- ⬜ Publish logs cannot be modified after writing (append-only)
- ⬜ Logs are queryable (e.g., "what was published to Slack on 2026-01-15?")

**Why this matters**: Publishing is irreversible. Without logs and rollback, mistakes are permanent and unexplainable.

**Failure Message**:
```
❌ Auditability: Publishing lacks comprehensive logging or rollback.
                Phase 7 MUST:
                - Log every publish action (who/when/where/what)
                - Store logs persistently in machine-readable format
                - Support rollback/unpublish for all channels
                - Recover from failed publishes
                - Use append-only logs (no modification)
                - Support log queries
```

**Verification**: Publish test content, check log completeness, test rollback, test failed publish recovery

---

### 🟨 5️⃣ Scheduling & Automation (Strong Requirement)

**Checks**:
- ⬜ Delayed or scheduled publishing is supported (e.g., "publish at 2026-02-01 09:00")
- ⬜ Retry behavior is defined for transient failures
- ⬜ Publish operations are idempotent (publishing same content twice = no harm)
- ⬜ Scheduled publishes can be cancelled before execution
- ⬜ Retry logic respects exponential backoff (no spam)
- ⬜ Automation can be disabled (manual-only mode)

**Why this matters**: Distribution channels have unreliable delivery. Scheduling and retry enable robust, hands-off publishing.

**Failure Message**:
```
⚠️ Scheduling: Scheduling or retry behavior is missing or incomplete.
              Phase 7 SHOULD:
              - Support delayed/scheduled publishing
              - Define retry behavior for failures
              - Ensure idempotent publish operations
              - Allow cancelling scheduled publishes
              - Use exponential backoff for retries
              - Support manual-only mode
```

**Allowed**: 1 item may fail, but must explain why

**Verification**: Test scheduled publish, test retry on failure, test idempotence (publish twice), test cancellation

---

### 🟨 6️⃣ Channel Health & Monitoring (Strong Requirement)

**Checks**:
- ⬜ Channel health is monitored (availability, rate limits, errors)
- ⬜ Failed channels are isolated (do not block other channels)
- ⬜ Rate limiting is respected (e.g., Slack API limits)
- ⬜ Channel errors are logged with full context
- ⬜ Health status is queryable (e.g., "is Slack channel healthy?")
- ⬜ Degraded channels trigger alerts or warnings

**Why this matters**: Distribution channels fail. Monitoring and isolation prevent single-channel failures from blocking all publishing.

**Failure Message**:
```
⚠️ Channel Health: Channel monitoring or isolation is missing.
                   Phase 7 SHOULD:
                   - Monitor channel health
                   - Isolate failed channels
                   - Respect rate limits
                   - Log channel errors with context
                   - Support health status queries
                   - Alert on degraded channels
```

**Allowed**: 1 item may fail, but must explain why

**Verification**: Test channel failure, verify isolation, test rate limiting, check health status query

---

### 🟩 7️⃣ Preview & Dry-Run (Optional but Recommended)

**Checks**:
- ⬜ `--dry-run` mode exists and shows what WILL be published
- ⬜ Dry run outputs channel, destination, and content preview
- ⬜ Human can preview content before actual publish
- ⬜ Preview works for all channels (not just some)
- ⬜ Preview can be saved to file for review

**Why this matters**: Dry runs enable safe testing and human verification before committing to irreversible publish actions.

**Failure Message**:
```
⚠️ Preview: Dry-run or preview capabilities are missing.
            Phase 7 SHOULD:
            - Support --dry-run mode
            - Show channel, destination, and content in preview
            - Allow human preview before publish
            - Support preview for all channels
            - Save preview to file
```

**Status**: Recommended for v1, but not blocking

**Verification**: Run with `--dry-run`, verify preview completeness, test all channels

---

### 🟩 8️⃣ Bulk & Batch Publishing (Optional but Recommended)

**Checks**:
- ⬜ Multiple outputs can be published in one operation
- ⬜ Batch publishing is atomic (all succeed or all fail)
- ⬜ Batch operations are logged completely (all items in one log entry)
- ⬜ Partial batch failures are handled gracefully (some succeed, some fail)
- ⬜ Batch operations support dry-run

**Why this matters**: Users often need to publish multiple outputs at once (e.g., all monthly stories). Batch support reduces manual work.

**Failure Message**:
```
⚠️ Batch Publishing: Bulk publishing is not supported.
                     Phase 7 SHOULD:
                     - Support publishing multiple outputs
                     - Make batch operations atomic
                     - Log batch operations completely
                     - Handle partial failures gracefully
                     - Support dry-run for batches
```

**Status**: Recommended for v1, but not blocking

**Verification**: Publish batch of outputs, test atomicity, test partial failure handling

---

### 🟩 9️⃣ Content Transformation Hooks (Optional but Recommended)

**Checks**:
- ⬜ Channels can apply minimal, channel-specific transformations
- ⬜ Transformations are explicitly declared (not hidden)
- ⬜ Transformations are reversible (original content preserved)
- ⬜ Transformations are logged (what was changed)
- ⬜ Transformations are optional (can publish raw content)

**Why this matters**: Some channels require format changes (e.g., Slack formatting vs HTML). Explicit, reversible transformations enable this without sacrificing integrity.

**Failure Message**:
```
⚠️ Transformations: Channel-specific transformations are not supported.
                     Phase 7 SHOULD:
                     - Allow channel-specific transformations
                     - Declare transformations explicitly
                     - Make transformations reversible
                     - Log transformations
                     - Support raw content publishing
```

**Status**: Recommended for v1, but not blocking

**Verification**: Test channel transformation, verify reversibility, check transformation logging

---

## Phase 7 Final Decision

### Review Result

**Phase 7 Review Result**: _____ ACCEPTED / REJECTED _____

### Critical Findings

If REJECTED, list ALL Hard Stop failures:

1. ________________________________________________________________
2. ________________________________________________________________
3. ________________________________________________________________

### Strong Requirement Findings

List any Strong Requirement failures (allow max 2):

1. ________________________________________________________________
2. ________________________________________________________________

### Optional Findings

List any Optional failures (for informational purposes):

1. ________________________________________________________________
2. ________________________________________________________________

### Approval

**Approved By**:
- Human Reviewer: _______________________ Date: ________
- AI Reviewer (optional): _______________________ Date: ________

**Conditions** (if any):
________________________________________________

---

## Review Process

### Automated Execution

```bash
./wins phase review 7
```

### Automated Checks Run

1. **Check 1**: Phase boundary integrity (no modifications to Phase 6)
2. **Check 2**: Publish control & visibility (explicit decisions, visibility enforcement)
3. **Check 3**: Channel-driven architecture (pluggable channels)
4. **Check 4**: Auditability & rollback (comprehensive logging, rollback support)
5. **Check 5**: Scheduling & automation
6. **Check 6**: Channel health & monitoring
7. **Check 7**: Preview & dry-run
8. **Check 8**: Bulk & batch publishing
9. **Check 9**: Content transformation hooks

### Manual Review Steps

After automated checks pass, manually review:

1. **Channel Architecture**: Are channels pluggable? Can you add a new channel without modifying core?
2. **Publish Workflow**: Test publish → approve → publish → rollback → unpublish
3. **Visibility Enforcement**: Try publishing internal content externally (should fail)
4. **Log Completeness**: Review publish logs, are they complete and queryable?
5. **Channel Isolation**: Fail one channel, verify others continue working
6. **Dry Run**: Test `--dry-run`, verify no actual publish occurs
7. **Scheduling**: Schedule a publish, cancel it, verify cancellation works
8. **Rollback**: Publish content, then rollback, verify content is removed

---

## Exit Criteria

Phase 7 is considered complete when:

- ✅ ALL Hard Stop (🟥) checks pass (no exceptions)
- ✅ At most 2 Strong Requirement (🟨) checks fail (with explanation)
- ✅ User has manually tested publish workflow
- ✅ User has verified rollback functionality
- ✅ User has tested channel isolation
- ✅ User explicitly approves Phase 7 completion

---

## Next Steps After Approval

Once Phase 7 is approved:

```bash
# Phase 7 is optional final phase
./wins phase complete 7

# Publish content
./wins publish --channel slack --story-id win-2026-01-us-001
./wins publish --channel web --all --month 2026-01
```

The full pipeline is now complete:
- Phase 3: Mechanical processing (file discovery, text extraction)
- Phase 4: Semantic extraction (LLM-based story extraction)
- Phase 5: Business logic (ranking, merging, curation)
- Phase 6: Output generation (formatting, templates)
- Phase 7: Publishing gate (distribution to channels)

---

## Historical Context

### Why This Checklist Exists

1. **Prevent Uncontrolled Publishing**: Publishing is irreversible, needs explicit control
2. **Enforce Visibility Boundaries**: Internal content must not leak externally
3. **Enable Channel Extensibility**: Distribution channels evolve, architecture must adapt
4. **Maintain Audit Trail**: Every publish must be traceable and explainable
5. **Support Rollback**: Mistakes happen, rollback capabilities are essential

### Relationship to DESIGN.md

| DESIGN.md Section | Checklist Item |
|-------------------|----------------|
| Publishing Gate | Publish Control & Visibility |
| Channel Architecture | Channel-Driven Architecture |
| Audit Requirements | Auditability & Rollback |
| Distribution Logic | Scheduling & Automation |

### Relationship to MASTER_EXECUTION_BLUEPRINT.md

| Blueprint Section | Checklist Item |
|-------------------|----------------|
| Phase 7: Publishing Gate | Publish Control & Visibility |
| Phase 7: Channel-Driven | Channel-Driven Architecture |
| Phase 7: Audit Trail | Auditability & Rollback |
| Phase 7: Scheduling | Scheduling & Automation |

---

## Critical Differences from Phase 6

| Aspect | Phase 6 | Phase 7 |
|--------|---------|---------|
| Primary Purpose | Format and generate outputs | Distribute to external channels |
| Content Changes | Allowed (formatting only) | FORBIDDEN |
| Artifacts | Creates output files | Consumes output files |
| Templates | Core to Phase 6 | NOT USED |
| Decision Type | None (generate all) | Explicit (publish/hold/reject) |
| Reversibility | Easy (regenerate) | Varies by channel (rollback required) |
| Risk Type | Output formatting errors | Public content exposure |

---

## Publish vs Generate

### Phase 6 (Generate)
- Creates formatted output files
- Applies templates and formatting
- Saves to filesystem
- No visibility control (all outputs local)
- No audit trail required (local files)

### Phase 7 (Publish)
- Distributes to external channels
- NO content changes
- Enforces visibility levels
- Requires explicit approval
- Comprehensive audit trail
- Rollback capabilities

**Key Principle**: Phase 6 generates artifacts. Phase 7 distributes them. Phase 7 is optional (local-only workflows don't need it).

---

## Phase 7 is OPTIONAL

Phase 7 is ONLY required if:
- Publishing to external channels (Slack, CRM, web, etc.)
- Enforcing visibility levels (internal vs external)
- Needing publish audit trails
- Requiring rollback capabilities

Phase 7 is NOT required if:
- All outputs are local files only
- No external distribution needed
- Manual publishing workflow is acceptable

**Decision**: Phase 7 can be skipped for v1 if local-only outputs are sufficient.

---

## Checklist Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial version for Phase 7 |

---

## End of Document

**Maintained by**: `wins` command
**Last Updated**: 2026-02-01
**Status**: Active - Used by `./wins phase review 7`
