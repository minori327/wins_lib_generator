# Phase 6 Review Checklist

**Purpose**: Review checklist for Phase 6 (Output Generation & Distribution Layer)
**Version**: 1.0
**Date**: 2026-02-01

---

## Overview

This checklist is used to validate that the Phase 6 output (Output Generation & Distribution Layer) meets all requirements and follows the constraints defined in MASTER_EXECUTION_BLUEPRINT.md and DESIGN.md.

**Critical Context**: Phase 6 is the FINAL phase where stories are formatted and distributed. Phase 6 MUST NOT alter content, only format it. Formatting is distinct from content modification.

**Review Method**: ✅ / ❌ / N/A
**Rule**: Any Hard Stop (🟥) failure → Phase 6 REJECTED

---

## Checklist Items

### 🟥 1️⃣ Phase Boundary Integrity (Hard Stop)

**Checks**:
- ⬜ Phase 6 does NOT modify Phase 3 code
- ⬜ Phase 6 does NOT modify Phase 4 code
- ⬜ Phase 6 does NOT modify Phase 5 code
- ⬜ Phase 6 does NOT introduce business logic
- ⬜ Phase 6 does NOT filter, merge, delete, or rank stories
- ⬜ Phase 6 consumes Phase 5 outputs as immutable input

**Why this matters**: Phase 6 is purely cosmetic/formatting. Any content modification invalidates the entire pipeline.

**Failure Message**:
```
❌ Phase Boundary: Phase 6 modified earlier phases or introduced business logic.
                  Phase 6 MUST:
                  - NOT modify Phase 3, 4, or 5 code
                  - NOT introduce business logic (filtering, merging, ranking)
                  - Treat Phase 5 outputs as immutable input
```

**Verification**: Git diff against Phase 5, check for filtering/merging logic, verify input immutability

---

### 🟥 2️⃣ Content Immutability (Hard Stop)

**Checks**:
- ⬜ Story text is NOT altered (no rewriting, paraphrasing, summarizing)
- ⬜ Customer names are preserved exactly from Phase 5
- ⬜ Metrics and confidence values are preserved exactly
- ⬜ No inferred or synthesized data is added
- ⬜ Empty fields remain empty (not filled with "N/A" or inferred content)
- ⬜ Only formatting changes are allowed (Markdown, HTML, layout)

**Why this matters**: Phase 6 must be a pure formatting layer. Any content change bypasses all prior validation and governance.

**Failure Message**:
```
❌ Content Immutability: Phase 6 modified story content.
                        Phase 6 MUST:
                        - NOT rewrite or paraphrase story text
                        - Preserve customer names exactly
                        - Preserve metrics exactly
                        - NOT infer or synthesize data
                        - Leave empty fields empty
                        - Only apply formatting (Markdown, layout, etc.)
```

**Verification**: Compare Phase 5 outputs to Phase 6 outputs character-by-character for content fields

---

### 🟥 3️⃣ Template-Driven Output (Hard Stop)

**Checks**:
- ⬜ All formatting lives in template files (`.md`, `.jinja2`, etc.)
- ⬜ Templates are versioned (e.g., `v1.0`, `v1.1`)
- ⬜ Templates have human-readable names (e.g., `executive_summary`, `marketing_one_pager`)
- ⬜ Switching templates does NOT require code changes
- ⬜ No hardcoded layout logic in agents or workflow code
- ⬜ Templates are stored in `templates/` directory

**Why this matters**: Templates enable non-technical users to modify formatting without touching code. Hardcoded formatting is inflexible and error-prone.

**Failure Message**:
```
❌ Template-Driven Output: Formatting is hardcoded in code.
                          Phase 6 MUST:
                          - Store all formatting in template files
                          - Version templates
                          - Name templates descriptively
                          - Allow template switching without code changes
                          - NOT hardcode layout logic
                          - Store templates in templates/ directory
```

**Verification**: Check `templates/` directory, verify all formatting uses templates, search for hardcoded layout in code

---

### 🟥 4️⃣ Determinism & Reproducibility (Hard Stop)

**Checks**:
- ⬜ Same input + same template ⇒ same output (byte-for-byte)
- ⬜ No randomness in output generation
- ⬜ No time-dependent formatting (e.g., "generated 2 seconds ago")
- ⬜ Output generation can be re-run identically
- ⬜ No dependence on external state (e.g., current directory, environment variables)
- ⬜ Timestamps are either from source data or explicitly provided (not "now")

**Why this matters**: Outputs must be reproducible for audit and debugging. Non-deterministic outputs are untrustworthy.

**Failure Message**:
```
❌ Determinism: Output generation is non-deterministic.
               Phase 6 MUST:
               - Produce identical output for same input + template
               - NOT use randomness
               - NOT use time-dependent formatting
               - Be reproducible on re-run
               - NOT depend on external state
               - Use source timestamps or explicitly provided ones
```

**Verification**: Run output generation twice with same inputs, compare outputs byte-for-byte

---

### 🟥 5️⃣ Output Auditability (Hard Stop)

**Checks**:
- ⬜ Every output file records metadata:
  - `story_ids` (list of SuccessStory IDs included)
  - `template_name` (e.g., `executive_summary`)
  - `template_version` (e.g., `v1.0`)
  - `generated_at` (timestamp of generation)
  - `output_path` (absolute path to output file)
- ⬜ Output metadata is stored in a machine-readable format (JSON or YAML)
- ⬜ Output can be traced back to Phase 5 decisions (via `story_ids`)
- ⬜ Metadata is stored alongside outputs or in a centralized registry
- ⬜ Metadata is human-readable (plain text JSON/YAML, not binary)

**Why this matters**: Audit trails are essential for compliance, debugging, and understanding how outputs were produced.

**Failure Message**:
```
❌ Auditability: Outputs lack metadata.
                Every output MUST record:
                - story_ids (traces to Phase 5)
                - template_name + version
                - generated_at timestamp
                - output_path
                - In machine-readable, human-accessible format
```

**Verification**: Check output directory for metadata files, verify all required fields present

---

### 🟨 6️⃣ Output Configuration & Extensibility (Strong Requirement)

**Checks**:
- ⬜ Output destinations are configurable (filesystem, S3, API, email, etc.)
- ⬜ Output formats are extendable without refactoring
- ⬜ Templates are reusable across agents
- ⬜ Adding a new output format does NOT require code changes (only new template)
- ⬜ Output paths are configurable (e.g., `vault/40_outputs/` vs custom path)
- ⬜ Multiple outputs can be generated from same input (e.g., both executive and marketing)

**Why this matters**: Distribution requirements evolve. Configurable outputs make the system adaptable without engineering work.

**Failure Message**:
```
⚠️ Configuration: Outputs are hardcoded or inflexible.
                 Phase 6 SHOULD:
                 - Support configurable output destinations
                 - Allow extending output formats without refactoring
                 - Reuse templates across agents
                 - Add new formats via templates only (no code changes)
                 - Configure output paths
                 - Support multiple outputs from same input
```

**Allowed**: 1 item may fail, but must explain why

**Verification**: Modify output destination in config, verify works; add new template, verify no code changes needed

---

### 🟨 7️⃣ Distribution Safety (Strong Requirement)

**Checks**:
- ⬜ No output file is overwritten without explicit config
- ⬜ `--dry-run` or `--preview` mode exists and shows what will be written
- ⬜ Failure in one output does NOT corrupt other outputs
- ⬜ Output writing is atomic (either full success or no write)
- ⬜ Existing outputs are protected unless `--overwrite` flag is set
- ⬜ Network/external distribution failures are logged and do NOT crash the system

**Why this matters**: Distribution is the last step. Corruption here ruins all prior work. Safety mechanisms prevent data loss.

**Failure Message**:
```
⚠️ Distribution Safety: Output writing lacks safety guarantees.
                        Phase 6 SHOULD:
                        - NOT overwrite without explicit config
                        - Support --dry-run / --preview mode
                        - Isolate failures (one failure ≠ all corrupted)
                        - Write atomically (all or nothing)
                        - Protect existing outputs
                        - Handle distribution failures gracefully
```

**Allowed**: 1 item may fail, but must explain why

**Verification**: Test `--dry-run`, test overwrite protection, test failure isolation

---

### 🟩 8️⃣ Presentation Quality (Optional but Recommended)

**Checks**:
- ⬜ Outputs are professionally formatted (consistent spacing, alignment)
- ⬜ Headings and sections are consistent across all outputs
- ⬜ Metrics are presented clearly (tables, bullet points, highlighted)
- ⬜ No template placeholders left unfilled (e.g., `{{customer}}`)
- ⬜ No truncation or cutoff in outputs
- ⬜ Markdown/HTML renders correctly without syntax errors

**Why this matters**: User-facing outputs must be professional. Poor formatting undermines trust and requires manual cleanup.

**Failure Message**:
```
⚠️ Presentation Quality: Outputs have formatting issues.
                         Phase 6 SHOULD produce:
                         - Professional formatting
                         - Consistent headings and sections
                         - Clear metric presentation
                         - No unfilled placeholders
                         - No truncation
                         - Valid Markdown/HTML
```

**Status**: Recommended for v1, but not blocking

**Verification**: Spot-check 20 outputs, render Markdown, check for formatting issues

---

### 🟩 9️⃣ Batch & Bundle Support (Optional but Recommended)

**Checks**:
- ⬜ Multiple stories can be combined into single output (e.g., weekly summary)
- ⬜ Bundled reports are supported (e.g., all stories for one customer)
- ⬜ Batch generation is efficient (not O(n) template instantiations)
- ⬜ Batch outputs record all included story IDs
- ⬜ Batch templates exist (e.g., `weekly_summary.md`, `customer_digest.md`)

**Why this matters**: Users often need aggregated views. Batch/bundle support reduces manual work.

**Failure Message**:
```
⚠️ Batch Support: Batch or bundle outputs are not supported.
                 Phase 6 SHOULD:
                 - Support multiple stories per output
                 - Support bundled reports (e.g., by customer)
                 - Generate batches efficiently
                 - Record all story IDs in batch metadata
                 - Provide batch templates
```

**Status**: Recommended for v1, but not blocking

**Verification**: Generate batch output, verify efficiency, check metadata

---

### 🟩 🔟 Human Review Hooks (Optional but Recommended)

**Checks**:
- ⬜ Human can preview output before publishing/distributing
- ⬜ Approval step exists before external distribution (S3, API, email)
- ⬜ Human edits to previewed output are preserved
- ⬜ Approval can be done via CLI flag or config file
- ⬜ Rejected outputs are NOT distributed but are saved for review

**Why this matters**: Final outputs are user-facing. Human review prevents embarrassing errors from reaching audiences.

**Failure Message**:
```
⚠️ Human Review: No human review hooks before distribution.
                Phase 6 SHOULD:
                - Support preview before distribution
                - Require approval for external distribution
                - Preserve human edits
                - Allow approval via CLI or config
                - Save rejected outputs for review
```

**Status**: Recommended for v1, but not blocking

**Verification**: Test preview workflow, test approval workflow, verify rejected outputs saved

---

## Phase 6 Final Decision

### Review Result

**Phase 6 Review Result**: _____ ACCEPTED / REJECTED _____

### Critical Findings

If REJECTED, list ALL Hard Stop failures:

1. ________________________________________________________________
2. ________________________________________________________________
3. ________________________________________________________________

### Strong Requirement Findings

List any Strong Requirement failures (allow max 2):

1. ________________________________________________________________
2. ________________________________________________________________

### Optional Findings

List any Optional failures (for informational purposes):

1. ________________________________________________________________
2. ________________________________________________________________

### Approval

**Approved By**:
- Human Reviewer: _______________________ Date: ________
- AI Reviewer (optional): _______________________ Date: ________

**Conditions** (if any):
________________________________________________

---

## Review Process

### Automated Execution

```bash
./wins phase review 6
```

### Automated Checks Run

1. **Check 1**: Phase boundary integrity (no modifications to Phases 3-5)
2. **Check 2**: Content immutability (no content changes)
3. **Check 3**: Template-driven output (all formatting in templates)
4. **Check 4**: Determinism & reproducibility (same input → same output)
5. **Check 5**: Output auditability (metadata recorded)
6. **Check 6**: Output configuration & extensibility
7. **Check 7**: Distribution safety
8. **Check 8**: Presentation quality
9. **Check 9**: Batch & bundle support
10. **Check 10**: Human review hooks

### Manual Review Steps

After automated checks pass, manually review:

1. **Content Preservation**: Compare 10 Phase 5 outputs to Phase 6 outputs, verify no content changes
2. **Template Quality**: Review all templates, are they well-formatted and professional?
3. **Metadata Completeness**: Check metadata files, are all required fields present?
4. **Reproducibility**: Run output generation twice, compare outputs byte-for-byte
5. **Safety Features**: Test `--dry-run`, `--preview`, and overwrite protection
6. **Distribution Test**: Generate outputs to different destinations (filesystem, etc.)
7. **Batch Outputs**: Generate a weekly summary or customer digest, verify correctness

---

## Exit Criteria

Phase 6 is considered complete when:

- ✅ ALL Hard Stop (🟥) checks pass (no exceptions)
- ✅ At most 2 Strong Requirement (🟨) checks fail (with explanation)
- ✅ User has manually reviewed output quality
- ✅ User has verified content immutability
- ✅ User has tested safety features (dry-run, preview)
- ✅ User explicitly approves Phase 6 completion

---

## Next Steps After Approval

Once Phase 6 is approved:

```bash
# Phase 6 is the final phase
./wins phase complete 6

# Generate final outputs
./wins generate --country US --month 2026-01
```

The full pipeline is now complete:
- Phase 3: Mechanical processing (file discovery, text extraction)
- Phase 4: Semantic extraction (LLM-based story extraction)
- Phase 5: Business logic (ranking, merging, curation)
- Phase 6: Output generation (formatting, distribution)

---

## Historical Context

### Why This Checklist Exists

1. **Prevent Content Drift**: Phase 6 must only format, not modify content
2. **Ensure Template-Driven Architecture**: Formatting must be user-editable without code
3. **Maintain Reproducibility**: Outputs must be reproducible for audit
4. **Enable Distribution Safety**: Last step requires extra safeguards
5. **Support Extensibility**: Output formats evolve; templates enable this

### Relationship to DESIGN.md

| DESIGN.md Section | Checklist Item |
|-------------------|----------------|
| Output Generation Layer | Template-Driven Output |
| Template Specifications | Template-Driven Output |
| Output Formats | Output Configuration |
| Distribution Logic | Distribution Safety |

### Relationship to MASTER_EXECUTION_BLUEPRINT.md

| Blueprint Section | Checklist Item |
|-------------------|----------------|
| Phase 6: Output Generation | Template-Driven Output |
| Phase 6: No Content Changes | Content Immutability |
| Phase 6: Determinism | Determinism & Reproducibility |
| Phase 6: Metadata | Output Auditability |
| Phase 6: Distribution | Distribution Safety |

---

## Critical Differences from Phase 5

| Aspect | Phase 5 | Phase 6 |
|--------|---------|---------|
| Primary Purpose | Business decisions (rank, merge, delete) | Formatting and distribution |
| Content Changes | Allowed (merging, deletion) | FORBIDDEN (formatting only) |
| Business Logic | Central to Phase 5 | NOT ALLOWED |
| Template Use | N/A | REQUIRED |
| Human Review | Required for destructive ops | Optional (preview before publish) |
| Risk Type | Data loss | Output corruption |
| Reversibility | Difficult (merges/deletes) | Easy (regenerate outputs) |

---

## Formatting vs Content Change

### ✅ ALLOWED (Formatting)
- Converting plain text to Markdown
- Adding headings, sections, bullet points
- Applying HTML/CSS styling
- Layout changes (tables, columns)
- Adding metadata headers/footers
- Template-based structure

### ❌ FORBIDDEN (Content Change)
- Rewriting story text
- Paraphrasing or summarizing
- Changing customer names
- Modifying metrics
- Inferring missing data
- Filling empty fields with inferred content
- Changing confidence values
- Altering timestamps (unless from source)

**Key Principle**: If the change affects what the story SAYS, it's forbidden. If the change only affects how the story LOOKS, it's allowed.

---

## Checklist Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial version for Phase 6 |

---

## End of Document

**Maintained by**: `wins` command
**Last Updated**: 2026-02-01
**Status**: Active - Used by `./wins phase review 6`
