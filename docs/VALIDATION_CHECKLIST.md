# ITERATION 2 — FINAL VALIDATION CHECKLIST

**Purpose**: This document is used to validate that all phases of Iteration 2 implementation pass their frozen checklists.

**Usage**: For each phase, run the specified tests/commands and mark PASS or FAIL.

**Status**: AUTHORITATIVE - Aligned with frozen phase checklists

---

## VALIDATION INSTRUCTIONS

1. For each checklist item, perform the specified validation
2. Mark ✅ PASS or ❌ FAIL
3. If ANY item fails, the phase fails
4. All phases must pass for Iteration 2 to be complete

---

## PHASE 1: FOUNDATION (CLI + CONFIG + LLM)

### Validation Commands

```bash
# Test 1: Check run.py exists
ls -la run.py

# Test 2: Test CLI help
python run.py --help

# Test 3: Test invalid command (should error)
python run.py --nonexistent-command

# Test 4: Check config exists
cat config/config.yaml

# Test 5: Test config loading
python -c "import yaml; config = yaml.safe_load(open('config/config.yaml')); print(config)"
```

### Checklist

| # | Criterion | Reference | PASS | FAIL |
|---|-----------|-----------|------|------|
| 1 | CLI entry point exists at project root | WS5 | | |
| 2 | CLI supports three explicit commands only | WS5 | | |
| 3 | CLI rejects unknown commands | WS5 | | |
| 4 | Configuration file exists at `config/config.yaml` | WS5 | | |
| 5 | Configuration defines LLM connection settings | WS5 | | |
| 6 | Configuration defines paths | WS5 | | |
| 7 | Configuration defines Excel status values | Row Ownership | | |
| 8 | LLM wrapper module exists | WS5 | | |
| 9 | LLM wrapper is offline-only | WS5 | | |
| 10 | All operations log to stdout | WS5 | | |
| 11 | Logging format follows specification | WS5 | | |

**Phase 1 Result**: _____ PASS / FAIL

---

## PHASE 2: MARKDOWN EXTRACTION

### Validation Commands

```bash
# Test 1-2: Check directories exist
ls -la vault/00_sources/
ls -la vault/20_notes/sources/

# Test 3: Run markdown extraction
python run.py --extract-markdown --sources vault/00_sources/2026-01/

# Test 4-6: Verify output
ls -la vault/20_notes/sources/
head -20 vault/20_notes/sources/*.md

# Test 7: Check source IDs are unique
cut -d' ' -f1 vault/20_notes/sources/*.md | sort | uniq -d

# Test 8: Verify frontmatter
grep -A 5 "^---" vault/20_notes/sources/*.md
```

### Checklist

| # | Criterion | Reference | PASS | FAIL |
|---|-----------|-----------|------|------|
| 1 | Source directory structure exists | WS1 | | |
| 2 | Markdown output directory exists | WS1 | | |
| 3 | `--extract-markdown` command accepts source path argument | WS1 | | |
| 4 | Source file discovery scans recursively | WS1 | | |
| 5 | Source file discovery identifies supported types | WS1 | | |
| 6 | Source files are never modified | WS1 | | |
| 7 | Unique source_id is generated for each file | WS1 | | |
| 8 | Markdown files are generated with frontmatter | WS1 | | |
| 9 | Markdown is stored in correct location | WS1 | | |
| 10 | Markdown extraction logs progress | WS5 | | |
| 11 | Markdown may be regenerated (overwrites previous) | WS1 | | |

**Phase 2 Result**: _____ PASS / FAIL

---

## PHASE 3: CANDIDATE GENERATION

### Validation Commands

```bash
# Test 1-4: Run story identification
python run.py --identify-stories --sources vault/20_notes/sources/ --output outputs/candidates_v1_20260201.xlsx

# Test 5-9: Open Excel and verify
# Open outputs/candidates_v1_20260201.xlsx in Excel/LibreOffice
# Verify:
# - Stories worksheet has status column
# - All rows have status=candidate
# - Consolidation hints column exists
# - Evidence worksheet populated

# Test 10-13: Code inspection for violations
grep -r "consolidat" src/ --exclude-dir=__pycache__
grep -r "dedup" src/ --exclude-dir=__pycache__
grep -r "merge" src/ --exclude-dir=__pycache__
```

### Checklist

| # | Criterion | Reference | PASS | FAIL |
|---|-----------|-----------|------|------|
| 1 | `--identify-stories` command exists | WS2 | | |
| 2 | Command accepts source input argument | WS2 | | |
| 3 | Command outputs to new Excel file | WS2 | | |
| 4 | Excel workbook has required worksheets | WS3 | | |
| 5 | Stories worksheet has status column | Row Ownership | | |
| 6 | All generated rows have status=candidate | WS2 | | |
| 7 | Candidate rows include required fields | WS2 | | |
| 8 | Consolidation hints are generated | WS2 | | |
| 9 | Multiple candidates per source are allowed | WS2 | | |
| 10 | NO consolidation logic exists | WS2 Non-Responsibilities | | |
| 11 | NO deduplication logic exists | WS2 Non-Responsibilities | | |
| 12 | Evidence references are tracked | WS2 | | |
| 13 | System treats rows as candidates only | Row Ownership | | |

**Phase 3 Result**: _____ PASS / FAIL

---

## PHASE 4: EXCEL CONSOLIDATION WORKSPACE

### Validation Commands

```bash
# Test 1-2: Check output directory and versioning
ls -la outputs/

# Run multiple times to verify versioning
python run.py --identify-stories --sources vault/20_notes/sources/
python run.py --identify-stories --sources vault/20_notes/sources/
python run.py --identify-stories --sources vault/20_notes/sources/
ls -la outputs/*.xlsx

# Test 3-11: Manual verification
# Open each generated Excel file
# Verify version numbers increment
# Modify a row: set status to "final"
# Re-run command
# Verify new file created, "final" row not modified

# Test 10: Check metadata worksheet
# Verify Metadata sheet contains: version, generated_at, generated_by
```

### Checklist

| # | Criterion | Reference | PASS | FAIL |
|---|-----------|-----------|------|------|
| 1 | Excel output directory exists | WS3 | | |
| 2 | New Excel files are always created | WS3 Versioning | | |
| 3 | Version numbering increments | WS3 | | |
| 4 | Human-owned rows are read-only | Row Ownership | | |
| 5 | Row status column exists and is validated | Row Ownership | | |
| 6 | NO automatic merge logic exists | WS3 Key Principles | | |
| 7 | NO conflict resolution logic exists | WS3 Key Principles | | |
| 8 | NO stable entity ID requirement | WS3 Key Principles | | |
| 9 | Excel file can be opened and edited by humans | WS3 | | |
| 10 | Metadata worksheet tracks version info | WS3 | | |
| 11 | System NEVER overwrites existing Excel files | WS3 Versioning | | |

**Phase 4 Result**: _____ PASS / FAIL

---

## PHASE 5: EXECUTIVE SUMMARY GENERATION

### Validation Commands

```bash
# Test 1-4: Prepare test data
# Create Excel file with some rows status=final, some status=candidate
# Then run:
python run.py --summary executive --input outputs/wins_library_v1_20260201.xlsx --output outputs/executive_summary_20260201.md

# Test 5: Check prompts directory
ls -la prompts/
cat prompts/executive_summary.yaml

# Test 6-7: Verify summary content
cat outputs/executive_summary_20260201.md
# Verify: Only final rows included, warning if no final rows

# Test 8-11: Verify no modification
# Compare summary content to Excel final rows
# Verify content is identical, not rewritten
```

### Checklist

| # | Criterion | Reference | PASS | FAIL |
|---|-----------|-----------|------|------|
| 1 | `--summary` command exists | WS5 | | |
| 2 | Command accepts Excel input argument | WS4 | | |
| 3 | Command accepts prompt template argument | WS4 | | |
| 4 | Command outputs Markdown file | WS4 | | |
| 5 | Prompt templates directory exists | WS4 | | |
| 6 | ONLY final rows are consumed | WS4 Rule | | |
| 7 | Summary warns if no final rows exist | WS4 | | |
| 8 | NO ambiguity resolution is attempted | WS4 Behavior | | |
| 9 | NO content rewriting occurs | WS4 Behavior | | |
| 10 | Summary includes traceability references | WS4 Output | | |
| 11 | Summary reflects human-approved content only | WS4 Behavior | | |

**Phase 5 Result**: _____ PASS / FAIL

---

## FINAL VALIDATION: SUCCESS CRITERIA

### Cross-Cutting Validation

```bash
# Test 1: Search for autonomous decision-making
grep -r "consolidat" src/ --exclude-dir=__pycache__
grep -r "dedup" src/ --exclude-dir=__pycache__
grep -r "auto.*merge" src/ --exclude-dir=__pycache__

# Test 2: Verify file versioning
ls -la outputs/*.xlsx
# Confirm: No files have been overwritten

# Test 3: Generate and inspect summary
python run.py --summary executive --input outputs/wins_library_v1.xlsx
cat outputs/executive_summary_*.md
# Confirm: Only final rows, traceability present

# Test 4: Review all AI decisions
grep -r "final" src/ --exclude-dir=__pycache__ | grep -i "status"
# Confirm: AI never sets status=final automatically
```

### Checklist

| # | Criterion | Reference | PASS | FAIL |
|---|-----------|-----------|------|------|
| 1 | Humans control all consolidation and decisions | Success Criteria | | |
| 2 | Excel files are never overwritten | Success Criteria | | |
| 3 | Summaries are trustworthy without post-editing | Success Criteria | | |
| 4 | AI never acts as a decision-maker | Success Criteria | | |

**Final Validation Result**: _____ PASS / FAIL

---

## HUMAN PRIMACY ENFORCEMENT VALIDATION

### Critical Safety Checks

| # | Criterion | Reference | PASS | FAIL |
|---|-----------|-----------|------|------|
| 1 | No autonomous consolidation exists | Human Primacy MUST NOT | | |
| 2 | No automatic deduplication exists | Human Primacy MUST NOT | | |
| 3 | Human-owned content is never modified | Human Primacy MUST NOT | | |
| 4 | Human-edited Excel files are never overwritten | Human Primacy MUST NOT | | |
| 5 | System treats human-owned rows as read-only | Human Primacy MUST | | |
| 6 | System generates new files on every run | Human Primacy MUST | | |
| 7 | System provides traceability | Human Primacy MUST | | |
| 8 | System favors simplicity over automation | Human Primacy MUST | | |

**Human Primacy Result**: _____ PASS / FAIL

---

## OVERALL ITERATION 2 RESULT

**Status**: _____ COMPLETE / INCOMPLETE

**Sign-off**: __________________

**Date**: __________________

---

## NOTES

- All checklist items must PASS for phase to pass
- All phases must PASS for Iteration 2 to be COMPLETE
- Any FAIL requires fix and re-validation
- Human Primacy Enforcement items are veto criteria (any fail = iteration fails)
