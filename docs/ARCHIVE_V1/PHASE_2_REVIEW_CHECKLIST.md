# Phase 2 Scaffolding Review Checklist

**Purpose**: Automated checks for Phase 2 (Scaffolding) output
**Version**: 1.0
**Date**: 2026-02-01

---

## Overview

This checklist is used by the `wins phase review 2` command to automatically validate that the Phase 2 output (project scaffolding) meets all requirements and follows the constraints defined in MASTER_EXECUTION_BLUEPRINT.md and DESIGN.md.

---

## Checklist Items

### Check 0: Basic Compliance (先挡明显越权)

**Checks**:
- All changes only involve directory structure / empty files
- No business logic implemented
- No LLM calls
- No workflow orchestration
- No modifications to Phase 1 artifacts (DESIGN.md)

**Rationale**: Phase 2 is scaffolding ONLY. Any implementation logic is out of scope.

**Failure Message**:
```
❌ Basic Compliance: Phase 2 must only create empty scaffolding.
                   No business logic, LLM calls, or orchestration allowed.
```

**Implementation**: Combination of other checks (forbidden patterns, file content checks)

---

### Check 1: Directory Structure Matches DESIGN.md (核心)

**Checks**: All required directories exist (no more, no less)

**Required Top-Level Directories**:
- `workflow/`
- `models/`
- `processors/`
- `agents/`
- `utils/`
- `config/`
- `templates/`
- `wins/`
- `vault/`

**Required Subdirectories**:
- `workflow/outputs/`

**Rationale**: Per MASTER_EXECUTION_BLUEPRINT.md Phase 2:
> "Create directories strictly derived from module specifications"
> "NOT be inferred or invented"

**Failure Message**:
```
❌ Directory Structure: Missing required directory: workflow/outputs/
```

**Implementation**: File system check against required list

---

### Check 1 (continued): All Required Files Exist

**Checks**: Every .py file from DESIGN.md exists

**Required Files**:

**workflow/**:
- `workflow/__init__.py`
- `workflow/ingest.py`
- `workflow/normalize.py`
- `workflow/deduplicate.py`
- `workflow/outputs/__init__.py`
- `workflow/outputs/executive.py`
- `workflow/outputs/marketing.py`
- `workflow/writer.py`

**models/**:
- `models/__init__.py`
- `models/raw_item.py`
- `models/library.py`

**processors/**:
- `processors/__init__.py`
- `processors/pdf_processor.py`
- `processors/email_processor.py`
- `processors/image_processor.py`
- `processors/text_processor.py`

**agents/**:
- `agents/__init__.py`
- `agents/extraction_agent.py`
- `agents/planner_agent.py`

**utils/**:
- `utils/__init__.py`
- `utils/llm_utils.py`

**config/**:
- `config/config.yaml`

**Root**:
- `requirements.txt`

**Rationale**: All files specified in DESIGN.md must be created. No extra files.

**Failure Message**:
```
❌ Required Files: Missing required file: workflow/ingest.py
```

**Implementation**: File system check against required list

---

### Check 2: All Python Files are "Empty Implementation" (空实现)

**Checks**: For each .py file:
- File exists
- File has module-level docstring
- All function bodies contain only: `pass`
- Functions may have TODO comments before `pass`
- NO logic code

**Explicitly Forbidden** (看到即 Reject):
- `if`, `for`, `while`
- `try` / `except`
- `with`
- Any expressions
- `return` (except implicit None)

**Rationale**: Phase 2 creates structure ONLY. Implementation happens in Phase 3.

**Failure Message**:
```
❌ Empty Implementation: File workflow/ingest.py contains forbidden pattern
                         at line 25: if file_path.exists():
```

**Implementation**: Regex search for forbidden patterns in all .py files

---

### Check 3: Function Signatures Strictly Match DESIGN.md

**Checks**:
- Each function name matches DESIGN.md exactly
- Parameter names and order match DESIGN.md
- Type annotations present
- Return type present
- No extra functions
- No missing functions

**Example**:
```python
# DESIGN.md says:
discover_files(source_dir: Path, country: str, month: str) -> List[Path]

# File must contain:
def discover_files(source_dir: Path, country: str, month: str) -> List[Path]:
    # TODO: Implement
    pass
```

**Rationale**: Scaffolding must be derived from DESIGN.md. No deviations allowed.

**Failure Message**:
```
❌ Function Signatures: Function signature mismatch in workflow/ingest.py
                       Expected: discover_files(source_dir: Path, country: str, month: str) -> List[Path]
                       Found:    discover_files(source_dir, country, month)
```

**Implementation**: Parse function signatures from DESIGN.md and compare with actual files

---

### Check 4: Imports Must All Work (但不能多)

**Checks**:
- `python -c "import workflow.ingest"` succeeds
- `python -c "import models.raw_item"` succeeds
- `python -c "import agents.extraction_agent"` succeeds
- All imports only from:
  - Python stdlib
  - Project internal modules

**Required Imports to Work**:
- workflow.ingest
- workflow.normalize
- workflow.deduplicate
- workflow.outputs.executive
- workflow.outputs.marketing
- workflow.writer
- models.raw_item
- models.library
- processors.pdf_processor
- processors.email_processor
- processors.image_processor
- processors.text_processor
- agents.extraction_agent
- agents.planner_agent
- utils.llm_utils

**Rationale**: Scaffolding must be importable. Broken imports indicate structural errors.

**Failure Message**:
```
❌ Import Check: Import failed: workflow.ingest: No module named 'pathlib'
```

**Implementation**: Attempt to import each module, report ImportError

---

### Check 5: __init__.py Completeness

**Checks**:
- Each package directory has `__init__.py`
- `__init__.py` only contains imports (or is empty)
- No logic code in `__init__.py`

**Required __init__.py Files**:
- `workflow/__init__.py`
- `workflow/outputs/__init__.py`
- `models/__init__.py`
- `processors/__init__.py`
- `agents/__init__.py`
- `utils/__init__.py`

**Rationale**: Python packages require __init__.py. Logic in __init__.py is premature.

**Failure Message**:
```
❌ __init__.py Check: workflow/__init__.py contains logic code
                    or is missing
```

**Implementation**: Check existence and content of all __init__.py files

---

### Check 6: Config / Placeholder Files

**Checks**:
- `config/config.yaml` exists (can be empty structure)
- `templates/` directory exists (can be empty)
- `README.md` exists (placeholder OK)
- `requirements.txt` exists

**Rationale**: These files are part of the scaffold structure.

**Failure Message**:
```
❌ Placeholder Files: Missing config/config.yaml
```

**Implementation**: File existence checks

---

### Check 7: Explicitly Forbidden Behaviors (Phase Boundaries)

**Scaffolding Phase MUST NOT**:
- Implement any business logic
- Call Ollama / LLM
- Write files (except creating scaffold files themselves)
- Infer directory structure
- Refactor DESIGN.md
- "Implement a little feature while we're here"

**Rationale**: These are explicit Phase 2 boundaries from MASTER_EXECUTION_BLUEPRINT.md.

**Failure Message**:
```
❌ Phase Boundary: Scaffolding implemented business logic.
                  Phase 2 MUST NOT contain logic.
```

**Implementation**: Combination of other checks

---

### Check 8: Automation Feasibility Check (为 wins phase review 2)

**Checks**: The following rules MUST be script-checkable:
- All .py files exist
- All function bodies only contain `pass`
- No `if`/`for`/`while`/`try`
- Imports succeed
- File paths align with DESIGN.md

**Rationale**: Automated reviews require automatable checks.

**Implementation**: All checks in this document are implemented in `wins` command

---

### Check 9: Final Decision

**If ALL checks pass**:
```
✅ APPROVE Phase 2 – Proceed to Phase 3
```

**If ANY check fails**:
```
❌ REJECT – Fix Scaffolding
```

**Reviewer Notes**: (Single sentence summary)

---

## Review Process

### Automated Execution

```bash
./wins phase review 2
```

### Automated Checks Run

1. **Check 0**: Basic compliance (no logic, no LLM, no orchestration)
2. **Check 1**: Directory structure matches DESIGN.md
3. **Check 1 (cont)**: All required files exist
4. **Check 2**: All Python files are empty (pass only)
5. **Check 3**: Function signatures match DESIGN.md
6. **Check 4**: All imports work
7. **Check 5**: __init__.py files are complete and empty
8. **Check 6**: Config and placeholder files exist
9. **Check 7**: No forbidden behaviors
10. **Check 8**: All checks are automatable (meta-check)

### Manual Review Steps

After automated checks pass, the user should manually review:

1. **File Count**: Correct number of files (no extras, no missing)
2. **Docstrings**: Each file has a module docstring
3. **TODOs**: Functions have TODO comments indicating what to implement
4. **Type Annotations**: All functions have proper type hints
5. **Import Structure**: Imports are clean and only use stdlib/internal modules

---

## Exit Criteria

Phase 2 is considered complete when:

- ✅ All automated checks pass
- ✅ User has manually reviewed scaffolding
- ✅ User explicitly approves Phase 2 completion

---

## Next Steps After Approval

Once Phase 2 is approved:

```bash
# Move to Phase 3 (not yet implemented)
./wins phase start 3
```

Phase 3 will use the scaffolding to implement:
- Deterministic, non-semantic logic
- Mechanical file discovery
- Mechanical text extraction
- JSON persistence
- String-based deduplication
- CLI argument parsing

---

## Historical Context

### Why This Checklist Exists

1. **Prevent Premature Implementation**: Automated checks catch early implementation attempts
2. **Ensure Design Compliance**: Validates scaffolding matches DESIGN.md exactly
3. **Maintain Quality**: Consistent review process for all phases
4. **Documentation**: Creates audit trail of scaffolding decisions

### Relationship to DESIGN.md

This checklist operationalizes the constraints from DESIGN.md:

| DESIGN.md Section | Checklist Item |
|-------------------|----------------|
| Module List | Directory Structure Check |
| Function Signatures | Function Signature Check |
| MUST NOT Sections | Empty Implementation Check |
| Module Specifications | Import Check |

### Relationship to MASTER_EXECUTION_BLUEPRINT.md

| Blueprint Section | Checklist Item |
|-------------------|----------------|
| Phase 2: Create directories | Directory Structure Check |
| Phase 2: Create all .py files | Required Files Check |
| Phase 2: Add TODOs and pass | Empty Implementation Check |
| Phase 2: Verify imports | Import Check |
| Phase 2: MUST NOT implement logic | Basic Compliance Check |

---

## Checklist Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial version for Phase 2 |

---

## End of Document

**Maintained by**: `wins` command
**Last Updated**: 2026-02-01
**Status**: Active - Used by `./wins phase review 2`
