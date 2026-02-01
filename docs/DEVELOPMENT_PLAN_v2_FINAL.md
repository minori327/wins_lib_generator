# ITERATION 2 DEVELOPMENT PLAN
**(HUMAN-PRIMARY · FINAL · AUTHORITATIVE)**

**Based on**: REQUIREMENTS_v2.md (Authoritative)
**Date**: 2026-02-01
**Status**: FINAL — AUTHORITATIVE FOR ITERATION 2

---

This document is AUTHORITATIVE for Iteration 2.
No architectural or control-flow changes are allowed without explicit human approval.

---

## HUMAN PRIMACY CLAUSE

### Foundational Principle

This system exists to support human decision-making, not to replace it.

### Human Authority vs System Role

| Aspect | Human Role | System Role |
|--------|-----------|-------------|
| **Business judgment** | Decide what constitutes a Success Story | Extract and suggest candidates |
| **Consolidation** | Combine multiple candidates into final stories | Provide consolidation hints only |
| **Deduplication** | Decide whether stories are duplicates | Flag possible similarities |
| **Quality assurance** | Validate accuracy and completeness | Provide traceable evidence |
| **Prioritization** | Decide what matters | Provide sortable fields |

### System Constraints

**The system MUST NOT**:
- Make autonomous consolidation decisions
- Perform automatic deduplication
- Modify human-approved content
- Overwrite human-edited Excel files
- Make final business judgments

**The system MUST**:
- Treat human-owned rows as read-only
- Generate new files on every run
- Provide clear evidence and traceability
- Favor simplicity over automation

---

## ROW-LEVEL OWNERSHIP MODEL

Excel rows have a lifecycle status:

| Status | Meaning | System Behavior |
|--------|---------|-----------------|
| `candidate` | AI-generated, awaiting review | Read-write (append only) |
| `consolidated` | Human-merged from candidates | Read-only |
| `final` | Human-approved, business-ready | Read-only |
| `archived` | Human-excluded | Read-only |

**Rule**:
Once a row is marked `consolidated`, `final`, or `archived`, it is human-owned and must never be modified by the system.

**Clarification**:
- `consolidated` rows may still be draft-quality.
- Only rows with `status = final` are eligible for executive summaries or downstream use.

---

## WORK STREAM 1: KNOWLEDGE BASE PROCESSING

**Goal**: Transform original source files into navigable Markdown working views while preserving source integrity.

- Sources stored in `vault/00_sources/` (authoritative)
- Markdown stored in `vault/20_notes/sources/`
- Markdown is non-authoritative and may be regenerated
- Human edits to Markdown may be overwritten

*(No structural change from previous plan)*

---

## WORK STREAM 2: SUCCESS STORY CANDIDATE GENERATION

### Purpose

Generate candidate Success Story rows and consolidation hints for human review.

### Explicit Non-Responsibilities

- No consolidation
- No deduplication
- No final judgment

### Candidate Model

Each candidate row includes:

- Customer
- Context
- Action
- Outcome
- Metrics
- Evidence references
- Consolidation hints (textual, advisory only)

Multiple candidates per source are explicitly allowed.

### Output

Excel workbook: `candidates_v{N}_YYYYMMDD.xlsx`
- Status for all rows: `candidate`

### Single Command (Iteration 2)

```bash
python run.py --identify-stories
```

This command:
- Scans sources or Markdown
- Generates candidate rows
- Generates consolidation hints
- Outputs a new Excel file

---

## WORK STREAM 3: EXCEL CONSOLIDATION WORKSPACE

### Purpose

Provide Excel as a human consolidation workspace, not an entity store.

### Key Principles

- Humans may merge multiple candidates into one final story
- No stable entity IDs required
- No automatic merging or conflict resolution
- New files are always created

### Workbook Structure

Worksheets:
- **Stories** (row status, story fields, hints)
- **Evidence**
- **Metrics**
- **Metadata**

### Versioning Philosophy

- System never overwrites files
- Each run creates a new file
- Humans decide when to rename or publish as `wins_library_vN.xlsx`

---

## WORK STREAM 4: EXECUTIVE SUMMARY GENERATION

### Rule

**Only rows with `status = final` are consumed.**

### Behavior

- Summaries reflect human-approved content only
- No ambiguity resolution
- No content rewriting

### Output

- Markdown file in `outputs/`

---

## WORK STREAM 5: INTEGRATION & TOOLING

### CLI Philosophy

- Explicit commands only
- No full automation pipeline
- Human review between every step

### Supported Commands (Iteration 2)

| Command | Purpose |
|---------|---------|
| `--extract-markdown` | Source → Markdown |
| `--identify-stories` | Generate candidates + hints |
| `--summary` | Generate summaries from final rows |

---

## BLOCKING QUESTIONS (ITERATION 2)

### BQ-1: Story Persistence
**Owner Decision**: Direct to Excel only. No JSON intermediate.

### BQ-2: Source ID Strategy
(Choose path hash / content hash / UUID)

### BQ-3: Consolidation Hint Representation
(Text column vs separate worksheet)

*(Remaining questions unchanged and explicitly human-decided)*

---

## IMPLEMENTATION SEQUENCE

1. **WS5** — CLI + config + LLM wrapper
2. **WS1** — Markdown extraction
3. **WS2** — Candidate generation
4. **WS3** — Human consolidation in Excel
5. **WS4** — Summary generation

---

## SUCCESS CRITERIA

- [ ] Humans control all consolidation and decisions
- [ ] Excel files are never overwritten
- [ ] Summaries are trustworthy without post-editing
- [ ] AI never acts as a decision-maker

---

## END OF DOCUMENT
