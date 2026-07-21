# Project Goal

This repository defines a V1.0 Codex skill for analyzing user feedback and extracting traceable user needs.

The repository must help future maintainers:
- keep the skill evidence-based;
- distinguish needs from solutions and non-need issues;
- preserve traceability from conclusions back to raw evidence;
- keep the scope limited to user-need analysis, not full product planning.

# Repository Structure and Directory Responsibilities

- `SKILL.md`: executable skill entry protocol, workflow, inputs, outputs, and hard guardrails.
- `AGENTS.md`: repository maintenance rules for Codex and other agents.
- `IMPLEMENTATION_PLAN.md`: build roadmap and V1.0 boundary record.
- `references/`: method rules, classification logic, validation criteria, evidence-strength rules, and prioritization rules.
- `templates/`: output structures for evidence tables, need cards, ranking views, and final reports.
- `scripts/`: validation utilities for inputs, evidence links, and report structure.
- `examples/`: fictional sample cases only.
- `tests/`: structured cases that verify classification, validity judgment, and ranking behavior.

# Modification Principles

- Keep V1.0 narrow and executable.
- Prefer explicit rules over broad theory.
- Update the smallest correct surface first.
- Preserve traceability: every rule change should still allow outputs to point back to raw evidence IDs.
- Preserve separations:
  - facts vs interpretation;
  - behavior vs attitude;
  - need vs solution;
  - product issue vs bug/usability/operations/service/training issue.
- If a rule becomes impossible to test later, rewrite it to be checkable.

# Prohibited Actions

- Do not turn the skill into one giant prompt.
- Do not bypass evidence traceability.
- Do not bypass counterexample checking.
- Do not expand V1.0 into roadmap generation, solution design, market sizing, or automated product planning.
- Do not submit real user privacy data to the repository.
- Do not commit recordings, real names, email addresses, phone numbers, account identifiers, or company-confidential material.
- Do not claim unsupported percentages, benchmarks, or population-level findings.
- Do not merge segment-specific needs into one generic need without evidence.
- Do not treat internal retellings as equivalent to direct user evidence.

# Documentation Style

- Write core documents in clear, professional English.
- A key term may include a Chinese gloss on first mention only when helpful.
- Prefer concrete rules, checklists, and examples.
- Avoid slogans, inflated capability claims, and framework-name dumping.
- Use fictional examples only.
- Keep headings stable so future templates and scripts can target them reliably.

# Where New Rules Must Go

- Evidence-type definitions belong in `references/evidence-taxonomy.md`.
- Need vs solution and issue-boundary rules belong in `references/need-vs-solution.md`.
- Requirement validity logic belongs in `references/requirement-validation.md`.
- Evidence hierarchy or confidence rules belong in `references/evidence-strength.md`.
- Demand-side ranking rules belong in `references/prioritization-rules.md`.
- Workflow and guardrails belong in `SKILL.md`.
- Build sequencing or scope changes belong in `IMPLEMENTATION_PLAN.md`.

# If Output Structure Changes

When changing output fields, order, or labels, update all affected templates and tests together.

At minimum, review and update:
- `templates/evidence-table.md`
- `templates/user-need-card.md`
- `templates/needs-ranking.md`
- `templates/final-report.md`
- `tests/normal-cases.json`
- `tests/insufficient-evidence-cases.json`
- `tests/trap-cases.json`

# If Judgment Logic Changes

When changing classification logic, validity conditions, evidence weighting, or ranking rules, add or update tests that cover:
- correct evidence typing;
- need vs solution separation;
- bug/usability/operations/service/training classification boundaries;
- `成立 (valid)` / `条件成立 (conditionally valid)` / `需求假设 (need hypothesis)` / `证据不足 (insufficient evidence)` / `不成立或不属于本产品范围 (not valid or out of product scope)` outcomes;
- counterexample handling;
- segment-difference handling;
- conflicting behavior vs verbal-report handling;
- secondhand-evidence downgrading;
- prioritization edge cases where evidence is weak but pain is high.

# Privacy and Sensitive Data Rules

- Never commit raw recordings.
- Never commit real names, direct quotes with identity markers, email addresses, phone numbers, street addresses, or company secrets.
- If example data is needed, synthesize fictional data.
- If a file accidentally contains sensitive data, stop and remove or redact it before any commit.

# Scope Guardrails

- Do not simplify the skill into a single prompt blob.
- Do not remove the fixed workflow from `SKILL.md`.
- Do not remove the requirement for counterexample checking.
- Do not remove the requirement for evidence IDs.
- Do not widen V1.0 without explicitly updating the implementation plan.

# Required Checks Before Finishing a Change

Before declaring a change complete, run and review:
- `find . -maxdepth 3 -type f | sort`
- `git diff --check`
- `git status --short`

Also confirm manually:
- only intended files changed;
- links or file references point to real repository paths;
- terminology is consistent across `SKILL.md` and `references/`;
- no private or real user data was added.
