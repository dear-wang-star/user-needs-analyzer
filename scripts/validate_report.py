#!/usr/bin/env python3
"""Validate need cards, ranking files, and final reports for structure and rule compliance.

Inputs:
- One need-card markdown file or directory.
- Optional ranking markdown file.
- Optional final report markdown file.

Outputs:
- Human-readable output by default.
- Machine-readable output with --json.

Exit codes:
- 0: validation passed with no blocking errors
- 1: validation errors found, or warnings found in --strict mode
- 2: argument errors, file access errors, or unexpected internal errors
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

VALIDITY_VALUES = {
    "validated",
    "conditionally_validated",
    "need_hypothesis",
    "insufficient_evidence",
    "invalid_or_out_of_scope",
}
OVERALL_STRENGTH_VALUES = {"strong", "medium", "weak"}
PRIORITY_VALUES = {"P0", "P1", "P2", "P3"}
SOLUTION_COST_VALUES = {"unknown", "low", "medium", "high"}
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?%")
GENERALIZATION_RE = re.compile(r"\b(all users|most users|users always)\b", re.IGNORECASE)
SOLUTION_WORD_RE = re.compile(r"\b(button|page|module|ai integration|reminder|export)\b", re.IGNORECASE)
LARGE_CUSTOMER_RE = re.compile(r"\b(large customer|enterprise customer|big client)\b", re.IGNORECASE)
NEED_ID_RE = re.compile(r"\bN\d{3,}\b")
EVIDENCE_ID_RE = re.compile(r"\bE\d{3,}\b")


@dataclass(frozen=True)
class ResultItem:
    rule_id: str
    severity: str
    file: str
    location: str
    message: str


@dataclass
class MarkdownTable:
    headers: list[str]
    rows: list[dict[str, str]]
    start_line: int


class ValidationFailure(Exception):
    """Raised for operational failures that prevent reliable validation."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate user-needs markdown reports, cards, and ranking artifacts.",
    )
    parser.add_argument("--need-cards", required=True, help="Need-card markdown file or directory.")
    parser.add_argument("--ranking", help="Optional needs-ranking markdown file.")
    parser.add_argument("--report", help="Optional final-report markdown file.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as a failing result.")
    return parser


def make_item(rule_id: str, severity: str, file: Path | str, location: str, message: str) -> ResultItem:
    return ResultItem(rule_id=rule_id, severity=severity, file=str(file), location=location, message=message)


def read_text(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValidationFailure(f"Unable to read file: {path} ({exc})") from exc
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationFailure(f"Invalid UTF-8 in file: {path} ({exc})") from exc


def parse_scalar(value: str) -> Any:
    stripped = value.strip()
    if stripped == "":
        return ""
    if stripped in {'""', "''"}:
        return ""
    lowered = stripped.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", stripped):
        return int(stripped)
    if (stripped.startswith('"') and stripped.endswith('"')) or (
        stripped.startswith("'") and stripped.endswith("'")
    ):
        return stripped[1:-1]
    return stripped


def parse_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValidationFailure(f"Missing YAML frontmatter start marker in {path}")
    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        raise ValidationFailure(f"Missing YAML frontmatter end marker in {path}")

    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for offset, line in enumerate(lines[1:closing_index], start=2):
        if not line.strip():
            continue
        if line.startswith("  - ") or line.startswith("- "):
            if current_list_key is None:
                raise ValidationFailure(f"Unexpected list item at {path}:{offset}")
            result.setdefault(current_list_key, [])
            result[current_list_key].append(parse_scalar(line.split("- ", 1)[1]))
            continue
        if ":" not in line:
            raise ValidationFailure(f"Unsupported frontmatter syntax at {path}:{offset}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value == "":
            result[key] = []
            current_list_key = key
        else:
            result[key] = parse_scalar(value)
            current_list_key = None
    body = "\n".join(lines[closing_index + 1 :])
    return result, body


def extract_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_heading: str | None = None
    buffer: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(buffer).strip()
            current_heading = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(buffer).strip()
    return sections


def extract_code_blocks(section_text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    lines = section_text.splitlines()
    inside = False
    language = ""
    buffer: list[str] = []
    for line in lines:
        if line.startswith("```"):
            if not inside:
                inside = True
                language = line[3:].strip()
                buffer = []
            else:
                blocks.append((language, "\n".join(buffer).strip()))
                inside = False
                language = ""
                buffer = []
            continue
        if inside:
            buffer.append(line)
    return blocks


def parse_simple_yaml_block(block: str, path: Path, context: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") or line.startswith("- "):
            if current_list_key is None:
                raise ValidationFailure(f"Unexpected list item in {path} ({context})")
            result.setdefault(current_list_key, [])
            result[current_list_key].append(parse_scalar(line.split("- ", 1)[1]))
            continue
        if ":" not in line:
            raise ValidationFailure(f"Unsupported YAML-like syntax in {path} ({context})")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value == "":
            result[key] = []
            current_list_key = key
        else:
            result[key] = parse_scalar(value)
            current_list_key = None
    return result


def parse_markdown_tables(text: str) -> list[MarkdownTable]:
    lines = text.splitlines()
    tables: list[MarkdownTable] = []
    index = 0
    while index < len(lines) - 1:
        header_line = lines[index]
        separator_line = lines[index + 1]
        if "|" not in header_line or "|" not in separator_line:
            index += 1
            continue
        separator_cells = [cell.strip() for cell in separator_line.strip().strip("|").split("|")]
        if not separator_cells or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator_cells if cell):
            index += 1
            continue
        headers = [cell.strip() for cell in header_line.strip().strip("|").split("|")]
        rows: list[dict[str, str]] = []
        row_index = index + 2
        while row_index < len(lines) and "|" in lines[row_index]:
            row_cells = [cell.strip() for cell in lines[row_index].strip().strip("|").split("|")]
            if len(row_cells) != len(headers):
                break
            rows.append(dict(zip(headers, row_cells)))
            row_index += 1
        tables.append(MarkdownTable(headers=headers, rows=rows, start_line=index + 1))
        index = row_index
    return tables


def collect_markdown_files(path: Path) -> list[Path]:
    if not path.exists():
        raise ValidationFailure(f"Path does not exist: {path}")
    if path.is_file():
        return [path]
    return sorted(file_path for file_path in path.rglob("*.md") if file_path.is_file())


def validate_need_card(path: Path, issues: list[ResultItem]) -> dict[str, Any]:
    frontmatter, body = parse_frontmatter(read_text(path), path)
    sections = extract_sections(body)

    required_frontmatter = {
        "need_id",
        "title",
        "validity_verdict",
        "overall_evidence_strength",
        "priority_tier",
        "analysis_date",
    }
    for key in sorted(required_frontmatter):
        if key not in frontmatter:
            issues.append(make_item("RPT001", "error", path, "frontmatter", f"Missing frontmatter key: {key}."))

    required_sections = [
        "1. Need Statement",
        "2. Target User and Segment",
        "3. Context and Trigger",
        "4. User Goal and Task",
        "5. Current Barrier",
        "8. Supporting Evidence",
        "9. Counterevidence and Limitations",
        "10. Evidence Assessment",
        "11. Requirement Validation",
        "12. Product Opportunity",
        "13. Priority Assessment",
        "14. Traceability Checklist",
    ]
    for section_name in required_sections:
        if section_name not in sections:
            issues.append(make_item("RPT002", "error", path, section_name, "Required section is missing."))

    need_id = str(frontmatter.get("need_id", "")).strip()
    validity_verdict = str(frontmatter.get("validity_verdict", "")).strip()
    overall_evidence_strength = str(frontmatter.get("overall_evidence_strength", "")).strip()
    priority_tier = str(frontmatter.get("priority_tier", "")).strip()

    if validity_verdict and validity_verdict not in VALIDITY_VALUES:
        issues.append(make_item("RPT003", "error", path, "frontmatter", f"Invalid validity_verdict: {validity_verdict}."))
    if overall_evidence_strength and overall_evidence_strength not in OVERALL_STRENGTH_VALUES:
        issues.append(
            make_item(
                "RPT004",
                "error",
                path,
                "frontmatter",
                f"Invalid overall_evidence_strength: {overall_evidence_strength}.",
            )
        )
    if priority_tier and priority_tier not in PRIORITY_VALUES:
        issues.append(make_item("RPT005", "error", path, "frontmatter", f"Invalid priority_tier: {priority_tier}."))

    need_statement = sections.get("1. Need Statement", "")
    if SOLUTION_WORD_RE.search(need_statement):
        issues.append(
            make_item(
                "RPT101",
                "warning",
                path,
                "1. Need Statement",
                "Heuristic review: need statement contains solution-shaped wording and may require manual review.",
            )
        )
    for required_phrase in ["When [target_user]", "they need [capability_or_outcome]", "to accomplish [user_task]", "because [current_barrier_or_workaround]"]:
        if required_phrase not in need_statement:
            issues.append(
                make_item(
                    "RPT102",
                    "warning",
                    path,
                    "1. Need Statement",
                    "Heuristic review: need statement may be missing user, context, task, outcome, or barrier structure.",
                )
            )
            break

    def first_yaml(section_name: str) -> dict[str, Any]:
        blocks = extract_code_blocks(sections.get(section_name, ""))
        for language, content in blocks:
            if language in {"yaml", ""}:
                return parse_simple_yaml_block(content, path, section_name)
        return {}

    supporting = first_yaml("8. Supporting Evidence")
    counter = first_yaml("9. Counterevidence and Limitations")
    evidence_assessment = first_yaml("10. Evidence Assessment")
    priority_assessment = first_yaml("13. Priority Assessment")

    validation_section = sections.get("11. Requirement Validation", "")
    validation_blocks = extract_code_blocks(validation_section)
    validation_yaml_blocks = [
        parse_simple_yaml_block(content, path, "11. Requirement Validation")
        for language, content in validation_blocks
        if language in {"yaml", ""}
    ]
    validation_summary = validation_yaml_blocks[-1] if validation_yaml_blocks else {}

    supporting_ids = list(supporting.get("supporting_evidence_ids", []))
    counter_ids = list(counter.get("counterevidence_ids", []))
    representative_verbatim = str(supporting.get("representative_verbatim", ""))
    if representative_verbatim not in {"", "not_available"} and not supporting_ids:
        issues.append(
            make_item(
                "RPT103",
                "warning",
                path,
                "8. Supporting Evidence",
                "Heuristic review: representative_verbatim is present without an evidence anchor.",
            )
        )

    evidence_strength_score = priority_assessment.get("evidence_strength_score")
    frequency_score = priority_assessment.get("frequency_score")
    pain_intensity_score = priority_assessment.get("pain_intensity_score")
    core_user_fit_score = priority_assessment.get("core_user_fit_score")
    relative_priority_score = priority_assessment.get("relative_priority_score")
    solution_cost = priority_assessment.get("solution_cost")
    human_review_required = priority_assessment.get("human_review_required")

    for field_name, value in {
        "frequency_score": frequency_score,
        "pain_intensity_score": pain_intensity_score,
        "evidence_strength_score": evidence_strength_score,
        "core_user_fit_score": core_user_fit_score,
    }.items():
        if not isinstance(value, int) or value < 1 or value > 5:
            issues.append(
                make_item(
                    "RPT006",
                    "error",
                    path,
                    "13. Priority Assessment",
                    f"{field_name} must be an integer from 1 to 5.",
                )
            )

    if isinstance(relative_priority_score, int) and all(isinstance(value, int) for value in [frequency_score, pain_intensity_score, evidence_strength_score, core_user_fit_score]):
        expected_score = frequency_score * pain_intensity_score * evidence_strength_score * core_user_fit_score
        if relative_priority_score != expected_score:
            issues.append(
                make_item(
                    "RPT007",
                    "error",
                    path,
                    "13. Priority Assessment",
                    f"relative_priority_score must equal the score product ({expected_score}).",
                )
            )

    if solution_cost not in SOLUTION_COST_VALUES:
        issues.append(
            make_item("RPT008", "error", path, "13. Priority Assessment", f"Invalid solution_cost: {solution_cost}.")
        )
    if human_review_required not in {True, False, "yes", "no"}:
        issues.append(
            make_item("RPT009", "error", path, "13. Priority Assessment", "human_review_required must exist.")
        )

    if validity_verdict == "validated":
        if overall_evidence_strength == "weak":
            issues.append(
                make_item("RPT010", "error", path, "frontmatter", "validated need cannot have weak overall_evidence_strength.")
            )
        if not supporting_ids:
            issues.append(make_item("RPT011", "error", path, "8. Supporting Evidence", "validated need lacks supporting evidence."))
        if not counter_ids:
            issues.append(make_item("RPT012", "error", path, "9. Counterevidence and Limitations", "validated need lacks counterevidence review."))
        if "segment_difference" not in counter:
            issues.append(make_item("RPT013", "error", path, "9. Counterevidence and Limitations", "validated need lacks segment_difference."))
        if "existing_feature_check" not in counter:
            issues.append(make_item("RPT014", "error", path, "9. Counterevidence and Limitations", "validated need lacks existing_feature_check."))

    if validity_verdict == "conditionally_validated":
        if not str(validation_summary.get("conditions_for_validation", "")).strip():
            issues.append(
                make_item(
                    "RPT015",
                    "error",
                    path,
                    "11. Requirement Validation",
                    "conditionally_validated need must define conditions_for_validation.",
                )
            )
        context_text = sections.get("2. Target User and Segment", "") + "\n" + sections.get("3. Context and Trigger", "")
        if "unknown" in context_text and "segment_scope" not in context_text:
            issues.append(
                make_item(
                    "RPT104",
                    "warning",
                    path,
                    "2. Target User and Segment",
                    "Heuristic review: conditionally_validated need may be missing segment or scenario boundaries.",
                )
            )

    if validity_verdict == "need_hypothesis":
        if priority_tier == "P0":
            issues.append(make_item("RPT016", "error", path, "frontmatter", "need_hypothesis cannot be P0."))
        if not str(validation_summary.get("missing_evidence", "")).strip() and not str(validation_summary.get("next_validation_action", "")).strip():
            issues.append(
                make_item(
                    "RPT017",
                    "error",
                    path,
                    "11. Requirement Validation",
                    "need_hypothesis must define missing_evidence or next_validation_action.",
                )
            )

    if validity_verdict == "insufficient_evidence":
        if priority_tier == "P0":
            issues.append(make_item("RPT018", "error", path, "frontmatter", "insufficient_evidence cannot be P0."))
        if not str(validation_summary.get("missing_evidence", "")).strip():
            issues.append(
                make_item(
                    "RPT019",
                    "error",
                    path,
                    "11. Requirement Validation",
                    "insufficient_evidence must define missing_evidence.",
                )
            )

    if validity_verdict == "invalid_or_out_of_scope":
        issues.append(
            make_item(
                "RPT105",
                "warning",
                path,
                "frontmatter",
                "Heuristic review: invalid_or_out_of_scope needs must later carry exclusion or routing information in ranking/report artifacts.",
            )
        )

    if isinstance(evidence_strength_score, int) and evidence_strength_score == 1 and priority_tier in {"P0", "P1"}:
        issues.append(
            make_item("RPT020", "error", path, "13. Priority Assessment", "evidence_strength_score=1 cannot rank above P2.")
        )
    if priority_tier == "P0":
        if not isinstance(evidence_strength_score, int) or evidence_strength_score < 3:
            issues.append(
                make_item(
                    "RPT021",
                    "warning",
                    path,
                    "13. Priority Assessment",
                    "Heuristic review: P0 appears weakly supported by evidence_strength_score.",
                )
            )
        if validity_verdict in {"need_hypothesis", "insufficient_evidence"}:
            issues.append(
                make_item(
                    "RPT022",
                    "error",
                    path,
                    "frontmatter",
                    "P0 cannot be used with need_hypothesis or insufficient_evidence.",
                )
            )

    if priority_tier == "P3" and isinstance(relative_priority_score, int) and relative_priority_score >= 100:
        issues.append(
            make_item(
                "RPT106",
                "warning",
                path,
                "13. Priority Assessment",
                "Heuristic review: very high score with P3 may need manual reconciliation.",
            )
        )

    opportunity_section = sections.get("12. Product Opportunity", "")
    if SOLUTION_WORD_RE.search(opportunity_section):
        issues.append(
            make_item(
                "RPT107",
                "warning",
                path,
                "12. Product Opportunity",
                "Heuristic review: opportunity language may be too solution-specific.",
            )
        )

    return {
        "need_id": need_id,
        "validity_verdict": validity_verdict,
        "priority_tier": priority_tier,
        "evidence_strength_score": evidence_strength_score,
    }


def validate_ranking(path: Path, known_need_ids: set[str], issues: list[ResultItem]) -> set[str]:
    text = read_text(path)
    tables = parse_markdown_tables(text)
    ranking_table = next(
        (
            table
            for table in tables
            if {"rank", "need_id", "validity_verdict", "frequency_score", "pain_intensity_score", "evidence_strength_score", "core_user_fit_score", "relative_priority_score", "priority_tier", "solution_cost", "human_review_required"}.issubset(set(table.headers))
        ),
        None,
    )
    if ranking_table is None:
        raise ValidationFailure(f"Could not parse the formal ranking table in {path}")

    ranked_need_ids: set[str] = set()
    validation_queue = next(
        (
            table
            for table in tables
            if {"need_id", "current_signal", "missing_evidence", "recommended_validation", "decision_deadline"}.issubset(set(table.headers))
        ),
        None,
    )
    validation_queue_need_ids = {row.get("need_id", "").strip() for row in validation_queue.rows} if validation_queue else set()

    excluded_table = next(
        (
            table
            for table in tables
            if {"need_id_or_feedback_id", "exclusion_reason", "classification", "whether_to_route_elsewhere"}.issubset(set(table.headers))
        ),
        None,
    )
    excluded_need_ids = {
        row.get("need_id_or_feedback_id", "").strip()
        for row in excluded_table.rows
        if NEED_ID_RE.fullmatch(row.get("need_id_or_feedback_id", "").strip())
    } if excluded_table else set()

    for offset, row in enumerate(ranking_table.rows, start=ranking_table.start_line + 2):
        need_id = row.get("need_id", "").strip()
        ranked_need_ids.add(need_id)
        verdict = row.get("validity_verdict", "").strip()
        priority_tier = row.get("priority_tier", "").strip()
        solution_cost = row.get("solution_cost", "").strip()
        human_review_required = row.get("human_review_required", "").strip().lower()
        if need_id not in known_need_ids:
            issues.append(make_item("RPT023", "error", path, f"line {offset}", f"Ranking contains unknown need_id {need_id}."))
        if verdict not in VALIDITY_VALUES:
            issues.append(make_item("RPT024", "error", path, f"line {offset}", f"Invalid validity_verdict: {verdict}."))
        if priority_tier not in PRIORITY_VALUES:
            issues.append(make_item("RPT025", "error", path, f"line {offset}", f"Invalid priority_tier: {priority_tier}."))
        if solution_cost not in SOLUTION_COST_VALUES:
            issues.append(make_item("RPT026", "error", path, f"line {offset}", f"Invalid solution_cost: {solution_cost}."))
        if human_review_required not in {"yes", "no", "true", "false"}:
            issues.append(make_item("RPT027", "error", path, f"line {offset}", "human_review_required must exist."))

        try:
            frequency_score = int(row.get("frequency_score", ""))
            pain_score = int(row.get("pain_intensity_score", ""))
            evidence_score = int(row.get("evidence_strength_score", ""))
            core_user_fit_score = int(row.get("core_user_fit_score", ""))
            relative_priority_score = int(row.get("relative_priority_score", ""))
        except ValueError:
            issues.append(make_item("RPT028", "error", path, f"line {offset}", "Ranking scores must be integers."))
            continue

        for field_name, value in {
            "frequency_score": frequency_score,
            "pain_intensity_score": pain_score,
            "evidence_strength_score": evidence_score,
            "core_user_fit_score": core_user_fit_score,
        }.items():
            if value < 1 or value > 5:
                issues.append(
                    make_item("RPT029", "error", path, f"line {offset}", f"{field_name} must be between 1 and 5.")
                )

        expected_score = frequency_score * pain_score * evidence_score * core_user_fit_score
        if relative_priority_score != expected_score:
            issues.append(
                make_item("RPT030", "error", path, f"line {offset}", f"relative_priority_score must equal {expected_score}.")
            )
        if evidence_score == 1 and priority_tier in {"P0", "P1"}:
            issues.append(
                make_item("RPT031", "error", path, f"line {offset}", "evidence_strength_score=1 cannot rank above P2.")
            )
        if verdict == "need_hypothesis" and priority_tier == "P0":
            issues.append(make_item("RPT032", "error", path, f"line {offset}", "need_hypothesis cannot enter P0."))
        if verdict == "insufficient_evidence" and priority_tier == "P0":
            issues.append(make_item("RPT033", "error", path, f"line {offset}", "insufficient_evidence cannot enter P0."))
        if verdict == "insufficient_evidence" and need_id not in validation_queue_need_ids:
            issues.append(
                make_item(
                    "RPT108",
                    "warning",
                    path,
                    f"line {offset}",
                    "Heuristic review: insufficient_evidence need is ranked formally but not found in the validation queue.",
                )
            )
        if verdict == "invalid_or_out_of_scope":
            issues.append(
                make_item(
                    "RPT034",
                    "error",
                    path,
                    f"line {offset}",
                    "invalid_or_out_of_scope must not appear in the formal ranking table.",
                )
            )
        if priority_tier == "P0" and evidence_score < 3:
            issues.append(
                make_item(
                    "RPT109",
                    "warning",
                    path,
                    f"line {offset}",
                    "Heuristic review: P0 looks inconsistent with a low evidence_strength_score.",
                )
            )

    if excluded_table:
        for offset, row in enumerate(excluded_table.rows, start=excluded_table.start_line + 2):
            classification = row.get("classification", "").strip()
            if not classification:
                issues.append(make_item("RPT035", "error", path, f"line {offset}", "Excluded item is missing classification."))

    return excluded_need_ids


def validate_report(path: Path, known_need_ids: set[str], issues: list[ResultItem]) -> None:
    frontmatter, body = parse_frontmatter(read_text(path), path)
    required_frontmatter = {"analysis_id", "title", "analysis_date", "status", "analyst"}
    for key in sorted(required_frontmatter):
        if key not in frontmatter:
            issues.append(make_item("RPT036", "error", path, "frontmatter", f"Missing report frontmatter key: {key}."))

    required_sections = [
        "1. Executive Summary",
        "2. Scope and Inputs",
        "3. Method",
        "4. Evidence Overview",
        "5. Key User Needs",
        "6. Detailed Findings",
        "7. Cross-User Patterns",
        "8. Non-Need Classifications",
        "9. Needs Ranking",
        "10. Recommended Next Actions",
        "11. Limitations",
        "12. Traceability Appendix",
        "13. Completion Checklist",
    ]
    sections = extract_sections(body)
    for section_name in required_sections:
        if section_name not in sections:
            issues.append(make_item("RPT037", "error", path, section_name, "Required report section is missing."))

    tables = parse_markdown_tables(body)
    key_table = next(
        (
            table
            for table in tables
            if {"need_id", "need_title", "target_segment", "validity_verdict", "overall_evidence_strength", "priority_tier", "key_evidence_ids"}.issubset(set(table.headers))
        ),
        None,
    )
    if key_table is None:
        issues.append(make_item("RPT038", "error", path, "5. Key User Needs", "Key user needs summary table is missing."))
    else:
        for offset, row in enumerate(key_table.rows, start=key_table.start_line + 2):
            need_id = row.get("need_id", "").strip()
            if need_id not in known_need_ids:
                issues.append(make_item("RPT039", "error", path, f"line {offset}", f"Report references unknown need_id {need_id}."))
            if row.get("validity_verdict", "").strip() not in VALIDITY_VALUES:
                issues.append(make_item("RPT040", "error", path, f"line {offset}", "Invalid validity_verdict in report summary table."))
            if row.get("overall_evidence_strength", "").strip() not in OVERALL_STRENGTH_VALUES:
                issues.append(
                    make_item("RPT041", "error", path, f"line {offset}", "Invalid overall_evidence_strength in report summary table.")
                )
            if row.get("priority_tier", "").strip() not in PRIORITY_VALUES:
                issues.append(make_item("RPT042", "error", path, f"line {offset}", "Invalid priority_tier in report summary table."))
            if not EVIDENCE_ID_RE.findall(row.get("key_evidence_ids", "")):
                issues.append(make_item("RPT043", "error", path, f"line {offset}", "Report summary row is missing key_evidence_ids."))

    if PERCENT_RE.search(body):
        issues.append(
            make_item(
                "RPT110",
                "warning",
                path,
                "report",
                "Heuristic review: percentage sign detected; confirm no small sample was generalized to a population claim.",
            )
        )
    if GENERALIZATION_RE.search(body):
        issues.append(
            make_item(
                "RPT111",
                "warning",
                path,
                "report",
                "Heuristic review: generalized user language detected; confirm it is supported by evidence.",
            )
        )
    if LARGE_CUSTOMER_RE.search(body):
        issues.append(
            make_item(
                "RPT112",
                "warning",
                path,
                "report",
                "Heuristic review: large-customer wording detected; confirm it was not generalized into a common need.",
            )
        )
    if not re.search(r"###\s+need_id:\s*N\d{3,}", body):
        issues.append(
            make_item(
                "RPT044",
                "error",
                path,
                "6. Detailed Findings",
                "Detailed findings do not contain need_id-labelled entries.",
            )
        )
    if "known_biases" not in sections.get("2. Scope and Inputs", "") or "sample_limitations" not in sections.get("11. Limitations", ""):
        issues.append(
            make_item(
                "RPT113",
                "warning",
                path,
                "11. Limitations",
                "Heuristic review: source bias or limitation fields may not be fully documented.",
            )
        )


def summarize(script_name: str, issues: list[ResultItem], summary: dict[str, Any], json_mode: bool) -> None:
    if json_mode:
        grouped = {"errors": [], "warnings": [], "info": []}
        for item in issues:
            grouped[f"{item.severity}s"].append(asdict(item))
        print(
            json.dumps(
                {
                    "script": script_name,
                    "status": summary["status"],
                    "errors": grouped["errors"],
                    "warnings": grouped["warnings"],
                    "info": grouped["info"],
                    "summary": summary,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    status_word = {"passed": "PASS", "passed_with_warnings": "WARN", "failed": "FAIL", "internal_error": "FAIL"}[
        summary["status"]
    ]
    print(f"{status_word} {script_name}")
    print(
        f"files={summary['checked_file_count']} errors={summary['error_count']} warnings={summary['warning_count']}"
    )
    for item in issues:
        print(f"[{item.severity.upper()}] {item.rule_id} {item.file}:{item.location} - {item.message}")
    print("Summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def compute_status(error_count: int, warning_count: int, strict: bool) -> tuple[str, int]:
    if error_count > 0:
        return "failed", 1
    if warning_count > 0:
        return ("failed", 1) if strict else ("passed_with_warnings", 0)
    return "passed", 0


def run(args: argparse.Namespace) -> int:
    need_cards_path = Path(args.need_cards)
    ranking_path = Path(args.ranking) if args.ranking else None
    report_path = Path(args.report) if args.report else None

    if not need_cards_path.exists():
        raise ValidationFailure(f"--need-cards path does not exist: {need_cards_path}")
    if ranking_path and not ranking_path.exists():
        raise ValidationFailure(f"--ranking path does not exist: {ranking_path}")
    if report_path and not report_path.exists():
        raise ValidationFailure(f"--report path does not exist: {report_path}")

    issues: list[ResultItem] = []
    need_card_files = collect_markdown_files(need_cards_path)
    if not need_card_files:
        raise ValidationFailure(f"No markdown need-card files found under {need_cards_path}")

    need_card_results = [validate_need_card(path, issues) for path in need_card_files]
    known_need_ids = {result["need_id"] for result in need_card_results if result["need_id"]}
    excluded_need_ids: set[str] = set()
    if ranking_path:
        excluded_need_ids = validate_ranking(ranking_path, known_need_ids, issues)
    if report_path:
        validate_report(report_path, known_need_ids, issues)

    error_count = sum(1 for item in issues if item.severity == "error")
    warning_count = sum(1 for item in issues if item.severity == "warning")
    status, exit_code = compute_status(error_count, warning_count, args.strict)
    summary = {
        "status": status,
        "checked_file_count": len(need_card_files) + int(bool(ranking_path)) + int(bool(report_path)),
        "error_count": error_count,
        "warning_count": warning_count,
        "need_card_count": len(need_card_files),
        "known_need_ids": sorted(known_need_ids),
        "excluded_need_ids": sorted(excluded_need_ids),
    }
    summarize("validate_report.py", issues, summary, args.json)
    return exit_code


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return run(args)
    except ValidationFailure as exc:
        issues = [make_item("RPT000", "error", "", "path", str(exc))]
        summary = {"status": "internal_error", "checked_file_count": 0, "error_count": 1, "warning_count": 0}
        summarize("validate_report.py", issues, summary, args.json)
        return 2
    except Exception as exc:  # pragma: no cover - defensive fallback
        issues = [make_item("RPT999", "error", "", "internal", f"Unexpected internal error: {exc}")]
        summary = {"status": "internal_error", "checked_file_count": 0, "error_count": 1, "warning_count": 0}
        summarize("validate_report.py", issues, summary, args.json)
        return 2


if __name__ == "__main__":
    sys.exit(main())
