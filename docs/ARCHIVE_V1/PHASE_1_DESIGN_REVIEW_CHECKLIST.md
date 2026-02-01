# Phase 1 Design Review Checklist

**Purpose**: Automated checks for Phase 1 (System Design) output
**Version**: 1.0
**Date**: 2026-02-01

---

## Overview

This checklist is used by the `wins phase review 1` command to automatically validate that the Phase 1 output (DESIGN.md) meets all requirements and follows the constraints defined in CLAUDE.md.

---

## Checklist Items

### 1. File Existence Check

**Check**: Verify that `docs/DESIGN.md` exists

**Rationale**: Phase 1 must produce a design document.

**Failure Message**:
```
❌ File Existence: DESIGN.md not found at /path/to/docs/DESIGN.md
```

**Implementation**: File system check

---

### 2. Required Sections Check

**Check**: Verify that all required sections are present in DESIGN.md

**Required Sections**:
- `## 1. Overview`
- `## 2. Module List`
- `## 3. Data Models`
- `## 4. Function Signatures`
- `## 5. Data Flow`
- `## 6. Error Boundaries`

**Rationale**: Each section represents a critical aspect of system design. Missing sections indicate incomplete design work.

**Failure Message**:
```
❌ Required Sections: Missing section: ## 2. Module List
```

**Implementation**: String matching in document content

---

### 3. Code Block Detection

**Check**: Verify that no code blocks (triple backticks ```) are present

**Rationale**: Phase 1 is a design phase. Code blocks indicate implementation details, which are out of scope for Phase 1. Function signatures should use simple formatting, not code blocks.

**Failure Message**:
```
❌ Code Blocks: Design document contains code blocks (```).
                Phase 1 should not contain implementation code.
                (line <N>)
```

**Exception**: None - Phase 1 should have NO code blocks.

**Implementation**: Regex search for triple backticks

---

### 4. Forbidden Phrases Detection

**Check**: Verify that forbidden phrases are NOT present in the document

**Forbidden Phrases** (from CLAUDE.md Section 18):
- "future scalability"
- "generic pipeline"
- "adaptive"
- "intelligent"

**Rationale**: These phrases indicate over-engineering or autonomous behavior, which violate the core constraints of the project:
- CLAUDE.md Section 3.1: "Do Not Be Clever"
- CLAUDE.md Section 3.2: "Determinism Over Autonomy"
- CLAUDE.md Section 17: "Boring, Explicit, Predictable"

**Failure Message**:
```
❌ Forbidden Phrases: Found forbidden phrase: 'future scalability' (line <N>)
```

**Implementation**: Case-insensitive search across all lines

---

### 5. MUST NOT Sections Check

**Check**: Verify that each module section includes a "MUST NOT" subsection

**Rationale**: Per MASTER_EXECUTION_BLUEPRINT.md Phase 1 requirements:
> "Define what each module MUST NOT do"

This is a critical constraint that prevents scope creep and ensures clear boundaries.

**Failure Message**:
```
❌ MUST NOT Section: Module '2.6 processors/*' missing MUST NOT subsection
```

**Implementation**: Parse each `### 2.x` section and verify presence of `**MUST NOT**:` or `MUST NOT:`

---

## Review Process

### Automated Execution

```bash
./wins phase review 1
```

### Manual Review Steps

After automated checks pass, the user should manually review:

1. **Module Boundaries**: Are module responsibilities clear and non-overlapping?
2. **MUST NOT Constraints**: Are MUST NOT sections specific and meaningful?
3. **Data Models**: Do schemas match REQUIREMENTS.md exactly?
4. **Function Signatures**: Are all signatures type-only (no implementation)?
5. **Data Flow**: Is the flow clear and deterministic?
6. **Error Boundaries**: Are error boundaries explicit?

---

## Exit Criteria

Phase 1 is considered complete when:

- ✅ All automated checks pass
- ✅ User has manually reviewed DESIGN.md
- ✅ User explicitly approves Phase 1 completion

---

## Next Steps After Approval

Once Phase 1 is approved:

```bash
# Move to Phase 2 (not yet implemented)
./wins phase start 2
```

Phase 2 will use DESIGN.md as the authoritative specification for:
- Creating directory structure
- Creating empty .py files
- Adding module docstrings
- Adding TODOs

---

## Historical Context

### Why This Checklist Exists

1. **Prevent Scope Creep**: Automated checks catch over-engineering early
2. **Ensure Compliance**: Validates adherence to CLAUDE.md constraints
3. **Maintain Quality**: Consistent review process for all phases
4. **Documentation**: Creates audit trail of design decisions

### Relationship to CLAUDE.md

This checklist operationalizes the constraints from CLAUDE.md:

| CLAUDE.md Section | Checklist Item |
|-------------------|----------------|
| Section 3.1 "Do Not Be Clever" | Forbidden Phrases Check |
| Section 3.2 "Determinism Over Autonomy" | Forbidden Phrases Check |
| Section 4.2 "Directory Structure Is Sacred" | Module Boundaries Review |
| Section 16 "When in Doubt" | All Checks (choose simplest) |

---

## Checklist Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial version for Phase 1 |

---

## End of Document

**Maintained by**: `wins` command
**Last Updated**: 2026-02-01
**Status**: Active - Used by `./wins phase review 1`
