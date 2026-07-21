# Evidence Strength Rules

This file defines how to judge the strength of evidence behind each candidate need.

## Three Distinct Concepts

Do not mix these concepts:
- `evidence_weight`
  - the default relative weight of a specific evidence type;
  - for example, direct observed behavior usually starts higher than hypothetical desire;
  - it is not the final conclusion.
- `evidence_strength_score`
  - the `1-5` score used as the prioritization input;
  - it can be assigned only after reviewing the full need-level evidence set.
- `overall_evidence_strength`
  - the final text conclusion:
    - `strong`
    - `medium`
    - `weak`

Rules:
- Do not use one evidence type's default `evidence_weight` as the final `evidence_strength_score`.
- `overall_evidence_strength` and `evidence_strength_score` are related, but not by a simple mechanical mapping.
- Final evidence judgment must combine independent sources, completeness, behavioral evidence, counterevidence, leading risk, and segment differences.

## Default Evidence Order

Use this default order as a starting point:

Real observed behavior
> product behavior data
> concrete historical experience
> multiple independent users expressing the same issue
> single-user attitudinal expression
> hypothetical intention
> internal staff retelling

This order is not mechanical. Final judgment must also consider:
- completeness;
- independence;
- recency;
- leading risk;
- consistency with other evidence;
- whether the source actually supports the claimed conclusion.

## Evidence Quality Modifiers

### Completeness

Higher when:
- the scenario, task, barrier, and outcome are concrete.

Lower when:
- the statement is vague, partial, or stripped of context.

### Independence

Higher when:
- evidence comes from different users, sessions, or data sources that do not simply repeat each other.

Lower when:
- several sources are all derived from one original case;
- internal teams repeat the same story and it is counted multiple times.

### Recency

Higher when:
- the evidence reflects current product behavior and current workflows.

Lower when:
- the evidence is old, tied to a previous product version, or clearly outdated.

### Leading Risk

Higher risk when:
- users respond to suggested solutions instead of describing their own experience;
- interviews rely on agreement prompts.

Higher leading risk lowers usable strength.

## Minimum Evidence Assessment Fields Per Need

Each candidate need must record at least:
- support_user_count
- independent_source_count
- behavior_evidence_count
- attitude_evidence_count
- product_data_evidence
- opposing_evidence
- segment_difference
- leading_risk
- evidence_strength_score: `1-5`
- overall_evidence_strength: `strong` / `medium` / `weak`
- conclusion_nature: `directional` / `relatively stable` / `still needs validation`

`evidence_strength_score` is used for prioritization input.
`overall_evidence_strength` is the narrative summary shown in analysis outputs.

## How to Assign Overall Strength

### `strong`

Use when most of these are true:
- more than one independent source supports the pattern;
- at least one behavioral or product-data signal exists;
- the scenario and barrier are concrete;
- opposing evidence does not overturn the conclusion;
- leading risk is low or managed.

### `medium`

Use when:
- support exists but is narrower, less independent, or less complete;
- behavioral support may be limited;
- some uncertainty remains about scope or causality.

### `weak`

Use when:
- evidence is mainly attitudinal, hypothetical, secondhand, or isolated;
- the scenario is incomplete;
- the conclusion depends heavily on interpretation;
- leading risk is high;
- counterevidence is unresolved.

## How to Set `evidence_strength_score`

Set `evidence_strength_score` only after the full review of:
- independent source count;
- completeness of scenario and task reconstruction;
- behavioral and product-data support;
- counterevidence;
- leading risk;
- segment differences.

Guidance:
- `1`: highly fragile evidence picture
- `2`: weak but non-zero support
- `3`: moderate support with important limits
- `4`: strong support with manageable limits
- `5`: unusually strong and well-corroborated support

Do not infer `evidence_strength_score` by a direct lookup from `overall_evidence_strength`.
Do not infer `overall_evidence_strength` by a direct lookup from one evidence type's `evidence_weight`.

## What Not to Do

- Do not write `4/5 users = 80% of users`.
- Do not use one memorable quote as a stand-in for the whole population.
- Do not overweight the most recent interview because it feels vivid.
- Do not count repeated retellings as independent evidence.
- Do not hide opposing evidence because it is inconvenient.
- Do not upgrade a solution request into strong evidence of a need by itself.

## Interpretation Rules

- High emotion is not the same as high prevalence.
- High frequency is not the same as high pain.
- Strong evidence of a bug is not the same as strong evidence of an unmet need.
- A single observed behavior can be more important than several vague opinions, but still may not justify a broad conclusion alone.

## Output Guidance

When summarizing evidence strength for a need:
- separate what is directly observed from what is inferred;
- state whether the conclusion is directional, relatively stable, or still needs validation;
- mention key limitations if independence, recency, or segment coverage is weak.
