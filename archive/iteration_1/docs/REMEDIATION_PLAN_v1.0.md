# Wins Library System - POST-AUDIT REMEDIATION PLAN v1.0

**Analysis Date**: 2026-02-01
**Analyst**: Remediation Agent
**Purpose**: Make system operational as v1.0 while preserving phase boundaries

---

## 1️⃣ v1.0 Enablement Summary

### Current State: NON-OPERATIONAL

The system is non-operational because:

1. **No Entry Point**: No `run.py` or equivalent to execute workflows
2. **No Orchestrator**: Phases are implemented but not connected
3. **Config Incomplete**: `config.yaml` is empty placeholder
4. **No Tests**: Zero test coverage prevents safe deployment

### What Changes After Remediation

After completing this plan, the system will:

✅ **Be executable** via CLI commands: `python run.py --mode weekly`
✅ **Run end-to-end** from raw files to published outputs
✅ **Handle errors** gracefully with clear reporting
✅ **Be testable** with basic test coverage for critical paths
✅ **Be configurable** via validated YAML files

### What Does NOT Change

❌ Phase boundaries (preserved exactly)
❌ Module responsibilities (no refactoring)
❌ Feature scope (no new features)
❌ Architecture design (no restructure)

---

## 2️⃣ Remediation Work Breakdown Table

| Step | File(s) | Description | Risk Addressed | Est. Effort |
|------|---------|-------------|----------------|-------------|
| **1** | `config/config.yaml` | Populate with complete system configuration | Config validation failures | 1h |
| **2** | `run.py` | Create CLI entry point with argparse | No execution capability | 2-3h |
| **3** | `workflow/orchestrator.py` | Create phase orchestration coordinator | No end-to-end execution | 4-6h |
| **4** | `tests/test_processors.py` | Test PDF, email, image processors | Untested core logic | 2-3h |
| **5** | `tests/test_models.py` | Test RawItem and SuccessStory | Untested data models | 1-2h |
| **6** | `tests/test_extraction.py` | Test LLM extraction with mocks | Untested LLM integration | 2-3h |
| **7** | `tests/test_orchestration.py` | Test end-to-end workflow | Untested integration | 3-4h |
| **8** | `utils/config_validator.py` | Validate YAML configs on startup | Runtime config errors | 2h |
| **9** | `README.md` | Update with setup and usage instructions | Operators can't run system | 1h |
| **10** | `requirements.txt` | Ensure all dependencies listed | Missing dependencies | 0.5h |

**Total Estimated Effort**: 18.5-25.5 hours

---

## 3️⃣ Minimal Orchestrator Specification

### Phase Execution Order

```
┌─────────────────────────────────────────────────────────────┐
│                   USER TRIGGERS CLI                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  1. LOAD CONFIG & VALIDATE                                  │
│     - Load config/config.yaml                                │
│     - Validate all YAML files                               │
│     - Exit on error with clear message                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. DISCOVER FILES (Phase 3)                                │
│     - workflow.ingest.discover_files()                      │
│     - Return: List[Path]                                    │
│     - On error: Log, continue with empty list              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. NORMALIZE TO RAWITEMS (Phase 3)                         │
│     - workflow.normalize.normalize_*()                      │
│     - For each discovered file                             │
│     - Return: List[RawItem]                                 │
│     - On error: Log file, skip, continue                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. EXTRACT DRAFT STORIES (Phase 4)                         │
│     - agents.extraction_agent.extract_from_raw_item()      │
│     - For each RawItem                                      │
│     - Return: List[DraftSuccessStory]                       │
│     - On error: Log, create failure record, continue       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  5. NORMALIZE DRAFTS (Phase 4)                              │
│     - agents.draft_normalization_agent.normalize_draft()   │
│     - For each DraftSuccessStory                            │
│     - Return: List[DraftSuccessStory]                       │
│     - On error: Log, skip draft, continue                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  6. SEMANTIC DEDUPLICATION (Phase 4)                        │
│     - agents.semantic_dedup_agent.detect_duplicates()       │
│     - Input: List[DraftSuccessStory]                        │
│     - Return: DuplicateFlag list                           │
│     - On error: Log, continue without dedup                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  7. FINALIZE TO SUCCESSSTORY (Phase 4)                      │
│     - agents.finalization_agent.finalize_stories()         │
│     - Input: DraftSuccessStory list                         │
│     - Output: List[SuccessStory]                            │
│     - On error: Log, skip story, continue                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  8. MECHANICAL DEDUPLICATION (Phase 3)                      │
│     - workflow.deduplicate.deduplicate_stories()           │
│     - Input: List[SuccessStory]                             │
│     - Output: Deduplicated List[SuccessStory]              │
│     - On error: Log, continue with all stories             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  9. SAVE TO LIBRARY (Phase 4)                               │
│     - models.library.save_success_story()                  │
│     - For each SuccessStory                                 │
│     - Output: JSON files in library_dir                     │
│     - On error: Log, skip story, continue                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  10. SUCCESS EVALUATION (Phase 5)                          │
│      - agents.success_evaluation_agent.evaluate_story()    │
│      - For each SuccessStory                                │
│      - Return: EvaluationResult                             │
│      - On error: Log, mark as "pending", continue          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  11. RANKING (Phase 5)                                      │
│      - agents.ranking_agent.rank_stories()                 │
│      - Input: List[SuccessStory]                            │
│      - Output: Ranked List[SuccessStory]                    │
│      - On error: Log, preserve original order              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  12. OUTPUT PREPARATION (Phase 5)                           │
│      - agents.output_preparation_agent.prepare_outputs()   │
│      - Input: List[SuccessStory]                            │
│      - Output: Prepared outputs for each story             │
│      - On error: Log, skip story, continue                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  13. WRITE OUTPUTS (Phase 6)                                │
│      - workflow.writer.write_executive_outputs()           │
│      - workflow.writer.write_marketing_outputs()            │
│      - Input: SuccessStory list, output_dir                 │
│      - Output: Markdown files in vault/                     │
│      - On error: Log, continue with remaining              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  14. PUBLISHING (Phase 7) - OPTIONAL                         │
│      - workflow.publisher.publish_artifact()               │
│      - If publish enabled in config                         │
│      - Input: PublishRequest for each output               │
│      - On error: Log publish failure, continue              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  15. SUMMARY & REPORT                                       │
│      - Log total stories processed                          │
│      - Log errors encountered                               │
│      - Write summary to vault/summaries/                    │
└─────────────────────────────────────────────────────────────┘
```

### Control Flow

**Main Orchestrator Function**:
```python
def run_weekly_workflow(
    countries: List[str],
    month: str,
    source_dir: Path,
    library_dir: Path,
    output_dir: Path
) -> WorkflowResult:
    """
    Execute end-to-end weekly update workflow.

    Returns:
        WorkflowResult with stories_processed, errors, output_paths
    """
```

**Error Handling Semantics**:

| Phase | Failure Behavior | Continuation |
|-------|-----------------|--------------|
| File Discovery | Log error, continue with empty list | ✅ Continue |
| Normalization | Log file, skip file | ✅ Continue |
| Extraction | Log, create failure record | ✅ Continue |
| Finalization | Log, skip story | ✅ Continue |
| Deduplication | Log, continue without dedup | ✅ Continue |
| Save | Log, skip story | ⚠️ Partial save |
| Evaluation | Log, mark as "pending" | ✅ Continue |
| Output Write | Log, continue with remaining | ⚠️ Partial output |
| Publish | Log publish failure | ✅ Continue |

**Rollback Behavior**:
- No automatic rollback (would require transaction state)
- Failed phases log errors but continue
- Partial output is acceptable (better than complete failure)
- Human can re-run to fix specific failures

---

## 4️⃣ Minimal CLI Specification

### Command Syntax

```bash
python run.py <mode> [options]
```

### Modes

| Mode | Purpose | Required Flags | Example |
|------|---------|----------------|---------|
| `weekly` | Run weekly update workflow | `--country`, `--month` | `python run.py weekly --country US --month 2026-01` |
| `status` | Show library statistics | None | `python run.py status` |
| `validate` | Validate configuration files | None | `python run.py validate` |
| `review` | Review pending stories (Phase 5) | `--story-id` | `python run.py review --story-id win-2026-01-US-1234` |
| `publish` | Publish prepared outputs | `--artifact-id` | `python run.py publish --artifact-id pub-xxx` |

### Flags

| Flag | Type | Description | Example |
|------|------|-------------|---------|
| `--country` | string | Country code (can specify multiple) | `--country US --country UK` |
| `--month` | string | Month in YYYY-MM format | `--month 2026-01` |
| `--source-dir` | path | Override source directory | `--source-dir ./vault/00_sources` |
| `--library-dir` | path | Override library directory | `--library-dir ./wins` |
| `--output-dir` | path | Override output directory | `--output-dir ./vault/outputs` |
| `--config` | path | Override config file | `--config ./config/config.yaml` |
| `--dry-run` | flag | Validate without processing | `--dry-run` |
| `--verbose` | flag | Enable debug logging | `--verbose` |
| `--story-id` | string | Story ID to review | `--story-id win-2026-01-US-1234` |
| `--approve` | flag | Approve story for publishing | `--approve` |

### Example Invocations

#### Weekly Update (Primary Use Case)
```bash
# Update all countries for January 2026
python run.py weekly --month 2026-01

# Update specific countries
python run.py weekly --country US --country UK --month 2026-01

# Dry run to validate configuration
python run.py weekly --month 2026-01 --dry-run
```

#### Status Check
```bash
# Show library statistics
python run.py status

# Output example:
# Library: ./wins
# Total Stories: 42
# By Country: US: 15, UK: 12, CN: 10, Other: 5
# By Month: 2026-01: 42
# By Confidence: high: 28, medium: 12, low: 2
```

#### Configuration Validation
```bash
# Validate all configuration files
python run.py validate

# Checks:
# - config/config.yaml syntax
# - config/business_rules.yaml syntax
# - config/output_config.yaml syntax
# - config/publish_config.yaml syntax
# - Required directories exist
```

#### Story Review (Phase 5)
```bash
# Review a specific story
python run.py review --story-id win-2026-01-US-1234

# Interactive output:
# Story: ACME Corporation (US)
# Confidence: high
# Evaluation: Approved
# Rank: 5/42
# Approve? (y/n): _
```

#### Publishing (Phase 7)
```bash
# Publish an artifact
python run.py publish --artifact-id pub-xxx --approve

# Output:
# Publishing pub-xxx to website...
# ✓ Published to: https://example.com/api/stories
# Audit log: vault/publish_audit.log.jsonl
```

### Human-Interaction Pause Points

1. **Story Review** (`--review` mode)
   - Display story details
   - Display evaluation results
   - Prompt for approval/rejection
   - Wait for human input

2. **Publish Approval** (`--publish` mode without `--approve`)
   - Display publish request details
   - Prompt for approval
   - Wait for human input

---

## 5️⃣ Configuration Integrity Analysis

### Required Config Files

| File | Status | Missing Fields | Action Required |
|------|--------|----------------|-----------------|
| `config/config.yaml` | ⚠️ EMPTY | All fields | Populate with complete config |
| `config/business_rules.yaml` | ✅ COMPLETE | None | None |
| `config/output_config.yaml` | ✅ COMPLETE | None | None |
| `config/publish_config.yaml` | ✅ COMPLETE | None | None |

### Required `config/config.yaml` Structure

```yaml
# Wins Library System Configuration v1.0

# System paths
paths:
  vault_root: "./vault"
  sources_dir: "./vault/00_sources"
  library_dir: "./wins"
  outputs_dir: "./vault/outputs"
  notes_dir: "./vault/notes"
  weekly_dir: "./vault/weekly"

# LLM configuration
llm:
  backend: "ollama"
  base_url: "http://localhost:11434"
  model: "glm-4:9b"
  temperature: 0.3
  max_tokens: 2000
  timeout_seconds: 120

# Processing configuration
processing:
  batch_size: 10  # Number of files to process per batch
  max_retries: 3  # Number of LLM retry attempts
  retry_delay_seconds: 5

# Deduplication configuration
deduplication:
  similarity_threshold: 0.85
  method: "content_hash"  # Phase 3: content_hash, Phase 4: llm

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/wins_library.log"

# Orchestrator configuration
orchestrator:
  continue_on_error: true
  save_partial_results: true
  create_missing_dirs: true
```

### Startup Validation Rules

**Pre-flight Checks** (must pass before execution):

1. **Config File Validation**
   - All YAML files parse correctly
   - Required top-level keys exist
   - Paths are valid (if specified)

2. **Directory Validation**
   - Source directory exists OR can be created
   - Library directory exists OR can be created
   - Output directory exists OR can be created

3. **LLM Connectivity**
   - Ollama server is reachable
   - Model is available
   - API responds to health check

**Runtime Config Checks** (during execution):

1. **File Type Support**
   - PDF processor dependencies available
   - OCR dependencies available (if images present)
   - Email parser dependencies available

2. **Template Validation**
   - All Jinja2 templates are valid
   - Templates can be loaded

3. **Channel Availability**
   - Publish channels configured (if publishing enabled)
   - Required env vars set (for API channels)

---

## 6️⃣ Test Strategy (Code-Aware)

### Minimal Test Suite for v1.0

#### Test Priority Matrix

| Priority | Test | Module | Risk Mitigated |
|----------|------|--------|----------------|
| P0 | `test_config_validation` | utils/config_validator.py | Invalid config crashes system |
| P0 | `test_raw_item_creation` | models/raw_item.py | Data model corruption |
| P0 | `test_success_story_serialization` | models/library.py | Can't save/load stories |
| P0 | `test_pdf_extraction` | processors/pdf_processor.py | Can't process PDFs |
| P0 | `test_email_extraction` | processors/email_processor.py | Can't process emails |
| P1 | `test_normalize_pdf` | workflow/normalize.py | RawItem creation fails |
| P1 | `test_file_discovery` | workflow/ingest.py | Can't find source files |
| P1 | `test_draft_extraction` | agents/extraction_agent.py | LLM extraction fails |
| P1 | `test_story_finalization` | agents/finalization_agent.py | ID generation broken |
| P1 | `test_orchestrator_happy_path` | workflow/orchestrator.py | End-to-end broken |
| P2 | `test_mechanical_dedup` | workflow/deduplicate.py | Duplicates not removed |
| P2 | `test_output_generation` | workflow/outputs/ | Can't generate outputs |
| P2 | `test_error_handling` | workflow/orchestrator.py | Errors crash system |

### Explicitly Excluded Tests (Low Value for v1.0)

- ❌ Performance tests (not critical for v1.0)
- ❌ Stress tests with large datasets (defer to v1.1)
- ❌ LLM output quality tests (subjective, hard to automate)
- ❌ Template rendering edge cases (covered by manual testing)
- ❌ Channel adapter integrations (stubs are acceptable for v1.0)
- ❌ Signal aggregation tests (Phase 8 is operational but not critical path)

---

## 7️⃣ File-Level Remediation Plan

### File 1: `config/config.yaml`

**Purpose**: Provide complete system configuration

**Scope**:
- ✅ Add all required configuration sections
- ✅ Do NOT add new features
- ✅ Use documented structure from audit

**Dependencies**: None

**Estimated Effort**: 1 hour

**Content**:
```yaml
paths:
  vault_root: "./vault"
  sources_dir: "./vault/00_sources"
  library_dir: "./wins"
  outputs_dir: "./vault/outputs"

llm:
  backend: "ollama"
  base_url: "http://localhost:11434"
  model: "glm-4:9b"

processing:
  batch_size: 10
  max_retries: 3
  retry_delay_seconds: 5

deduplication:
  similarity_threshold: 0.85

logging:
  level: "INFO"
  file: "logs/wins_library.log"
```

---

### File 2: `run.py`

**Purpose**: CLI entry point for system execution

**Scope**:
- ✅ Parse command-line arguments
- ✅ Load configuration
- ✅ Call orchestrator
- ✅ Handle errors gracefully
- ❌ NOT implement business logic
- ❌ NOT modify phase responsibilities

**Dependencies**:
- `workflow/orchestrator.py` (must be created first)
- `utils/config_validator.py` (must be created first)

**Estimated Effort**: 2-3 hours

**Key Functions**:
```python
def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Wins Library System")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Weekly mode
    weekly_parser = subparsers.add_parser("weekly")
    weekly_parser.add_argument("--country", action="append", required=True)
    weekly_parser.add_argument("--month", required=True)
    weekly_parser.add_argument("--dry-run", action="store_true")

    # Status mode
    status_parser = subparsers.add_parser("status")

    # Validate mode
    validate_parser = subparsers.add_parser("validate")

    # Review mode
    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("--story-id", required=True)

    # Publish mode
    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("--artifact-id", required=True)
    publish_parser.add_argument("--approve", action="store_true")

    args = parser.parse_args()

    # Execute mode
    if args.mode == "weekly":
        run_weekly(args)
    elif args.mode == "status":
        run_status(args)
    elif args.mode == "validate":
        run_validate(args)
    elif args.mode == "review":
        run_review(args)
    elif args.mode == "publish":
        run_publish(args)
```

---

### File 3: `workflow/orchestrator.py` (NEW)

**Purpose**: Coordinate phase execution in correct order

**Scope**:
- ✅ Call phases in documented order
- ✅ Handle errors per phase semantics
- ✅ Provide clear logging
- ✅ Return WorkflowResult
- ❌ NOT modify phase implementations
- ❌ NOT add new business logic

**Dependencies**:
- All phase modules (already exist)
- `models/library.py`

**Estimated Effort**: 4-6 hours

**Key Function**:
```python
@dataclass
class WorkflowResult:
    stories_processed: int
    stories_succeeded: int
    stories_failed: int
    errors: List[str]
    output_paths: List[Path]
    duration_seconds: float

def run_weekly_workflow(
    countries: List[str],
    month: str,
    source_dir: Path,
    library_dir: Path,
    output_dir: Path,
    config: Dict[str, Any]
) -> WorkflowResult:
    """
    Execute end-to-end weekly workflow.

    Coordinates phases in order:
    1. File discovery
    2. Normalization
    3. Extraction
    4. Deduplication
    5. Finalization
    6. Save
    7. Evaluation
    8. Ranking
    9. Output preparation
    10. Write outputs
    11. Publishing (optional)
    """
    start_time = time.time()
    errors = []
    stories_succeeded = 0

    # Phase 3: Discovery
    all_files = []
    for country in countries:
        try:
            files = discover_files(source_dir, country, month)
            all_files.extend(files)
        except Exception as e:
            errors.append(f"Discovery failed for {country}: {e}")
            continue

    # Phase 3: Normalization
    raw_items = []
    for file_path in all_files:
        try:
            if file_path.suffix == ".pdf":
                raw_item = normalize_pdf(file_path, country, month)
            elif file_path.suffix == ".eml":
                raw_item = normalize_email(file_path, country, month)
            # ... other types
            raw_items.append(raw_item)
        except Exception as e:
            errors.append(f"Normalization failed for {file_path.name}: {e}")
            continue

    # Phase 4: Extraction
    draft_stories = []
    for raw_item in raw_items:
        try:
            draft_story, failure = extract_from_raw_item(raw_item, ...)
            if draft_story:
                draft_stories.append(draft_story)
            else:
                errors.append(f"Extraction failed for {raw_item.id}: {failure.reason}")
        except Exception as e:
            errors.append(f"Extraction error for {raw_item.id}: {e}")
            continue

    # Continue through remaining phases...
    # (Full implementation in actual file)

    duration = time.time() - start_time

    return WorkflowResult(
        stories_processed=len(raw_items),
        stories_succeeded=stories_succeeded,
        stories_failed=len(raw_items) - stories_succeeded,
        errors=errors,
        output_paths=[],
        duration_seconds=duration
    )
```

---

### File 4: `utils/config_validator.py` (NEW)

**Purpose**: Validate configuration files on startup

**Scope**:
- ✅ Validate YAML syntax
- ✅ Check required keys exist
- ✅ Validate paths (if specified)
- ✅ Clear error messages
- ❌ NOT validate business logic

**Dependencies**: PyYAML

**Estimated Effort**: 2 hours

**Key Functions**:
```python
def validate_config_file(config_path: Path) -> List[str]:
    """Validate YAML config file.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML syntax error: {e}"]

    # Check required top-level keys
    required_keys = ["paths", "llm", "processing"]
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")

    # Validate paths section
    if "paths" in config:
        required_paths = ["vault_root", "sources_dir", "library_dir"]
        for path_key in required_paths:
            if path_key not in config["paths"]:
                errors.append(f"Missing path: paths.{path_key}")

    return errors

def validate_all_configs(config_dir: Path) -> bool:
    """Validate all config files.

    Returns:
        True if all valid, False otherwise
    """
    configs = [
        config_dir / "config.yaml",
        config_dir / "business_rules.yaml",
        config_dir / "output_config.yaml",
        config_dir / "publish_config.yaml"
    ]

    all_valid = True
    for config_path in configs:
        errors = validate_config_file(config_path)
        if errors:
            print(f"❌ {config_path.name}:")
            for error in errors:
                print(f"  - {error}")
            all_valid = False
        else:
            print(f"✅ {config_path.name}")

    return all_valid
```

---

### File 5: `tests/test_processors.py` (NEW)

**Purpose**: Test Phase 3 processors

**Scope**:
- ✅ Test PDF extraction with mock PDFs
- ✅ Test email extraction with mock emails
- ✅ Test text normalization
- ✅ Cover error paths
- ❌ NOT test OCR (requires Tesseract, test manually)

**Dependencies**: pytest, pytest-mock

**Estimated Effort**: 2-3 hours

**Key Tests**:
```python
def test_pdf_extraction_with_mock_pdf(tmp_path, monkeypatch):
    """Test PDF text extraction with mocked pdfplumber."""
    # Mock PDF content
    mock_text = "Sample PDF content for testing"

    # Mock pdfplumber.PDFFile
    def mock_extract(filepath):
        return mock_text

    monkeypatch.setattr(pdf_processor, "extract_text_from_pdf", mock_extract)

    result = pdf_processor.extract_text_from_pdf("test.pdf")
    assert result == mock_text

def test_email_parsing_with_mock_email(tmp_path):
    """Test email parsing with mock .eml file."""
    # Create test email
    email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Subject

Test email body."""

    email_file = tmp_path / "test.eml"
    email_file.write_text(email_content)

    result = email_processor.extract_email_data(email_file)
    assert result["subject"] == "Test Subject"
    assert "Test email body" in result["body"]
```

---

### File 6: `tests/test_models.py` (NEW)

**Purpose**: Test data model serialization

**Scope**:
- ✅ Test RawItem creation
- ✅ Test SuccessStory serialization/deserialization
- ✅ Test round-trip (save + load)
- ❌ NOT test validation logic (minimal in models)

**Dependencies**: pytest

**Estimated Effort**: 1-2 hours

**Key Tests**:
```python
def test_raw_item_creation():
    """Test RawItem dataclass creation."""
    item = RawItem(
        id="test-id",
        text="Test text",
        source_type="pdf",
        filename="test.pdf",
        country="US",
        month="2026-01",
        created_at="2026-01-01T00:00:00Z",
        metadata={}
    )
    assert item.id == "test-id"
    assert item.source_type == "pdf"

def test_success_story_round_trip(tmp_path):
    """Test SuccessStory save and load."""
    story = SuccessStory(
        id="win-2026-01-US-001",
        country="US",
        month="2026-01",
        customer="Test Customer",
        context="Test context",
        action="Test action",
        outcome="Test outcome",
        metrics=["+100% revenue"],
        confidence="high",
        internal_only=False,
        raw_sources=["test.pdf"],
        last_updated="2026-01-01T00:00:00Z",
        tags=[],
        industry="",
        team_size=""
    )

    # Save
    library_dir = tmp_path / "wins"
    library_dir.mkdir()
    saved_path = save_success_story(story, library_dir)

    # Load
    loaded_story = load_success_story(story.id, library_dir)

    assert loaded_story.id == story.id
    assert loaded_story.customer == story.customer
    assert loaded_story.context == story.context
```

---

### File 7: `tests/test_extraction.py` (NEW)

**Purpose**: Test LLM extraction with mocks

**Scope**:
- ✅ Test extraction with mocked LLM
- ✅ Test retry logic
- ✅ Test failure handling
- ❌ NOT test actual LLM calls (integration test)

**Dependencies**: pytest, pytest-mock

**Estimated Effort**: 2-3 hours

**Key Tests**:
```python
def test_extract_from_raw_item_with_mock_llm(monkeypatch):
    """Test extraction with mocked LLM response."""
    # Mock LLM response
    mock_response = {
        "customer": "ACME Corp",
        "context": "Test problem",
        "action": "Test solution",
        "outcome": "Test results",
        "metrics": ["+10% revenue"],
        "confidence": "high",
        "internal_only": False,
        "tags": ["test"],
        "industry": "Tech",
        "team_size": "Enterprise"
    }

    def mock_call_ollama_json(prompt, model, url):
        return mock_response

    monkeypatch.setattr(llm_utils, "call_ollama_json", mock_call_ollama_json)

    raw_item = RawItem(
        id="test-raw",
        text="Test content",
        source_type="pdf",
        filename="test.pdf",
        country="US",
        month="2026-01",
        created_at="2026-01-01T00:00:00Z"
    )

    draft_story, failure = extract_from_raw_item(raw_item)

    assert draft_story is not None
    assert failure is None
    assert draft_story.customer == "ACME Corp"
    assert draft_story.confidence == "high"
```

---

### File 8: `tests/test_orchestration.py` (NEW)

**Purpose**: Test end-to-end workflow

**Scope**:
- ✅ Test orchestrator with mocked phases
- ✅ Test error handling
- ✅ Test partial failure recovery
- ❌ NOT test actual LLM calls (use mocks)

**Dependencies**: pytest, pytest-mock

**Estimated Effort**: 3-4 hours

**Key Tests**:
```python
def test_orchestrator_happy_path(monkeypatch, tmp_path):
    """Test orchestrator with all phases mocked."""
    # Mock all phase functions to return expected values
    # This tests orchestration, not individual phases

    mock_files = [tmp_path / "test.pdf"]
    mock_raw_items = [RawItem(...)]
    mock_drafts = [DraftSuccessStory(...)]
    mock_stories = [SuccessStory(...)]

    monkeypatch.setattr(ingest, "discover_files", lambda *args: mock_files)
    monkeypatch.setattr(normalize, "normalize_pdf", lambda *args: mock_raw_items[0])
    # ... mock other phases

    result = run_weekly_workflow(
        countries=["US"],
        month="2026-01",
        source_dir=tmp_path,
        library_dir=tmp_path / "wins",
        output_dir=tmp_path / "outputs",
        config={}
    )

    assert result.stories_processed == 1
    assert result.stories_succeeded == 1
    assert len(result.errors) == 0

def test_orchestrator_handles_extraction_failure(monkeypatch, tmp_path):
    """Test orchestrator continues when extraction fails."""
    # Mock extraction to raise exception
    def mock_extract_failure(raw_item, model, url):
        raise Exception("LLM timeout")

    monkeypatch.setattr(extraction_agent, "extract_from_raw_item", mock_extract_failure)

    result = run_weekly_workflow(...)

    assert result.stories_failed == 1
    assert len(result.errors) > 0
    assert "LLM timeout" in result.errors[0]
```

---

### File 9: `requirements.txt` (UPDATE)

**Purpose**: Ensure all dependencies are listed

**Scope**:
- ✅ Add missing dependencies
- ✅ Pin versions for reproducibility
- ❌ NOT add unnecessary packages

**Dependencies**:
```txt
# Core dependencies
PyYAML>=6.0
jinja2>=3.1.0

# Phase 3: Processors
pypdf>=3.0.0

# Optional: OCR (for images)
# pytesseract>=0.3.10
# Pillow>=10.0.0

# Testing
pytest>=7.4.0
pytest-mock>=3.11.0

# Logging
python-json-logger>=2.0.0
```

**Estimated Effort**: 0.5 hours

---

### File 10: `README.md` (UPDATE)

**Purpose**: Provide setup and usage instructions

**Scope**:
- ✅ Installation instructions
- ✅ Quick start guide
- ✅ Configuration guide
- ✅ CLI reference
- ❌ NOT include development guide (separate document)

**Estimated Effort**: 1 hour

**Sections**:
```markdown
# Wins Library System v1.0

## Installation

1. Install dependencies: `pip install -r requirements.txt`
2. Install Ollama: https://ollama.com/
3. Pull model: `ollama pull glm-4:9b`
4. Configure system: Edit config/config.yaml

## Quick Start

```bash
# Validate configuration
python run.py validate

# Run weekly update
python run.py weekly --country US --month 2026-01

# Check status
python run.py status
```

## Configuration

See config/config.yaml for all settings.

## CLI Reference

### Modes
- `weekly`: Run weekly update workflow
- `status`: Show library statistics
- `validate`: Validate configuration
- `review`: Review pending stories
- `publish`: Publish prepared outputs

### Examples

[Provide examples for each mode]
```

---

## 8️⃣ Execution Readiness Checklist

### Operator Steps for First Run

**Step 0: Prerequisites**
- [ ] Python 3.10+ installed
- [ ] Ollama installed and running
- [ ] GLM-4 model pulled: `ollama pull glm-4:9b`
- [ ] Required directories exist: `vault/00_sources/`, `wins/`

**Step 1: Configuration**
- [ ] Copy `config/config.yaml.example` to `config/config.yaml`
- [ ] Edit paths in `config/config.yaml` if needed
- [ ] Edit LLM settings if Ollama is not at default URL
- [ ] Validate: `python run.py validate`
- [ ] Expected: All configs show ✅

**Step 2: Prepare Source Files**
- [ ] Place source files in `vault/00_sources/YYYY-MM/COUNTRY/`
- [ ] Organize by type: `pdf/`, `email/`, `teams/`, `images/`
- [ ] Verify files are discoverable: `python run.py status` (should show file count)

**Step 3: Dry Run**
- [ ] Execute: `python run.py weekly --country US --month 2026-01 --dry-run`
- [ ] Expected: "Dry run complete, 0 files processed (dry-run mode)"

**Step 4: First Execution**
- [ ] Execute: `python run.py weekly --country US --month 2026-01 --verbose`
- [ ] Expected outputs:
  - "Discovered N files..."
  - "Processing file 1/N..."
  - "Extracting from RawItem..."
  - "Saved SuccessStory to wins/..."
  - "Wrote executive output to..."
  - "Weekly workflow complete: M stories processed, N errors"
- [ ] Check log file: `logs/wins_library.log`

**Step 5: Verify Outputs**
- [ ] Check `wins/` directory for JSON files
- [ ] Check `vault/outputs/` for Markdown files
- [ ] Open Obsidian vault and verify notes appear
- [ ] Review generated stories for quality

### Human Approval Checkpoints

**Checkpoint 1: Story Review (Phase 5)**
- Trigger: `python run.py review --story-id win-XXX`
- Human sees: Story details, evaluation, rank
- Human chooses: Approve (y) or Reject (n)
- System action: Updates story status or flags for re-extraction

**Checkpoint 2: Publish Approval (Phase 7)**
- Trigger: `python run.py publish --artifact-id pub-XXX`
- Human sees: Publish destination, visibility, preview
- Human chooses: Approve with `--approve` flag
- System action: Publishes to channel, logs to audit trail

### Expected Outputs at Each Step

| Step | Output Location | Format | Example |
|------|----------------|--------|---------|
| Discovery | Log | Text | "Discovered 5 files" |
| Normalization | Log | Text | "Normalized PDF to RawItem" |
| Extraction | Log + JSON | Text + JSON | "Extracting from RawItem..." + `wins/win-XXX.json` |
| Deduplication | Log | Text | "Found 1 duplicate" |
| Output Generation | Markdown | Markdown | `vault/outputs/executive/XXX.md` |
| Publishing | Log + Audit log | Text + JSONL | "Published to website" + audit entry |

### Error Recovery

**If LLM is unreachable**:
- Error: "Connection error: Cannot connect to Ollama"
- Action: Check Ollama is running: `ollama list`
- Recovery: Restart Ollama, re-run command

**If source directory not found**:
- Error: "Source directory does not exist: vault/00_sources"
- Action: Create directory structure
- Recovery: Re-run command

**If extraction fails for all files**:
- Error: "All extractions failed, 0 stories created"
- Action: Check LLM model availability, review source file quality
- Recovery: Fix issue, re-run command

---

## 9️⃣ Explicit Non-Goals for v1.0

### Features NOT Implemented in v1.0

| Feature | Reason | Deferred To |
|---------|--------|-------------|
| **Web UI** | CLI sufficient for initial deployment | v1.1 or v2.0 |
| **Automated signal collection** | Manual ingestion acceptable | v1.1 |
| **Full API adapter implementations** | Stubs acceptable for v1.0 | v1.1 |
| **Performance optimization** | Not critical for small datasets | v1.1 |
| **Multi-language support** | English-only is requirement | v2.0 |
| **Real-time monitoring** | Logging sufficient for v1.0 | v1.1 |
| **Advanced error recovery** | Basic error handling sufficient | v1.1 |
| **Automated testing for LLM quality** | Subjective, hard to automate | v1.1 |
| **Database backend** | JSON files sufficient for v1.0 | v2.0 |
| **Docker deployment** | Manual setup acceptable | v1.1 |

### Scope Boundaries (Do Not Cross)

❌ **No new phases**: Phases 0-8 are complete
❌ **No phase refactoring**: Phase boundaries are fixed
❌ **No feature additions**: Only infrastructure for existing features
❌ **No architectural changes**: Design is frozen
❌ **No optimization work**: Focus on operational readiness only

### What IS in Scope

✅ **Entry point creation**: `run.py` CLI
✅ **Orchestration**: Connecting existing phases
✅ **Configuration**: Completing and validating YAML files
✅ **Testing**: Basic test coverage for critical paths
✅ **Documentation**: Setup and usage instructions
✅ **Error handling**: Basic error recovery and logging
✅ **Glue code**: Making existing components work together

---

## 🔟 Final Statement

**After completing this remediation plan, the system WILL be v1.0 operational.**

### Justification

The remediation plan addresses all blocking issues identified in the audit:

1. ✅ **Entry Point**: `run.py` provides CLI interface
2. ✅ **Orchestration**: `orchestrator.py` connects phases
3. ✅ **Configuration**: `config.yaml` populated
4. ✅ **Tests**: Basic test coverage for critical paths
5. ✅ **Error Handling**: Graceful degradation with logging

The system will be:
- **Executable**: Can run via `python run.py weekly`
- **Deterministic**: All phases produce reproducible outputs
- **Phase-compliant**: No boundary violations introduced
- **Safe to run**: Basic tests and error handling in place

### Remaining Limitations (Acceptable for v1.0)

- ⚠️ Manual signal collection (Phase 8)
- ⚠️ Stub channel adapters (Phase 7)
- ⚠️ CLI-only interface (no web UI)
- ⚠️ Basic error recovery (no auto-retry)

These limitations are documented and acceptable for v1.0 deployment.

---

**End of Remediation Plan**

**Next Step**: Begin implementation with File 1 (`config/config.yaml`)

**Estimated Completion Time**: 18.5-25.5 hours

**Readiness Date**: After 2-3 days of focused development
