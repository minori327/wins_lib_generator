# Iteration 2 — Operator Usage Guide

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**System Version**: 2.0 (Human-Primary)

---

## 1. What This Tool Is (and What It Is Not)

### 1.1 Purpose

This tool transforms raw source materials (PDFs, emails, presentations, documents) into two outputs:

1. **Navigable Markdown files** — For understanding and searching source content
2. **Candidate Success Story rows in Excel** — For human review, consolidation, and approval

The tool is designed for teams who need to:
- Preserve original source materials
- Extract and organize success stories from diverse inputs
- Produce executive summaries for stakeholders

### 1.2 What This Tool Is NOT

This is **NOT** an automated system that:
- Makes business decisions about what constitutes a "real" success story
- Consolidates or deduplicates stories automatically
- Produces final, ready-to-use outputs without human review
- Prioritizes or ranks stories based on AI judgment

This tool **does NOT have**:
- A web interface, dashboard, or GUI
- One-click approval or confirmation workflows
- Automatic background processing
- Cloud APIs or external dependencies

### 1.3 Core Design Principles

| Principle | Meaning |
|-----------|---------|
| **Human control** | The AI extracts and suggests. Humans decide. |
| **No overwrites** | The system never modifies your work. Every run creates new files. |
| **Full transparency** | All processing is logged and traceable to source files. |
| **CLI-only** | All operations are triggered from the command line. |

---

## 2. System Overview

### 2.1 Technology Stack

- **Storage**: File system only (original files, Markdown, Excel)
- **Computation**: Local LLM (Ollama + GLM-4, fully offline)
- **Interface**: Command-line interface (CLI) only
- **Review Workspace**: Microsoft Excel

### 2.2 The Three Work Streams

```
┌─────────────────────────────────────────────────────────────────────────┐
│ WORK STREAM 1: Markdown Extraction                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ Input:  Raw source files (PDF, PPT, DOC, EML, etc.)                    │
│ Output: Navigable Markdown files in vault/20_notes/sources/             │
│ Purpose: Make source content searchable and understandable              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ WORK STREAM 2: Candidate Generation                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ Input:  Markdown files from WS1                                         │
│ Output: Excel workbook with candidate rows                              │
│ Purpose: Suggest potential success stories for human review             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ WORK STREAM 3: Human Review & Consolidation (in Excel)                 │
├─────────────────────────────────────────────────────────────────────────┤
│ Input:  Candidate Excel workbook from WS2                               │
│ Output: Human-approved rows marked as 'final'                          │
│ Purpose: Humans consolidate, deduplicate, and approve stories          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ WORK STREAM 4: Executive Summary                                        │
├─────────────────────────────────────────────────────────────────────────┤
│ Input:  Excel rows with status='final' (human-approved only)            │
│ Output: Executive summary in Markdown                                   │
│ Purpose: Generate stakeholder communications from approved stories      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 The Role of AI vs. The Role of Humans

| Activity | AI Role | Human Role |
|----------|---------|------------|
| **Extraction** | Identify potential success story candidates | Decide which candidates are valid |
| **Consolidation** | Suggest which candidates might be related | Combine candidates into final stories |
| **Deduplication** | Flag possible similarities or overlaps | Decide whether stories are duplicates |
| **Quality** | Provide evidence and source references | Validate accuracy and completeness |
| **Prioritization** | Provide sortable fields (customer, metrics, date) | Decide what matters for your context |

**Key Point**: The system treats rows marked `consolidated`, `final`, or `archived` as **read-only**. Once you approve a row, the system will never modify it.

---

## 3. Command-Line Operations

### 3.1 Prerequisites

Before running any command, ensure:

1. **Ollama is running**:
   ```bash
   ollama serve
   ```

2. **The GLM-4 model is available**:
   ```bash
   ollama pull glm-4:9b
   ```

3. **Source files are in place**:
   - Place raw sources in `vault/00_sources/YYYY-MM/`

### 3.2 Command 1: Extract Markdown

Transform raw source files into navigable Markdown.

```bash
python run.py --extract-markdown --sources vault/00_sources/2026-01/
```

**What happens**:
- Scans the source directory for supported file types
- Extracts text from each file
- Creates a Markdown file with source metadata and extracted content
- Outputs to `vault/20_notes/sources/`

**Output**: One Markdown file per source, containing:
- Frontmatter with source metadata (file type, original path, extraction timestamp)
- Extracted text content
- Source ID for traceability

**Why this step**: Markdown is easier to read, search, and process than binary files.

### 3.3 Command 2: Identify Story Candidates

Generate candidate Success Story rows from Markdown sources.

```bash
python run.py --identify-stories \
  --sources vault/20_notes/sources/ \
  --output outputs/candidates_v1_20260201.xlsx
```

**What happens**:
- Reads all Markdown files from the sources directory
- Sends each file to the local LLM with a structured prompt
- The LLM identifies potential success stories and extracts fields
- Creates a new Excel workbook with candidate rows

**Output Excel structure**:
- **Stories worksheet**: Candidate rows with all fields
- **Evidence worksheet**: Source references for each story
- **Metrics worksheet**: Extracted metrics
- **Metadata worksheet**: Generation timestamp, source paths

**What the AI does**:
- Identifies potential success stories in source text
- Extracts: customer, context, action, outcome, metrics, evidence references
- Provides consolidation hints (e.g., "This appears similar to the ACME story from source_email_123")

**What the AI does NOT do**:
- Decide whether something is "real" success story
- Merge or consolidate candidates
- Perform deduplication
- Make final business judgments

**Versioning**: Each run creates a new file with an incremented version number. The system never overwrites existing Excel files.

### 3.4 Command 3: Generate Executive Summary

Generate an executive summary from human-approved stories only.

```bash
python run.py --summary executive \
  --input outputs/wins_library_final_20260201.xlsx \
  --output outputs/executive_summary.md
```

**What happens**:
- Reads the Excel file
- **Filters for rows with status='final' only** (candidate and consolidated rows are ignored)
- Sends final stories to the LLM with an executive summary prompt
- Writes a Markdown summary

**Important**: This command only processes rows you have marked as `final`. If no rows are marked `final`, the command will produce a warning and exit.

---

## 4. Working with Excel

### 4.1 Understanding Row Statuses

Every row in the Excel workbook has a `status` column with four possible values:

| Status | Meaning | System Can Modify? | Human Should |
|--------|---------|-------------------|--------------|
| `candidate` | AI-generated, awaiting review | ✅ Append only | Review and edit |
| `consolidated` | Human-merged from candidates | ❌ Read-only | Continue editing or mark as final |
| `final` | Human-approved, business-ready | ❌ Read-only | Use for summaries, presentations |
| `archived` | Human-excluded from use | ❌ Read-only | Exclude from outputs |

**Rules**:
- The system **only writes** rows with status=`candidate`
- The system **never modifies** rows with status=`consolidated`, `final`, or `archived`
- You are free to edit candidate rows in Excel
- Once you mark a row as `consolidated`, `final`, or `archived`, the system will treat it as read-only

### 4.2 The Human Review Workflow

After running `--identify-stories`, open the Excel file and review the candidate rows:

1. **Review each candidate** for accuracy, completeness, and relevance
2. **Edit fields** directly in Excel as needed
3. **Consolidate related candidates**:
   - Copy relevant content from multiple candidates into one row
   - Change status to `consolidated`
   - Delete or mark duplicates as `archived`
4. **Approve final stories**:
   - When a story is ready for use, change status to `final`
   - Only `final` stories will be included in executive summaries

**Excel is your control point**. The system does not provide automation for these steps because they require business judgment.

### 4.3 Consolidation Hints

The AI provides a `consolidation_hints` column with advisory notes like:
- "Note: This appears similar to the story about ACME Corp from source_email_123"
- "Consider: May be related to the Q3 marketing campaign story"

These are **textual suggestions only**. The system does not perform merging. You decide whether to consolidate based on your domain knowledge.

### 4.4 Saving Your Work

After reviewing and editing:
- Save the Excel file (the system will not overwrite it)
- Use a clear filename indicating the stage (e.g., `wins_library_final_20260201.xlsx`)
- Keep the original candidate file as an audit trail

**Recommendation**: Create a separate file for your final library to avoid confusion with generated candidates.

---

## 5. Versioning and File Management

### 5.1 How Versioning Works

The system uses automatic versioning to prevent data loss:

- **Candidate files**: `candidates_v{N}_YYYYMMDD.xlsx`
  - Each run increments the version number
  - Datestamp indicates generation date
  - Previous versions are never overwritten

- **Summary files**: You specify the output path
  - Use descriptive names to distinguish versions
  - The system will not overwrite existing files

### 5.2 File Organization

```
vault/
├── 00_sources/           # Original source files (authoritative, never modified)
│   └── 2026-01/
│       ├── customer_emails/
│       ├── case_studies/
│       └── presentations/
├── 20_notes/             # Generated Markdown (non-authoritative)
│   └── sources/
│       ├── source_001.md
│       └── source_002.md
└── 30_weekly/            # Weekly summaries (future use)

outputs/
├── candidates_v1_20260201.xlsx    # First generation
├── candidates_v2_20260202.xlsx    # Second generation (if you re-run)
└── wins_library_final_20260201.xlsx  # Your reviewed and approved library
```

### 5.3 Best Practices

1. **Never edit source files** in `vault/00_sources/`. These are the authoritative originals.
2. **Markdown files** can be regenerated if needed. Edits may be overwritten.
3. **Keep all versions** of candidate Excel files for audit trail.
4. **Create a separate "final" library** file after human review.
5. **Back up your work** regularly, especially the final library files.

---

## 6. Common Mistakes and Misunderstandings

### 6.1 "The AI Missed a Story"

**Expected behavior**. The AI is not perfect. It extracts candidates based on pattern recognition, not business judgment. You should:
- Review the source Markdown files manually
- Add missing stories directly to Excel
- Edit extracted stories for accuracy

### 6.2 "There Are Too Many Candidates"

**Expected behavior**. The system is conservative — it prefers false positives over missing stories. You should:
- Review candidates in Excel
- Mark irrelevant or low-quality candidates as `archived`
- Consolidate related candidates into final stories

### 6.3 "The System Should Auto-Deduplicate"

**By design, it does not**. Deduplication requires business judgment. The system provides:
- `consolidation_hints` column with similarity suggestions
- Evidence references to help you compare candidates
- Sortable fields to group related stories

**You decide** whether two stories are duplicates or distinct.

### 6.4 "I Accidentally Deleted My Final Stories"

The system never deletes or overwrites. However, Excel is under your control:
- Always keep backups of final library files
- Consider using version control (Git) for critical files
- Save frequently during review sessions

### 6.5 "The Summary Command Says 'No Final Rows Found'"

This means no rows in your Excel file have `status='final'`. You must:
- Open the Excel file
- Review candidate rows
- Mark approved stories as `final` in the status column
- Re-run the summary command

### 6.6 "Can I Add Stories Manually?"

Yes. Excel is your workspace. You can:
- Add new rows manually
- Edit AI-generated rows
- Copy content between rows
- Change status values

The system only generates initial candidates. After that, Excel is under your control.

### 6.7 "Why No Web Interface?"

Excel **is** the interface for review and consolidation. It provides:
- Familiar editing tools
- Filtering and sorting
- Multi-user collaboration (if using shared storage)
- No learning curve for business users

A web interface would add complexity without improving human control.

---

## 7. Troubleshooting

### 7.1 Ollama Connection Errors

**Error**: `Connection refused` or `Cannot connect to Ollama`

**Solution**:
- Ensure Ollama is running: `ollama serve`
- Verify Ollama is accessible: `curl http://localhost:11434/api/tags`
- Check that GLM-4 is pulled: `ollama list`

### 7.2 LLM Timeout

**Error**: `LLM request timed out after 120 seconds`

**Solution**:
- This may occur with large source files or slow hardware
- Adjust `timeout_seconds` in `config/config.yaml`
- Process smaller batches of sources

### 7.3 Empty Excel Output

**Error**: Excel file is created but has no rows

**Possible causes**:
- No Markdown files found in sources directory
- LLM did not identify any success stories in the sources
- Source files are not relevant to success story extraction

**Solution**:
- Check that Markdown files exist in the sources directory
- Review a few Markdown files manually to confirm they contain relevant content
- Try with sources known to contain success stories

### 7.4 Markdown Extraction Fails

**Error**: `Failed to extract text from [filename]`

**Possible causes**:
- Corrupted or password-protected PDF
- Unsupported file format
- File encoding issues

**Solution**:
- Check the file can be opened normally
- Try converting the file to a supported format
- Skip problematic files and continue with others

---

## 8. Configuration

The system behavior is controlled by `config/config.yaml`:

```yaml
# Paths (absolute or relative to project root)
paths:
  vault_root: "./vault"
  sources_dir: "./vault/00_sources"
  outputs_dir: "./outputs"

# LLM settings (OFFLINE ONLY)
llm:
  backend: "ollama"
  base_url: "http://localhost:11434"
  model: "glm-4:9b"
  temperature: 0.3          # Lower = more deterministic
  max_tokens: 2000
  timeout_seconds: 120

# Excel row statuses
excel:
  statuses:
    - "candidate"           # AI-generated
    - "consolidated"        # Human-merged (read-only)
    - "final"               # Human-approved (read-only)
    - "archived"            # Human-excluded (read-only)
```

**Note**: Configuration is for technical settings only. There are no behavioral switches or automation flags (e.g., no `auto_merge`, `auto_dedup`) because these would violate Human Primacy.

---

## 9. Summary of Key Points

1. **CLI-only interface**: All operations are command-line driven. There is no web UI or dashboard.

2. **Human control is mandatory**: The AI extracts candidates. You decide what's real.

3. **Excel is your workspace**: Review, edit, consolidate, and approve stories in Excel.

4. **Status controls behavior**: Only `final` rows are used in executive summaries. The system never modifies human-owned rows (`consolidated`, `final`, `archived`).

5. **No automatic decisions**: The system does not merge, deduplicate, rank, or judge quality. These are your responsibilities.

6. **Versioned outputs**: Every run creates new files. The system never overwrites your work.

7. **Full transparency**: All outputs include source references and timestamps. You can always trace a story back to its origin.

8. **Offline-only**: The system works entirely offline using local LLM. No cloud APIs or external services.

---

## 10. Getting Help

If you encounter issues:

1. **Check the logs**: All commands output detailed logs with `[component_name]` prefixes.
2. **Review this guide**: Most questions are covered in Section 6 (Common Mistakes).
3. **Verify prerequisites**: Ensure Ollama is running and the model is available.
4. **Check file paths**: Use absolute paths if relative paths cause confusion.

For technical issues or bugs, refer to the project documentation in `docs/`.

---

**End of Guide**
