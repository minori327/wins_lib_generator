# Wins Library System – Master Execution Blueprint

**Document Type**: Execution Blueprint
**Version**: 1.0 (Final)
**Based on**: Agent Development Plan v1.2, Complete Project Work Plan (Advisory), REQUIREMENTS.md, CLAUDE.md
**Status**: DEFINITIVE – Does NOT authorize execution

This Blueprint defines the complete agentic workflow.
Execution requires explicit User authorization at each Phase boundary.

---

## Purpose

This document defines:

- Responsibilities of each sub-agent
- Execution order within each Phase
- Cross-Phase agentic workflow
- Mandatory user gating and control points

This document:

- ✅ Defines workflow
- ❌ Does NOT grant execution authority
- ❌ Does NOT allow autonomous phase transitions

---

## Phase 0 – Requirements Freeze

### A. Phase Purpose

Freeze all requirements and establish a stable baseline.

### B. Participating Agents

- User

### C. Sub-Agent Responsibilities

**User**:
- Finalize business requirements
- Document supported input data types
- Define SuccessStory requirements (conceptual)
- Specify constraints (offline, local model)
- Define output requirements
- Specify Obsidian integration (conceptual only)
- Document explicit non-goals

### D. Execution Order

1. User reviews business requirements
2. User documents requirements in REQUIREMENTS.md
3. User creates CLAUDE.md
4. User explicitly confirms requirements freeze

### E. Inputs

- Business requirements
- Technical constraints

### F. Artifacts

- `docs/REQUIREMENTS.md`
- `CLAUDE.md`

### G. Explicit Phase Boundaries

**MUST NOT**:
- Design system architecture
- Define modules or schemas
- Select technologies (beyond Ollama + GLM-4)

**CANNOT assume**:
- User approval
- Complete edge-case coverage

### H. Completion Conditions

- REQUIREMENTS.md complete
- CLAUDE.md complete
- User explicitly approves Phase 0 completion

---

## Phase 1 – System Design

### A. Phase Purpose

Define system design without implementation.

### B. Participating Agents

- Agent 1 – System Architect
- User (approval only)

### C. Sub-Agent Responsibilities

**Agent 1**:
- Analyze REQUIREMENTS.md
- Map requirements to modules
- Define module boundaries and responsibilities
- Specify what each module MUST NOT do
- Define RawItem schema (dataclass structure)
- Define SuccessStory schema (dataclass structure)
- Define function signatures (types only)
- Specify module inputs/outputs
- Create data flow diagram
- Produce DESIGN.md

**User**:
- Review DESIGN.md
- Approve or request revision

### D. Execution Order

1. User authorizes Phase 1
2. Agent 1 produces DESIGN.md
3. Agent 1 stops
4. User reviews and approves/rejects

### E. Inputs

- REQUIREMENTS.md
- CLAUDE.md

### F. Artifacts

- `docs/DESIGN.md`
- Data schemas (documented)
- Module specifications
- Data flow diagram

### G. Explicit Phase Boundaries

**MUST NOT**:
- Write code
- Create files or directories
- Choose libraries
- Optimize performance
- Add future-oriented abstractions

### H. Completion Conditions

- DESIGN.md complete and consistent
- Clear module boundaries
- User approval required to proceed

---

## Phase 2 – Scaffolding

### A. Phase Purpose

Create empty, importable project structure.

### B. Participating Agents

- Agent 2 – Scaffolding
- User (approval only)

### C. Sub-Agent Responsibilities

**Agent 2**:
- Read DESIGN.md
- Create directories strictly derived from module specifications
- Create all .py files
- Add module docstrings
- Add TODOs and pass
- Create __init__.py
- Create config placeholders
- Verify imports

**User**:
- Review structure
- Approve or request revision

### D. Execution Order

1. User authorizes Phase 2
2. Agent 2 scaffolds project
3. Agent 2 stops
4. User reviews and approves

### E. Inputs

- Approved DESIGN.md

### F. Artifacts

- Directory structure
- Empty .py files
- Config placeholders

### G. Explicit Phase Boundaries

**MUST NOT**:
- Implement logic
- Add new functions
- Modify design

**Directory structure MUST**:
- Be derived strictly from module specifications
- NOT be inferred or invented

### H. Completion Conditions

- Import tests pass
- No premature implementation
- User approval required

---

## Phase 3 – Core Logic

### A. Phase Purpose

Implement deterministic, non-semantic logic only.

### B. Participating Agents

- Agent 3 – Core Logic
- User (approval only)

### C. Sub-Agent Responsibilities

**Agent 3**:
- Implement RawItem dataclass
- Implement mechanical file discovery
- Implement mechanical text extraction (PDF, email, OCR)
- Implement JSON persistence
- Implement string-based deduplication
- Implement CLI argument parsing ONLY

**User**:
- Review logic
- Verify no semantic interpretation

### D. Execution Order

1. User authorizes Phase 3
2. Agent 3 implements logic
3. Agent 3 stops
4. User reviews and approves

### E. Inputs

- Phase 2 scaffolding
- DESIGN.md

### F. Artifacts

- Deterministic logic modules
- run.py (CLI parsing only)

### G. Explicit Phase Boundaries

**MUST NOT**:
- Call LLMs
- Interpret semantics
- Add workflow orchestration

**CLI arguments MUST**:
- Be limited strictly to those defined in DESIGN.md
- NOT introduce additional flags or modes

### H. Completion Conditions

- Lossless parsing verified
- Deduplication purely string-based
- No LLM usage
- User approval required

---

## Phase 4 – LLM Integration

### A. Phase Purpose

Implement all LLM-based behavior.

### B. Participating Agents

- Agent 4 – LLM Integration
- User (approval only)

### C. Sub-Agent Responsibilities

**Agent 4**:
- Implement Ollama wrapper
- Write prompts (English, JSON schema, examples)
- Implement extraction agent
- Implement advisory-only planner
- Implement output generators
- Implement writer modules

**Writer constraints**:
- MUST write only to provided paths
- MUST NOT infer paths or structure

**Templates MUST**:
- Strictly reflect SuccessStory schema
- NOT add, remove, rename, reorder, or infer fields

**User**:
- Review prompts
- Approve outputs

### D. Execution Order

1. User authorizes Phase 4
2. Agent 4 implements LLM modules
3. Agent 4 stops
4. User reviews and approves

### E. Inputs

- Phase 3 logic
- Data models

### F. Artifacts

- LLM utilities
- Prompts
- Output generators
- Writer

### G. Explicit Phase Boundaries

**MUST NOT**:
- Control workflow
- Modify core logic
- Infer storage structure

### H. Completion Conditions

- Valid JSON outputs
- Planner advisory only
- User approval required

---

## Phase 5 – Workflow Integration

### A. Phase Purpose

Connect all components deterministically.

### B. Participating Agents

- Agent 5 – Workflow Integrator
- User (approval only)

### C. Sub-Agent Responsibilities

**Agent 5**:
- Implement orchestration
- Route CLI modes
- Pass explicit output paths
- Add logging and error handling

**User**:
- Test workflows
- Approve integration

### D. Execution Order

1. User authorizes Phase 5
2. Agent 5 integrates workflow
3. Agent 5 stops
4. User tests and approves

### E. Inputs

- Phase 3 + Phase 4 outputs

### F. Artifacts

- Complete run.py

### G. Explicit Phase Boundaries

**MUST NOT**:
- Generate content
- Modify prompts
- Refactor logic

### H. Completion Conditions

- Workflows run end-to-end
- Logs clear
- User approval required

---

## Phase 6 – User Acceptance Testing

### A. Phase Purpose

Validate correctness and reproducibility.

### B. Participating Agents

- User
- Claude Code (tooling assistance under direct User control, not an autonomous agent)

### C. Completion Conditions

- Offline operation verified
- Outputs correct
- Reproducibility confirmed
- User grants final acceptance

---

## Cross-Phase Workflow Summary

```
User → Agent 1 → User → Agent 2 → User → Agent 3 → User
     → Agent 4 → User → Agent 5 → User → Acceptance
```

- No agent-to-agent autonomy
- All transitions gated by User

---

## Blueprint Self-Check

- [x] No execution authority granted
- [x] No agent autonomy introduced
- [x] Phase gating explicit
- [x] Agent boundaries match v1.2
- [x] User approval required at all boundaries

---

## End of Blueprint

**Status**: FINAL

**Execution requires explicit User authorization per Phase**
