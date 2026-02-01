# CLAUDE.md

## Guidelines for Using Claude Code in This Project

---

### 1. Purpose of This Document

This document defines how Claude Code should operate inside this repository.

The goal is to ensure that:

- The system is built correctly according to the [requirements](docs/REQUIREMENTS.md)
- The codebase remains deterministic, readable, and auditable
- Claude Code does not over-engineer or invent functionality
- All AI behavior is explicit, inspectable, and reproducible

**Claude Code should treat this file as a hard constraint, not a suggestion.**

---

### 2. Operating Assumptions

Claude Code **must** assume:

✅ The system runs **fully offline**
✅ No external APIs or cloud services are allowed
✅ All LLM calls are local (via Ollama + GLM-4)
✅ All business content (input/output) is in **English**
✅ File system is the only storage mechanism
✅ Obsidian is for reading only, not computation
✅ This repository is the single source of truth

If a requirement is ambiguous, Claude Code **must** choose the **simplest possible implementation**.

---

### 3. General Rules of Engagement

#### 3.1 Do Not Be Clever

Claude Code **must** prefer boring, explicit solutions.

**Forbidden behaviors**:

- Introducing frameworks not explicitly required (e.g., FastAPI, Django)
- Adding abstractions "for future scalability"
- Designing generic pipelines beyond the stated scope
- Refactoring for elegance instead of clarity
- Using vector databases or search engines
- Implementing web UIs or dashboards

**Allowed behaviors**:

✅ Clarity > Elegance
✅ Explicit > Implicit
✅ Files > Magic
✅ Functions > Classes (when appropriate)
✅ Standard library > External dependencies

#### 3.2 Determinism Over Autonomy

This project is **not** an autonomous agent system.

Claude Code **must**:

- Use explicit function calls
- Use manual or CLI-triggered workflows
- Avoid background daemons or hidden schedulers
- Make all LLM calls synchronous and traceable

**All actions must be traceable to**:

```bash
python run.py --mode weekly --country US
```

No hidden background processes. No cron jobs unless explicitly requested.

---

### 4. Code Style & Structure Constraints

#### 4.1 File System Is the Database

Claude Code **must** treat the file system as the primary storage layer.

**Forbidden**:

- SQL databases (PostgreSQL, MySQL, SQLite)
- Vector stores (Chroma, FAISS, Pinecone)
- In-memory caches (Redis, Memcached)
- Message queues (RabbitMQ, Kafka)

**Required**:

- All data stored as JSON or Markdown
- All intermediate artifacts must be human-readable
- All files inspectable on disk

#### 4.2 Directory Structure Is Sacred

Claude Code **must not** deviate from the defined structure:

```
vault/
├── 00_sources/     # Raw inputs ONLY - never modify
├── 20_notes/       # Generated Obsidian notes
├── 30_weekly/      # Weekly summaries
└── 40_outputs/     # Final outputs (executive/marketing)

wins/               # Success Story JSON library
```

**Rules**:
- Never write to `00_sources/` (read-only)
- Never delete files from `20_notes/` or `30_weekly/` without explicit command
- Always write to `wins/` as the source of truth

#### 4.3 No Silent Side Effects

Every write operation **must** be:

- **Explicit**: Function name clearly indicates what it writes
- **Logged**: Print to stdout what file was created/modified
- **Idempotent**: Safe to run multiple times

**Forbidden**:

- Overwriting files without user intent
- Deleting user data automatically
- Mutating files outside defined directories
- Modifying `00_sources/` in any way

#### 4.4 Always Write the Full File

When modifying code:

✅ **Always** output the entire file
❌ **Never** say "rest of the file remains unchanged"
❌ **Never** patch partially

This is required for:

- Auditability
- Human review
- Version control clarity

---

### 5. LLM Usage Rules

#### 5.1 LLMs Are Tools, Not Decision Makers

Claude Code **must** treat LLMs as:

- Text transformation engines
- Pattern extractors
- Rewriting tools

**LLMs must not**:

- Decide system architecture
- Decide file locations
- Decide control flow
- Decide business logic
- Make "smart" inferences about user intent

**All LLM calls must be**:

- Wrapped in explicit functions (e.g., `extract_success_story()`)
- Prompted with static, inspectable prompts
- Logged (print prompt + response length)
- Reproducible (same input → same output)

#### 5.2 Prompt Handling Rules

Prompts **must**:

- Be stored as strings in code or YAML files
- Be deterministic (no randomness unless specified in config)
- Clearly state the expected output format (JSON, Markdown, etc.)
- Include examples in the prompt when possible

**Claude Code must never**:

- Inline large prompts ad-hoc inside business logic
- Use dynamic prompt generation without clear templates
- Hide prompts behind multiple layers of abstraction

**Example - Acceptable**:

```python
# config/prompts.py
EXTRACTION_PROMPT = """
You are a business analyst extracting success stories.

Extract:
- customer: str
- context: str
- action: str
- outcome: str
- metrics: List[str]

Output as JSON.
"""

def extract_story(raw_items: List[RawItem]) -> SuccessStory:
    prompt = EXTRACTION_PROMPT + "\n\nInput:\n" + format_items(raw_items)
    return call_llm(prompt)
```

**Example - Forbidden**:

```python
# BAD: Hidden prompt, unclear behavior
def extract_story(raw_items):
    return smart_llm_call("extract story from this", raw_items)
```

#### 5.3 Local Model Constraints

**All LLM calls must use Ollama**:

- Model: `glm-4:9b` (or specified in config.yaml)
- Host: `http://localhost:11434`
- No fallback to OpenAI, Anthropic, or other cloud APIs

**Configuration**:

```python
# utils/llm_utils.py
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL = "glm-4:9b"
```

---

### 6. Error Handling Philosophy

Claude Code **must**:

- **Fail loudly**: Raise exceptions, don't suppress errors
- **Prefer exceptions**: Over silent recovery
- **Log clearly**: What failed, why, and where
- **Never guess**: If data is missing, fail explicitly

**Error Handling Pattern**:

```python
def process_pdf(file_path: str) -> RawItem:
    try:
        text = extract_text_from_pdf(file_path)
        if not text or len(text.strip()) < 10:
            raise ValueError(f"PDF extraction failed or empty: {file_path}")
        return RawItem(...)
    except Exception as e:
        print(f"ERROR: Failed to process {file_path}: {e}")
        raise  # Re-raise to stop execution
```

**If a raw input cannot be parsed**:

1. Log the failure (print to stdout)
2. Skip the file
3. Continue processing others
4. Report summary at end

---

### 7. Data Model Constraints

#### 7.1 Success Story Is First-Class

The `SuccessStory` model is the core business object.

**Rules**:

- All functions must return or accept `SuccessStory` objects, not dicts
- Never bypass the model with raw dicts
- Validation happens at model construction time

**Example**:

```python
# models/success_story.py
@dataclass
class SuccessStory:
    id: str
    customer: str
    context: str
    action: str
    outcome: str
    metrics: List[str]
    # ... other fields

    def __post_init__(self):
        if not self.customer:
            raise ValueError("customer is required")
        if not self.id.startswith("win-"):
            raise ValueError(f"Invalid ID format: {self.id}")
```

#### 7.2 RawItem Is Immutable

Once a `RawItem` is created from source files:

- **Never modify** the `text` field
- **Never change** the `source_type` or `filename`
- Treat as read-only evidence

---

### 8. Output Generation Rules

#### 8.1 Obsidian Notes Are Generated, Not Edited

Claude Code **must**:

- Generate Obsidian notes from `SuccessStory` objects
- Never parse or read Obsidian notes as input
- Treat `vault/` as output-only (except `00_sources/`)

#### 8.2 Output Templates

All outputs **must** use templates:

- `templates/success_story.md`
- `templates/weekly_summary.md`
- `templates/executive_output.md`
- `templates/marketing_output.md`

**Forbidden**:

- Inline Markdown generation in business logic
- String concatenation for complex outputs
- Hardcoded output formats

**Required**:

```python
from jinja2 import Template

def write_obsidian_note(story: SuccessStory, template_path: str):
    with open(template_path) as f:
        template = Template(f.read())
    output = template.render(story=story)
    # Write output...
```

---

### 9. Incremental Development Expectations

Claude Code **should assume**:

- This system will evolve
- Humans will read and modify the code
- Debugging will happen manually
- New source types may be added (e.g., new file formats)

**Therefore**:

- ✅ Avoid deep call stacks (max 3-4 levels)
- ✅ Avoid meta-programming (no `exec`, `eval`, dynamic imports)
- ✅ Prefer composition over inheritance
- ✅ Keep functions under 50 lines when possible
- ✅ Use type hints (Python 3.10+)

---

### 10. Explicit Non-Goals (v1)

Claude Code **must not** implement:

| Feature | Status | Response If Asked |
|---------|--------|-------------------|
| Automatic email ingestion | ❌ Out of scope | "This requires IMAP/POP3 APIs, explicitly out of scope for v1" |
| Teams / Outlook APIs | ❌ Out of scope | "This requires cloud APIs, violates offline constraint" |
| Real-time monitoring | ❌ Out of scope | "System is CLI-triggered only" |
| UI dashboards | ❌ Out of scope | "Obsidian is the UI" |
| Vector search / semantic retrieval | ❌ Out of scope | "No vector databases in v1" |
| Cloud LLM fallback | ❌ Out of scope | "System must be fully offline" |
| Multi-language support | ❌ Out of scope | "English only in v1" |
| Automatic scheduling | ❌ Out of scope | "Manual CLI trigger only" |
| Web server / API | ❌ Out of scope | "CLI tool, not a web service" |

**If asked for any of these, Claude Code must respond**:

> "This is explicitly out of scope for v1. See [REQUIREMENTS.md](docs/REQUIREMENTS.md) Section 12.2."

---

### 11. Testing Expectations

Formal unit tests are **optional** in v1.

**However**, Claude Code **must** ensure:

- Each major function is runnable in isolation
- CLI commands are easy to test manually
- Sample inputs/outputs are provided when possible
- All functions have clear docstrings

**Acceptable testing approach**:

```python
# Example manual test function
def test_extraction_agent():
    """Manual test for extraction agent."""
    sample_raw = [
        RawItem(
            id="test-1",
            text="ACME Corp achieved 15% revenue growth.",
            source_type="email",
            filename="test.eml",
            country="US",
            month="2026-01",
            created_at="2026-01-01T00:00:00Z"
        )
    ]

    story = extract_success_story(sample_raw)

    assert story.customer == "ACME Corp"
    assert "+15% revenue" in story.metrics[0]
    print("✅ Test passed")
```

---

### 12. Human-in-the-Loop Assumption

Claude Code **must assume**:

- A human will review outputs
- A human will correct errors
- A human will curate raw inputs
- A human will trigger CLI commands

**Therefore**:

- Outputs must be **readable** (JSON, Markdown)
- Logs must be **understandable** (plain English)
- Errors must be **actionable** (what to do next)
- All file paths in logs must be **absolute** or **clearly relative to project root**

---

### 13. File Naming and Location Rules

#### 13.1 Success Story IDs

Format: `win-YYYY-MM-{country}-{seq}`

Examples:
- `win-2026-01-us-001`
- `win-2026-01-uk-023`
- `win-2026-02-cn-007`

**Rules**:
- Always lowercase
- Always zero-padded sequence (3 digits)
- Always derived from month + country

#### 13.2 File Locations

| Content | Location | Format |
|---------|----------|--------|
| Raw inputs | `vault/00_sources/YYYY-MM/COUNTRY/{type}/` | Original |
| RawItem (processed) | `cache/raw_items/YYYY-MM.json` | JSON |
| SuccessStory | `wins/win-YYYY-MM-{country}-{seq}.json` | JSON |
| Obsidian notes | `vault/20_notes/wins/win-*.md` | Markdown |
| Weekly summaries | `vault/30_weekly/YYYY-WW.md` | Markdown |
| Executive outputs | `vault/40_outputs/executive/YYYY-MM.md` | Markdown |
| Marketing outputs | `vault/40_outputs/marketing/YYYY-MM.md` | Markdown |

---

### 14. Configuration Rules

**All configuration must be in**:

- `config.yaml` - System settings (paths, models, thresholds)
- `config/prompts.yaml` - Agent prompts

**Forbidden**:

- Hardcoded paths in code (use `config.yaml`)
- Hardcoded model names (use `config.yaml`)
- Environment variables for configuration (use YAML)

**Required**:

```python
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

PATHS = config['paths']
MODEL = config['system']['model']
```

---

### 15. Logging Requirements

All functions **must** print:

```
[FUNCTION_NAME] Starting operation...
[FUNCTION_NAME] Processing file: /path/to/file.pdf
[FUNCTION_NAME] Extracted 2500 characters
[FUNCTION_NAME] Generated SuccessStory: win-2026-01-us-001
[FUNCTION_NAME] Completed in 2.3s
```

**Error format**:

```
[ERROR] Failed to process file.pdf: PDF parsing error
[ERROR] Extraction failed for raw-abc123: LLM timeout
```

---

### 16. When in Doubt

If Claude Code is unsure:

1. **Choose the simplest implementation**
2. **Document the assumption in comments**
3. **Do not invent requirements**
4. **Do not add "just in case" features**
5. **Ask the user** if still unclear after reading requirements

**Default decisions**:

| Question | Default Answer |
|----------|----------------|
| Should I use a class or function? | Function (unless state needed) |
| Should I add error handling? | Yes, but fail loudly |
| Should I make this configurable? | No (unless explicitly required) |
| Should I optimize performance? | No (clarity > speed) |
| Should I add logging? | Yes (print to stdout) |

---

### 17. Final Instruction to Claude Code

Build a system that is:

- **Boring**: Standard patterns, no clever tricks
- **Explicit**: Clear function names, obvious data flow
- **Predictable**: Same input → same output
- **Easy to debug**: Human-readable files, clear logs

**This project values trust and repeatability over cleverness.**

---

### 18. Quick Reference Checklist

Before writing any code, Claude Code **must** verify:

- [ ] Is this feature in [REQUIREMENTS.md](docs/REQUIREMENTS.md)?
- [ ] Does this work offline (no external APIs)?
- [ ] Is the file system the only storage mechanism?
- [ ] Is the output human-readable (JSON/Markdown)?
- [ ] Are all LLM calls explicit and logged?
- [ ] Is error handling explicit (no silent failures)?
- [ ] Is this the simplest possible implementation?

**If any answer is "No", stop and reconsider.**

---

## End of CLAUDE.md
