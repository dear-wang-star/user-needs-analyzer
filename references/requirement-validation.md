# Requirement Validation Rules

This file defines how to decide whether a candidate need is validated in V1.0.

## Six Validation Dimensions

### 1. Authenticity

- Evidence needed:
  - observed behavior;
  - concrete historical behavior;
  - direct quotes tied to a real scenario.
- Strong signal:
  - direct observation or product data plus concrete task context.
- Medium signal:
  - user verbatim plus credible historical behavior.
- Weak signal:
  - hypothetical preference or internal retelling only.
- If missing:
  - do not conclude `成立 / validated`; use `需求假设 / need_hypothesis` or `证据不足 / insufficient_evidence`.

### 2. Frequency

- Evidence needed:
  - repeated cases across users, time, or sessions;
  - product data when available;
  - multiple independent sources.
- Strong signal:
  - repeated independent occurrences across multiple users or repeated behavior over time.
- Medium signal:
  - more than one credible occurrence but limited span or independence.
- Weak signal:
  - one isolated case or vague "many users say" statement.
- If missing:
  - treat the need as specific or directional only; do not claim commonality.

### 3. Pain Intensity

- Evidence needed:
  - delay, failure, rework, risk, anxiety, abandonment, or measurable effort.
- Strong signal:
  - task blocked, error-prone, high rework, or severe consequence.
- Medium signal:
  - meaningful friction but task still completes.
- Weak signal:
  - mild annoyance with limited task consequence.
- If missing:
  - lower confidence and avoid high priority conclusions.

### 4. Impact Scope

- Evidence needed:
  - segment coverage, workflow criticality, account type, or affected journey stage.
- Strong signal:
  - affects a core journey, important segment, or many instances within that segment.
- Medium signal:
  - affects a meaningful but narrower workflow or subgroup.
- Weak signal:
  - affects edge cases only or the affected scope is unclear.
- If missing:
  - do not generalize beyond the observed group.

### 5. Workaround Cost

- Evidence needed:
  - manual effort, time loss, error risk, switching tools, delay, or social coordination cost.
- Strong signal:
  - repeated manual work, high error exposure, or blocked downstream steps.
- Medium signal:
  - moderate inconvenience with a workable substitute.
- Weak signal:
  - easy substitute with little cost.
- If missing:
  - keep the need provisional and do not infer hidden cost.

### 6. Product Fit

- Evidence needed:
  - product scope context, current feature coverage, user expectation alignment.
- Strong signal:
  - the problem sits in a core workflow the product is meant to support.
- Medium signal:
  - adjacent to product value but may depend on integration or process choices.
- Weak signal:
  - outside the product's intended job, or better solved by another function or team.
- If missing:
  - avoid a `成立 / validated` conclusion until scope fit is checked.

## Allowed Validity Conclusions

Use only these five conclusion labels.

### `成立 / validated`

Use only when all conditions below are met:
- authenticity is at least medium and supported by direct or near-direct evidence;
- there is at least some repeated or corroborated signal;
- pain intensity or workaround cost is meaningful;
- product fit is not weak;
- counterexample review has been completed;
- no unresolved conflict makes the conclusion unstable.

### `条件成立 / conditionally_validated`

Use when:
- the need appears real in a defined segment, condition, or workflow;
- one or more dimensions are limited in scope or certainty;
- the conclusion is stronger than a hypothesis but not broad enough for a plain `成立 / validated` label.

### `需求假设 / need_hypothesis`

Use when:
- the pattern is plausible;
- some evidence points toward a need;
- key dimensions such as frequency, scenario, or product fit are still incomplete.

### `证据不足 / insufficient_evidence`

Use when:
- evidence is too sparse, contradictory, low quality, or missing key context;
- the task cannot be reconstructed reliably;
- no grounded conclusion should be made yet.

### `不成立或不属于本产品范围 / invalid_or_out_of_scope`

Use when:
- the issue is better classified as bug, usability, operations, service, or training;
- the proposed need conflicts with stronger evidence;
- the product is not the correct place to solve the problem;
- the issue is already solved by the current product and the actual gap is discoverability or enablement.

## Counterexample Check Flow

Counterexample review is mandatory before using `成立 / validated`.

Run this sequence:
1. Look for users who completed the same task without the reported problem.
2. Look for segments where the pattern does not appear.
3. Look for evidence that the current workaround is acceptable to some users.
4. Look for evidence that the requested problem is caused by process, permissions, or training instead.
5. Record whether the counterexample weakens scope, severity, or product fit.

If counterexamples are found:
- narrow the segment or context;
- downgrade the conclusion if needed;
- do not hide the contradiction.

## User-Segment Difference Check

Before merging needs:
- compare role, company size, workflow maturity, usage frequency, and environment when available;
- check whether one segment sees value while another does not;
- keep separate needs when barriers, goals, or workaround costs differ materially.

If segment evidence is missing:
- say so explicitly;
- avoid broad claims.

## Interview Leading Check

Interview-derived evidence must be screened for leading risk.

Warning signs:
- the moderator named the solution first;
- yes/no agreement questions dominated the evidence;
- the user adopted the interviewer's language without giving their own scenario;
- enthusiasm appeared only after prompting about a feature concept.

Handling:
- downgrade evidence strength;
- require independent behavioral or historical support before strong conclusions.

## Behavior vs Verbal Conflict Handling

If spoken preference conflicts with observed or historical behavior:
- prefer the behavioral evidence for what users actually do;
- use the verbal evidence to understand framing, expectation, or emotion;
- do not ignore the conflict;
- output a narrower conclusion if necessary.

Example:
- a user says reminders are unnecessary, but repeatedly misses time-sensitive steps and uses calendar workarounds.
- The correct conclusion is not "the user wants reminders."
- The stronger conclusion may be "the user needs reliable time-sensitive task support."

## Existing Feature Satisfaction Check

Before concluding a new need:
- verify whether the product already provides the needed outcome;
- check whether the real issue is discoverability, permissions, trust, or training;
- if the need is already supported, do not label the output as a missing new product need.

In that case, classify as:
- usability issue;
- training or awareness issue;
- operations issue;
- or bug if the feature should work but does not.

## Core Product Problem Check

Ask:
- Is this problem inside the product's core job?
- Would solving it mainly require product change, or another team/process?
- Is this a stable user task or a one-off special request?

If the answer points outside product scope:
- use `不成立或不属于本产品范围 / invalid_or_out_of_scope`;
- explain the boundary clearly.
