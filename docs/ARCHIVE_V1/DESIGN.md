# Wins Library System – System Design Document

**Document Version**: 1.1
**Date**: 2026-02-01
**Author**: Agent 1 (System Architect Agent)
**Status**: Phase 1 Deliverable (Revised)

---

## 1. Overview

### 1.1 System Purpose

The Wins Library System is an offline, local-first Agentic Workflow that:

1. **Collects** raw success story data from multiple sources (PDF, email, Teams messages, images)
2. **Standardizes** raw data into machine-readable format (RawItem)
3. **Extracts** structured SuccessStory objects using local LLM (Ollama + GLM-4)
4. **Maintains** a persistent Wins Library (JSON)
5. **Generates** multiple output versions (Executive for internal, Marketing for external)
6. **Publishes** to Obsidian as Markdown notes

### 1.2 Design Principles

| Principle | Implementation |
|----------|----------------|
| **Determinism** | All workflows are explicit, CLI-triggered, traceable |
| **Offline-first** | No cloud dependencies, all LLM calls via local Ollama |
| **Auditability** | All intermediate artifacts are human-readable (JSON/Markdown) |
| **Reproducibility** | Same input produces same output |
| **Explicit over Autonomous** | No background daemons, no hidden decisions |

### 1.3 SuccessStory is First-Class

- `SuccessStory` is the core business object
- All functions return or accept `SuccessStory` objects
- Original data (RawItem) is treated as immutable evidence
- Validation happens at model construction time

---

## 2. Module List and Responsibilities

### 2.1 workflow/ingest.py

**Responsibility**: Scan source directories and discover new raw input files for processing.

**Inputs**:
- Configuration from `config.yaml`
- Directory path (e.g., `vault/00_sources`)
- Country code (e.g., "US")
- Month (e.g., "2026-01")

**Outputs**:
- `List[Path]` - List of discovered file paths

**MUST NOT**:
- Read file contents
- Parse files
- Call LLM
- Judge whether files are relevant

---

### 2.2 workflow/normalize.py

**Responsibility**: Convert raw files into RawItem objects through mechanical text extraction.

**Inputs**:
- File paths from ingest module
- File type (pdf/email/teams/image)

**Outputs**:
- `RawItem` object per file

**MUST NOT**:
- Interpret text semantics
- Classify content
- Extract business meaning
- Call LLM

---

### 2.3 workflow/deduplicate.py

**Responsibility**: Remove duplicate SuccessStory objects using string-based similarity.

**Inputs**:
- List of `SuccessStory` objects

**Outputs**:
- List of deduplicated `SuccessStory` objects

**MUST NOT**:
- Use embedding or semantic similarity
- Rewrite or summarize fields
- Drop or modify data beyond concatenating source lists

**Constraint**: `merge_stories()` MUST only concatenate `raw_sources` lists and preserve all other fields exactly.

---

### 2.4 models/raw_item.py

**Responsibility**: Define RawItem data schema for standardized raw data representation.

**Inputs**:
- Extracted text content
- File metadata
- Source file information

**Outputs**:
- `RawItem` dataclass instance

**MUST NOT**:
- Implement parsing logic (that's in processors/*)
- Modify text content after creation
- Implement validation beyond type checking

---

### 2.5 models/library.py

**Responsibility**: Persist and retrieve SuccessStory objects to/from JSON files.

**Inputs**:
- `SuccessStory` object to save
- File path to load

**Outputs**:
- Saved JSON file
- Loaded `SuccessStory` object

**MUST NOT**:
- Implement deduplication (use workflow/deduplicate.py)
- Implement extraction logic
- Modify SuccessStory data

---

### 2.6 processors/*

#### 2.6.1 processors/pdf_processor.py

**Responsibility**: Extract text from PDF files mechanically.

**Inputs**:
- PDF file path

**Outputs**:
- Extracted text string

**MUST NOT**:
- Interpret PDF meaning
- Classify content
- Filter or analyze text

---

#### 2.6.2 processors/email_processor.py

**Responsibility**: Extract headers and body from email files mechanically.

**Inputs**:
- Email file path (.eml)

**Outputs**:
- Extracted subject, from, to, body, date

**MUST NOT**:
- Interpret email sentiment
- Classify email importance
- Extract business entities

---

#### 2.6.3 processors/image_processor.py

**Responsibility**: Extract text from images using OCR.

**Inputs**:
- Image file path (.png, .jpg)

**Outputs**:
- Extracted text string

**MUST NOT**:
- Interpret image content
- Classify image subjects
- Extract business meaning

---

#### 2.6.4 processors/text_processor.py

**Responsibility**: Clean and normalize text encoding.

**Inputs**:
- Text string

**Outputs**:
- Cleaned text string

**MUST NOT**:
- Interpret text
- Filter content based on meaning
- Extract entities

---

### 2.7 agents/extraction_agent.py

**Responsibility**: Extract SuccessStory objects from RawItem list using LLM.

**Inputs**:
- List of `RawItem` objects

**Outputs**:
- List of `SuccessStory` objects

**MUST NOT**:
- Perform file IO
- Control workflow execution
- Implement deduplication

---

### 2.8 agents/planner_agent.py

**Responsibility**: Analyze state and suggest tasks (ADVISORY ONLY).

**Inputs**:
- Current system state
- Last run timestamp
- CLI arguments

**Outputs**:
- Suggested task list

**MUST NOT**:
- Control whether workflow steps execute
- Make autonomous decisions
- Block or skip steps based on its output

**Constraint**: Output MUST NOT affect execution flow. Workflow MUST run safely if this agent is ignored or returns empty list.

---

### 2.9 workflow/outputs/executive.py

**Responsibility**: Generate executive version outputs from SuccessStory objects.

**Inputs**:
- `SuccessStory` object

**Outputs**:
- Formatted executive output (text)

**MUST NOT**:
- Perform file IO
- Modify SuccessStory data
- Implement extraction logic

---

### 2.10 workflow/outputs/marketing.py

**Responsibility**: Generate marketing version outputs from SuccessStory objects.

**Inputs**:
- `SuccessStory` object

**Outputs**:
- Formatted marketing output (text)

**MUST NOT**:
- Perform file IO
- Modify SuccessStory data
- Implement extraction logic

---

### 2.11 workflow/writer.py

**Responsibility**: Write Markdown files to Obsidian vault.

**Inputs**:
- `SuccessStory` object or list
- Output file path (explicitly provided)

**Outputs**:
- Markdown file written to disk

**MUST NOT**:
- Infer file paths
- Infer file names
- Create directory structures
- Decide where to store files
- Modify SuccessStory data

**Constraint**: MUST write only to paths explicitly provided by caller.

---

### 2.12 utils/llm_utils.py

**Responsibility**: Wrapper around Ollama API for LLM calls.

**Inputs**:
- Prompt string
- Model name
- Optional parameters

**Outputs**:
- LLM response text

**MUST NOT**:
- Implement prompts (that's in config/prompts.yaml)
- Control workflow
- Store hidden state

---

## 3. Data Models (Schema Only)

### 3.1 RawItem Schema

```python
@dataclass
class RawItem:
    id: str  # UUID v4 format
    text: str  # Extracted English text content
    source_type: str  # "pdf" | "email" | "teams" | "image"
    filename: str  # Original filename with extension
    country: str  # ISO 3166-1 alpha-2 code
    month: str  # YYYY-MM format
    created_at: str  # ISO-8601 datetime
    metadata: dict  # Optional metadata (file_path, file_size, etc.)
```

**Field Descriptions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | ✅ | Unique identifier (UUID v4) |
| `text` | str | ✅ | Extracted English text content |
| `source_type` | str | ✅ | Raw data source type |
| `filename` | str | ✅ | Original filename |
| `country` | str | ✅ | Country code |
| `month` | str | ✅ | Month (YYYY-MM) |
| `created_at` | str | ✅ | Creation timestamp (ISO-8601) |
| `metadata` | dict | ❌ | Optional metadata |

---

### 3.2 SuccessStory Schema

```python
@dataclass
class SuccessStory:
    id: str  # Format: win-YYYY-MM-{country}-{seq}
    country: str  # ISO 3166-1 alpha-2
    month: str  # YYYY-MM
    customer: str  # Customer name
    context: str  # Business problem or situation
    action: str  # What was done
    outcome: str  # Results achieved
    metrics: List[str]  # Quantifiable impact metrics
    confidence: str  # "high" | "medium" | "low"
    internal_only: bool  # Whether restricted to internal use
    raw_sources: List[str]  # Source filenames
    last_updated: str  # ISO-8601 timestamp
    tags: List[str]  # Optional business tags
    industry: str  # Optional industry classification
    team_size: str  # Optional team size category
```

**Field Descriptions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | ✅ | Unique identifier |
| `country` | str | ✅ | Country code |
| `month` | str | ✅ | Month |
| `customer` | str | ✅ | Customer name |
| `context` | str | ✅ | Business context |
| `action` | str | ✅ | Action taken |
| `outcome` | str | ✅ | Outcome achieved |
| `metrics` | List[str] | ✅ | Metrics list |
| `confidence` | str | ✅ | Information confidence |
| `internal_only` | bool | ✅ | Internal-only flag |
| `raw_sources` | List[str] | ✅ | Source filenames |
| `last_updated` | str | ✅ | Last update timestamp |
| `tags` | List[str] | ❌ | Optional tags |
| `industry` | str | ❌ | Optional industry |
| `team_size` | str | ❌ | Optional team size |

---

## 4. Function Signatures

### 4.1 workflow/ingest.py

```
discover_files(source_dir: Path, country: str, month: str) -> List[Path]
```

```
get_file_metadata(file_path: Path) -> Dict[str, Any]
```

```
is_new_file(file_path: Path, processed_files: List[str]) -> bool
```

---

### 4.2 workflow/normalize.py

```
normalize_pdf(file_path: Path, country: str, month: str) -> RawItem
```

```
normalize_email(file_path: Path, country: str, month: str) -> RawItem
```

```
normalize_image(file_path: Path, country: str, month: str) -> RawItem
```

```
normalize_teams_text(file_path: Path, country: str, month: str) -> RawItem
```

---

### 4.3 workflow/deduplicate.py

```
is_duplicate(story: SuccessStory, existing_stories: List[SuccessStory], threshold: float = 0.85) -> bool
```

```
merge_stories(original: SuccessStory, duplicate: SuccessStory) -> SuccessStory
```

```
deduplicate_stories(stories: List[SuccessStory]) -> List[SuccessStory]
```

---

### 4.4 models/library.py

```
save_success_story(story: SuccessStory, library_dir: Path) -> Path
```

```
load_success_story(story_id: str, library_dir: Path) -> SuccessStory
```

```
load_all_stories(library_dir: Path) -> List[SuccessStory]
```

---

### 4.5 processors/pdf_processor.py

```
extract_text_from_pdf(file_path: Path) -> str
```

---

### 4.6 processors/email_processor.py

```
extract_email_data(file_path: Path) -> Dict[str, Any]
```

---

### 4.7 processors/image_processor.py

```
extract_text_from_image(file_path: Path) -> str
```

---

### 4.8 processors/text_processor.py

```
normalize_text_encoding(text: str) -> str
```

---

### 4.9 agents/extraction_agent.py

```
extract_success_stories(raw_items: List[RawItem], ollama_base_url: str = "http://localhost:11434", model: str = "glm-4:9b") -> List[SuccessStory]
```

---

### 4.10 agents/planner_agent.py

```
plan_tasks(last_run_timestamp: Optional[str], new_items_count: int, cli_args: Dict[str, Any]) -> Dict[str, Any]
```

---

### 4.11 workflow/outputs/executive.py

```
generate_executive_output(story: SuccessStory) -> str
```

---

### 4.12 workflow/outputs/marketing.py

```
generate_marketing_output(story: SuccessStory) -> str
```

---

### 4.13 workflow/writer.py

```
write_success_story_note(story: SuccessStory, output_path: Path, template_path: Path) -> None
```

```
write_weekly_summary(stories: List[SuccessStory], output_path: Path, template_path: Path, week_str: str) -> None
```

---

### 4.14 utils/llm_utils.py

```
call_ollama(prompt: str, model: str = "glm-4:9b", ollama_base_url: str = "http://localhost:11434") -> str
```

```
call_ollama_json(prompt: str, model: str = "glm-4:9b", ollama_base_url: str = "http://localhost:11434") -> Dict[str, Any]
```

---

## 5. Data Flow

### 5.1 End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Raw Input Sources                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                        │
│  │   PDF    │  │  Email   │  │  Teams  │  │  Image  │                        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘                        │
└─────┼────────┼─────┼──────────┼────────┴─────────┘
      │        │     │          │
      ▼        ▼     ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│              1. Ingest: Discover Files (workflow/ingest.py)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│        2. Normalize: Extract Text (workflow/normalize.py)               │
│        + processors/*.py (PDF/Email/OCR/Text)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      ┌─────────────────┐
                      │   RawItem objects  │
                      └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│      3. Extract: Extract SuccessStories (agents/extraction_agent.py)        │
│                    Ollama + GLM-4                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      ┌─────────────────┐
                      │  SuccessStory      │
                      │      objects       │
                      └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│       4. Deduplicate: Remove Duplicates (workflow/deduplicate.py)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      ┌─────────────────┐
                      │  Unique           │
                      │  SuccessStory      │
                      │      objects       │
                      └─────────────────┘
                              │
                              ├──────────────────────┐
                              ▼                      ▼
┌──────────────────────┐  ┌───────────────────────────────────┐
│ 5. Save: Persist to JSON │  │ 6. Output: Generate Versions           │
│    (models/library.py)  │  │      - Executive (outputs/executive.py)  │
│                       │  │      - Marketing (outputs/marketing.py) │
└──────────┬───────────┘  └────────────────┬──────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐                  ┌──────────────────┐
│ 7. Write: Markdown     │                  │ 8. Wins Library    │
│    (workflow/writer.py) │                  │    (JSON files)    │
└──────────────────────┘                  └──────────────────┘
           │
           ▼
┌──────────────────────┐
│  Obsidian Vault        │
│  (Markdown files)     │
└──────────────────────┘
```

### 5.2 Data Flow Steps (Textual)

1. **User** triggers workflow with mode, country, month parameters
2. **Ingest** scans source directory for files matching country/month
3. **Normalize** processes each file through appropriate processor
4. **RawItems** are created (mechanical extraction only)
5. **Extract** calls Ollama with RawItems to generate SuccessStories
6. **Deduplicate** removes duplicate SuccessStories using string similarity
7. **Save** persists each SuccessStory to JSON files
8. **Output** generates Executive and Marketing versions
9. **Write** creates Markdown notes in Obsidian vault
10. **Obsidian** displays notes for human reading

---

## 6. Error Boundaries

### 6.1 File Discovery Layer (workflow/ingest.py)

**May raise**:
- `FileNotFoundError`: Source directory does not exist
- `ValueError`: Invalid country or month format

**Must NOT handle**:
- File parsing errors (handled by processors)
- File access permissions (let system raise naturally)

---

### 6.2 Normalization Layer (workflow/normalize.py + processors/*)

**May raise**:
- `ValueError`: PDF extraction failed or returned empty
- `ValueError`: Email parsing failed
- `ValueError`: OCR failed or returned empty
- `UnicodeDecodeError`: Text encoding errors

**Must NOT handle**:
- LLM errors (not applicable at this layer)
- Workflow orchestration errors

---

### 6.3 Extraction Layer (agents/extraction_agent.py)

**May raise**:
- `ConnectionError`: Ollama unreachable
- `ValueError`: Invalid JSON response from LLM
- `TimeoutError`: LLM request timeout

**Must NOT handle**:
- File IO errors (should be caught upstream)
- Schema validation errors (raise as-is)

---

### 6.4 Output Generation Layer (workflow/outputs/*.py)

**May raise**:
- `ValueError`: Invalid SuccessStory input
- `ValueError`: Template rendering failed

**Must NOT handle**:
- File IO errors (handled by writer)
- LLM errors (should be caught upstream)

---

### 6.5 Writer Layer (workflow/writer.py)

**May raise**:
- `IOError`: Cannot write to output path
- `ValueError`: Invalid output path
- `TemplateError`: Template rendering failed

**Must NOT handle**:
- LLM errors (should be caught upstream)
- Template missing errors (let it fail explicitly)

---

## End of DESIGN.md

**Document Status**: Design Specification
**Author**: Agent 1 (System Architect Agent)
**Version**: 1.1
**Date**: 2026-02-01

---
