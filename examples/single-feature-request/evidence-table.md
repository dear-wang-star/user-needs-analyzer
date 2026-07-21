# Evidence Table

```yaml
analysis_id: A001
source_name: single-feature-request
source_type: interview
collection_date: 2026-07-21
analyst: demo
product_context: Enterprise operations data management platform
research_question: What real user need sits behind the bulk export request?
source_limitations: Small fictional qualitative sample with no product telemetry.
```

| evidence_id | participant_id | user_segment | source_type | source_reference | timestamp_or_date | evidence_type | raw_evidence | context | prompted | observation_or_self_report | completeness | analyst_interpretation | linked_need_ids | confidence_note | privacy_check |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E001 | P001 | high_frequency_ops | interview | INT-001 | 2026-07-21 | user_verbatim | "I hope the platform can support bulk export. Copying records one by one for the weekly report is too troublesome." | Weekly external reporting workflow | no | self_report | complete | The quote includes a proposed solution and a concrete reporting pain point; the need is not automatically bulk export itself. | N001 | Direct quote with a concrete recurring scenario. | passed |
| E002 | P001 | high_frequency_ops | interview | INT-001 | 2026-07-21 | historical_behavior | P001 organizes around 30 business records every week by copying them one by one into Excel, and one reporting cycle takes about 40 minutes. | Weekly external reporting workflow | no | self_report | complete | This supports a recurring downstream data-preparation task with measurable manual cost. | N001 | Historical behavior reported by the same user as E001. | passed |
| E003 | P002 | high_frequency_ops | interview | INT-002 | 2026-07-21 | user_verbatim | "I do not necessarily need Excel. I mainly need a faster way to pull this batch of data out so I can keep working on it." | Batch data reuse for downstream preparation | no | self_report | complete | This narrows the need to faster batch retrieval and reuse rather than a fixed export format. | N001 | Direct quote that helps separate need from solution. | passed |
| E004 | P002 | high_frequency_ops | interview | OBS-002 | 2026-07-21 | observed_behavior | P002 repeated the sequence "open detail -> copy -> return to list" 18 times, missed 2 records, and then rechecked the list. | One batch data-preparation task | no | observation | complete | This is direct behavior evidence of repeated effort, omission risk, and rework. | N001 | Strong direct observation from a fictional moderated session. | passed |
| E005 | P003 | low_frequency_ops | interview | INT-003 | 2026-07-21 | user_verbatim | "I only look at this once or twice a month, so copying one by one is still acceptable for me." | Low-frequency use of the same product area | no | self_report | complete | This is counterevidence showing the problem is not equally strong for lower-frequency users. | N001 | Useful scope-limiting counterexample. | passed |
