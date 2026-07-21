# Need vs Solution Rules

This file defines how to distinguish a real user need from adjacent statements and non-need issues.

## Term Definitions

### User voice

The raw expression from a user, including quotes, complaints, requests, or descriptions. It is input, not a conclusion.

### Pain point

A friction, barrier, risk, delay, or failure that makes a task harder or more costly.

### Goal

The task result the user is trying to achieve.

### Need

A capability or outcome the user must obtain in a specific context to complete a real task and reduce real cost or loss.

### Product opportunity

A potentially valuable area for product response, discovered from one or more needs. An opportunity is broader than a single need and still does not prescribe one solution.

### Solution

A proposed way to solve a problem. This may come from the user, the analyst, or the product team.

### Feature

A concrete product capability or implementation element. Features are one possible solution form.

### Bug

Something expected to work in the current product behavior but failing, broken, incorrect, or unavailable.

### Usability issue

The capability may exist, but users struggle to find, understand, trust, or complete it because of interface or interaction friction.

### Operations issue

A non-product workflow problem such as billing policy, account setup, permissions process, handoff delay, or internal process friction.

### Service issue

A support, customer success, fulfillment, or response-quality problem rather than a core product need.

### Training or awareness issue

The product may already support the goal, but the user does not know it exists or does not understand how to use it.

## Core Distinction Rules

- User voice is not automatically a need.
- A pain point is not automatically a feature request.
- A feature request is not automatically the right solution.
- A bug or usability issue is not automatically a missing need.
- A repeated internal request is not automatically independent user demand.

## Analysis Chain for Restoring a Real Need

Always analyze a surface request through this chain:

User quote
→ Situation
→ Goal task
→ Barrier
→ Current workaround
→ Workaround cost
→ Desired outcome
→ Standard need statement

Use this fixed need statement form:

When `[target user]` is in `[specific situation]`,
to complete `[goal task]`,
the user needs `[capability or outcome]`,
because the current `[barrier or workaround]` causes `[cost or loss]`.

## Classification Questions

Ask these questions in order:

1. Is the user describing what they want to achieve, or what they want us to build?
2. Is the problem that something is broken, hard to use, operationally blocked, or not understood?
3. Is there evidence of a real recurring task and a meaningful cost?
4. Is the requested feature only one possible means to the desired outcome?
5. Does the issue belong to the product's core scope?

## Worked Examples

### Example 1: "I want bulk export."

- Surface expression:
  - a feature request
- What cannot be concluded directly:
  - that bulk export is the correct solution;
  - that many users share the same problem;
  - that the real need is "export faster" without scenario evidence.
- Evidence still needed:
  - which user segment needs it;
  - what task they are trying to complete;
  - frequency;
  - current workaround;
  - cost of the workaround.
- Possible real need:
  - users need to transfer multiple records out of the system efficiently for a recurring downstream workflow.
- May also be a non-need issue:
  - training issue if bulk handling already exists but is hard to discover;
  - operations issue if the export is blocked by permission settings.

Analysis chain:
- User quote:
  - "I want bulk export."
- Situation:
  - a finance manager is preparing a weekly reconciliation pack.
- Goal task:
  - send one combined report for many projects.
- Barrier:
  - current export works one project at a time.
- Current workaround:
  - repeated single exports plus spreadsheet merging.
- Workaround cost:
  - 40 minutes per week and error risk.
- Desired outcome:
  - one efficient transfer step for grouped data.
- Standard need statement:
  - When a finance manager is preparing a weekly reconciliation pack,
    to complete a multi-project reporting task,
    the user needs an efficient way to transfer grouped data out of the product,
    because the current one-by-one export workflow causes repeated manual effort and error risk.

### Example 2: "You should add reminders."

- Surface expression:
  - a solution suggestion
- What cannot be concluded directly:
  - that reminders are the real need;
  - that forgetting is the main problem;
  - that the problem belongs to the product rather than process ownership.
- Evidence still needed:
  - what users are trying to avoid missing;
  - whether missed steps are common;
  - whether current cues exist but are ineffective;
  - whether users rely on external reminders already.
- Possible real need:
  - users need reliable task-state visibility or timely prompts to avoid missing time-sensitive steps.
- May also be a non-need issue:
  - training issue if reminder settings already exist;
  - operations issue if the true problem is unclear responsibility between teams.

### Example 3: "Please add AI."

- Surface expression:
  - a broad solution request
- What cannot be concluded directly:
  - that AI is needed;
  - that automation is the main problem;
  - that users will trust or adopt an AI feature.
- Evidence still needed:
  - what task is too slow, difficult, or repetitive;
  - what current workaround exists;
  - what quality threshold matters;
  - whether users want speed, guidance, summarization, or decision support.
- Possible real need:
  - users need help reducing manual synthesis effort or decision latency in a repeated analysis task.
- May also be a non-need issue:
  - product marketing expectation rather than grounded user need;
  - training issue if the existing workflow already supports the task adequately.

### Example 4: "I can't find the save button."

- Surface expression:
  - a usability complaint
- Default judgment:
  - first classify it as a usability issue or information-architecture issue;
  - it may also be a copy, visual hierarchy, interaction feedback, or training/cognition issue;
  - if the button exists but users cannot find it, do not elevate it directly into a new user need.
- What cannot be concluded directly:
  - that users need a new save feature;
  - that the workflow itself is unnecessary;
  - that the user wants more functionality.
- Evidence still needed:
  - whether save exists;
  - whether more than one user fails the same step;
  - whether the issue is label, placement, state feedback, or permissions.
- Possible real need:
  - only as a higher-level hypothesis, users may need confirmation that content has been safely saved;
  - users may need lower loss risk when system state is not transparent;
  - this should be elevated only if multiple scenarios repeatedly show "cannot confirm the result" problems.
- May also be a non-need issue:
  - usability issue if save exists but is hidden or poorly signaled;
  - bug if save is missing only in a broken state.

### Example 5: "The page won't open."

- Surface expression:
  - a failure report
- What cannot be concluded directly:
  - that users need a new capability;
  - that the page itself is unimportant;
  - that the problem is strategic product scope.
- Evidence still needed:
  - whether this is a reproducible failure;
  - how many users are affected;
  - whether the root cause is outage, permissions, browser issue, or workflow dependency.
- Possible real need:
  - often none; the immediate issue is service availability or defect recovery.
- May also be a non-need issue:
  - bug if the page is broken;
  - operations issue if access provisioning failed;
  - service issue if the incident response path is the true problem.

## Boundary Reminders

- Not every strong complaint is a need.
- Not every feature request is wrong; it is simply not the final conclusion.
- A need must still be stated as a user outcome in context, not as a UI element.
- If the product already satisfies the need and the issue is awareness, classify it as training or discoverability first.
