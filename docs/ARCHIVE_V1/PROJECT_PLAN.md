# Wins Library System – Complete Project Work Plan

**Document Type**: Advisory Work Plan
**Planner Agent Output**
**Based on**: [Agent Development Plan v1.2](DEVELOPMENT_PLAN.md), [REQUIREMENTS.md](REQUIREMENTS.md), [CLAUDE.md](CLAUDE.md)
**Status**: ADVISORY ONLY – Does NOT authorize execution

---

## Important Notice

**This Work Plan is advisory and frozen.**

Execution MUST follow Phase-specific prompts only from [Agent Development Plan v1.2](DEVELOPMENT_PLAN.md).

---

## Phase 0: Requirements Freeze

### A. Phase Objective

Freeze all requirements and establish baseline documentation.

### B. Responsible Agent

User

### C. Ordered Task List

- Review and finalize business requirements
- Document input data types (PDF, email, Teams text, images)
- Define SuccessStory data structure requirements (conceptual)
- Specify offline and local model constraints
- Define output requirements (Executive, Marketing versions)
- Specify Obsidian integration requirements (conceptual only)
- Document all explicit non-goals for v1

### D. Required Inputs

- Business requirements from stakeholders
- Technical constraints analysis

### E. Output Artifacts

- `docs/REQUIREMENTS.md`
- `CLAUDE.md`

### F. Explicit Non-Goals

- No system design
- No module definitions
- No implementation details
- No technology selection beyond Ollama + GLM-4

### G. Exit Criteria

- All requirements documented
- User confirms requirements freeze
- No further requirement changes allowed

---

## Phase 1: System Design

### A. Phase Objective

Define module boundaries, data models, and interfaces without writing code.

### B. Responsible Agent

**Agent 1 – System Architect Agent**

### C. Ordered Task List

1. Analyze `REQUIREMENTS.md` to identify functional requirements
2. Map requirements to required system modules
3. Define module responsibilities:
   - `workflow/ingest`
   - `workflow/normalize`
   - `workflow/deduplicate`
   - `models/raw_item`
   - `models/library`
   - `processors/*`
   - `agents/extraction_agent`
   - `agents/planner_agent`
   - `workflow/outputs/executive`
   - `workflow/outputs/marketing`
   - `workflow/writer`
   - `utils/llm_utils`
4. Specify RawItem data schema (dataclass)
5. Specify SuccessStory data schema (dataclass)
6. Define function signatures (types only)
7. Specify module inputs and outputs
8. Document what each module MUST NOT do
9. Create data flow diagram
10. Document all data models

### D. Required Inputs

- `docs/REQUIREMENTS.md`
- `CLAUDE.md`

### E. Output Artifacts

- `docs/DESIGN.md`
- Data schemas (documented, not implemented)
- Module specifications
- Data flow diagram

### F. Explicit Non-Goals

- No implementation code
- No directory or file creation
- No library selection
- No performance optimization
- No future-oriented abstractions

### G. Exit Criteria

- `DESIGN.md` complete and consistent
- All modules have clear boundaries
- Data models cover all requirements
- No "future scalability" language
- User review and approval

---

## Phase 2: Scaffolding

### A. Phase Objective

Create a complete project structure with empty but importable Python files.

### B. Responsible Agent

**Agent 2 – Scaffolding Agent**

### C. Ordered Task List

1. Read `DESIGN.md`
2. Create required directories as specified by design
3. Create all `.py` files with module docstrings
4. Add function signatures as TODO comments
5. Use `pass` as placeholder for all functions
6. Create all `__init__.py` files
7. Create `config.yaml` with empty structure
8. Create `requirements.txt`
9. Create placeholder `README.md`
10. Verify imports succeed for representative modules

### D. Required Inputs

- `docs/DESIGN.md`
- Module specifications

### E. Output Artifacts

- Complete directory structure
- All `.py` files with docstrings and TODOs
- `__init__.py` files
- `config.yaml`
- `requirements.txt`
- `README.md`

### F. Explicit Non-Goals

- No business logic
- No functional implementations
- No additional functions beyond design
- No structural decisions beyond `DESIGN.md`

### G. Exit Criteria

- All files exist
- All functions contain TODO + pass
- Import tests succeed
- No premature implementation
- User review and approval

---

## Phase 3: Core Logic

### A. Phase Objective

Implement deterministic, mechanical, non-semantic logic.

### B. Responsible Agent

**Agent 3 – Core Logic Agent**

### C. Ordered Task List

#### Data Models & Discovery

1. Implement RawItem dataclass
2. Add type-only validation
3. Implement mechanical file discovery
4. Implement metadata extraction from paths
5. Verify discovery with test files

#### Data Normalization

6. Implement PDF text extraction
7. Implement email header/body extraction
8. Implement OCR text extraction
9. Implement encoding normalization
10. Verify normalization output equals raw extracted text without filtering or analysis

#### Persistence & Deduplication

11. Implement JSON save/load
12. Verify JSON round-trip preserves all fields
13. Implement string-based similarity checks
14. Implement `merge_stories()` as strict concatenation only
15. Verify no field rewriting or loss

#### CLI Parsing

16. Implement argument parsing only in `run.py`
17. Verify no orchestration or workflow execution exists

### D. Required Inputs

- Phase 2 scaffolding
- `DESIGN.md` specifications

### E. Output Artifacts

- Implemented deterministic logic modules
- `run.py` with argument parsing only

### F. Explicit Non-Goals

- No LLM calls
- No semantic interpretation
- No classification or entity extraction
- No workflow orchestration

### G. Exit Criteria

- Mechanical parsing verified
- JSON persistence lossless
- Deduplication string-based only
- No LLM usage anywhere
- User review and approval

---

## Phase 4: LLM Integration

### A. Phase Objective

Implement all LLM-based extraction and output generation.

### B. Responsible Agent

**Agent 4 – LLM Integration Agent**

### C. Ordered Task List

#### LLM Infrastructure

1. Implement Ollama client wrapper
2. Verify local model connectivity
3. Verify JSON response parsing

#### Prompts & Extraction

4. Write extraction and output prompts (English)
5. Specify JSON schemas and examples
6. Implement extraction agent
7. Validate parsed outputs

#### Planner

8. Implement advisory-only planner
9. Verify workflow does not depend on planner output

#### Output Generation

10. Implement executive output generator
11. Implement marketing output generator

#### Writer

12. Implement markdown writer functions
13. Templates MUST strictly reflect fields defined in SuccessStory schema
14. Writer MUST write only to explicitly provided paths
15. Verify no path inference occurs

### D. Required Inputs

- Implemented core logic
- Data models

### E. Output Artifacts

- LLM utilities
- Prompt templates
- Extraction agent
- Output generators
- Writer module

### F. Explicit Non-Goals

- No workflow control
- No core logic changes
- No deduplication
- No path inference
- No hidden state

### G. Exit Criteria

- LLM calls succeed
- Outputs valid and well-formed
- Planner advisory only
- Writer path-explicit only
- User review and approval

---

## Phase 5: Workflow Integration

### A. Phase Objective

Orchestrate all components with logging and error handling.

### B. Responsible Agent

**Agent 5 – Workflow Integrator Agent**

### C. Ordered Task List

1. Implement weekly workflow orchestration
2. Route CLI modes
3. Wire modules in defined sequence
4. Pass explicit output paths via arguments or config
5. Add step-level logging
6. Add try/except around each stage
7. Ensure per-file failures do not halt workflow

### D. Required Inputs

- Core logic (Phase 3)
- LLM integration (Phase 4)

### E. Output Artifacts

- Fully implemented `run.py`
- Logging and error handling

### F. Explicit Non-Goals

- No content generation
- No markdown formatting
- No prompt modification
- No schema changes
- No refactoring

### G. Exit Criteria

- Weekly workflow runs end-to-end
- Output generation works
- Status mode works
- Failures handled gracefully
- User review and approval

---

## Phase 6: User Acceptance Testing

### A. Phase Objective

Validate system correctness and usability.

### B. Responsible Agent

User

### C. Ordered Task List

1. Install dependencies
2. Run functional tests
3. Verify outputs
4. Test edge cases
5. Record execution time and memory usage for reference only

### D. Required Inputs

- Completed system
- Documentation

### E. Output Artifacts

- Test notes
- Bug reports (if any)
- Acceptance decision

### F. Explicit Non-Goals

- No code changes
- No design changes
- No new features

### G. Exit Criteria

- Offline operation verified
- Outputs correct and reproducible
- Obsidian vault renders correctly
- User acceptance granted

---

## Planner Self-Check

- [x] This output is planning only
- [x] No execution or implementation is included
- [x] No agent authority was expanded
- [x] No phase boundaries were crossed
- [x] All tasks comply with Agent Development Plan v1.2

---

## End of Work Plan

**Status**: ADVISORY ONLY

**Execution requires explicit Phase authorization by User**

**Next Steps**:

1. User reviews this work plan
2. User starts Phase 1 by invoking Claude Code as System Architect Agent
3. Follow each Phase sequentially using Phase-specific prompts from [Agent Development Plan v1.2](DEVELOPMENT_PLAN.md)
4. User reviews and approves at each handoff
5. Enforce agent boundaries
6. Complete Phase 6 for final acceptance

**Remember**: Simple, explicit, deterministic. Trust over cleverness.
