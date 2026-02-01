# Phase 5 Review Checklist

**Purpose**: Review checklist for Phase 5 (Business Logic & Decision Layer)
**Version**: 1.0
**Date**: 2026-02-01

---

## Overview

This checklist is used to validate that the Phase 5 output (Business Logic & Decision Layer) meets all requirements and follows the constraints defined in MASTER_EXECUTION_BLUEPRINT.md and DESIGN.md.

**Critical Context**: Phase 5 is the FIRST phase where business judgment, ranking, merging, and deletion are permitted. Phase 5 outputs are user-facing and IRREVERSIBLE if done incorrectly.

**Review Method**: ✅ / ❌ / N/A
**Rule**: Any Hard Stop (🟥) failure → Phase 5 REJECTED

---

## Checklist Items

### 🟥 1️⃣ Phase Boundary & Scope Control (Hard Stop)

**Checks**:
- ⬜ Phase 3 code was not modified
- ⬜ Phase 4 code was not modified
- ⬜ No Phase 6 behaviors introduced (output formatting, rendering)
- ⬜ No raw source file modifications
- ⬜ No modifications to immutable RawItem objects
- ⬜ All business logic is contained within Phase 5 modules

**Why this matters**: Phase 5 must not corrupt earlier phases. Any modification to Phases 3-4 invalidates the entire pipeline.

**Failure Message**:
```
❌ Phase Boundary: Phase 5 modified earlier phases or introduced Phase 6 behaviors.
                  Phase 5 MUST operate ONLY on SuccessStory outputs from Phase 4.
                  MUST NOT modify Phase 3, Phase 4, or raw source files.
```

**Verification**: Git diff against Phase 4, file modification timestamps, module import analysis

---

### 🟥 2️⃣ Business Rule Explicitness & Documentation (Hard Stop)

**Checks**:
- ⬜ All ranking rules are documented in `config/business_rules.yaml`
- ⬜ All merging rules are documented with explicit criteria
- ⬜ All deletion/suppression rules are documented with explicit criteria
- ⬜ Every business rule has a human-readable name and description
- ⬜ No business rules exist only in code
- ⬜ All rule thresholds (e.g., similarity scores, confidence thresholds) are in config files

**Why this matters**: Business rules must be inspectable, auditable, and modifiable without touching code. Hidden rules are silent bugs.

**Failure Message**:
```
❌ Business Rule Documentation: Business rules exist only in code.
                                ALL rules MUST be in config/business_rules.yaml with:
                                - Human-readable names
                                - Clear descriptions
                                - Explicit thresholds and criteria
```

**Verification**: Read `config/business_rules.yaml`, grep for hardcoded thresholds in code, compare documented vs actual rules

---

### 🟥 3️⃣ Merge, Delete & Suppression Safety (Hard Stop)

**Checks**:
- ⬜ Every merge operation logs the source IDs being merged
- ⬜ Every merge operation logs the merge reason (which rule triggered)
- ⬜ Every delete/suppression operation logs the target ID and reason
- ⬜ Merged stories preserve a `merged_from` field listing source IDs
- ⬜ Deleted stories are moved to `wins/deleted/` with metadata (not erased)
- ⬜ No merge or delete happens without explicit human approval OR explicit config rule

**Why this matters**: Merges and deletions are irreversible. Without logging and preservation, data loss is undetectable and unrecoverable.

**Failure Message**:
```
❌ Merge/Delete Safety: Destructive operations lack safety guarantees.
                       Every merge MUST:
                       - Log source IDs
                       - Log merge reason
                       - Preserve source IDs in `merged_from` field

                       Every delete MUST:
                       - Log target ID and reason
                       - Move to wins/deleted/ (not erase)
                       - Require explicit human approval OR config rule
```

**Verification**: Check logs for merge/delete operations, verify `wins/deleted/` directory exists, inspect merged story objects for `merged_from` field

---

### 🟥 4️⃣ Human Override & Governance (Hard Stop)

**Checks**:
- ⬜ Human approval is required before ANY merge (unless auto-merge explicitly enabled)
- ⬜ Human approval is required before ANY delete (unless auto-delete explicitly enabled)
- ⬜ Human decisions are persisted and not overwritten by AI
- ⬜ There is a "dry run" mode that previews merges/deletes without executing
- ⬜ Human can disable all automation and review all decisions manually
- ⬜ All automated decisions can be manually reversed

**Why this matters**: AI must not make irreversible business decisions without human oversight. Governance prevents silent data corruption.

**Failure Message**:
```
❌ Human Governance: AI makes irreversible decisions without human approval.
                     Phase 5 MUST:
                     - Require human approval for merges (unless auto-merge enabled)
                     - Require human approval for deletes (unless auto-delete enabled)
                     - Persist human decisions (not overwritten by AI)
                     - Support dry-run mode for preview
                     - Allow manual review of all automated decisions
                     - Allow reversal of automated decisions
```

**Verification**: Test merge/delete with and without auto-merge flags, verify dry-run mode, check that human decisions persist on re-run

---

### 🟨 5️⃣ Ranking, Scoring & Prioritization Logic (Strong Requirement)

**Checks**:
- ⬜ All ranking scores are deterministic (same input → same score)
- ⬜ Ranking scores are NOT based on random numbers or timestamps
- ⬜ Ranking logic uses ONLY fields present in SuccessStory
- ⬜ Ranking criteria are clearly documented (e.g., "metrics presence > customer type > confidence")
- ⬜ Ranking outputs can be reproduced by re-running with same inputs
- ⬜ No story is dropped or ignored during ranking without explicit rule

**Why this matters**: Ranking must be reproducible and explainable. Non-deterministic ranking hides bugs and makes debugging impossible.

**Failure Message**:
```
⚠️ Ranking Logic: Ranking is non-deterministic or uses undocumented criteria.
                 Ranking MUST:
                 - Be deterministic (same input → same score)
                 - Use only SuccessStory fields
                 - Document scoring criteria clearly
                 - Be reproducible
                 - Never drop stories without explicit rule
```

**Allowed**: 1 item may fail, but must explain why

**Verification**: Run ranking twice on same inputs, verify scores match, review ranking criteria documentation

---

### 🟨 6️⃣ Traceability & Provenance (Strong Requirement)

**Checks**:
- ⬜ Every final SuccessStory has `source_raw_item_id` field
- ⬜ Every merged SuccessStory has `merged_from` field listing source IDs
- ⬜ Every deleted SuccessStory in `wins/deleted/` has `deleted_at` and `deleted_reason` fields
- ⬜ Every ranking score has `ranking_method` and `ranking_timestamp` fields
- ⬜ Full provenance chain exists: RawItem → DraftSuccessStory → SuccessStory → (optional) MergedSuccessStory
- ⬜ Any story can be traced back to its original source file and line number

**Why this matters**: Provenance is essential for audit, debugging, and compliance. Without it, outputs are untrustworthy.

**Failure Message**:
```
⚠️ Traceability: Output lacks full provenance chain.
                 Every SuccessStory MUST have:
                 - source_raw_item_id (traces to RawItem)
                 - merged_from (if applicable, traces to source stories)
                 - deleted_at and deleted_reason (if deleted)
                 - ranking_method and ranking_timestamp
                 - Complete chain to original source file
```

**Allowed**: 1 item may fail, but must explain why

**Verification**: Spot-check 10 stories, trace each to original source, verify all provenance fields present

---

### 🟨 7️⃣ Configuration & Evolvability (Strong Requirement)

**Checks**:
- ⬜ All business thresholds are in `config.yaml` or `config/business_rules.yaml`
- ⬜ Changing a config value does NOT require code changes
- ⬜ Config changes are validated on startup (invalid config → explicit error)
- ⬜ Config file has comments explaining each threshold/rule
- ⬜ Default config values are conservative (avoid aggressive merging/deleting)
- ⬜ Config can be overridden per-country or per-month if needed

**Why this matters**: Business rules evolve. Config-driven systems are maintainable. Hardcoded rules are technical debt.

**Failure Message**:
```
⚠️ Configuration: Business rules are hardcoded in code.
                   All thresholds and rules MUST be in config files with:
                   - Clear comments explaining each rule
                   - Validation on startup
                   - Conservative defaults
                   - Per-country/per-month override capability
```

**Allowed**: 1 item may fail, but must explain why

**Verification**: Modify config values, verify behavior changes without code changes, test invalid config, review config comments

---

### 🟩 8️⃣ Output Integrity & User Impact (Optional but Recommended)

**Checks**:
- ⬜ All outputs are syntactically valid (JSON parses, Markdown renders)
- ⬜ No output contains template placeholders (e.g., `{{customer}}` left unfilled)
- ⬜ No output contains truncated or cutoff text
- ⬜ All metrics in outputs are preserved from source (not dropped during formatting)
- ⬜ All customer names are spelled correctly (not corrupted by merge)
- ⬜ No cross-story contamination (e.g., metrics from story A appear in story B)

**Why this matters**: Outputs are user-facing. Poor quality outputs undermine trust and require manual cleanup.

**Failure Message**:
```
⚠️ Output Integrity: Outputs contain formatting errors or data corruption.
                     All outputs MUST:
                     - Be syntactically valid
                     - Have no unfilled placeholders
                     - Have no truncation
                     - Preserve all metrics from source
                     - Have correct spelling (no merge corruption)
                     - Have no cross-story contamination
```

**Status**: Recommended for v1, but not blocking

**Verification**: Spot-check 20 outputs, parse JSON, render Markdown, compare metrics to source

---

### 🟩 9️⃣ Dry Run & Preview Capabilities (Optional but Recommended)

**Checks**:
- ⬜ `--dry-run` flag exists and prevents all destructive operations
- ⬜ Dry run outputs a preview of what WILL be merged/deleted
- ⬜ Dry run outputs human-readable explanation of each decision
- ⬜ Dry run can be saved to a file for review
- ⬜ Dry run output can be applied in a second step (human approval workflow)

**Why this matters**: Dry runs enable safe experimentation and human oversight. They are essential for trust in automated systems.

**Failure Message**:
```
⚠️ Dry Run: Dry run capabilities are missing or incomplete.
            Phase 5 SHOULD support:
            - --dry-run flag
            - Preview of merges/deletes
            - Human-readable explanations
            - Save to file for review
            - Two-step apply workflow
```

**Status**: Recommended for v1, but not blocking

**Verification**: Run with `--dry-run`, verify no destructive operations, check output format

---

### 🟩 🔟 Reversibility & Rollback (Optional but Recommended)

**Checks**:
- ⬜ Merges can be undone (split back into original stories)
- ⬜ Deletes can be undone (restore from `wins/deleted/`)
- ⬜ Rollback command exists to revert Phase 5 changes
- ⬜ Rollback restores previous state completely
- ⬜ Rollback operations are logged

**Why this matters**: Mistakes happen. Reversibility reduces the cost of errors and encourages experimentation.

**Failure Message**:
```
⚠️ Reversibility: Rollback capabilities are missing or incomplete.
                 Phase 5 SHOULD support:
                 - Undo merges (split stories)
                 - Restore deleted stories
                 - Rollback command
                 - Complete state restoration
                 - Logged rollback operations
```

**Status**: Recommended for v1, but not blocking

**Verification**: Perform merge, then undo, verify original state restored

---

## Phase 5 Final Decision

### Review Result

**Phase 5 Review Result**: _____ ACCEPTED / REJECTED _____

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
./wins phase review 5
```

### Automated Checks Run

1. **Check 1**: Phase boundary (no modifications to Phases 3-4)
2. **Check 2**: Business rule documentation (all rules in config)
3. **Check 3**: Merge/delete safety (logging and preservation)
4. **Check 4**: Human override (approval requirements)
5. **Check 5**: Ranking logic (determinism and reproducibility)
6. **Check 6**: Traceability (provenance chain)
7. **Check 7**: Configuration (config-driven rules)
8. **Check 8**: Output integrity (data quality)
9. **Check 9**: Dry run capabilities (preview)
10. **Check 10**: Reversibility (rollback)

### Manual Review Steps

After automated checks pass, manually review:

1. **Business Logic**: Are rules sensible and well-documented?
2. **Merge Quality**: Spot-check 20 merged stories, are merges correct?
3. **Delete Justification**: Review 20 deleted stories, are deletions justified?
4. **Ranking Fairness**: Review top 10 and bottom 10 ranked stories, is ranking sensible?
5. **Human Workflow**: Test approval workflow, is it smooth and safe?
6. **Config Clarity**: Read `config/business_rules.yaml`, is it understandable?
7. **Provenance Trace**: Pick 5 stories, trace each to original source file

---

## Exit Criteria

Phase 5 is considered complete when:

- ✅ ALL Hard Stop (🟥) checks pass (no exceptions)
- ✅ At most 2 Strong Requirement (🟨) checks fail (with explanation)
- ✅ User has manually reviewed business rules
- ✅ User has spot-checked merges/deletes
- ✅ User has tested dry-run and approval workflows
- ✅ User explicitly approves Phase 5 completion

---

## Next Steps After Approval

Once Phase 5 is approved:

```bash
# Move to Phase 6
./wins phase start 6
```

Phase 6 will implement:
- Obsidian note generation
- Markdown formatting
- Executive summary generation
- Marketing output generation
- Template rendering
- Output file writing

---

## Historical Context

### Why This Checklist Exists

1. **Prevent Silent Data Loss**: Phase 5 performs irreversible operations
2. **Ensure Business Rule Transparency**: Hidden rules are unacceptable
3. **Maintain Human Control**: AI must not make unreviewed decisions
4. **Enable Audit and Compliance**: Every decision must be traceable
5. **Support System Evolution**: Config-driven rules enable iteration

### Relationship to DESIGN.md

| DESIGN.md Section | Checklist Item |
|-------------------|----------------|
| Business Logic Layer | Business Rule Explicitness |
| Ranking & Scoring | Ranking Logic |
| Merge & Dedup | Merge/Delete Safety |
| Human Oversight | Human Override & Governance |
| Traceability Requirements | Traceability & Provenance |

### Relationship to MASTER_EXECUTION_BLUEPRINT.md

| Blueprint Section | Checklist Item |
|-------------------|----------------|
| Phase 5: Business Judgment | Business Rule Explicitness |
| Phase 5: Ranking | Ranking Logic |
| Phase 5: Merging | Merge/Delete Safety |
| Phase 5: Human Review | Human Override & Governance |
| Phase 5: Configuration | Configuration & Evolvability |

---

## Critical Differences from Phase 4

| Aspect | Phase 4 | Phase 5 |
|--------|---------|---------|
| Allowed Operations | Extract semantics only | Rank, merge, delete |
| Business Rules | None (extraction only) | Central to Phase 5 |
| Human Review | Optional | REQUIRED for destructive ops |
| Reversibility | All operations reversible | Merges/deletes are IRREVERSIBLE without safeguards |
| Config | Prompts only | Full business rule config |
| Risk Level | Low (data preservation) | HIGH (data loss potential) |

---

## Checklist Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial version for Phase 5 |

---

## End of Document

**Maintained by**: `wins` command
**Last Updated**: 2026-02-01
**Status**: Active - Used by `./wins phase review 5`
