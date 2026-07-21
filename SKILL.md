---
name: user-needs-analyzer
description: Analyze user interviews, support tickets, survey free-text answers, and product feedback to extract real user needs; distinguish needs, pain points, feature suggestions, bugs, usability issues, operations issues, and service issues; judge requirement validity and evidence strength; and output traceable need cards and need-side prioritization.
---

# Purpose

`user-needs-analyzer` is a V1.0 skill for turning raw feedback into traceable user-need conclusions.

Its job is to:
- analyze user interviews, support tickets, survey open-text answers, feature requests, and mixed feedback sets;
- extract user needs rather than jump directly to solutions;
- separate needs, pain points, goals, bugs, usability issues, operations issues, service issues, and training issues;
- judge requirement validity and evidence strength;
- produce outputs that can be traced back to raw evidence IDs.

This skill does not prove market size, decide implementation scope, or generate a final product roadmap.

# When to use

Use this skill when the task is to:
- interpret raw user feedback or research material;
- determine whether a reported pattern is a real user need;
- distinguish a proposed feature from an underlying need;
- compare several candidate needs on the demand side;
- prepare structured need cards, ranked needs, or an evidence-based summary.

# When not to use

Do not use this skill when the task is to:
- write a product requirements document or feature specification directly;
- prioritize engineering bugs by severity;
- design a UI, write copy, or propose detailed solutions first;
- estimate TAM, market share, or business revenue impact;
- summarize feedback without evidence tracing;
- analyze only internal opinions with no user-facing material.

If the input is mainly about outages, defects, internal process issues, billing operations, or support quality, classify first instead of forcing everything into a product need.

# Required and Optional Inputs

## Required inputs

- Raw source materials with stable source IDs.
  - Examples: interview notes, verbatim quotes, support tickets, survey responses, product data snapshots, observed session notes.
- Basic source context.
  - At minimum: source type, collection date or period, and user or segment label if available.

## Optional inputs

- Product area or workflow scope.
- Known target segment definitions.
- Existing feature context.
- Previous analysis artifacts.
- Business context that explains why the analysis is being requested.

# Missing-Input Handling

If required inputs are missing, do not invent user psychology or hidden motivations.

Handle gaps as follows:
- Missing raw source IDs: stop and request IDs before producing traceable conclusions.
- Missing concrete scenario: output only `需求假设 / need_hypothesis` or `证据不足 / insufficient_evidence`.
- Missing segment context: continue, but mark segment conclusions as uncertain.
- Only one feedback item: treat it as a signal, not as a common need.
- Only internal retellings: treat them as low-grade secondhand evidence.
- Missing negative or counter evidence: do not conclude `成立 / validated`.

# Complete Workflow

The workflow must follow this fixed order:

Input check
→ Raw material normalization
→ Evidence unit construction
→ Evidence classification
→ Reconstruction of scenario, goal, barrier, workaround, and cost
→ Separation of need and solution
→ Similar-need clustering
→ Requirement validity judgment
→ Evidence strength evaluation
→ Active counterexample search
→ User-segment difference check
→ Need-side prioritization
→ Report output
→ Structure and evidence traceability validation

## Stage instructions

### 1. Input check
- Confirm source IDs exist.
- Confirm each source has at least minimal context.
- Mark any missing fields before analysis.

### 2. Raw material normalization
- Convert mixed inputs into a consistent record structure.
- Keep facts, quotes, and analyst notes in separate fields.
- Do not merge different users into one composite voice.

### 3. Evidence unit construction
- Split materials into atomic evidence units.
- Each unit must have one evidence type only.
- `What the user did` and `what the user said` must not share the same evidence field.
- Observed facts and analyst explanations must be separated.

### 4. Evidence classification
- Assign one primary evidence type using `references/evidence-taxonomy.md`.
- Distinguish product need signals from bugs, usability issues, operations issues, service issues, and training issues.

### 5. Scenario, goal, barrier, workaround, and cost reconstruction
- Reconstruct only what the evidence supports.
- If the scenario is absent, do not fill it from intuition.
- If workaround or cost is unknown, keep it unknown.

### 6. Need and solution separation
- User-proposed features are not equal to real needs.
- Convert solution-shaped feedback into need analysis using `references/need-vs-solution.md`.

### 7. Similar-need clustering
- Group only when scenario, goal, and barrier are materially compatible.
- If segment differences are meaningful, keep clusters separate.

### 8. Requirement validity judgment
- Judge using `references/requirement-validation.md`.
- Allowed conclusion labels are only:
  - `成立 / validated`
  - `条件成立 / conditionally_validated`
  - `需求假设 / need_hypothesis`
  - `证据不足 / insufficient_evidence`
  - `不成立或不属于本产品范围 / invalid_or_out_of_scope`

### 9. Evidence strength evaluation
- Evaluate support and opposition using `references/evidence-strength.md`.
- Separate behavioral evidence from attitudinal evidence.
- Do not present small samples as population statistics.

### 10. Active counterexample search
- Search for users, segments, or data points that contradict the current conclusion.
- Without counterexample checking, the conclusion cannot be `成立 / validated`.

### 11. User-segment difference check
- Compare by segment where possible.
- Do not force-merge conflicting segment needs.

### 12. Need-side prioritization
- Use only demand-side prioritization rules from `references/prioritization-rules.md`.
- Do not convert the result directly into a feature delivery list.

### 13. Report output
- Every need must link to source evidence IDs.
- If evidence is missing, state uncertainty directly.

### 14. Structure and evidence traceability validation
- Confirm every conclusion points to evidence.
- Confirm facts and interpretations remain separated.
- Confirm non-need issues are labeled correctly.

# Output Artifacts

The skill may produce:
- an evidence table;
- a set of user need cards;
- a need prioritization view;
- a final report summary.

Every need statement must use this fixed format:

When `[target user]` is in `[specific situation]`,
to complete `[goal task]`,
the user needs `[capability or outcome]`,
because the current `[barrier or workaround]` causes `[cost or loss]`.

# Hard Guardrails

- A user-requested feature is not automatically a real need.
- A single feedback item cannot automatically become a common need.
- Behavioral evidence and attitudinal expression must be kept separate.
- Observed facts and analytical interpretation must be kept separate.
- Every need must link to raw evidence IDs.
- If no scenario is known, output only `需求假设 / need_hypothesis` or `证据不足 / insufficient_evidence`.
- Without a counterexample check, do not mark a need as `成立 / validated`.
- Internal retellings are low-grade secondhand evidence.
- Do not invent user psychology, intent, or hidden motivation.
- Do not convert the output directly into a feature list.
- Distinguish needs, bugs, usability issues, operations issues, service issues, and training issues.
- If user-segment differences exist, do not force them into one merged need.
- Check whether the issue is already solved by an existing feature before concluding a new need exists.

# Reference-File Loading Rules

Load only the reference files needed for the current stage.

- During evidence typing, load `references/evidence-taxonomy.md`.
- During solution stripping and issue classification, load `references/need-vs-solution.md`.
- During validity judgment, load `references/requirement-validation.md`.
- During evidence-strength assessment, load `references/evidence-strength.md`.
- During need-side ranking, load `references/prioritization-rules.md`.

Do not copy full reference files into the final output. Use them as rules, then cite the relevant judgment succinctly.

# Validation and Completion Checklist

Before finishing, confirm all items below:

- The workflow followed the fixed stage order.
- Every source has a stable ID.
- Every need links to evidence IDs.
- Facts, quotes, and inferences are stored separately.
- Behavior and attitude evidence are separated.
- Solution statements were translated into need analysis.
- Non-need issues were classified correctly.
- Counterexamples were actively checked.
- Segment differences were checked.
- Existing-feature fit was checked.
- Only allowed conclusion labels were used.
- Need statements follow the fixed sentence format.
- No unsupported percentages or market-size claims were introduced.
