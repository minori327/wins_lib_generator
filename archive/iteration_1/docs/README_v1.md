# Wins Library System v1.0

An offline, local-first Agentic Workflow for managing success stories.

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Ollama (local LLM runtime)
- GLM-4 model (9B parameters)

### Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama:**
   - Download from https://ollama.com/
   - Follow installation instructions for your OS

3. **Pull the GLM-4 model:**
   ```bash
   ollama pull glm-4:9b
   ```

4. **Verify Ollama is running:**
   ```bash
   ollama list
   ```
   You should see `glm-4:9b` in the model list.

---

## Configuration

All configuration is managed through YAML files in the `config/` directory:

- `config/config.yaml` - Main system configuration
- `config/business_rules.yaml` - Phase 5 business rules
- `config/output_config.yaml` - Phase 6 output settings
- `config/publish_config.yaml` - Phase 7 publish channels

### Validate Configuration

Before running the system, validate your configuration:

```bash
python run.py validate
```

Expected output:
```
✅ config.yaml
✅ business_rules.yaml
✅ output_config.yaml
✅ publish_config.yaml
```

---

## Quick Start

### 1. Prepare Source Files

Place your raw source files in the correct directory structure:

```
vault/00_sources/
└── 2026-01/
    ├── US/
    │   ├── pdf/
    │   │   └── report.pdf
    │   ├── email/
    │   │   └── success_story.eml
    │   ├── teams/
    │   │   └── chat.txt
    │   └── images/
    │       └── screenshot.png
    ├── UK/
    └── CN/
```

### 2. Run Weekly Update

Process all source files for a specific month and country:

```bash
python run.py weekly --country US --month 2026-01
```

Process multiple countries:

```bash
python run.py weekly --country US --country UK --country CN --month 2026-01
```

### 3. Check Library Status

View statistics about processed stories:

```bash
python run.py status
```

Output:
```
Library: ./wins
Total Stories: 42

By Country:
  CN: 10
  UK: 12
  US: 15
  Other: 5

By Month:
  2026-01: 42

By Confidence:
  high: 28
  low: 2
  medium: 12
```

---

## CLI Reference

### Commands

#### `weekly` - Run Weekly Update Workflow

The primary command for processing source files into success stories.

```bash
python run.py weekly --country <CODE> --month <YYYY-MM> [OPTIONS]
```

**Required Flags:**
- `--country` - Country code (can specify multiple)
- `--month` - Month in YYYY-MM format

**Optional Flags:**
- `--dry-run` - Validate configuration and inputs without processing
- `--config` - Path to config.yaml (default: config/config.yaml)
- `--verbose` - Enable debug logging

**Examples:**
```bash
# Process US files for January 2026
python run.py weekly --country US --month 2026-01

# Dry run to validate setup
python run.py weekly --country US --month 2026-01 --dry-run

# Verbose output for debugging
python run.py weekly --country US --month 2026-01 --verbose
```

#### `status` - Show Library Statistics

Display statistics about the success story library.

```bash
python run.py status
```

#### `validate` - Validate Configuration

Check all YAML configuration files for syntax and structure errors.

```bash
python run.py validate
```

#### `review` - Review Story (Phase 5 Checkpoint)

Review a specific story for approval (Phase 5 human checkpoint).

```bash
python run.py review --story-id <STORY_ID>
```

**Example:**
```bash
python run.py review --story-id win-2026-01-US-1234abcd
```

This displays story details and prompts for approval.

#### `publish` - Publish Artifact (Phase 7 Checkpoint)

Publish an artifact to external channels (Phase 7 publish checkpoint).

```bash
python run.py publish --artifact-id <ARTIFACT_ID> [--approve]
```

**Example:**
```bash
# Check what would be published
python run.py publish --artifact-id pub-xxx

# Approve and publish
python run.py publish --artifact-id pub-xxx --approve
```

---

## Directory Structure

After running the system, your vault will have the following structure:

```
vault/
├── 00_sources/              # Raw input files
│   └── YYYY-MM/
│       └── COUNTRY/
│           ├── pdf/
│           ├── email/
│           ├── teams/
│           └── images/
├── outputs/                 # Generated outputs (Phase 6)
│   ├── executive/
│   └── marketing/
├── notes/                   # Obsidian notes
└── weekly/                  # Weekly summaries

wins/                        # Success story library (JSON)
├── win-2026-01-US-1234abcd.json
└── ...
```

---

## Workflow

The system processes data through the following phases:

1. **Discovery** (Phase 3) - Scan source directories for files
2. **Normalization** (Phase 3) - Extract text into RawItem objects
3. **Extraction** (Phase 4) - LLM extracts success stories from RawItems
4. **Deduplication** (Phase 3/4) - Remove duplicate stories
5. **Finalization** (Phase 4) - Create SuccessStory objects
6. **Save** (Phase 4) - Persist to JSON files
7. **Evaluation** (Phase 5) - Apply business rules
8. **Ranking** (Phase 5) - Score and sort stories
9. **Output Generation** (Phase 6) - Create executive/marketing versions
10. **Publishing** (Phase 7) - Route to channels (optional)

---

## Human Approval Checkpoints

There are two human approval checkpoints in the workflow:

### 1. Story Review (Phase 5)

When you need to approve or reject a story:

```bash
python run.py review --story-id win-2026-01-US-1234abcd
```

This displays:
- Customer name
- Context, action, outcome
- Metrics
- Confidence level
- Source files

**Note**: Full Phase 5 integration is pending for v1.0. This is currently a manual review checkpoint.

### 2. Publish Approval (Phase 7)

When publishing to external channels:

```bash
python run.py publish --artifact-id pub-xxx --approve
```

The `--approve` flag is required for publishing to external channels (website, CMS, email).

**Note**: Full Phase 7 integration is pending for v1.0. Publishing is logged but not yet executed to external channels.

---

## Error Handling

The system is designed to continue processing when errors occur:

- **Phase 3-4 errors**: Logged, processing continues with remaining files
- **Phase 5-6 errors**: Logged, partial outputs may be generated
- **LLM failures**: Automatic retry (up to 3 attempts)

Check the log file for errors:

```
logs/wins_library.log
```

---

## Troubleshooting

### "Config file not found"

Ensure `config/config.yaml` exists. Run `python run.py validate` to check.

### "LLM connectivity failed"

1. Check Ollama is running: `ollama list`
2. Check the model is available: `ollama list` should show `glm-4:9b`
3. Check the URL in `config/config.yaml` matches your Ollama instance

### "Source directory not found"

Ensure the directory structure exists:

```bash
mkdir -p vault/00_sources/2026-01/US/pdf
```

### "No stories processed"

1. Check that source files exist in the correct location
2. Run with `--verbose` flag to see detailed logs
3. Check the log file for specific errors

---

## Development

### Running Tests

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=workflow --cov=models --cov=agents --cov=processors
```

---

## Architecture

The system is organized into 8 phases:

- **Phase 0**: System Design (frozen)
- **Phase 1**: Data Models (frozen)
- **Phase 2**: Scaffolding (frozen)
- **Phase 3**: Core Logic - Mechanical processing
- **Phase 4**: Semantic Extraction - LLM-based extraction
- **Phase 5**: Business Logic - Evaluation and ranking
- **Phase 6**: Output Generation - Template-driven rendering
- **Phase 7**: Publish Gate - Channel routing
- **Phase 8**: Feedback Loop - Signal collection

Phase boundaries are strictly enforced. Each phase has:
- Specific responsibilities
- Clear input/output contracts
- No overlap with other phases

---

## License

[Specify your license here]

---

## Version

**Version**: 1.0
**Last Updated**: 2026-02-01
