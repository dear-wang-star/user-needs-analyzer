# user-needs-analyzer

`user-needs-analyzer` is a V1.0 skill for turning raw user materials into traceable user-need conclusions.

## Project Purpose

Use this repository when you need to analyze raw feedback and decide whether it supports a real user need rather than jumping directly to a feature idea.

## Supported Input Types

- User interview notes and verbatim quotes
- Product feedback and feature requests
- Support tickets and service-adjacent feedback
- Survey free-text answers
- Mixed qualitative evidence sets with stable source IDs

## Core Analysis Capabilities

- Evidence classification and evidence-to-need traceability
- Separation of user needs from user-proposed solutions
- Requirement validity judgment using fixed verdict labels
- Counterexample review and user-segment difference checks
- Relative need-side prioritization

## Output Artifacts

- `evidence-table.md`
- `need-card-Nxxx.md`
- `needs-ranking.md`
- `final-report.md`

## Minimal Usage Example

```text
Please use user-needs-analyzer to analyze the following user feedback,
and follow SKILL.md to output an evidence table, user need cards,
needs ranking, and an analysis report.
```

## Validation Commands

Run the built-in validation scripts from the repository root:

```bash
python3 scripts/validate_input.py PATH_TO_RAW_INPUT --json
python3 scripts/validate_evidence_links.py \
  --evidence-table PATH_TO_EVIDENCE_TABLE \
  --need-cards PATH_TO_NEED_CARD_OR_DIR \
  --ranking PATH_TO_NEEDS_RANKING \
  --report PATH_TO_FINAL_REPORT \
  --json
python3 scripts/validate_report.py \
  --need-cards PATH_TO_NEED_CARD_OR_DIR \
  --ranking PATH_TO_NEEDS_RANKING \
  --report PATH_TO_FINAL_REPORT \
  --json
```

## V1.0 Boundaries

V1.0 can:
- classify evidence and distinguish needs from adjacent issues;
- judge whether a candidate need is validated, conditionally validated, hypothetical, insufficiently supported, or out of scope;
- rank candidate needs on the demand side only.

V1.0 does not:
- prove market size or business opportunity size;
- decide engineering delivery order or product roadmap sequencing;
- auto-generate a final feature specification from limited evidence.

## Structure

```text
.
├── AGENTS.md
├── IMPLEMENTATION_PLAN.md
├── LICENSE
├── README.md
├── SKILL.md
├── examples
│   ├── interview-synthesis
│   │   └── .gitkeep
│   ├── single-feature-request
│   │   ├── evidence-table.md
│   │   ├── final-report.md
│   │   ├── need-card-N001.md
│   │   ├── needs-ranking.md
│   │   └── raw-feedback.txt
│   └── support-ticket-analysis
│       └── .gitkeep
├── references
│   ├── evidence-strength.md
│   ├── evidence-taxonomy.md
│   ├── need-vs-solution.md
│   ├── prioritization-rules.md
│   └── requirement-validation.md
├── scripts
│   ├── validate_evidence_links.py
│   ├── validate_input.py
│   └── validate_report.py
├── templates
│   ├── evidence-table.md
│   ├── final-report.md
│   ├── needs-ranking.md
│   └── user-need-card.md
└── tests
    ├── insufficient-evidence-cases.json
    ├── normal-cases.json
    └── trap-cases.json
```
