"""
Governance Test Suite for Iteration 2

This test suite enforces Human Primacy constraints and prevents
regression to autonomous v1 behaviors.

These tests represent a binding governance contract between the
development team and the system's human users.

Violations of these tests indicate critical governance failures
and must be addressed immediately before any feature work.

Test Categories:
- Capability Denial: Forbidden capabilities cannot exist
- CLI Authority: Single entry point, three commands only
- Human Primacy: AI never makes final decisions
- Ownership & Non-Mutation: Human decisions are never overwritten
- Mechanical Invariants: Only technical filtering allowed
- Configuration Safety: No config enables autonomous behavior
- Determinism & Traceability: All processing is observable

Reference: docs/DEVELOPMENT_PLAN_v2_FINAL.md
Reference: docs/REQUIREMENTS_v2.md
Reference: docs/VALIDATION_CHECKLIST.md
Reference: Post-Remediation Audit Report (2026-02-01)
"""

__version__ = "2.0"
__governance_level__ = "STRICT"
