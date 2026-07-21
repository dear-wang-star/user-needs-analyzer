# Prioritization Rules

V1.0 supports need-side prioritization only. It does not replace formal product planning, delivery scoping, or engineering sequencing.

## Evidence Terms Used Here

This file uses three different evidence concepts:
- `evidence_weight`
  - the default relative weight of an evidence type from `references/evidence-taxonomy.md`;
  - not a prioritization input by itself.
- `evidence_strength_score`
  - the `1-5` score used in prioritization after full need-level review.
- `overall_evidence_strength`
  - the narrative text judgment `strong` / `medium` / `weak`.

Rules:
- Do not copy an evidence type's `evidence_weight` directly into `evidence_strength_score`.
- Do not mechanically convert `overall_evidence_strength` into a fixed numeric value.
- Final scoring must reflect independent sources, completeness, behavioral evidence, counterevidence, leading risk, and segment differences.

## Scoring Dimensions

Score each candidate need on:
- frequency: `1-5`
- pain_intensity: `1-5`
- evidence_strength: `1-5`
- core_user_fit: `1-5`

## Base Formula

Use this formula:

`priority_score = frequency × pain_intensity × evidence_strength × core_user_fit`

In this formula, `evidence_strength` means the reviewed `evidence_strength_score` input, not raw `evidence_weight` and not the text-only `overall_evidence_strength` label.

## Additional Recorded Fields

Record these separately from the core score:
- strategic_fit
- solution_cost: `unknown` / `low` / `medium` / `high`
- needs_further_validation: `yes` / `no`

Do not calculate technical cost inside this skill. Only record known information when it already exists.

## Scoring Guidance

### Frequency

- `1`: isolated or unconfirmed
- `2`: occasional or segment-limited
- `3`: recurring within a clear subgroup
- `4`: frequent across a meaningful group
- `5`: highly frequent in a core workflow

### Pain intensity

- `1`: minor inconvenience
- `2`: noticeable friction
- `3`: meaningful extra effort or risk
- `4`: repeated blockage, delay, or workaround cost
- `5`: core task is blocked or materially degraded

### Evidence strength

- `1`: weak, mostly attitudinal or secondhand
- `2`: limited direct support
- `3`: moderate support with some corroboration
- `4`: strong support with direct or behavioral evidence
- `5`: very strong, multi-source, low-risk support

### Core user fit

- `1`: outside the main product audience
- `2`: peripheral to main users
- `3`: relevant to an important subgroup
- `4`: important for a core segment
- `5`: central to a core segment's recurring task

## Priority Bands

### `P0`

Use only when:
- a core task is blocked or severely degraded;
- evidence is strong enough to support the conclusion;
- the issue fits a core user and core workflow.

Evidence-poor items cannot enter `P0`, even if other dimensions are high.
If `evidence_strength = 1`, the item should normally rank no higher than `P2`, unless it represents a clearly blocking risk and receives explicit human review.

### `P1`

Use when:
- the issue is high-frequency, high-cost, and strongly matched to an important user group;
- evidence is solid but the situation is not as severe as `P0`, or not as universally blocking.

### `P2`

Use when:
- the issue is local, conditional, segment-bound, or moderate;
- evidence may be decent, but scope or severity is limited.

### `P3`

Use when:
- the signal is weak;
- the fit is low;
- the issue is likely secondary;
- or more validation is still required.

## Guardrails

- Scores support judgment; they are not objective truth.
- Do not promote an evidence-poor item to `P0` because the pain sounds dramatic.
- A single large customer request does not automatically become a common need because the commercial voice is loud.
- Bug severity and need priority are not the same scoring system.
- Technical delivery cost is outside this skill and must not silently override need-side evidence.
- The raw product score is for relative ordering between candidate needs only.
- Do not present a raw score such as `625` as if it had absolute business meaning.

## Interpretation Notes

- Use the numeric score to compare, not to replace reasoning.
- Keep segment context visible; similar scores can still mean different strategic decisions later.
- If `needs_further_validation = yes`, keep the narrative cautious even when the numeric score looks high.

## Recommended Output

Prefer to show:
- rank order
- `P0-P3`
- dimension scores
- scoring rationale

Do not emphasize the raw multiplied score as a precise decision answer.
