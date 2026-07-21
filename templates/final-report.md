---
analysis_id: ""
title: ""
analysis_date: YYYY-MM-DD
status: draft
analyst: ""
---

# Final Report Template

Use this template to assemble the final user-needs analysis report.

Template relationship:
- `evidence-table.md` -> source evidence
- `user-need-card.md` -> analyzed need unit
- `needs-ranking.md` -> relative demand-side ranking
- `final-report.md` -> traceable summary and delivery artifact

The report must not create conclusions that cannot be traced back to the first three artifacts.

## 1. Executive Summary

- analysis purpose:
- input material count:
- independent user count:
- data sources:
- need theme count:
- highest-priority needs:
- most important evidence limitations:

## 2. Scope and Inputs

```yaml
product_context: ""
target_users: ""
research_question: ""
included_sources: ""
excluded_sources: ""
time_range: ""
known_biases: ""
privacy_and_deidentification: ""
```

## 3. Method

Briefly confirm that the analysis performed:
- evidence normalization
- evidence classification
- need and solution separation
- clustering
- validity assessment
- counterevidence review
- segment-difference review
- relative prioritization
- traceability validation

Do not copy the reference files into this section.

## 4. Evidence Overview

```yaml
evidence_count_by_type: ""
evidence_count_by_source: ""
participant_or_source_coverage: ""
behavioral_vs_attitudinal_balance: ""
secondhand_evidence_count: ""
missing_context_summary: ""
```

Reference artifact:
- [evidence-table.md](evidence-table.md)

## 5. Key User Needs

| need_id | need_title | target_segment | validity_verdict | overall_evidence_strength | priority_tier | key_evidence_ids |
|---|---|---|---|---|---|---|
| N001 | "" | unknown | need_hypothesis | weak | P3 | E001 |

Each row must map to a completed need card.

## 6. Detailed Findings

For each need, include:

### need_id: N001

```yaml
need_statement: ""
supporting_evidence: ""
counterevidence: ""
segment_differences: ""
validity_verdict: need_hypothesis
overall_evidence_strength: weak
opportunity_direction: ""
priority_rationale: ""
remaining_uncertainty: ""
```

## 7. Cross-User Patterns

```yaml
common_patterns: ""
segment_specific_patterns: ""
contradictory_patterns: ""
single_user_signals: ""
patterns_not_yet_validated: ""
```

Do not rewrite a single-user signal as a common pattern.

## 8. Non-Need Classifications

```yaml
bugs: ""
usability_issues: ""
operations_issues: ""
service_issues: ""
training_or_awareness_issues: ""
already_satisfied: ""
invalid_or_out_of_scope: ""
```

## 9. Needs Ranking

Reference artifact:
- [needs-ranking.md](needs-ranking.md)

Include:
- ranking summary
- `P0-P3` distribution
- validation queue summary
- human overrides

## 10. Recommended Next Actions

Allowed action types only:
- further research
- product discovery
- usability evaluation
- data validation
- route to bug fixing
- route to operations, service, or training
- human product review

Do not promise direct feature delivery.

## 11. Limitations

```yaml
sample_limitations: ""
source_limitations: ""
behavioral_data_gaps: ""
prompting_bias: ""
recency_bias: ""
missing_segments: ""
directional_vs_conclusive_status: ""
```

## 12. Traceability Appendix

```yaml
need_id_to_evidence_id_mapping: ""
excluded_feedback_reasons: ""
unassigned_evidence: ""
missing_sources: ""
validation_status: ""
```

## 13. Completion Checklist

- [ ] All needs have `evidence_id` links
- [ ] All needs have `validity_verdict`
- [ ] All needs have `overall_evidence_strength`
- [ ] All validated needs completed counterevidence review
- [ ] All needs completed segment-difference review
- [ ] No feature suggestion was directly treated as the need
- [ ] No small sample was rewritten as a population percentage
- [ ] Limitations are listed
- [ ] Privacy review is complete
- [ ] The report is ready for script-based validation
