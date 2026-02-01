# Development Plan v2.0
## Local Knowledge Base & Success Story System

**Document Version**: 2.0
**Status**: HIGH-LEVEL PLAN - No Implementation Details
**Date**: 2026-02-01
**Based on**: REQUIREMENTS_v2.md

---

## Table of Contents

1. [Development Approach](#1-development-approach)
2. [Work Stream 1: Knowledge Base Processing](#2-work-stream-1-knowledge-base-processing)
3. [Work Stream 2: Success Story Extraction](#3-work-stream-2-success-story-extraction)
4. [Work Stream 3: Excel Library & Versioning](#4-work-stream-3-excel-library--versioning)
5. [Work Stream 4: Executive Summaries](#5-work-stream-4-executive-summaries)
6. [Work Stream 5: Integration & CLI](#6-work-stream-5-integration--cli)
7. [Sequence & Dependencies](#7-sequence--dependencies)
8. [Testing Strategy](#8-testing-strategy)
9. [Assumptions](#9-assumptions)

---

## 1. Development Approach

### 1.1 Refactoring Philosophy

This is a **refactoring project**, not a greenfield build.

**Starting State**:
- Existing v1.0 codebase with multi-agent architecture
- JSON-based Success Story storage
- Obsidian-focused output pipeline

**Target State**:
- Excel-focused business output
- Abstract Success Story entities (not JSON files)
- Prompt-driven Executive Summaries
- Human-AI co-editing with versioning

### 1.2 Refactoring Principles

| Principle | Application |
|-----------|-------------|
| **Preserve what works** | Source discovery, Markdown extraction, LLM integration |
| **Remove what conflicts** | JSON storage, multi-agent orchestration, automatic deduplication |
| **Add what's missing** | Excel generation, versioning logic, prompt management |
| **Simplify over engineer** | Explicit pipelines over autonomous agents |

### 1.3 Decision Points Requiring User Input

| Decision | Options | Impact |
|----------|---------|--------|
| **Excel library structure** | Single workbook vs. multiple workbooks | Affects versioning and delivery |
| **Story curation workflow** | Edit-in-place vs. export-edit-import | Affects human-AI interaction |
| **Prompt storage format** | YAML vs. JSON vs. plain text | Affects extensibility |
| **Version granularity** | File-level vs. sheet-level vs. row-level | Affects merge complexity |

---

## 2. Work Stream 1: Knowledge Base Processing

**Objective**: Extract Markdown from source files for navigation and understanding.

### 2.1 Scope

**In Scope**:
- Scanning source directories for files
- Reading binary files (PDF, PPT, DOC, Excel, email, images)
- Generating Markdown representations
- Writing Markdown to Obsidian vault
- Storing metadata (source file path, type, timestamps)

**Out of Scope**:
- Interpreting or classifying content (that's Work Stream 2)
- Making business judgments about relevance
- Modifying original source files

### 2.2 Key Components

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| **Source Scanner** | Discover files in `vault/00_sources/` | Reuse v1.0 ingest logic |
| **Format Handlers** | Extract text from each file type | PDF, PPT, DOC, Excel, email, OCR |
| **Markdown Generator** | Create structured Markdown | Include metadata frontmatter |
| **Vault Writer** | Write to `vault/20_notes/sources/` | Preserve directory structure or flatten |

### 2.3 Data Flow

```
Source Files → Format Handler → Markdown Generator → Vault Writer → Obsidian
```

### 2.4 Open Questions

| Question | Impact | Decision Needed |
|----------|--------|-----------------|
| **Directory structure in `20_notes/`** | Flat vs. mirrored from sources | User preference |
| **Markdown detail level** | Full text vs. summary vs. outline | Balance: file size vs. usefulness |
| **Re-generation strategy** | Always overwrite vs. preserve edits | Define re-run behavior |

---

## 3. Work Stream 2: Success Story Extraction

**Objective**: Identify Success Stories across sources and extract structured information.

### 3.1 Scope

**In Scope**:
- Reading Markdown (or original sources)
- LLM-based extraction of Success Stories
- Structuring stories (Customer, Context, Action, Outcome, Metrics)
- Tracking evidence (source references)
- Assessing extraction confidence

**Out of Scope**:
- Automatic deduplication (human judgment required)
- Publishing to Excel (that's Work Stream 3)
- Making final business judgments

### 3.2 Key Components

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| **Content Reader** | Load Markdown or source files | Needs to handle multiple formats |
| **Extraction Pipeline** | Call LLM with structured prompts | Reuse v1.0 LLM integration |
| **Story Structure Validator** | Validate extracted stories | Ensure required fields present |
| **Evidence Linker** | Link stories to source files | Track file paths and sections |

### 3.3 Data Model (Abstract)

Success Story is an **in-memory entity** during extraction:

```python
# Pseudo-code - NOT implementation detail
@dataclass
class SuccessStory:
    customer: str          # Who
    context: str           # Business problem
    action: str            # What was done
    outcome: str           # Result
    metrics: List[str]     # Quantified impact
    evidence: List[str]    # Source file references
    confidence: str        # high | medium | low
```

**Note**: This is NOT stored as JSON. It flows directly to Excel.

### 3.4 Data Flow

```
Markdown/Source Files → Content Reader → Extraction Pipeline → Success Stories (in-memory)
```

### 3.5 Open Questions

| Question | Impact | Decision Needed |
|----------|--------|-----------------|
| **Batch vs. incremental extraction** | Process all files vs. process new/changed | Affects re-run cost |
| **Story boundary detection** | How to identify separate stories in one source | LLM prompt design |
| **Confidence scoring** | Manual vs. automated confidence levels | Affects human review workload |

---

## 4. Work Stream 3: Excel Library & Versioning

**Objective**: Generate Excel workbooks as the primary business output, with support for human co-editing and versioning.

### 4.1 Scope

**In Scope**:
- Creating Excel workbook(s) from Success Stories
- Writing structured data to sheets
- Implementing version numbering scheme
- Detecting and preserving human edits
- Generating new versions without overwriting edits

**Out of Scope**:
- Story extraction (that's Work Stream 2)
- Executive Summary generation (that's Work Stream 4)
- Advanced Excel features (pivot tables, charts) unless simple

### 4.2 Key Components

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| **Workbook Generator** | Create .xlsx file structure | Define sheet layout |
| **Sheet Writers** | Populate Stories, Evidence, Metrics, Metadata sheets | |
| **Version Manager** | Track version numbers and metadata | Read existing versions before writing |
| **Change Detector** | Detect human modifications in existing Excel | Compare before overwriting |

### 4.3 Sheet Structure (Candidate)

```
Sheet 1: Stories
- ID | Customer | Context | Action | Outcome | Confidence | Last Updated

Sheet 2: Metrics
- Story ID | Metric | Category | Value

Sheet 3: Evidence
- Story ID | Source File | Section | Confidence

Sheet 4: Metadata
- Version | Generated At | Generated By | Parent Version | Change Summary
```

### 4.4 Versioning Strategy

**File Naming Convention**:
```
wins_library_v{N}_{YYYYMMDD}.xlsx           # System-generated
wins_library_v{N}_human_{YYYYMMDD}.xlsx     # Human-edited
```

**Version Promotion**:
- System generates v1 → Human edits → Saved as `v1_human_...`
- System re-runs → Generates v2 (based on v1) → Human can merge or keep separate

### 4.5 Data Flow

```
Success Stories (in-memory) → Workbook Generator → Excel Writer → File System
                                     ↑                              |
                                     |                              |
                              Version Manager ────────── Change Detector
```

### 4.6 Open Questions

| Question | Impact | Decision Needed |
|----------|--------|-----------------|
| **Single vs. multiple workbooks** | One file vs. split by country/month | Affects delivery and merging |
| **Merge strategy** | How to combine system updates with human edits | Complex: 3-way merge? |
| **Version metadata storage** | In workbook vs. separate manifest file | Affects portability |

---

## 5. Work Stream 4: Executive Summaries

**Objective**: Generate high-quality Executive Summaries using explicit, stored prompts.

### 5.1 Scope

**In Scope**:
- Loading prompts from file system
- Rendering prompts with Success Story data
- Calling LLM with formatted prompts
- Writing summary output (Markdown for flexibility)
- Supporting multiple summary types (Executive, Marketing, etc.)

**Out of Scope**:
- Story extraction (that's Work Stream 2)
- Excel generation (that's Work Stream 3)
- Automatic formatting or delivery of summaries

### 5.2 Key Components

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| **Prompt Loader** | Load and parse prompt definitions | YAML or JSON |
| **Template Renderer** | Substitute variables in prompts | Success Stories, metadata |
| **Summary Generator** | Call LLM and parse response | |
| **Summary Writer** | Write output to file system | Markdown or text |

### 5.3 Prompt Schema (Candidate)

```yaml
# Pseudo-code, NOT implementation detail
name: "Executive Summary"
description: "Business-focused summary for stakeholders"
template: |
  You are a business analyst writing an executive summary.

  Stories:
  {{#each stories}}
  - {{customer}}: {{outcome}} ({{metrics}})
  {{/each}}

  Write a summary emphasizing quantified impact.
  Length: ~500 words
output_format: "markdown"
parameters:
  - name: "stories"
    type: "array_of_success_stories"
```

### 5.4 Data Flow

```
Prompt Definition → Template Renderer → LLM → Summary Output → File System
                         ↑
                   Success Stories
```

### 5.5 Open Questions

| Question | Impact | Decision Needed |
|----------|--------|-----------------|
| **Prompt template language** | Jinja2 vs. custom vs. f-string | Affects expressiveness |
| **Output format** | Markdown vs. plain text vs. direct to Excel | Affects usability |
| **Summary storage** | Next to Excel or separate directory | Affects organization |

---

## 6. Work Stream 5: Integration & CLI

**Objective**: Provide a command-line interface for triggering pipelines and workflows.

### 6.1 Scope

**In Scope**:
- CLI argument parsing
- Triggering individual work streams
- Logging and progress reporting
- Error handling and recovery
- Status reporting (what exists, what's changed)

**Out of Scope**:
- Automatic scheduling or background execution
- Multi-user access controls
- Web-based UI

### 6.2 Key Components

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| **CLI Parser** | Parse command-line arguments | Reuse v1.0 structure |
| **Workflow Orchestrator** | Call work streams in correct order | Simple, explicit logic |
| **Status Reporter** | Show current state (files, versions, stories) | |
| **Logger** | Print progress and diagnostics | |

### 6.3 Candidate Commands

```bash
# Knowledge Base processing
python run.py --process-sources [--dir PATH]

# Success Story extraction
python run.py --extract-stories [--from-sources] [--from-markdown]

# Excel generation
python run.py --generate-excel [--version N] [--output PATH]

# Executive Summary
python run.py --summary [--prompt PATH] [--output PATH]

# Status and reporting
python run.py --status [--detailed]
```

### 6.4 Data Flow

```
CLI Command → Orchestrator → Work Streams (1-4) → Outputs
                          ↓
                     Logging & Status
```

### 4.5 Open Questions

| Question | Impact | Decision Needed |
|----------|--------|-----------------|
| **Command granularity** | Fine-grained (each work stream) vs. high-level (all-at-once) | Affects usability |
| **Status format** | Table vs. JSON vs. human-readable | Affects scripting vs. human use |

---

## 7. Sequence & Dependencies

### 7.1 Recommended Development Sequence

```
Phase 1: Knowledge Base Processing (Work Stream 1)
  ↓
Phase 2: Success Story Extraction (Work Stream 2)
  ↓
Phase 3: Excel Library & Versioning (Work Stream 3)
  ↓
Phase 4: Executive Summaries (Work Stream 4)
  ↓
Phase 5: Integration & CLI (Work Stream 5)
```

### 7.2 Dependencies

| Work Stream | Depends On | Blocks |
|-------------|------------|--------|
| **WS1: Knowledge Base** | Nothing | WS2 |
| **WS2: Extraction** | WS1 (for Markdown) OR direct sources | WS3, WS4 |
| **WS3: Excel** | WS2 (for Success Stories) | Nothing |
| **WS4: Summaries** | WS2 (for Success Stories) | Nothing |
| **WS5: Integration** | WS1, WS2, WS3, WS4 | Nothing (last step) |

### 7.3 Parallel Opportunities

| Work Streams | Can Be Parallel? | Notes |
|--------------|------------------|-------|
| WS1 + WS2 | ⚠️ Partial | WS2 can start before WS1 finishes if using direct sources |
| WS3 + WS4 | ✅ Yes | Both consume Success Stories, produce different outputs |
| WS5 | ❌ No | Integrates everything, must be last |

---

## 8. Testing Strategy

### 8.1 Testing Philosophy

Given the human-in-the-loop nature, testing focuses on:

1. **Determinism**: Same inputs → same outputs (controlled LLM variation)
2. **Traceability**: Can trace every output to source
3. **Recoverability**: Errors don't destroy human work
4. **Usability**: Humans can understand and use outputs

### 8.2 Testing Levels

| Level | Focus | Approach |
|-------|-------|----------|
| **Unit** | Individual components (handlers, validators) | Sample files, mock LLM |
| **Integration** | Work stream end-to-end | Small corpus of real sources |
| **System** | Full pipeline with human review | Real workflow, manual validation |

### 8.3 Critical Test Scenarios

| Scenario | Validation |
|----------|------------|
| **Re-running pipeline** | Does it preserve or destroy previous outputs? |
| **Human-edited Excel** | Does system detect and avoid overwrite? |
| **Missing sources** | Does system fail gracefully? |
| **Low-confidence extraction** | Does system flag for human review? |
| **Version conflict** | Can human resolve system vs. human versions? |

---

## 9. Assumptions

### 9.1 Technical Assumptions

| Assumption | Impact | If False |
|------------|--------|----------|
| **Python 3.10+** | Language features | May need to adjust type hints |
| **Ollama running locally** | LLM access | Need offline LLM alternative |
| **Excel files < 100MB** | Performance | Need streaming/large-file handling |
| **Source files < 100MB each** | Memory usage | Need chunked processing |

### 9.2 Operational Assumptions

| Assumption | Impact | If False |
|------------|--------|----------|
| **Single user** | No concurrency needed | May need file locking |
| **Manual file placement** | No API integrations needed | May need ingest workflows |
| **Obsidian vault exists** | Output destination known | Need setup/validation |
| **Human reviews outputs** | Quality gate exists | Need automated validation |

### 9.3 Business Assumptions

| Assumption | Impact | If False |
|------------|--------|----------|
| **Success Stories exist in sources** | Extraction pipeline useful | May need different approach |
| **Stakeholders use Excel** | Output format appropriate | May need different output |
| **Executive Summaries valued** | Work Stream 4 justified | May deprioritize |
| **Offline requirement stands** | No cloud dependencies | Could simplify with cloud APIs |

---

## 10. Migration from v1.0

### 10.1 Reusable Components

| v1.0 Component | Reuse Potential | Notes |
|----------------|-----------------|-------|
| **Source file scanner** | ✅ High | Same requirements |
| **Format handlers (PDF, etc.)** | ✅ High | Same requirements |
| **Markdown generation** | ✅ High | Same requirements |
| **LLM integration (Ollama)** | ✅ High | Same requirements |
| **Extraction prompts** | ⚠️ Medium | May need adjustment for new data model |

### 10.2 Components to Remove

| v1.0 Component | Removal Reason |
|----------------|----------------|
| **JSON Success Story storage** | Success Stories are now abstract entities |
| **Deduplication logic** | Human judgment required |
| **Multi-agent orchestration** | Explicit pipelines only |
| **Planner Agent** | Not needed for explicit triggers |
| **Markdown Obsidian output** | Not primary output anymore |

### 10.3 New Components to Build

| Component | Complexity | Notes |
|-----------|------------|-------|
| **Excel workbook generator** | Medium | Straightforward with `openpyxl` |
| **Version manager** | High | Needs careful change detection |
| **Prompt loader** | Low | Simple file reading |
| **CLI integration** | Low | Wrap work streams |

---

## 11. Success Metrics

### 11.1 Development Success

The development plan is successful if:

- [ ] All work streams are implemented and testable
- [ ] CLI commands trigger correct pipelines
- [ ] Excel versioning preserves human edits
- [ ] Prompts are externalized and editable
- [ ] End-to-end pipeline runs without errors

### 11.2 System Success (from Requirements v2)

- [ ] Executive Summaries are high-quality and consistent
- [ ] Time to collect stories is reduced by >50%
- [ ] Time to structure information is reduced by >70%
- [ ] Time to generate summaries is reduced by >80%

---

## 12. Next Steps

1. **User reviews this plan** and confirms direction
2. **Resolve open questions** (Section 2.4, 3.5, 4.6, 5.5, 6.5)
3. **Confirm assumptions** (Section 9)
4. **Begin Work Stream 1**: Knowledge Base Processing
5. **Proceed sequentially** through WS2 → WS3 → WS4 → WS5

---

**End of Development Plan v2.0**
