# Phase 4 Review Checklist

**Purpose**: Review checklist for Phase 4 (Semantic Extraction Layer)
**Version**: 1.0
**Date**: 2026-02-01

---

## Overview

This checklist is used to validate that the Phase 4 output (Semantic Extraction Layer) meets all requirements and follows the constraints defined in MASTER_EXECUTION_BLUEPRINT.md and DESIGN.md.

**Review Method**: ✅ / ❌ / N/A
**Rule**: Any Hard Stop (🟥) failure → Phase 4 REJECTED

---

## Checklist Items

### 🟥 1️⃣ Phase Boundary (Hard Stop)

**Checks**:
- ⬜ Phase 3 code was not modified
- ⬜ RawItem is treated as immutable input
- ⬜ No Phase 5 business rules introduced in Phase 4
- ⬜ No sorting, scoring, or filtering of SuccessStory objects
- ⬜ No merging or deletion of SuccessStory objects
- ⬜ Phase 4 stops explicitly after completion (no continuation to Phase 5)

**Rationale**: Phase 4 MUST only extract semantics. Any Phase 5 behavior (curation, ranking, merging) is a hard violation.

**Failure Message**:
```
❌ Phase Boundary: Phase 4 violated phase boundaries.
                  Phase 4 MUST NOT include Phase 5 behaviors:
                  - Sorting, scoring, or filtering SuccessStory
                  - Merging or deleting SuccessStory
                  - Modifying Phase 3 code
```

**Implementation**: Code review, git diff check against Phase 3, search for forbidden patterns

---

### 🟥 2️⃣ Agent Responsibility Isolation (Hard Stop)

**Checks**:
- ⬜ Extraction Agent ONLY performs semantic extraction
- ⬜ Retry Agent does NOT modify semantic content
- ⬜ Dedup Agent ONLY performs "marking" (no merging)
- ⬜ Finalization Agent does NOT infer or complete missing facts
- ⬜ No Agent crosses responsibility boundaries

**Rationale**: Each Agent must have a single, well-defined responsibility. Cross-responsibility behavior violates the architecture.

**Failure Message**:
```
❌ Agent Isolation: Agent crossed responsibility boundaries.
                   Extraction Agent: Only extract semantics
                   Retry Agent: Only fix JSON/schema errors
                   Dedup Agent: Only mark duplicates (no merge)
                   Finalization Agent: Only finalize, do NOT infer
```

**Implementation**: Code review of each Agent's logic, verify no cross-cutting concerns

---

### 🟥 3️⃣ Schema & JSON Discipline (Hard Stop)

**Checks**:
- ⬜ All LLM outputs are parsed as JSON
- ⬜ All JSON passes explicit schema validation
- ⬜ Schema prohibits additionalProperties
- ⬜ Schema validation failures raise explicit errors
- ⬜ No silent fallback or implicit repair

**Rationale**: LLM outputs are untrustworthy. Schema validation is the ONLY guarantee of correctness.

**Failure Message**:
```
❌ JSON Discipline: LLM output failed schema validation or was not validated.
                   All LLM outputs MUST:
                   - Be parsed as JSON
                   - Pass schema validation
                   - Reject additionalProperties
                   - Fail explicitly on errors
```

**Implementation**: Search for LLM calls, verify all have schema validation, check schema definitions

---

### 🟥 4️⃣ Retry & Failure Handling (Hard Stop)

**Checks**:
- ⬜ Retry is ONLY used for JSON / schema failures
- ⬜ Retry prompt does NOT introduce new semantics
- ⬜ Retry count ≤ 2
- ⬜ Exceeding limit marks as extraction_failed
- ⬜ Single failure does NOT block entire workflow

**Rationale**: Retry is for formatting errors, not for "trying harder" to extract semantics. Failures must be isolated.

**Failure Message**:
```
❌ Retry Handling: Retry logic violated constraints.
                  Retry MUST:
                  - Only be used for JSON/schema failures
                  - NOT introduce new semantic prompts
                  - Limit to 2 attempts
                  - Mark as extraction_failed after limit
                  - Continue processing other items on failure
```

**Implementation**: Review retry logic, verify retry count limits, check error handling

---

### 🟨 5️⃣ Determinism & Reproducibility (Strong Requirement)

**Checks**:
- ⬜ Non-determinism exists ONLY in LLM calls
- ⬜ LLM inputs (prompts) are fully replayable
- ⬜ Same RawItem + Same LLM output ⇒ Same SuccessStory
- ⬜ SuccessStory ID does NOT depend on time or random numbers

**Rationale**: System must be reproducible. The only acceptable non-determinism is LLM output itself.

**Failure Message**:
```
⚠️ Determinism: System introduces non-determinism outside LLM calls.
               SuccessStory generation must be deterministic given:
               - Same RawItem
               - Same LLM output
```

**Allowed**: 1 item may fail, but must explain why

**Implementation**: Review SuccessStory ID generation, check for random/time-based logic

---

### 🟨 6️⃣ Traceability & Audit (Strong Requirement)

**Checks**:
- ⬜ Every DraftSuccessStory has source_raw_item_id
- ⬜ Every SuccessStory can be traced to Draft
- ⬜ Original RawItem text can be reviewed
- ⬜ Logs can locate failure points

**Rationale**: Every output must be traceable to its source for debugging and audit.

**Failure Message**:
```
⚠️ Traceability: Output cannot be traced to source.
               Every SuccessStory MUST have:
               - source_raw_item_id
               - Traceable to DraftSuccessStory
               - Reviewable RawItem text
```

**Allowed**: 1 item may fail, but must explain why

**Implementation**: Check DraftSuccessStory model, verify source_raw_item_id presence, review logging

---

### 🟨 7️⃣ Semantic Dedup (Flag-Only)

**Checks**:
- ⬜ Dedup logic ONLY performs similarity judgment
- ⬜ ONLY outputs potential_duplicate flag
- ⬜ NO merge / collapse behavior
- ⬜ Similarity threshold is configurable and explainable

**Rationale**: Dedup in Phase 4 is for FLAGGING only. Merging is Phase 5 behavior.

**Failure Message**:
```
⚠️ Semantic Dedup: Dedup performed merge/collapse.
                  Phase 4 dedup MUST:
                  - Only judge similarity
                  - Only set potential_duplicate flag
                  - NOT merge or collapse stories
```

**Allowed**: 1 item may fail, but must explain why

**Implementation**: Review dedup logic, verify no merge behavior, check flag-only implementation

---

### 🟩 8️⃣ Human-in-the-Loop (Optional)

**Checks**:
- ⬜ Supports manual review (if enabled)
- ⬜ Manual modifications are persisted
- ⬜ Manual results are NOT overwritten by subsequent Agents
- ⬜ Can distinguish AI output vs manual editing

**Rationale**: Human review is valuable but optional for v1. If implemented, must not be overwritten.

**Failure Message**:
```
⚠️ Human-in-the-Loop: Manual review not properly preserved.
                    If implemented:
                    - Manual edits must be persisted
                    - Not overwritten by AI
                    - Clearly distinguished from AI output
```

**Status**: Not required, but recommended

**Implementation**: If implemented, check review persistence, verify no overwrite

---

### ✅ 9️⃣ Output Sanity Check (Final Gate)

**Checks**:
- ⬜ customer / context / action / outcome fields were NOT fabricated
- ⬜ Empty fields are explicitly empty (NOT inferred/filled)
- ⬜ confidence uses consistent scale
- ⬜ No cross-story field contamination

**Rationale**: Final sanity check that outputs are honest and clean.

**Failure Message**:
```
❌ Output Sanity: Output violates sanity constraints.
                 - Fields must NOT be fabricated
                 - Empty fields must be explicitly empty
                 - Confidence must use consistent scale
                 - No cross-story contamination
```

**Required**: Must pass

**Implementation**: Spot-check outputs, verify empty fields, check confidence values

---

## Phase 4 Final Decision

### Review Result

**Phase 4 Review Result**: _____ ACCEPTED / REJECTED _____

### Blocking Issues

If REJECTED, list all blocking issues:

1. ________________________________________________________________
2. ________________________________________________________________
3. ________________________________________________________________

### Approval

**Approved By**:
- Human Reviewer: _______________________ Date: ________
- AI Reviewer (optional): _______________________ Date: ________

---

## Review Process

### Automated Execution

```bash
./wins phase review 4
```

### Automated Checks Run

1. **Check 1**: Phase boundary (no Phase 5 behavior)
2. **Check 2**: Agent responsibility isolation
3. **Check 3**: Schema & JSON discipline
4. **Check 4**: Retry & failure handling
5. **Check 5**: Determinism & reproducibility
6. **Check 6**: Traceability & audit
7. **Check 7**: Semantic dedup (flag-only)
8. **Check 8**: Human-in-the-loop (optional)
9. **Check 9**: Output sanity check

### Manual Review Steps

After automated checks pass, manually review:

1. **Code Quality**: Are Agent implementations clear and explicit?
2. **Error Handling**: Do failures fail loudly with clear messages?
3. **Logging**: Are all LLM calls logged with prompt/response length?
4. **Schema Definitions**: Are schemas well-defined and restrictive?
5. **Output Quality**: Spot-check 10-20 SuccessStory objects for correctness

---

## Exit Criteria

Phase 4 is considered complete when:

- ✅ All Hard Stop (🟥) checks pass
- ✅ At most 2 Strong Requirement (🟨) checks fail (with explanation)
- ✅ Output Sanity Check (✅) passes
- ✅ User has manually reviewed outputs
- ✅ User explicitly approves Phase 4 completion

---

## Next Steps After Approval

Once Phase 4 is approved:

```bash
# Move to Phase 5
./wins phase start 5
```

Phase 5 will implement:
- SuccessStory ranking and scoring
- SuccessStory merging and deduplication
- Story curation and selection
- Executive summary generation
- Marketing output generation

---

## Historical Context

### Why This Checklist Exists

1. **Prevent Scope Creep**: Phase 4 is for extraction only, not curation
2. **Ensure Agent Purity**: Each Agent must stay within its responsibility
3. **Maintain Data Quality**: Schema validation prevents corrupt outputs
4. **Enable Reproducibility**: Deterministic behavior is essential for debugging
5. **Preserve Traceability**: Every output must be traceable to its source

### Relationship to DESIGN.md

| DESIGN.md Section | Checklist Item |
|-------------------|----------------|
| Extraction Agent Specification | Agent Responsibility Isolation |
| Retry Guard Specification | Retry & Failure Handling |
| Semantic Dedup Specification | Semantic Dedup (Flag-Only) |
| DraftSuccessStory Model | Schema & JSON Discipline |
| Finalization Agent | Output Sanity Check |

### Relationship to MASTER_EXECUTION_BLUEPRINT.md

| Blueprint Section | Checklist Item |
|-------------------|----------------|
| Phase 4: Extraction Agent | Agent Responsibility Isolation |
| Phase 4: Retry Guard | Retry & Failure Handling |
| Phase 4: Schema Validation | Schema & JSON Discipline |
| Phase 4: Determinism | Determinism & Reproducibility |
| Phase 4: Traceability | Traceability & Audit |

---

## Checklist Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial version for Phase 4 |

---

## End of Document

**Maintained by**: `wins` command
**Last Updated**: 2026-02-01
**Status**: Active - Used by `./wins phase review 4`
