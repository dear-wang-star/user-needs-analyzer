# user-needs-analyzer
An evidence-based skill for analyzing user feedback and extracting validated user needs.

V1.0 is available for analyzing interviews, user feedback, support tickets, and survey free-text responses.

## Core Capabilities

- Evidence classification and traceability
- Separation of real user needs from user-proposed solutions
- Requirement validity judgment
- Counterexample review and user-segment difference checks
- Relative need-side prioritization

## Usage

```text
Please use user-needs-analyzer to analyze the following user feedback,
and follow SKILL.md to output an evidence table, user need cards,
needs ranking, and an analysis report.
```

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
│   │   └── .gitkeep
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
