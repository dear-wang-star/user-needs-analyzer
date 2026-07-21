# Needs Ranking Template

Use this template to rank multiple candidate needs on the demand side only.

Template relationship:
- input: `user-need-card.md`
- evidence source remains `evidence-table.md`
- summarized by `final-report.md`

This is not a delivery roadmap or engineering schedule.

## 1. Ranking Metadata

```yaml
analysis_id: A001
ranking_date: YYYY-MM-DD
included_need_ids:
  - N001
excluded_need_ids:
  - N099
decision_context: ""
scoring_limitations: ""
```

## 2. Ranking Table

| rank | need_id | need_title | target_segment | validity_verdict | frequency_score | pain_intensity_score | evidence_strength_score | core_user_fit_score | relative_priority_score | priority_tier | strategic_fit | solution_cost | human_review_required | rationale |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| 1 | N001 | "" | unknown | need_hypothesis | 1 | 1 | 1 | 1 | 1 | P3 | unknown | unknown | yes | "" |

Allowed enums:
- `validity_verdict`: `validated` / `conditionally_validated` / `need_hypothesis` / `insufficient_evidence` / `invalid_or_out_of_scope`
- `priority_tier`: `P0` / `P1` / `P2` / `P3`
- `solution_cost`: `unknown` / `low` / `medium` / `high`

## 3. Ranking Constraints

- `invalid_or_out_of_scope` does not enter formal need ranking.
- `insufficient_evidence` defaults to `P3` or the validation queue.
- `need_hypothesis` cannot enter `P0`.
- If `evidence_strength_score = 1`, the item should normally rank no higher than `P2`.
- A single large customer request does not automatically represent a common need.
- Bug severity is not ranked in this table.
- `relative_priority_score` has no absolute business meaning.
- Ties require human comparison.
- Rank order is not a delivery schedule.

## 4. Validation Queue

| need_id | current_signal | missing_evidence | recommended_validation | decision_deadline |
|---|---|---|---|---|
| N001 | need_hypothesis | "" | "" | YYYY-MM-DD |

## 5. Excluded Items

| need_id_or_feedback_id | exclusion_reason | classification | whether_to_route_elsewhere |
|---|---|---|---|
| E099 | "" | duplicate | yes |

Allowed `classification` values:
- `bug`
- `usability_issue`
- `operations_issue`
- `service_issue`
- `training_or_awareness_issue`
- `invalid_or_out_of_scope`
- `duplicate`
- `already_satisfied`

## 6. Human Review Log

```yaml
reviewer: ""
review_date: YYYY-MM-DD
ranking_changes: ""
reason_for_override: ""
approved_for_next_stage: no
```

## 7. Scoring Note

`relative_priority_score` should be derived from:

```text
priority_score =
frequency × pain_intensity × evidence_strength × core_user_fit
```

Use the score for relative comparison only. Prefer to show:
- ranking position
- `P0-P3`
- dimension scores
- scoring rationale

Do not present the raw multiplied number as an objective business truth.
