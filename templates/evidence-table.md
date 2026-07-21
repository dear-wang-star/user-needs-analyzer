# Evidence Table Template

Use this template to normalize raw material into traceable evidence units.

Template relationship:
- `evidence-table.md` -> source artifact
- `user-need-card.md` -> analysis unit built from evidence
- `needs-ranking.md` -> relative ranking built from need cards
- `final-report.md` -> delivery artifact that summarizes all three

## 1. Usage Notes

- One row represents one evidence unit only.
- Do not combine user behavior and user speech in the same evidence row.
- Do not change the meaning of a user quote.
- Any analytical guess must be marked through `evidence_type: analyst_inference`.
- Any secondhand retelling must be marked through `evidence_type: internal_secondhand_report`.
- If information is missing, use `unknown`, `not_available`, or `insufficient_evidence`.
- Do not include real private user data.

## 2. Source Metadata

```yaml
analysis_id: A001
source_name: ""
source_type: interview
collection_date: YYYY-MM-DD
analyst: ""
product_context: ""
research_question: ""
source_limitations: ""
```

Allowed `source_type` values for metadata:
- `interview`
- `support_ticket`
- `survey`
- `review`
- `product_data`
- `internal_report`
- `other`

## 3. Standard Evidence Table

| evidence_id | participant_id | user_segment | source_type | source_reference | timestamp_or_date | evidence_type | raw_evidence | context | prompted | observation_or_self_report | completeness | analyst_interpretation | linked_need_ids | confidence_note | privacy_check |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E001 | P001 | unknown | interview | INT-001 | 2026-07-21 10:14 | observed_behavior | "" | "" | no | observation | complete | not_available | unassigned | "" | passed |

Field requirements:

| field_name | requirement |
|---|---|
| evidence_id | Required. Format `E001`, `E002`, ... |
| participant_id | Anonymous ID. Use `not_available` when no participant exists. Format `P001`, `P002`, ... |
| user_segment | Known segment label, otherwise `unknown`. |
| source_type | `interview` / `support_ticket` / `survey` / `review` / `product_data` / `internal_report` / `other` |
| source_reference | Traceable location such as file name, ticket number, interview ID, dashboard query ID, or note reference. |
| timestamp_or_date | Timestamp or date from the source material. |
| evidence_type | Must be one of: `observed_behavior`, `user_verbatim`, `historical_behavior`, `product_data`, `emotion`, `pain_or_barrier`, `user_goal`, `workaround`, `user_proposed_solution`, `analyst_inference`, `internal_secondhand_report` |
| raw_evidence | Raw quote, observed fact, or source data only. No analytical conclusion. |
| context | Situation in which the evidence occurred. Use `unknown` if missing. |
| prompted | `yes` / `no` / `unknown` |
| observation_or_self_report | `observation` / `self_report` / `data` / `secondhand` / `inference` |
| completeness | `complete` / `partial` / `fragment` |
| analyst_interpretation | Keep separate from `raw_evidence`. Use `not_available` when none exists. |
| linked_need_ids | One or more `N001`-style IDs. Use `unassigned` before clustering. |
| confidence_note | Record prompting risk, lost context, secondhand risk, or other caveats. |
| privacy_check | `passed` / `needs_review` |

## 4. Correct Examples

Example rows below are fictional.

| evidence_id | participant_id | user_segment | source_type | source_reference | timestamp_or_date | evidence_type | raw_evidence | context | prompted | observation_or_self_report | completeness | analyst_interpretation | linked_need_ids | confidence_note | privacy_check |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E101 | P014 | finance_admin | interview | INT-014 | 2026-07-10 14:22 | observed_behavior | User exported three project reports separately, then copied rows into a spreadsheet before sending a weekly pack. | Weekly reconciliation workflow | no | observation | complete | Repeated manual export may indicate a grouped data transfer problem. | N003 | Direct observation from moderated session. | passed |
| E102 | P014 | finance_admin | interview | INT-014 | 2026-07-10 14:24 | user_verbatim | "Every Friday I rebuild this report by hand because I need all projects in one file." | Weekly reconciliation workflow | no | self_report | complete | not_available | N003 | Quote preserved close to source wording. | passed |
| E103 | not_available | enterprise_sales_feedback | internal_report | SALES-WINLOSS-022 | 2026-07-12 | internal_secondhand_report | Sales reported that two enterprise prospects asked for reminders during onboarding. | Onboarding follow-up discussion | unknown | secondhand | partial | This may suggest a task-state visibility issue, but source is secondhand and not independent. | unassigned | Secondhand retelling; original user records unavailable. | passed |

## 5. Wrong Examples

Do not use rows like these.

| problem_type | bad_example | why_it_is_wrong |
|---|---|---|
| mixed_behavior_and_quote | `raw_evidence: User clicked export three times and said "this is confusing"` | Behavior and quote must be split into separate evidence rows. |
| inference_as_fact | `raw_evidence: The user is afraid of losing data` | This is an interpretation, not a raw fact. Use `analyst_interpretation` or `analyst_inference` instead. |
| missing_source_trace | `source_reference: ""` | Evidence must remain traceable to a source location. |
| duplicated_secondhand_counting | `Three sales reps repeated the same customer story and each row was counted as independent user evidence` | Repeated retellings are not independent user evidence. |

## 6. Validation Reminders

- Keep `raw_evidence` and `analyst_interpretation` separate.
- Keep `observed_behavior` and `user_verbatim` in different rows.
- Use `internal_secondhand_report` for broken source chains.
- Every `linked_need_ids` value must later map to a need card.
