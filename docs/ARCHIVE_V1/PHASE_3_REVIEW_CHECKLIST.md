# Phase 3 Core Logic Review Checklist

**Purpose**: Automated and manual checks for Phase 3 (Core Logic Implementation) output
**Version**: 1.0
**Date**: 2026-02-01

---

## Overview

This checklist is used by the `wins phase review 3` command to automatically validate that the Phase 3 output (core logic implementation) meets all requirements and follows the constraints defined in MASTER_EXECUTION_BLUEPRINT.md and DESIGN.md.

**Phase 3 Scope**: Implement deterministic, non-semantic logic only.

---

## Checklist Items

### Check 0: Phase Prerequisites (Hard Gate)

**Checks**:
- Phase 1 ✅ Approved (DESIGN.md exists and is frozen)
- Phase 2 ✅ Approved (scaffolding complete)
- Phase 3 Checklist ✅ Frozen (this file exists)
- Phase 3 execution prompt is clearly defined

**Rationale**: Phase 3 depends on completed and approved Phase 1 and Phase 2 artifacts. Cannot proceed without solid foundation.

**Failure Message**:
```
❌ Phase Prerequisites: Phase 1 or Phase 2 not approved.
                     Cannot execute Phase 3 until prerequisites are met.
```

**Implementation**: Check for approval markers in Phase 1 and Phase 2 directories

---

### Check 1: Allowed Implementation Scope (Critical)

**Phase 3 MAY**:
- Implement functions declared in DESIGN.md Section 4
- Introduce necessary third-party libraries (must be explicitly documented)
- Write deterministic business logic
- Write pure functions or controlled side-effect I/O
- Explicit error handling boundaries (try/except allowed)

**Phase 3 MUST NOT**:
- Add new modules/files (beyond Phase 2 scaffolding)
- Modify directory structure
- Modify data model fields
- Change function signatures
- Introduce implicit orchestration (run/main/pipeline)

**Rationale**: Per MASTER_EXECUTION_BLUEPRINT.md Phase 3:
> "Implement deterministic, non-semantic logic only"
> "MUST NOT: Call LLMs, interpret semantics, orchestrate workflows"

**Failure Message**:
```
❌ Implementation Scope: File not in scaffolding: workflow/new_module.py
                        Phase 3 MUST NOT add new files.
```

**Implementation**: File system check against Phase 2 file list

---

### Check 2: Implementation Completeness (Per-Function)

**For each implemented function**:

Checks:
- Function signature matches DESIGN.md exactly
- Function has clear input → output
- No dependency on implicit global state
- Side effects (file I/O) are explicitly parameterized
- No "convenience logic" (only does what's in its responsibility)

**Rationale**: Functions must be predictable, testable, and have clear boundaries.

**Example of CORRECT implementation**:
```python
def discover_files(source_dir: Path, country: str, month: str) -> List[Path]:
    """Discover files matching country/month in source directory."""
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    pattern = f"{country}/{month}/*"
    matching_files = list(source_dir.glob(pattern))
    return matching_files
```

**Example of WRONG implementation**:
```python
def discover_files(source_dir: Path, country: str, month: str) -> List[Path]:
    # WRONG: Reading global config
    global_config = load_config()  # ❌ Implicit state

    # WRONG: Doing extra work beyond responsibility
    for file in matching_files:
        extract_text_from_pdf(file)  # ❌ Not discovery's job

    return matching_files
```

**Failure Message**:
```
❌ Implementation Completeness: Function signature changed in workflow/ingest.py
                                Expected: discover_files(source_dir: Path, country: str, month: str) -> List[Path]
                                Found:    discover_files(source_dir, country, month, extra_param: str)
```

**Implementation**: Parse function signatures from DESIGN.md and compare with actual files

---

### Check 3: Determinism & Reproducibility (Core Principle)

**Checks**:
- Same input → same output
- No randomness (unless explicitly in DESIGN.md)
- Time, paths, environment variables are explicitly passed as parameters
- LLM call results are NOT directly used as final SuccessStory objects

**Rationale**: Phase 3 is about deterministic, mechanical logic. No black boxes.

**Failure Message**:
```
❌ Determinism: Function uses random module: processors/pdf_processor.py:42
                Phase 3 logic must be deterministic.
```

**Implementation**: Search for `random`, `uuid.uuid4()` (outside RawItem creation), `time.time()` used as logic

---

### Check 4: LLM Usage Boundaries (High Risk Zone)

**✅ ALLOWED**:
LLM calls ONLY for:
- Text extraction
- Draft generation
- Candidate suggestions

**❌ FORBIDDEN**:
- LLM decides workflow flow
- LLM directly writes final SuccessStory
- LLM modifies data structures
- LLM self-calling / loop-calling

**Rationale**: LLM integration belongs to Phase 4. Phase 3 is mechanical only.

**Exception**: `utils/llm_utils.py` may be created as stub, but MUST NOT be called in Phase 3.

**Failure Message**:
```
❌ LLM Usage: workflow/extract.py calls Ollama directly
             Phase 3 MUST NOT call LLMs. LLM integration is Phase 4.
```

**Implementation**:
- Search for `ollama`, `openai`, `anthropic`, `llm` in function bodies
- Verify no imports of LLM libraries in Phase 3 modules
- Allow llm_utils.py to exist but check it's not imported/used

---

### Check 5: Error Handling & Failure Modes

**Checks**:
- Every I/O point has explicit failure path
- Errors are not silently swallowed
- Error messages are useful for debugging
- Single data failure doesn't crash entire flow

**Rationale**: Failures should be visible and debuggable.

**Example of CORRECT error handling**:
```python
def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF file."""
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            text = extract_text(reader)
            return text
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF {file_path}: {e}")
```

**Failure Message**:
```
❌ Error Handling: Bare except in workflow/ingest.py:25
                  Errors must be explicitly handled, not swallowed.
```

**Implementation**: Search for `except:`, `except Exception:` without logging/re-raising

---

### Check 6: Logging & Observability (Minimum)

**Checks**:
- Critical steps have log statements
- Logs don't contain sensitive information
- Logs are NOT used as control logic

**Rationale**: Observability is required for debugging.

**Required Logging Points**:
- File discovery: count of files found
- Text extraction: success/failure per file
- JSON save/load: file paths and success/failure
- Deduplication: number of duplicates found

**Failure Message**:
```
❌ Logging: Critical module workflow/ingest.py has no logging
           Add logging to track file discovery progress.
```

**Implementation**: Check for `import logging` and `logging.info/debug/error` in core modules

---

### Check 7: Testing Requirements (Minimum Threshold)

**Checks**:
- Each core module has at least 1 unit test
- Tests don't depend on LLM
- Tests don't write real files (use tmp_path fixtures)
- Tests cover failure paths

**Rationale**: Tests prevent regressions and document expected behavior.

**Required Test Coverage**:
- `tests/test_ingest.py` - file discovery logic
- `tests/test_normalize.py` - text extraction (with mock PDFs)
- `tests/test_deduplicate.py` - string-based similarity
- `tests/test_library.py` - JSON save/load round-trip
- `tests/test_raw_item.py` - RawItem dataclass validation

**Failure Message**:
```
❌ Testing: No tests found for workflow/ingest.py
          Phase 3 requires unit tests for all core modules.
```

**Implementation**:
- Check for `tests/` directory
- Count test files
- Verify tests import and run with `pytest --collect-only`

---

### Check 8: Prohibited "Slippery Slope" Behaviors (Red Lines)

**Seeing ANY of these behaviors → Immediate REJECT**:

- "While we're here, add CLI" → ❌ REJECT
- "While we're here, refactor directories" → ❌ REJECT
- "While we're here, abstract a framework layer" → ❌ REJECT
- "While we're here, prepare for Phase 4/5" → ❌ REJECT
- AI self-announces Phase 3 completion → ❌ REJECT

**Rationale**: Scope creep is the #1 cause of phase boundary violations.

**Failure Message**:
```
❌ Phase Boundary: CLI file found: run.py
                  Phase 3 MUST NOT implement orchestration or CLI.
                  That belongs to Phase 5.
```

**Implementation**: Check for files beyond Phase 2 scaffolding + test files

---

### Check 9: Automation Feasibility (for `wins phase review 3`)

**Script-Checkable Rules**:
- Function signatures unchanged from DESIGN.md
- No new files (except tests)
- Tests exist
- Prohibited items not present
- LLM call points are controlled (zero in Phase 3)

**Rationale**: Automated reviews require automatable checks.

**Implementation**: All checks in this document are implemented in `wins` command

---

### Check 10: Import & Dependency Validation

**Checks**:
- All imports are from stdlib or explicitly approved third-party libs
- No circular imports
- All third-party libs listed in `requirements.txt`
- `requirements.txt` has no unnecessary additions

**Allowed Third-Party Libraries for Phase 3**:
- `PyPDF2` or `pypdf` - PDF text extraction
- `email` - stdlib, email parsing
- `pytesseract` - OCR (if needed)
- `Pillow` - Image processing (if needed)

**NOT Allowed in Phase 3**:
- Any LLM libraries (ollama, openai, anthropic, etc.)
- Any workflow orchestration libraries (airflow, prefect, etc.)

**Failure Message**:
```
❌ Dependencies: Disallowed library found: ollama
                Phase 3 MUST NOT use LLM libraries.
```

**Implementation**: Parse `requirements.txt` and imports in all .py files

---

### Check 11: Data Model Preservation

**Checks**:
- RawItem dataclass fields unchanged from DESIGN.md
- SuccessStory dataclass fields unchanged from DESIGN.md
- No new methods added to dataclasses
- No validation logic added to dataclasses (that's Phase 4)

**Rationale**: Data models are frozen in Phase 1. Phase 3 only implements logic, not schema.

**Failure Message**:
```
❌ Data Model: RawItem field added: metadata
               Phase 3 MUST NOT modify data models.
```

**Implementation**: Compare dataclass fields in models/*.py with DESIGN.md Section 3

---

### Check 12: File I/O Boundaries

**Checks**:
- File I/O only happens in explicitly allowed modules:
  - `processors/*.py` - reading source files (PDF, email, image)
  - `models/library.py` - reading/writing JSON files
  - `workflow/ingest.py` - scanning directories (read-only)
- No file I/O in agent modules (that's Phase 4)
- No file I/O in output modules (that's Phase 5)

**Rationale**: File I/O boundaries prevent phase overlap.

**Failure Message**:
```
❌ File I/O: agents/extraction_agent.py contains file I/O
            Agents must not perform file I/O. Use RawItem inputs instead.
```

**Implementation**: Search for `open()`, `Path.read_text()`, `Path.write_text()` in prohibited modules

---

## Review Process

### Automated Execution

```bash
./wins phase review 3
```

### Automated Checks Run

1. **Check 0**: Phase prerequisites approved
2. **Check 1**: Implementation scope (no new files)
3. **Check 2**: Function signatures match DESIGN.md
4. **Check 3**: Determinism (no randomness in logic)
5. **Check 4**: LLM usage (zero LLM calls)
6. **Check 5**: Error handling boundaries
7. **Check 6**: Logging present
8. **Check 7**: Tests exist and run
9. **Check 8**: No slippery slope behaviors
10. **Check 9**: All checks automatable (meta-check)
11. **Check 10**: Import & dependency validation
12. **Check 11**: Data model preservation
13. **Check 12**: File I/O boundaries respected

### Manual Review Steps

After automated checks pass, the user should manually review:

1. **Code Quality**: Clear, readable, follows Python conventions
2. **Error Messages**: Useful and actionable
3. **Test Coverage**: Tests actually verify behavior
4. **Documentation**: Complex logic has inline comments
5. **Dependencies**: Third-party libraries are justified

---

## Exit Criteria

Phase 3 is considered complete when:

- ✅ All automated checks pass
- ✅ User has manually reviewed implementation
- ✅ Core logic is tested and deterministic
- ✅ User explicitly approves Phase 3 completion

---

## Next Steps After Approval

Once Phase 3 is approved:

```bash
# Move to Phase 4
./wins phase start 4
```

Phase 4 will implement:
- LLM integration (Ollama wrapper)
- Extraction agent
- Output generators (executive, marketing)
- Planner agent (advisory only)
- Writer agent (markdown rendering)

---

## Historical Context

### Why This Checklist Exists

1. **Prevent Scope Creep**: Phase 3 is最容易"顺手加功能"的阶段
2. **Ensure Determinism**: Core logic must be predictable and testable
3. **Maintain Boundaries**: Clear separation between mechanical (Phase 3) and semantic (Phase 4) logic
4. **Quality Control**: Tests and error handling are non-negotiable

### Relationship to DESIGN.md

This checklist operationalizes the constraints from DESIGN.md:

| DESIGN.md Section | Checklist Item |
|-------------------|----------------|
| Function Signatures (Section 4) | Implementation Completeness |
| MUST NOT Constraints (Section 2) | Slippery Slope Behaviors |
| Error Boundaries (Section 6) | Error Handling & Failure Modes |
| Module Responsibilities | File I/O Boundaries |

### Relationship to MASTER_EXECUTION_BLUEPRINT.md

| Blueprint Section | Checklist Item |
|-------------------|----------------|
| Phase 3: Implement RawItem dataclass | Data Model Preservation |
| Phase 3: Mechanical file discovery | Determinism & Reproducibility |
| Phase 3: Implement JSON persistence | File I/O Boundaries |
| Phase 3: MUST NOT call LLMs | LLM Usage Boundaries |
| Phase 3: No orchestration | Prohibited Behaviors |

---

## Example: Correct Phase 3 Implementation

### workflow/ingest.py (CORRECT)

```python
"""
Scan source directories and discover new raw input files for processing.
"""

import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def discover_files(source_dir: Path, country: str, month: str) -> List[Path]:
    """Discover files matching country/month in source directory.

    Args:
        source_dir: Root source directory
        country: Country code (e.g., 'US')
        month: Month in YYYY-MM format

    Returns:
        List of discovered file paths

    Raises:
        FileNotFoundError: If source_dir does not exist
    """
    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir}")
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    # Construct pattern: {country}/{month}/*
    pattern = f"{country}/{month}/*"
    matching_files = list(source_dir.glob(pattern))

    logger.info(f"Discovered {len(matching_files)} files matching {pattern}")
    return matching_files


def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """TODO: Extract metadata from file path."""
    # Mechanical extraction: parse path for country, month, etc.
    pass


def is_new_file(file_path: Path, processed_files: List[str]) -> bool:
    """TODO: Check if file has been processed before."""
    # String-based check: is file_path in processed_files list
    pass
```

**What makes this CORRECT**:
- ✅ Deterministic: no randomness
- ✅ Explicit error handling
- ✅ Logging at key points
- ✅ No LLM calls
- ✅ No orchestration
- ✅ Clear I/O boundary (only scanning, not reading)

---

## Example: WRONG Phase 3 Implementation

### workflow/ingest.py (WRONG)

```python
"""
WRONG: Contains LLM call and orchestration
"""

from utils.llm_utils import call_ollama  # ❌ WRONG: Phase 3
from agents.planner_agent import plan_tasks  # ❌ WRONG: Orchestration


def discover_files(source_dir: Path, country: str, month: str) -> List[Path]:
    # ❌ WRONG: Calling LLM to decide what to scan
    suggestion = call_ollama(f"Should I scan {source_dir}?")
    if "yes" not in suggestion.lower():
        return []

    # ❌ WRONG: Doing extra work (normalization)
    files = list(source_dir.glob(f"{country}/{month}/*"))
    for f in files:
        extract_text_from_pdf(f)  # ❌ Not discovery's job

    return files
```

**Why this is WRONG**:
- ❌ Calls LLM (Phase 4 responsibility)
- ❌ Does normalization (belongs in normalize.py)
- ❌ No deterministic behavior
- ❌ Violates single responsibility

---

## Checklist Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial version for Phase 3 |

---

## End of Document

**Maintained by**: `wins` command
**Last Updated**: 2026-02-01
**Status**: Active - Used by `./wins phase review 3`
