# Local Knowledge Base & Success Story System
## Requirements v2.0

**Document Version**: 2.0
**Status**: AUTHORITATIVE - Implementation Baseline
**Date**: 2026-02-01
**Supersedes**: REQUIREMENTS.md v1.0 (ARCHIVED)

---

## Table of Contents

1. [System Intent](#1-system-intent)
2. [Knowledge Base Layer](#2-knowledge-base-layer-obsidian-centered)
3. [Success Story / Wins Concept](#3-success-story--wins-concept)
4. [Pipeline & Agentic Workflows](#4-pipeline--agentic-workflows)
5. [Excel / Business Output Layer](#5-excel--business-output-layer)
6. [Executive Summary Generation](#6-executive-summary-generation)
7. [Success Criteria](#7-success-criteria)
8. [Out of Scope](#8-out-of-scope)

---

## 1. System Intent

### 1.1 Primary Purpose

The system is a **local-first knowledge infrastructure** centered on:

- **Obsidian** for knowledge navigation and working views
- **Excel** for business delivery and stakeholder communication

### 1.2 Core Objectives

The system exists to:

1. **Preserve original source materials** in their original form
2. **Extract navigable knowledge** into Markdown for understanding
3. **Curate and synthesize Success Stories** from diverse sources
4. **Produce high-quality Executive Summaries** that significantly reduce manual effort

### 1.3 Design Philosophy

| Priority | Rationale |
|----------|-----------|
| **Human control** | Humans make business judgments, not systems |
| **Transparency** | All processing must be inspectable and traceable |
| **Business usability** | Outputs must be immediately useful for stakeholders |
| **Quality over automation** | Better summaries > fully automated summaries |

### 1.4 Core Constraints

| Constraint | Requirement |
|------------|-------------|
| **Execution** | All pipelines triggered explicitly by humans |
| **Network** | Fully offline, no external API dependencies |
| **Storage** | File system only (original files, Markdown, Excel) |
| **Computation** | Local LLM only (Ollama + GLM-4) |
| **Language** | English for all processing and outputs |

---

## 2. Knowledge Base Layer (Obsidian-Centered)

### 2.1 Source Preservation (KB-1)

**Requirement**: The system MUST preserve all original source files in their original binary form.

**Supported Source Types**:

| Type | Format | Example |
|------|--------|---------|
| PDF | `.pdf` | Case study reports, white papers |
| Presentations | `.ppt`, `.pptx` | Slide decks, training materials |
| Documents | `.doc`, `.docx` | Meeting notes, project documentation |
| Spreadsheets | `.xls`, `.xlsx` | Data tables, metrics |
| Email | `.eml`, `.msg` | Customer communications |
| Text | `.txt` | Exported chat logs, notes |
| Images | `.png`, `.jpg`, `.jpeg` | Screenshots, photos |

**Storage Rule**:
```
vault/00_sources/
└── YYYY-MM/
    └── {any_structure}/
        └── {original_files}
```

**Invariant**: Original files are NEVER modified by the system.

---

### 2.2 Markdown Extraction (KB-2)

**Requirement**: For each relevant source file, the system MUST generate a Markdown document serving as:

1. **Index**: A searchable reference to the source
2. **Navigation aid**: A structured summary enabling quick understanding
3. **Working view**: A human-readable representation for downstream processing

**Markdown Generation**:

```python
# Pseudo-code
for source_file in discover_files():
    markdown_doc = extract_to_markdown(source_file)
    markdown_doc.metadata = {
        "source_file": source_file.path,
        "source_type": source_file.type,
        "extracted_at": timestamp(),
        "file_size": source_file.size
    }
    write_to_obsidian(markdown_doc)
```

**Storage Location**:
```
vault/20_notes/
└── sources/
    └── {source_id}.md
```

---

### 2.3 Role of Markdown (KB-3)

**Invariant**: Markdown documents are **working views**, not authoritative knowledge.

**Characteristics**:

| Aspect | Behavior |
|--------|----------|
| **Extraction fidelity** | Lossy extraction is acceptable and expected |
| **Purpose** | Support understanding, navigation, and downstream processing |
| **Authority** | Original source file remains the only authoritative version |
| **Re-generation** | Markdown may be re-generated from sources on demand |

**Acceptable Losses**:
- Formatting details (fonts, colors, layout)
- Binary data (embedded images, charts)
- Redundant content (duplicate sections, boilerplate)

**Must Preserve**:
- Core textual content
- Document structure (headings, sections)
- Metadata (authors, dates, titles)
- References to original source

---

### 2.4 Human Interaction with Markdown (KB-4)

**Capability**: Humans MAY edit Markdown files.

**System Behavior**:

| Scenario | System Behavior |
|----------|-----------------|
| Human edits Markdown | Edits are NOT guaranteed to persist across re-processing |
| Markdown re-generated | Human edits MAY be overwritten |
| Source file updated | Markdown is regenerated from new source |

**Guideline**: Markdown edits are temporary working notes, not long-term contributions to knowledge base.

---

## 3. Success Story / Wins Concept

### 3.1 Abstract Knowledge Object (W-1)

**Definition**: A Success Story (Win) is an **abstract conceptual entity**, not a file.

**Implications**:

| Aspect | Implication |
|--------|-------------|
| **Physical form** | Represented in Excel, not stored as discrete files |
| **Persistence** | Managed within Excel workbook(s) |
| **Identity** | Defined by business concept, not storage location |

**Core Structure**:

```
Success Story
├── Customer (who)
├── Context (business problem or situation)
├── Action (what was done)
├── Outcome (result achieved)
├── Metrics (quantifiable impact)
└── Evidence (reference to source files)
```

---

### 3.2 Flexible Source Mapping (W-2)

**Requirement**: A Success Story MAY reference any combination of source materials.

**Mapping Patterns**:

| Pattern | Example | Validity |
|---------|---------|----------|
| **1:1** | One Success Story from one PDF | ✅ Valid |
| **Many:1** | One Success Story from email + PDF + slides | ✅ Valid |
| **Partial** | One Success Story from section 3 of a 50-page report | ✅ Valid |
| **Synthesized** | One Success Story from fragments across 10 sources | ✅ Valid |

**No Strict Mapping**: There is NO requirement for 1:1, 1:many, or many:1 mapping between source files and Success Stories.

**Evidence Tracking**:

Each Success Story MUST include:
- List of referenced source files
- Specific sections or content used (if applicable)
- Confidence level in the extraction

---

## 4. Pipeline & Agentic Workflows

### 4.1 Explicit Human Control (P-1)

**Requirement**: All pipelines and agentic workflows MUST be triggered explicitly by a human.

**Allowed Triggers**:

| Trigger | Example |
|---------|---------|
| **CLI command** | `python run.py --extract-stories --sources vault/00_sources/2026-01/` |
| **Script execution** | Human runs a designated processing script |
| **Manual invocation** | Human directly calls pipeline functions |

**Forbidden Triggers**:

| Trigger | Status |
|---------|--------|
| **Cron jobs** | ❌ Not allowed |
| **File watchers** | ❌ Not allowed |
| **Background daemons** | ❌ Not allowed |
| **Automatic scheduling** | ❌ Not allowed |

**Rationale**: Humans must be aware of when processing occurs and must have the opportunity to intervene.

---

### 4.2 Purpose of Pipelines (P-2)

**Primary Responsibilities**:

Pipelines are responsible for:

1. **Identifying content relevant to Success Stories**
   - Scanning source files for business success events
   - Filtering out non-relevant materials
   - Flagging potential stories for human review

2. **Extracting key information across multiple sources**
   - Reading and analyzing source content (original or Markdown)
   - Correlating related information across files
   - Structuring information for business use

3. **Supporting human curation**
   - Presenting extracted information in reviewable format
   - Highlighting uncertainty or low-confidence extractions
   - Providing traceability to sources

**Explicitly NOT Responsible For**:

| Activity | Responsibility |
|----------|----------------|
| **Final business judgments** | Human decides if something is a Success Story |
| **Publishing results** | Human approves before business use |
| **Determining priority** | Human decides which stories matter most |
| **Quality assurance** | Human validates accuracy and completeness |

---

### 4.3 Pipeline Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Determinism** | Same inputs → Same outputs (when using same LLM temperature) |
| **Traceability** | Every extraction MUST reference source files |
| **Inspectability** | All intermediate outputs MUST be human-readable |
| **Reversibility** | Humans can undo or modify pipeline results |
| **Transparency** | All LLM prompts MUST be stored and viewable |

---

## 5. Excel / Business Output Layer

### 5.1 Excel as Primary Deliverable (E-1)

**Requirement**: Excel is the primary format for the Wins Library and Executive Summaries.

**Workbook Structure**:

```
wins_library.xlsx
├── [Stories]          # Success Story catalog
├── [Evidence]         # Source file references
├── [Metrics]          # Quantified impacts
└── [Metadata]         # Processing timestamps, confidence
```

**Rationale**:
- Stakeholders already use Excel for business reporting
- Sorting, filtering, and pivot analysis are built-in
- Familiar editing interface for non-technical users
- Compatible with existing business workflows

---

### 5.2 Human–AI Co-Editing (E-2)

**Requirement**: Excel outputs MAY be manually edited by humans.

**System Behavior**:

| Scenario | Required Behavior |
|----------|-------------------|
| **Human edits Excel** | System MUST preserve human edits |
| **Re-running pipeline** | System MUST NOT blindly overwrite human-modified Excel |
| **Conflict detected** | System MUST alert human and provide options |

**Edit Types**:

| Edit Type | Example | System Handling |
|-----------|---------|-----------------|
| **Correction** | Fix customer name | Preserve correction |
| **Enhancement** | Add missing metric | Preserve enhancement |
| **Curation** | Flag story as "high priority" | Preserve flag |
| **Deletion** | Remove invalid story | Preserve deletion (or archive) |

---

### 5.3 Versioning (E-3)

**Requirement**: The system MUST support multiple versions of Excel outputs.

**Versioning Strategy**:

```
outputs/
├── wins_library_v1_20260115.xlsx      # System-generated
├── wins_library_v2_20260116.xlsx      # System-generated (after update)
├── wins_library_v2_human_20260117.xlsx # Human-edited version
└── wins_library_v3_20260120.xlsx      # System-generated (after update)
```

**Version Coexistence**:

- System-generated versions represent raw pipeline outputs
- Human-modified versions represent curated business outputs
- Both types MUST be able to coexist in the file system
- File naming conventions MUST distinguish version types

**Version Metadata** (stored in workbook or separate manifest):

```yaml
version: 3
generated_at: "2026-01-20T10:30:00Z"
generated_by: "system"
source_version: 2
parent_version: "wins_library_v2_20260116.xlsx"
changes:
  - type: "added_stories"
    count: 5
  - type: "updated_stories"
    count: 2
```

---

## 6. Executive Summary Generation

### 6.1 Prompt-Driven Summaries (S-1)

**Requirement**: Executive Summaries are generated via explicit, stored prompts.

**Prompt as First-Class Artifact**:

```yaml
# prompts/executive_summary.yaml
name: "Executive Summary"
description: "Generate executive-facing summary of Success Stories"
template: |
  You are generating an executive summary for business stakeholders.

  For the provided Success Stories, create a summary that:
  - Emphasizes quantified business impact
  - Groups stories by theme or geography
  - Highlights top-priority items
  - Total length: ~500 words

  Input Success Stories: {{stories}}

  Output format: Markdown
```

**Prompt Storage**:

```
prompts/
├── executive_summary.yaml
├── marketing_summary.yaml
├── weekly_digest.yaml
└── custom_summary.yaml
```

**Usage**:

```bash
# Generate summary using specific prompt
python run.py --summary executive --prompt prompts/executive_summary.yaml
```

---

### 6.2 Quality & Consistency (S-2)

**Requirement**: Executive Summaries MUST follow a consistent structure and quality bar.

**Quality Dimensions**:

| Dimension | Criteria |
|-----------|----------|
| **Clarity** | Stakeholder can understand without domain expertise |
| **Accuracy** | All metrics and facts are traceable to sources |
| **Actionability** | Summary enables business decisions |
| **Consistency** | Same input produces similar output (with controlled LLM variation) |
| **Completeness** | No critical stories omitted without explicit flag |

**Quality > Automation**:

- It is better to require human review than to publish low-quality summaries
- The system SHOULD flag uncertain or low-confidence content
- The system SHOULD NOT attempt to fill gaps with hallucinated content

---

## 7. Success Criteria

The system is considered **successful** if:

### 7.1 Output Quality

| Criterion | Measure |
|-----------|---------|
| **Executive Summaries are high-quality** | Stakeholders can make decisions based on summaries alone |
| **Summaries are consistent** | Similar stories are summarized in similar ways across runs |
| **Summaries are usable** | No major post-processing required before business use |

### 7.2 Efficiency Gains

| Metric | Target |
|--------|--------|
| **Time to collect Success Stories** | Reduced by >50% vs. manual process |
| **Time to structure information** | Reduced by >70% vs. manual process |
| **Time to generate Executive Summary** | Reduced by >80% vs. manual process |

### 7.3 Human Experience

| Criterion | Measure |
|-----------|---------|
| **Transparency** | Humans can trace any summary point to source files |
| **Control** | Humans have final say over all business outputs |
| **Confidence** | Stakeholders trust the system's outputs |

---

## 8. Out of Scope (Explicit)

The following features are **explicitly out of scope** for this system:

| Feature | Status | Rationale |
|---------|--------|-----------|
| **Real-time autonomous agents** | ❌ Out of scope | Human control is required |
| **Multi-user collaboration** | ❌ Out of scope | Single-user local system |
| **Cloud-based services** | ❌ Out of scope | Must be fully offline |
| **Treating Markdown as authoritative knowledge base** | ❌ Out of scope | Original sources are authoritative |
| **Automatic background processing** | ❌ Out of scope | Explicit triggers only |
| **Automatic deduplication** | ❌ Out of scope | Human judgment required |
| **Web-based UI** | ❌ Out of scope | Excel and Obsidian are the UI |
| **Email / API integrations** | ❌ Out of scope | Manual file placement only |

---

## Appendix A: System Layers Summary

```
┌─────────────────────────────────────────────────────────────┐
│                   Layer 1: Sources                          │
│              Original files (read-only truth)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Layer 2: Working Knowledge                   │
│           Markdown (lossy, navigable, temporary)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Layer 3: Abstract Entities                     │
│          Success Stories (conceptual, curated)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Layer 4: Business Output                     │
│           Excel (versioned, co-edited, delivered)           │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix B: Key Invariants

1. **Source files are never modified**
2. **Markdown is temporary and lossy**
3. **Success Stories are abstract, not files**
4. **All processing is human-triggered**
5. **Excel is the business delivery format**
6. **Human edits in Excel are preserved**
7. **Prompts are first-class artifacts**
8. **Everything is offline and local**

---

**End of Requirements v2.0**
