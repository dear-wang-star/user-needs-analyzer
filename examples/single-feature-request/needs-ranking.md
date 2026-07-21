# Needs Ranking

## 1. Ranking Metadata

```yaml
analysis_id: A001
ranking_date: 2026-07-21
included_need_ids:
  - N001
excluded_need_ids:
decision_context: Single fictional V1.0 example focused on one candidate need
scoring_limitations: Small qualitative sample and no product telemetry
```

## 2. Ranking Table

| rank | need_id | need_title | target_segment | validity_verdict | frequency_score | pain_intensity_score | evidence_strength_score | core_user_fit_score | relative_priority_score | priority_tier | strategic_fit | solution_cost | human_review_required | rationale |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| 1 | N001 | Reduce batch data retrieval and reuse cost for high-frequency operations reporting | high_frequency_ops | conditionally_validated | 3 | 4 | 3 | 5 | 180 | P1 | high | unknown | yes | Strong fit to a recurring core workflow for high-frequency users, with meaningful manual cost and moderate but bounded evidence support. |

## 3. Ranking Constraints

- Rank order is relative need prioritization, not a delivery plan.
- This example includes one formal candidate need only.

## 4. Validation Queue

| need_id | current_signal | missing_evidence | recommended_validation | decision_deadline |
|---|---|---|---|---|

## 5. Excluded Items

| need_id_or_feedback_id | exclusion_reason | classification | whether_to_route_elsewhere |
|---|---|---|---|

## 6. Human Review Log

```yaml
reviewer: demo
review_date: 2026-07-21
ranking_changes: none
reason_for_override: not_available
approved_for_next_stage: no
```

## 7. Scoring Note

`relative_priority_score` is for relative comparison only and does not represent product delivery order.
