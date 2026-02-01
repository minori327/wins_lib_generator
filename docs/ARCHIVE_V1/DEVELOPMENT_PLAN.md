# Wins Library System – Agent Development Plan

## Agent-Based Development Workflow

**Document Version**: 1.2 (Final – Authority Hardened)
**Date**: 2026-02-01
**Based on**: [REQUIREMENTS.md](REQUIREMENTS.md) & [CLAUDE.md](CLAUDE.md)
**Owner**: User

**Document Status**: ✅ FINAL – Ready for Phase 1

---

## Table of Contents

1. [Agent Development Philosophy](#1-agent-development-philosophy)
2. [Agent Role Definitions](#2-agent-role-definitions)
3. [Phase-by-Phase Development Plan](#3-phase-by-phase-development-plan)
4. [Handoff Protocols](#4-handoff-protocols)
5. [User Responsibilities](#5-user-responsibilities)
6. [Success Criteria per Phase](#6-success-criteria-per-phase)
7. [Enforcement Rules](#7-enforcement-rules)
8. [Phase Timeline Estimate](#8-phase-timeline-estimate)
9. [Quick Reference for Claude Code Sessions](#9-quick-reference-for-claude-code-sessions)
10. [Important Reminders](#10-important-reminders)
11. [Troubleshooting Guide](#11-troubleshooting-guide)

---

## 1. Agent Development Philosophy

### 1.1 Core Principles

| Principle | Explanation | Why |
|-----------|-------------|-----|
| **Single Agent = Single Responsibility** | Each Agent owns exactly one dimension | Prevents scope creep |
| **Upstream Decides, Downstream Executes** | Design → Scaffolding → Logic → Integration | Prevents circular refactoring |
| **Design Agent Doesn't Write Code** | Thinking ≠ Doing | Prevents design drift |
| **Implementation Agent Doesn't Change Requirements** | Specs are binding | Prevents "smart interpretation" |
| **Integrator Agent Enters Last** | Glue comes last | Ensures clean boundaries |
| **Determinism Over Intelligence** | Explicit beats autonomous | Prevents emergent behavior |

### 1.2 Anti-Patterns

❌ **Forbidden**:

- One Agent doing think + design + write + refactor
- Agent 3 optimizing or "improving" design
- Agent 5 fixing interfaces or outputs
- Planner controlling execution
- Any "future scalability" abstractions

✅ **Required**:

- Sequential phases
- Explicit artifacts
- Human approval between phases
- Mechanical transformations only outside LLMs

---

## 2. Agent Role Definitions

### Agent 1: System Architect Agent

**Role**: Architecture & Design Only

#### Authority Boundaries

**MAY**:
- Define module boundaries
- Define data schemas (dataclass / TypedDict)
- Define function signatures with types
- Specify module inputs / outputs
- Specify what modules MUST NOT do

**MUST NOT**:
- Write implementation code
- Choose libraries or frameworks
- Optimize performance
- Add features not in requirements
- Add abstractions for future use

#### Output Artifacts

1. **DESIGN.md**
2. Data schemas
3. Module specs
4. Data flow diagram

---

### Agent 2: Scaffolding Agent

**Role**: Project Structure Setup

#### Authority Boundaries

**MAY**:
- Create directories and files per design
- Add docstrings
- Add TODOs
- Create `__init__.py`

**MUST NOT**:
- Implement logic
- Add new functions
- Modify design
- Make implementation decisions

---

### Agent 3: Core Logic Agent

**Role**: Deterministic, Non-Semantic Logic

#### Authority Boundaries

**MAY**:
- File discovery
- Mechanical parsing (PDF, email headers, OCR)
- Deterministic validation
- String-based deduplication
- JSON serialization
- CLI argument parsing

**MUST NOT**:
- Interpret meaning or intent
- Classify content
- Extract business entities
- Call or design LLMs
- Write prompts
- Orchestrate workflows
- Generate or format content

#### CRITICAL RULE

**If interpretation is required → Defer to Agent 4**

#### Deduplication Constraint (HARD)

`merge_stories()` MUST:
- Concatenate source lists only
- Preserve all fields exactly

**MUST NOT** summarize, rewrite, drop, or reinterpret any field.

---

### Agent 4: LLM Integration Agent

**Role**: LLM Behavior & Content Generation

#### Authority Boundaries

**MAY**:
- Implement Ollama wrapper
- Write prompt templates (English)
- Parse LLM JSON output
- Extract SuccessStory objects
- Generate Executive / Marketing outputs
- Implement Planner Agent (advisory only)
- Implement Writer modules

**MUST NOT**:
- Perform file IO directly
- Control workflow execution
- Modify core logic
- Implement deduplication
- Store hidden state
- Decide file naming conventions
- Infer or create Obsidian vault structures

#### Planner Agent Constraint

**ADVISORY ONLY**
- Safe to ignore
- Output MUST NOT affect execution flow
- May be stub

#### Writer Constraint (HARD)

Writer modules:
- **MUST** write only to paths explicitly provided by Agent 5
- **MUST NOT** infer paths, names, or folder structures

---

### Agent 5: Workflow Integrator Agent

**Role**: Orchestration Only

#### Authority Boundaries

**MAY**:
- Implement `run.py`
- Call Agent 3 & 4 modules
- Control execution order
- Handle errors
- Log progress

**MUST NOT**:
- Generate content
- Format markdown
- Modify prompts
- Change schemas
- Refactor logic
- Write files directly

---

## 3. Phase-by-Phase Development Plan

### Phase 0: Requirements Freeze ✅

**Owner**: User

**No changes allowed afterward.**

---

### Phase 1: System Design (Agent 1)

**Output**: DESIGN.md

- No code
- User approval required

---

### Phase 2: Scaffolding (Agent 2)

- Create all files
- All functions = TODO + pass
- Import tests must pass

---

### Phase 3: Core Logic (Agent 3)

**CRITICAL**:
- All parsing = mechanical + lossless + non-semantic
- No LLM calls
- No orchestration

**run.py in Phase 3 MUST NOT**:
- Import workflow orchestration
- Call business logic
- Execute workflows

---

### Phase 4: LLM Integration (Agent 4)

- Ollama wrapper
- Prompts
- Extraction
- Outputs
- Planner (advisory)
- Writer (path-explicit only)

---

### Phase 5: Workflow Integration (Agent 5)

- Full orchestration
- Logging
- Error handling
- No content generation

---

### Phase 6: User Acceptance Testing

**User validates**:
- Determinism
- Reproducibility
- Output quality
- Error handling

---

## 4. Handoff Protocols

Each phase requires:
- Explicit artifacts
- User approval
- No backward modification

---

## 5. User Responsibilities

- Review each phase
- Approve before proceeding
- Enforce boundaries
- Reject over-engineering

---

## 6. Success Criteria

Each phase has explicit exit conditions.

**No phase may proceed without meeting them.**

---

## 7. Enforcement Rules

### 7.1 Non-Refactoring Rule

**Agents may NOT modify outputs of previous phases.**

Violation → Stop → Report → User decides.

### 7.2 Boundary Violation Protocol

1. Identify violation
2. Report clearly
3. Wait for user decision

### 7.3 Over-Engineering Detection

**Red flags**:
- "future scalability"
- "generic pipeline"
- "framework for later"

**Action**: Remove.

### 7.4 Determinism Verification

**Before completing any phase**:
- No hidden state
- No inference
- File system = truth
- Explicit parameters only

### 7.5 Agent Self-Check Requirement (HARD)

**Before completing any task, each Agent MUST include**:

```markdown
## Agent Self-Check

- [ ] I operated strictly within my Authority Boundaries
- [ ] I did NOT modify artifacts from previous phases
- [ ] I did NOT introduce semantic interpretation beyond my role
- [ ] I did NOT add abstractions for future or speculative use
```

**Failure to include this checklist = violation.**

---

## 8. Phase Timeline Estimate

| Phase | Duration |
|-------|----------|
| Phase 1 | 1–2 hours |
| Phase 2 | ~1 hour |
| Phase 3 | 1–2 days |
| Phase 4 | 1–2 days |
| Phase 5 | ~1 day |
| Phase 6 | 2–3 days |

**Total**: 7–12 days

---

## 9. Quick Reference for Claude Code Sessions

### Starting Phase 1

```
You are the System Architect Agent.

Read REQUIREMENTS.md and create DESIGN.md.

Do NOT write code.
Focus on module boundaries and interfaces.
Do NOT add "future scalability" abstractions.

Complete your work with an Agent Self-Check (Section 7.5).

Output: DESIGN.md with complete system design.
```

### Starting Phase 2

```
You are the Scaffolding Agent.

Read DESIGN.md and create the complete project structure.

Create all .py files with docstrings and TODOs.
Do NOT implement any logic.
Follow DESIGN.md exactly.

Verify: python -c "import workflow.ingest" works.

Complete your work with an Agent Self-Check (Section 7.5).
```

### Starting Phase 3

```
You are the Core Logic Agent.

Implement all deterministic logic:
- File discovery
- MECHANICAL data normalization only
- JSON persistence
- STRING-BASED deduplication only
- CLI parsing

CRITICAL:
- Do NOT write LLM prompts or call Ollama
- Do NOT interpret text semantics
- Do NOT classify content
- All parsing must be mechanical and lossless
- run.py MUST contain argument parsing ONLY

Follow CLAUDE.md principles.

Complete your work with an Agent Self-Check (Section 7.5).
```

### Starting Phase 4

```
You are the LLM Integration Agent.

Implement all LLM functionality:
- Ollama wrapper
- Prompt templates (in English)
- Extraction agent
- Output agents
- Planner agent (ADVISORY ONLY)
- Writer agent (markdown rendering, path-explicit only)

Do NOT modify core logic from Phase 3.
All prompts must be readable and specify JSON schema.

IMPORTANT:
- Planner is advisory only, must not control execution flow
- Writer modules MUST NOT infer paths or structures

Complete your work with an Agent Self-Check (Section 7.5).
```

### Starting Phase 5

```
You are the Workflow Integrator Agent.

Connect all modules in run.py:
- Weekly workflow
- Output generation
- Status check
- Error handling
- Logging

CRITICAL:
- Do NOT refactor existing modules
- Do NOT generate content (use Agent 4 modules)
- Do NOT format markdown (use Agent 4 writer)
- Make sure all steps are logged clearly

Orchestration only, no content generation.

Complete your work with an Agent Self-Check (Section 7.5).
```

### Starting Phase 6

```
You are assisting with User Acceptance Testing.

Help the user:
- Test all CLI commands
- Verify error handling
- Check Obsidian integration
- Test edge cases
- Verify all acceptance criteria

Report any issues found.
```

---

## 10. Important Reminders

### For Claude Code

- ✅ One Agent role per session
- ✅ No refactors
- ✅ No cleverness
- ✅ Violations must be reported
- ✅ Always include Agent Self-Check

### For User

- ✅ Review each phase
- ✅ Approve explicitly
- ✅ Enforce boundaries
- ✅ Reject over-engineering

---

## 11. Troubleshooting Guide

### If blocked

- Simplify
- Remove autonomy
- Ask user
- **Never hack around design**

---

## ✅ End of Document

**Version**: 1.2 (Final – Authority Hardened)
**Status**: FINAL
**Purpose**: Hard authority boundary enforcement for AI Coding Agents

**Next Steps**:

1. User reviews this final plan
2. User starts Phase 1 by invoking Claude Code as System Architect
3. Follow each Phase sequentially
4. User reviews and approves at each handoff
5. Enforce agent boundaries
6. Complete Phase 6 for final acceptance

**Remember**: Simple, explicit, deterministic. Trust over cleverness.
