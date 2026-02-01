# Wins Library System - v1.0 Test Matrix

**Version**: 1.0
**Purpose**: Minimal test suite required for v1.0 operational readiness
**Total Tests**: 13 tests across 6 test files

---

## Test Matrix

| Test Name | Module | Type | Purpose | Priority |
|-----------|--------|------|---------|----------|
| **Config Tests** ||||||
| `test_config_yaml_syntax` | utils/config_validator.py | Unit | Validate YAML parsing | P0 |
| `test_config_required_keys` | utils/config_validator.py | Unit | Check required top-level keys | P0 |
| `test_config_paths_exist` | utils/config_validator.py | Unit | Validate path configuration | P1 |
| **Model Tests** ||||||
| `test_raw_item_creation` | models/raw_item.py | Unit | RawItem dataclass works | P0 |
| `test_success_story_save` | models/library.py | Unit | Save SuccessStory to JSON | P0 |
| `test_success_story_load` | models/library.py | Unit | Load SuccessStory from JSON | P0 |
| `test_success_story_round_trip` | models/library.py | Unit | Save + load preserves data | P0 |
| **Processor Tests** ||||||
| `test_pdf_extraction_mock` | processors/pdf_processor.py | Unit | PDF extraction with mock | P0 |
| `test_email_parsing_mock` | processors/email_processor.py | Unit | Email parsing with mock | P0 |
| `test_text_normalization` | processors/text_processor.py | Unit | Text encoding normalization | P1 |
| **Extraction Tests** ||||||
| `test_extract_with_mock_llm` | agents/extraction_agent.py | Unit | LLM extraction with mock | P1 |
| `test_extraction_retry_logic` | agents/retry_guard_agent.py | Unit | Retry on LLM failure | P1 |
| `test_extraction_failure_handling` | agents/extraction_agent.py | Unit | Graceful failure handling | P1 |
| **Orchestration Tests** ||||||
| `test_orchestrator_happy_path` | workflow/orchestrator.py | Integration | End-to-end with mocks | P1 |
| `test_orchestrator_phase_3_failure` | workflow/orchestrator.py | Integration | Handles file discovery failure | P2 |
| `test_orchestrator_extraction_failure` | workflow/orchestrator.py | Integration | Handles extraction failure | P2 |
| `test_orchestrator_continues_on_error` | workflow/orchestrator.py | Integration | Continues after partial failure | P2 |

---

## Test File Structure

```
tests/
├── __init__.py
├── test_config_validator.py     # 3 tests
├── test_models.py                 # 4 tests
├── test_processors.py             # 3 tests
├── test_extraction.py             # 3 tests
└── test_orchestration.py          # 4 tests

Total: 6 test files, 17 tests
```

---

## Test Descriptions

### 1. Config Tests (3 tests)

**File**: `tests/test_config_validator.py`

#### Test 1.1: `test_config_yaml_syntax`
- **Purpose**: Validate config/config.yaml parses as valid YAML
- **Method**: Load YAML, catch parsing errors
- **Expected**: No exceptions raised
- **Risk Mitigated**: Invalid YAML prevents system startup

#### Test 1.2: `test_config_required_keys`
- **Purpose**: Verify all required top-level keys exist
- **Method**: Check for `paths`, `llm`, `processing` keys
- **Expected**: All required keys present
- **Risk Mitigated**: Missing keys cause runtime errors

#### Test 1.3: `test_config_paths_exist`
- **Purpose**: Validate path configuration format
- **Method**: Check `paths` section has required sub-keys
- **Expected**: All required path keys present
- **Risk Mitigated**: Invalid paths cause file I/O errors

---

### 2. Model Tests (4 tests)

**File**: `tests/test_models.py`

#### Test 2.1: `test_raw_item_creation`
- **Purpose**: Verify RawItem dataclass instantiation
- **Method**: Create RawItem with all fields, assert values
- **Expected**: RawItem created with correct field values
- **Risk Mitigated**: Data model corruption

#### Test 2.2: `test_success_story_save`
- **Purpose**: Verify SuccessStory serialization to JSON
- **Method**: Create SuccessStory, save to temp file
- **Expected**: JSON file created with correct content
- **Risk Mitigated**: Can't persist stories

#### Test 2.3: `test_success_story_load`
- **Purpose**: Verify SuccessStory deserialization from JSON
- **Method**: Load JSON file, verify SuccessStory object
- **Expected**: SuccessStory object with correct field values
- **Risk Mitigated**: Can't retrieve persisted stories

#### Test 2.4: `test_success_story_round_trip`
- **Purpose**: Verify save + load preserves data
- **Method**: Save SuccessStory, load it back, compare
- **Expected**: Loaded story equals saved story
- **Risk Mitigated**: Data corruption during serialization

---

### 3. Processor Tests (3 tests)

**File**: `tests/test_processors.py`

#### Test 3.1: `test_pdf_extraction_mock`
- **Purpose**: Verify PDF text extraction with mocked pdfplumber
- **Method**: Mock `pdfplumber.PDFFile`, call extractor
- **Expected**: Correct text extraction
- **Risk Mitigated**: PDF processing broken

#### Test 3.2: `test_email_parsing_mock`
- **Purpose**: Verify email parsing with mock email
- **Method**: Create test .eml file, parse it
- **Expected**: Correct subject, from, body extracted
- **Risk Mitigated**: Email processing broken

#### Test 3.3: `test_text_normalization`
- **Purpose**: Verify text encoding normalization
- **Method**: Pass text with encoding issues, verify cleanup
- **Expected**: Clean UTF-8 text output
- **Risk Mitigated**: Text encoding errors crash system

---

### 4. Extraction Tests (3 tests)

**File**: `tests/test_extraction.py`

#### Test 4.1: `test_extract_with_mock_llm`
- **Purpose**: Verify LLM extraction with mocked Ollama response
- **Method**: Mock `call_ollama_json`, call extraction
- **Expected**: DraftSuccessStory created correctly
- **Risk Mitigated**: LLM integration broken

#### Test 4.2: `test_extraction_retry_logic`
- **Purpose**: Verify retry guard agent retries on failure
- **Method**: Mock LLM to fail twice, succeed on 3rd try
- **Expected**: Extraction succeeds after retries
- **Risk Mitigated**: Transient LLM failures

#### Test 4.3: `test_extraction_failure_handling`
- **Purpose**: Verify graceful failure handling
- **Method**: Mock LLM to fail permanently
- **Expected**: Returns failure record, no exception raised
- **Risk Mitigated**: LLM errors crash system

---

### 5. Orchestration Tests (4 tests)

**File**: `tests/test_orchestration.py`

#### Test 5.1: `test_orchestrator_happy_path`
- **Purpose**: Verify end-to-end orchestration with all mocks
- **Method**: Mock all phases to return expected values
- **Expected**: WorkflowResult with all successes
- **Risk Mitigated**: Phase integration broken

#### Test 5.2: `test_orchestrator_phase_3_failure`
- **Purpose**: Verify handling of file discovery failure
- **Method**: Mock file discovery to raise exception
- **Expected**: Error logged, workflow continues
- **Risk Mitigated**: Early failures crash system

#### Test 5.3: `test_orchestrator_extraction_failure`
- **Purpose**: Verify handling of extraction failure
- **Method**: Mock extraction to fail
- **Expected**: Story skipped, workflow continues
- **Risk Mitigated**: Partial failure stops entire workflow

#### Test 5.4: `test_orchestrator_continues_on_error`
- **Purpose**: Verify error continuation behavior
- **Method**: Mock multiple phases to fail partially
- **Expected**: Some stories succeed, errors logged
- **Risk Mitigated**: All-or-nothing failure behavior

---

## Test Execution Plan

### Pre-Test Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install test dependencies
pip install pytest pytest-mock

# 4. Create test directories
mkdir -p tests/tmp
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=workflow --cov=models --cov=agents --cov=processors --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_models.py::test_success_story_round_trip -v
```

### Expected Test Output

```
tests/test_config_validator.py::test_config_yaml_syntax PASSED
tests/test_config_validator.py::test_config_required_keys PASSED
tests/test_config_validator.py::test_config_paths_exist PASSED
tests/test_models.py::test_raw_item_creation PASSED
tests/test_models.py::test_success_story_save PASSED
tests/test_models.py::test_success_story_load PASSED
tests/test_models.py::test_success_story_round_trip PASSED
tests/test_processors.py::test_pdf_extraction_mock PASSED
tests/test_processors.py::test_email_parsing_mock PASSED
tests/test_processors.py::test_text_normalization PASSED
tests/test_extraction.py::test_extract_with_mock_llm PASSED
tests/test_extraction.py::test_extraction_retry_logic PASSED
tests/test_extraction.py::test_extraction_failure_handling PASSED
tests/test_orchestration.py::test_orchestrator_happy_path PASSED
tests/test_orchestration.py::test_orchestrator_phase_3_failure PASSED
tests/test_orchestration.py::test_orchestrator_extraction_failure PASSED
tests/test_orchestration.py::test_orchestrator_continues_on_error PASSED

========================= 17 passed in 2.45s =========================
```

---

## Coverage Targets

### Minimum Required Coverage for v1.0

| Module | Target Coverage | Critical Paths Covered |
|--------|----------------|----------------------|
| `models/library.py` | 80% | Save, load, round-trip |
| `workflow/ingest.py` | 60% | File discovery |
| `workflow/normalize.py` | 60% | PDF, email normalization |
| `workflow/orchestrator.py` | 70% | Phase coordination, error handling |
| `agents/extraction_agent.py` | 50% | Extraction with mocks |
| `utils/config_validator.py` | 90% | All validation paths |

### Overall Target

- **Line Coverage**: 60%+ overall
- **Branch Coverage**: 50%+ overall
- **Critical Path Coverage**: 100% (all P0 tests pass)

---

## Deferred Tests (v1.1+)

The following tests are deferred to v1.1 or later:

| Test | Reason | Priority |
|------|--------|----------|
| OCR integration tests | Requires Tesseract installation | P3 |
| Actual LLM integration tests | Requires Ollama running | P2 |
| Performance tests | Not critical for v1.0 | P3 |
| Stress tests with large datasets | Not critical for v1.0 | P3 |
| Template rendering edge cases | Manual testing sufficient | P3 |
| Channel adapter integration tests | Stubs acceptable for v1.0 | P3 |
| Signal aggregation tests | Phase 8 not critical path | P3 |

---

## Test Success Criteria

v1.0 is considered test-ready when:

- ✅ All 17 tests pass consistently
- ✅ Line coverage ≥ 60% overall
- ✅ All P0 tests pass
- ✅ No tests require manual setup (all self-contained)
- ✅ Tests complete in < 5 seconds
- ✅ Tests can run in CI/CD pipeline

---

**Test Matrix Complete**

**Total Development Effort**: 10-14 hours for test implementation

**Next Step**: Implement File 4 of remediation plan (`tests/test_processors.py`)
