# Evidence Taxonomy

This file defines the allowed evidence types for V1.0.

## Core Separation Rules

- One evidence unit must have one primary evidence type.
- `What the user did` and `what the user said` must not be stored in the same evidence field.
- Observed facts and analyst interpretation must be stored separately.
- A secondary note may be attached, but it must not replace the primary evidence type.

Recommended evidence record fields:
- `evidence_id`
- `source_id`
- `evidence_type`
- `fact_text`
- `quote_text` when relevant
- `inference_text` only if clearly marked as analyst inference

## Weight Scale

This file uses `evidence_weight` to describe the default relative weight of an evidence type.

Default `evidence_weight` in this file uses:
- `5`: very strong by default
- `4`: strong by default
- `3`: moderate by default
- `2`: weak by default
- `1`: very weak by default

Do not mix these concepts:
- `evidence_weight`: the default relative weight of an evidence type.
- `evidence_strength_score`: the `1-5` score used later in prioritization after full need-level review.
- `overall_evidence_strength`: the final text conclusion `strong` / `medium` / `weak`.

Rules:
- Do not treat `evidence_weight` as a final conclusion.
- Do not copy an evidence type's default `evidence_weight` directly into `evidence_strength_score`.
- `overall_evidence_strength` must be based on the full evidence set, not on one evidence type alone.

## Evidence Types

### `observed_behavior`

- Definition: Direct observation of what a user actually did in a real or realistic task flow.
- Judgment criteria:
  - the action is concrete and time-bounded;
  - the observer saw it directly or the system captured it directly;
  - the description avoids motive guessing.
- Example:
  - "User U-17 opened export settings three times, then copied rows manually into a spreadsheet."
- Common misreads:
  - turning an observed pause into "the user is confused" without support;
  - mixing the observed action with the user's quote in the same field.
- Default `evidence_weight`: `5`
- Can it support requirement validity alone: `No`, but it can strongly support authenticity or friction existence.

### `user_verbatim`

- Definition: A direct user quote about experience, belief, desire, confusion, or evaluation.
- Judgment criteria:
  - the wording is close to the user's original language;
  - the quote is attributed to one identifiable source ID;
  - the quote is not paraphrased into analyst language.
- Example:
  - "I need to send this report to finance every Friday, and copying it row by row is painful."
- Common misreads:
  - treating one vivid quote as a market-level truth;
  - rewriting a quote into a cleaner sentence and forgetting it is now interpretation.
- Default `evidence_weight`: `3`
- Can it support requirement validity alone: `No`

### `historical_behavior`

- Definition: A concrete report of what the user has actually done in the past in a real context.
- Judgment criteria:
  - the report describes a specific past event or repeated real behavior;
  - it includes context, not only opinion;
  - it is not purely hypothetical.
- Example:
  - "For the past two months, I export the CSV and merge it manually with payment records every week."
- Common misreads:
  - treating "I would probably do that" as historical behavior;
  - treating an unanchored memory as precise frequency data.
- Default `evidence_weight`: `4`
- Can it support requirement validity alone: `No`, but it can materially support it with context and corroboration.

### `product_data`

- Definition: Quantitative or system-captured product data relevant to the user problem.
- Judgment criteria:
  - the metric source is known;
  - the time window is known;
  - the metric describes behavior or outcome, not interpretation.
- Example:
  - "42% of users who reach step 4 leave before completion during the last 30 days."
- Common misreads:
  - treating correlation as proof of motivation;
  - ignoring segment mix and base size.
- Default `evidence_weight`: `4`
- Can it support requirement validity alone: `No`, because it rarely explains user intent or scenario by itself.

### `emotion`

- Definition: An expressed emotional state such as frustration, relief, anxiety, or delight.
- Judgment criteria:
  - the emotion is explicitly stated or directly observable;
  - it is not inferred from neutral behavior alone;
  - it is linked to a moment or context.
- Example:
  - "I get anxious every time I submit this because I cannot tell whether it saved."
- Common misreads:
  - equating strong emotion with high frequency;
  - assuming emotional intensity proves a product-fit solution.
- Default `evidence_weight`: `2`
- Can it support requirement validity alone: `No`

### `pain_or_barrier`

- Definition: A concrete obstacle, friction, or failure that blocks or slows a user task.
- Judgment criteria:
  - the barrier affects a real task;
  - the task impact is specific;
  - the statement identifies what gets blocked or degraded.
- Example:
  - "The user cannot export multiple projects in one action and repeats the workflow 12 times."
- Common misreads:
  - writing a vague complaint with no task context;
  - confusing dissatisfaction with a true barrier.
- Default `evidence_weight`: `4`
- Can it support requirement validity alone: `No`, but it can strongly support pain intensity.

### `user_goal`

- Definition: The result or progress state the user is trying to achieve.
- Judgment criteria:
  - the goal is task-oriented and concrete enough to analyze;
  - it is separated from the means;
  - it reflects the user's objective, not the product team's metric.
- Example:
  - "The user wants to send one complete weekly summary to finance before noon on Friday."
- Common misreads:
  - rewriting a requested feature as if it were the goal;
  - confusing a business KPI with the user's immediate task.
- Default `evidence_weight`: `3`
- Can it support requirement validity alone: `No`

### `workaround`

- Definition: The substitute behavior or tool the user uses because the current path is insufficient.
- Judgment criteria:
  - it is a real current behavior, not a hypothetical idea;
  - it compensates for a missing capability or poor current path;
  - it implies cost, risk, or inefficiency.
- Example:
  - "The user exports raw data, opens Excel, and combines files manually before sharing."
- Common misreads:
  - labeling any alternative feature use as a workaround;
  - assuming every workaround indicates a product opportunity worth solving.
- Default `evidence_weight`: `4`
- Can it support requirement validity alone: `No`

### `user_proposed_solution`

- Definition: A feature, design, automation, or implementation idea suggested by the user.
- Judgment criteria:
  - the content tells the product what to build or add;
  - it is phrased as a means, not a need outcome;
  - it may still carry useful need clues.
- Example:
  - "Please add a bulk export button on the dashboard."
- Common misreads:
  - treating the proposal itself as the need;
  - discarding it entirely instead of extracting the underlying problem.
- Default `evidence_weight`: `2`
- Can it support requirement validity alone: `No`

### `analyst_inference`

- Definition: A conclusion, interpretation, or hypothesis produced by the analyst from other evidence.
- Judgment criteria:
  - it is clearly marked as interpretation;
  - it points back to supporting evidence IDs;
  - it does not masquerade as raw fact.
- Example:
  - "This may indicate that weekly reporting users need a faster aggregation path."
- Common misreads:
  - presenting inference as observation;
  - adding ungrounded psychology or certainty.
- Default `evidence_weight`: `1`
- Can it support requirement validity alone: `No`

### `internal_secondhand_report`

- Definition: A report from sales, support, success, or another internal team retelling what users allegedly said or did.
- Judgment criteria:
  - the information is not first-hand user evidence;
  - the original user source is missing or incomplete;
  - the report is still captured with source context.
- Example:
  - "Support says enterprise admins often ask for reminders during onboarding."
- Common misreads:
  - counting repeated internal retellings as multiple independent users;
  - promoting internal confidence to direct evidence strength.
- Default `evidence_weight`: `1`
- Can it support requirement validity alone: `No`

## Practical Use Rules

- Use `observed_behavior` for direct actions, even when a quote exists nearby.
- Use `user_verbatim` for the quote itself, not for the analyst summary of the quote.
- Use `historical_behavior` only when the user refers to real past behavior.
- Use `user_proposed_solution` even when the proposal sounds reasonable; do not skip directly to `user_goal` or `need`.
- Use `analyst_inference` only as a derived layer that points back to other evidence.
- Use `internal_secondhand_report` whenever the chain to the original user is broken.
