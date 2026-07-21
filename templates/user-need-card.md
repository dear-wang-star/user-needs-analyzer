---
need_id: N001
title: ""
validity_verdict: need_hypothesis
overall_evidence_strength: weak
priority_tier: P3
owner: ""
analysis_date: YYYY-MM-DD
---

# User Need Card Template

Use this template for one candidate need only.

Template relationship:
- input: `evidence-table.md`
- output consumer: `needs-ranking.md`
- final summary consumer: `final-report.md`

Allowed enums:
- `validity_verdict`: `validated` / `conditionally_validated` / `need_hypothesis` / `insufficient_evidence` / `invalid_or_out_of_scope`
- `overall_evidence_strength`: `strong` / `medium` / `weak`
- `priority_tier`: `P0` / `P1` / `P2` / `P3`
- `solution_cost`: `unknown` / `low` / `medium` / `high`

## 1. Need Statement

```text
When [target_user] is in [specific_context],
they need [capability_or_outcome]
to accomplish [user_task],
because [current_barrier_or_workaround]
causes [cost_or_loss].
```

Rules:
- Do not write a specific feature, button, page, reminder, export action, or AI integration as the need itself.
- If the scenario is missing, downgrade to `need_hypothesis` or `insufficient_evidence`.

## 2. Target User and Segment

```yaml
target_user: ""
user_segment: unknown
segment_scope: ""
excluded_or_unverified_segments: ""
```

## 3. Context and Trigger

```yaml
specific_context: unknown
trigger: unknown
frequency_context: unknown
lifecycle_stage: unknown
```

## 4. User Goal and Task

```yaml
user_goal: ""
user_task: ""
expected_outcome: ""
```

## 5. Current Barrier

```yaml
barrier: ""
failure_point: ""
consequence: ""
emotional_effect: not_available
```

Only fill `emotional_effect` when evidence exists.

## 6. Current Workaround and Cost

```yaml
workaround: unknown
time_cost: unknown
financial_cost: unknown
cognitive_cost: unknown
operational_risk: unknown
switching_or_avoidance_behavior: unknown
```

Do not guess missing costs.

## 7. User-Proposed Solutions

These are user-proposed means, not validated needs or final product decisions.

```yaml
proposed_solution:
  - ""
proposing_evidence_ids:
  - E001
whether_solution_is_validated: no
```

## 8. Supporting Evidence

```yaml
supporting_evidence_ids:
  - E001
supporting_participant_count: 1
independent_source_count: 1
behavioral_evidence_count: 0
attitudinal_evidence_count: 0
product_data_available: no
representative_verbatim: not_available
```

Do not rewrite small samples into population percentages.

## 9. Counterevidence and Limitations

```yaml
counterevidence_ids:
  - none_found_in_current_material
users_without_the_problem: unknown
contradictory_behavior: unknown
segment_difference: unknown
interviewer_prompting_risk: unknown
source_limitations: ""
existing_feature_check: unknown
```

Rules:
- Even when no counterexample is found, use `none_found_in_current_material`.
- Do not write "no counterevidence, therefore proven."

## 10. Evidence Assessment

```yaml
evidence_weight_summary: ""
evidence_strength_score: 1
overall_evidence_strength: weak
directional_or_stable: directional
evidence_rationale: ""
```

Meaning:
- `evidence_weight_summary`: brief summary of the evidence mix and relative type weights.
- `evidence_strength_score`: `1-5` prioritization input after full evidence review.
- `overall_evidence_strength`: narrative conclusion `strong` / `medium` / `weak`.

Do not mix these three concepts.

## 11. Requirement Validation

### authenticity

```yaml
score_or_level: ""
supporting_evidence:
  - E001
uncertainty: ""
```

### frequency

```yaml
score_or_level: ""
supporting_evidence:
  - E001
uncertainty: ""
```

### pain_intensity

```yaml
score_or_level: ""
supporting_evidence:
  - E001
uncertainty: ""
```

### affected_scope

```yaml
score_or_level: ""
supporting_evidence:
  - E001
uncertainty: ""
```

### workaround_cost

```yaml
score_or_level: ""
supporting_evidence:
  - E001
uncertainty: ""
```

### product_fit

```yaml
score_or_level: ""
supporting_evidence:
  - E001
uncertainty: ""
```

```yaml
validity_verdict: need_hypothesis
verdict_rationale: ""
conditions_for_validation: ""
missing_evidence: ""
next_validation_action: ""
```

## 12. Product Opportunity

```yaml
opportunity_statement: ""
desired_user_outcome: ""
constraints: ""
non_goals: ""
```

Only describe higher-level opportunity direction. Do not lock to one feature.

## 13. Priority Assessment

```yaml
frequency_score: 1
pain_intensity_score: 1
evidence_strength_score: 1
core_user_fit_score: 1
relative_priority_score: 1
priority_tier: P3
strategic_fit: unknown
solution_cost: unknown
human_review_required: yes
priority_rationale: ""
```

`relative_priority_score` is for comparison across candidate needs only.

## 14. Traceability Checklist

- [ ] All conclusions trace back to `evidence_id`
- [ ] User need and user-proposed solution are separated
- [ ] Behavior and attitude are separated
- [ ] Facts and interpretation are separated
- [ ] Counterevidence has been checked
- [ ] Segment differences have been checked
- [ ] Existing-feature satisfaction has been checked
- [ ] No unvalidated population percentage is claimed
