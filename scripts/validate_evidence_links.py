#!/usr/bin/env python3
"""Validate traceability links across evidence, need cards, ranking, and report files.

Inputs:
- Evidence table markdown file.
- One need-card file or a directory of need-card markdown files.
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

EVIDENCE_ID_RE = re.compile(r"\bE\d{3,}\b")
NEED_ID_RE = re.compile(r"\bN\d{3,}\b")
PARTICIPANT_ID_RE = re.compile(r"\bP\d{3,}\b")
VALIDITY_VALUES = {
    "validated",
    "conditionally_validated",
    "need_hypothesis",
    "insufficient_evidence",
    "invalid_or_out_of_scope",
}
OVERALL_STRENGTH_VALUES = {"strong", "medium", "weak"}
PRIORITY_VALUES = {"P0", "P1", "P2", "P3"}


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


@dataclass
class NeedCard:
    path: Path
    frontmatter: dict[str, Any]
    sections: dict[str, str]
    supporting_evidence_ids: list[str]
    counterevidence_ids: list[str]
    proposing_evidence_ids: list[str]
    representative_verbatim: str
    users_without_the_problem: str
    contradictory_behavior: str
    segment_difference: str
    existing_feature_check: str


class ValidationFailure(Exception):
    """Raised when the script cannot continue safely."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate evidence-to-need traceability across repository analysis artifacts.",
    )
    parser.add_argument("--evidence-table", required=True, help="Path to the evidence-table markdown file.")
    parser.add_argument("--need-cards", required=True, help="Path to a need-card markdown file or directory.")
    parser.add_argument("--ranking", help="Optional path to the needs-ranking markdown file.")
    parser.add_argument("--report", help="Optional path to the final-report markdown file.")
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

    frontmatter_lines = lines[1:closing_index]
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for offset, line in enumerate(frontmatter_lines, start=2):
        if not line.strip():
            continue
        if line.startswith("  - ") or line.startswith("- "):
            if current_list_key is None:
                raise ValidationFailure(f"Unexpected list item in frontmatter at {path}:{offset}")
            result.setdefault(current_list_key, [])
            result[current_list_key].append(parse_scalar(line.split("- ", 1)[1]))
            continue
        if ":" not in line:
            raise ValidationFailure(f"Unsupported frontmatter syntax at {path}:{offset}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            raise ValidationFailure(f"Empty frontmatter key at {path}:{offset}")
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
    for offset, line in enumerate(block.splitlines(), start=1):
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


def first_table_with_headers(tables: list[MarkdownTable], required_headers: set[str]) -> MarkdownTable | None:
    for table in tables:
        if required_headers.issubset(set(table.headers)):
            return table
    return None


def collect_markdown_files(path: Path) -> list[Path]:
    if not path.exists():
        raise ValidationFailure(f"Path does not exist: {path}")
    if path.is_file():
        return [path]
    return sorted(file_path for file_path in path.rglob("*.md") if file_path.is_file())


def parse_need_card(path: Path) -> NeedCard:
    frontmatter, body = parse_frontmatter(read_text(path), path)
    sections = extract_sections(body)

    def parse_first_yaml(section_name: str) -> dict[str, Any]:
        blocks = extract_code_blocks(sections.get(section_name, ""))
        for language, content in blocks:
            if language in {"yaml", ""}:
                return parse_simple_yaml_block(content, path, section_name)
        return {}

    solutions = parse_first_yaml("7. User-Proposed Solutions")
    supporting = parse_first_yaml("8. Supporting Evidence")
    counter = parse_first_yaml("9. Counterevidence and Limitations")

    return NeedCard(
        path=path,
        frontmatter=frontmatter,
        sections=sections,
        supporting_evidence_ids=list(supporting.get("supporting_evidence_ids", [])),
        counterevidence_ids=list(counter.get("counterevidence_ids", [])),
        proposing_evidence_ids=list(solutions.get("proposing_evidence_ids", [])),
        representative_verbatim=str(supporting.get("representative_verbatim", "")),
        users_without_the_problem=str(counter.get("users_without_the_problem", "")),
        contradictory_behavior=str(counter.get("contradictory_behavior", "")),
        segment_difference=str(counter.get("segment_difference", "")),
        existing_feature_check=str(counter.get("existing_feature_check", "")),
    )


def parse_id_list(value: str) -> list[str]:
    if value.strip() in {"", "unassigned", "none_found_in_current_material"}:
        return []
    return NEED_ID_RE.findall(value) or EVIDENCE_ID_RE.findall(value)


def validate_evidence_table(path: Path, need_ids: set[str], issues: list[ResultItem]) -> dict[str, dict[str, str]]:
    tables = parse_markdown_tables(read_text(path))
    table = first_table_with_headers(
        tables,
        {
            "evidence_id",
            "participant_id",
            "source_reference",
            "evidence_type",
            "raw_evidence",
            "analyst_interpretation",
            "linked_need_ids",
            "privacy_check",
        },
    )
    if table is None:
        raise ValidationFailure(f"Could not find the standard evidence table in {path}")

    evidence_rows: dict[str, dict[str, str]] = {}
    for offset, row in enumerate(table.rows, start=table.start_line + 2):
        evidence_id = row.get("evidence_id", "").strip()
        if not evidence_id:
            continue
        if not EVIDENCE_ID_RE.fullmatch(evidence_id):
            issues.append(make_item("TRC004", "error", path, f"line {offset}", "Invalid evidence_id format."))
            continue
        if evidence_id in evidence_rows:
            issues.append(make_item("TRC005", "error", path, f"line {offset}", f"Duplicate evidence_id: {evidence_id}."))
            continue

        participant_id = row.get("participant_id", "").strip()
        if participant_id not in {"", "not_available"} and not PARTICIPANT_ID_RE.fullmatch(participant_id):
            issues.append(
                make_item("TRC007", "error", path, f"line {offset}", f"Invalid participant_id format: {participant_id}.")
            )
        if participant_id == "not_available":
            issues.append(
                make_item("TRC107", "warning", path, f"line {offset}", "participant_id is not_available; manual review may be needed.")
            )

        raw_evidence = row.get("raw_evidence", "").strip()
        if raw_evidence in {"", '""'}:
            issues.append(make_item("TRC006", "error", path, f"line {offset}", f"{evidence_id} has empty raw_evidence."))

        analyst_interpretation = row.get("analyst_interpretation", "").strip()
        if analyst_interpretation and analyst_interpretation == raw_evidence and analyst_interpretation != "not_available":
            issues.append(
                make_item(
                    "TRC011",
                    "error",
                    path,
                    f"line {offset}",
                    f"{evidence_id} appears to use the same content for raw_evidence and analyst_interpretation.",
                )
            )

        linked_need_value = row.get("linked_need_ids", "").strip()
        linked_ids = [] if linked_need_value == "unassigned" else NEED_ID_RE.findall(linked_need_value)
        if linked_need_value == "unassigned":
            issues.append(
                make_item("TRC108", "warning", path, f"line {offset}", f"{evidence_id} is still unassigned to any need_id.")
            )
        elif not linked_ids and linked_need_value:
            issues.append(
                make_item("TRC008", "error", path, f"line {offset}", f"{evidence_id} has invalid linked_need_ids format.")
            )
        for linked_id in linked_ids:
            if linked_id not in need_ids:
                issues.append(
                    make_item(
                        "TRC009",
                        "error",
                        path,
                        f"line {offset}",
                        f"{evidence_id} links to missing need_id {linked_id}.",
                    )
                )

        for field_name, field_value in row.items():
            matches = set(EVIDENCE_ID_RE.findall(field_value))
            if len(matches) > 1:
                issues.append(
                    make_item(
                        "TRC010",
                        "error",
                        path,
                        f"line {offset}",
                        f"{field_name} appears to mix multiple evidence IDs: {', '.join(sorted(matches))}.",
                    )
                )

        source_reference = row.get("source_reference", "").strip()
        if not source_reference or source_reference in {"unknown", "not_available"}:
            issues.append(
                make_item("TRC109", "warning", path, f"line {offset}", f"{evidence_id} has insufficient source_reference.")
            )

        context = row.get("context", "").strip()
        if not context or context == "unknown":
            issues.append(make_item("TRC110", "warning", path, f"line {offset}", f"{evidence_id} is missing context."))

        privacy_check = row.get("privacy_check", "").strip()
        if not privacy_check:
            issues.append(make_item("TRC012", "error", path, f"line {offset}", f"{evidence_id} is missing privacy_check."))
        elif privacy_check == "needs_review":
            issues.append(
                make_item("TRC111", "warning", path, f"line {offset}", f"{evidence_id} requires privacy review.")
            )

        evidence_rows[evidence_id] = row
    return evidence_rows


def validate_need_cards(
    need_cards: list[NeedCard],
    evidence_ids: set[str],
    issues: list[ResultItem],
) -> tuple[set[str], dict[str, NeedCard]]:
    need_id_to_card: dict[str, NeedCard] = {}
    for card in need_cards:
        need_id = str(card.frontmatter.get("need_id", "")).strip()
        if not NEED_ID_RE.fullmatch(need_id):
            issues.append(make_item("TRC013", "error", card.path, "frontmatter", "Invalid or missing need_id."))
            continue
        if need_id in need_id_to_card:
            issues.append(make_item("TRC014", "error", card.path, "frontmatter", f"Duplicate need_id: {need_id}."))
            continue

        need_id_to_card[need_id] = card

        verdict = str(card.frontmatter.get("validity_verdict", "")).strip()
        if verdict not in VALIDITY_VALUES:
            issues.append(
                make_item("TRC015", "error", card.path, "frontmatter", f"Invalid validity_verdict: {verdict}.")
            )

        strength = str(card.frontmatter.get("overall_evidence_strength", "")).strip()
        if strength not in OVERALL_STRENGTH_VALUES:
            issues.append(
                make_item(
                    "TRC016",
                    "error",
                    card.path,
                    "frontmatter",
                    f"Invalid overall_evidence_strength: {strength}.",
                )
            )

        tier = str(card.frontmatter.get("priority_tier", "")).strip()
        if tier not in PRIORITY_VALUES:
            issues.append(make_item("TRC017", "error", card.path, "frontmatter", f"Invalid priority_tier: {tier}."))

        if not card.supporting_evidence_ids:
            issues.append(
                make_item("TRC018", "error", card.path, "8. Supporting Evidence", f"{need_id} is missing supporting_evidence_ids.")
            )
        if not card.counterevidence_ids:
            issues.append(
                make_item(
                    "TRC019",
                    "error",
                    card.path,
                    "9. Counterevidence and Limitations",
                    f"{need_id} is missing counterevidence_ids.",
                )
            )

        for evidence_id in card.supporting_evidence_ids:
            if evidence_id not in evidence_ids:
                issues.append(
                    make_item("TRC020", "error", card.path, "8. Supporting Evidence", f"{need_id} references missing evidence_id {evidence_id}.")
                )
        for evidence_id in card.proposing_evidence_ids:
            if evidence_id not in evidence_ids:
                issues.append(
                    make_item("TRC021", "error", card.path, "7. User-Proposed Solutions", f"{need_id} references missing evidence_id {evidence_id}.")
                )
        for evidence_id in card.counterevidence_ids:
            if evidence_id == "none_found_in_current_material":
                continue
            if evidence_id not in evidence_ids:
                issues.append(
                    make_item(
                        "TRC022",
                        "error",
                        card.path,
                        "9. Counterevidence and Limitations",
                        f"{need_id} references missing counterevidence_id {evidence_id}.",
                    )
                )

        if card.representative_verbatim not in {"", "not_available"} and not card.supporting_evidence_ids:
            issues.append(
                make_item(
                    "TRC112",
                    "warning",
                    card.path,
                    "8. Supporting Evidence",
                    f"{need_id} has representative_verbatim but no supporting_evidence_ids to anchor it.",
                )
            )

        if verdict in {"validated", "conditionally_validated"} and not card.supporting_evidence_ids:
            issues.append(
                make_item(
                    "TRC023",
                    "error",
                    card.path,
                    "frontmatter",
                    f"{need_id} uses {verdict} without supporting evidence.",
                )
            )

        if verdict == "validated":
            counter_checked = bool(card.counterevidence_ids) and (
                card.users_without_the_problem
                or card.contradictory_behavior
                or card.segment_difference
                or "none_found_in_current_material" in card.counterevidence_ids
            )
            if not counter_checked:
                issues.append(
                    make_item(
                        "TRC024",
                        "error",
                        card.path,
                        "9. Counterevidence and Limitations",
                        f"{need_id} is validated but lacks counterexample review data.",
                    )
                )
            if card.counterevidence_ids == ["none_found_in_current_material"]:
                issues.append(
                    make_item(
                        "TRC113",
                        "warning",
                        card.path,
                        "9. Counterevidence and Limitations",
                        f"{need_id} reports no counterevidence found; manual review should confirm this was checked rather than assumed.",
                    )
                )

    return set(need_id_to_card), need_id_to_card


def validate_ranking(
    ranking_path: Path,
    need_ids: set[str],
    issues: list[ResultItem],
) -> tuple[set[str], set[str]]:
    tables = parse_markdown_tables(read_text(ranking_path))
    ranking_table = first_table_with_headers(
        tables,
        {
            "rank",
            "need_id",
            "validity_verdict",
            "evidence_strength_score",
            "priority_tier",
            "relative_priority_score",
            "human_review_required",
        },
    )
    if ranking_table is None:
        raise ValidationFailure(f"Could not find the ranking table in {ranking_path}")

    validation_queue = first_table_with_headers(
        tables,
        {"need_id", "current_signal", "missing_evidence", "recommended_validation", "decision_deadline"},
    )

    seen_need_ids: set[str] = set()
    ranked_need_ids: set[str] = set()
    validation_queue_ids: set[str] = set()

    for offset, row in enumerate(ranking_table.rows, start=ranking_table.start_line + 2):
        need_id = row.get("need_id", "").strip()
        verdict = row.get("validity_verdict", "").strip()
        priority_tier = row.get("priority_tier", "").strip()
        evidence_strength_raw = row.get("evidence_strength_score", "").strip()

        if need_id not in need_ids:
            issues.append(make_item("TRC025", "error", ranking_path, f"line {offset}", f"Ranking references missing need_id {need_id}."))
        if need_id in seen_need_ids:
            issues.append(make_item("TRC026", "error", ranking_path, f"line {offset}", f"Duplicate ranked need_id {need_id}."))
        seen_need_ids.add(need_id)
        ranked_need_ids.add(need_id)

        if verdict == "invalid_or_out_of_scope":
            issues.append(
                make_item(
                    "TRC027",
                    "error",
                    ranking_path,
                    f"line {offset}",
                    f"{need_id} is invalid_or_out_of_scope but appears in the formal ranking table.",
                )
            )
        if verdict == "need_hypothesis" and priority_tier == "P0":
            issues.append(make_item("TRC028", "error", ranking_path, f"line {offset}", f"{need_id} is need_hypothesis but ranked as P0."))
        if verdict == "insufficient_evidence" and priority_tier == "P0":
            issues.append(
                make_item(
                    "TRC029",
                    "error",
                    ranking_path,
                    f"line {offset}",
                    f"{need_id} is insufficient_evidence but ranked as P0.",
                )
            )
        if evidence_strength_raw:
            try:
                evidence_strength = int(evidence_strength_raw)
            except ValueError:
                evidence_strength = -1
            if evidence_strength == 1 and priority_tier in {"P0", "P1"}:
                issues.append(
                    make_item(
                        "TRC030",
                        "error",
                        ranking_path,
                        f"line {offset}",
                        f"{need_id} has evidence_strength_score=1 but is ranked {priority_tier}.",
                    )
                )

        if "relative_priority_score" not in row:
            issues.append(make_item("TRC031", "error", ranking_path, f"line {offset}", "Ranking row is missing relative_priority_score."))
        if "human_review_required" not in row:
            issues.append(make_item("TRC032", "error", ranking_path, f"line {offset}", "Ranking row is missing human_review_required."))

    if validation_queue is not None:
        for row in validation_queue.rows:
            queue_need_id = row.get("need_id", "").strip()
            if queue_need_id:
                validation_queue_ids.add(queue_need_id)
    return ranked_need_ids, validation_queue_ids


def validate_report(
    report_path: Path,
    need_ids: set[str],
    evidence_ids: set[str],
    cards_by_id: dict[str, NeedCard],
    issues: list[ResultItem],
) -> set[str]:
    text = read_text(report_path)
    frontmatter, body = parse_frontmatter(text, report_path)
    if "analysis_id" not in frontmatter:
        issues.append(make_item("TRC033", "error", report_path, "frontmatter", "Missing analysis_id in report frontmatter."))
    tables = parse_markdown_tables(body)
    key_table = first_table_with_headers(
        tables,
        {
            "need_id",
            "need_title",
            "target_segment",
            "validity_verdict",
            "overall_evidence_strength",
            "priority_tier",
            "key_evidence_ids",
        },
    )
    if key_table is None:
        raise ValidationFailure(f"Could not find the Key User Needs table in {report_path}")

    report_need_ids: set[str] = set()
    for offset, row in enumerate(key_table.rows, start=key_table.start_line + 2):
        need_id = row.get("need_id", "").strip()
        if need_id not in need_ids:
            issues.append(make_item("TRC034", "error", report_path, f"line {offset}", f"Report references unknown need_id {need_id}."))
        report_need_ids.add(need_id)

        key_evidence_ids = EVIDENCE_ID_RE.findall(row.get("key_evidence_ids", ""))
        if not key_evidence_ids:
            issues.append(make_item("TRC035", "error", report_path, f"line {offset}", f"{need_id} is missing key_evidence_ids."))
        for evidence_id in key_evidence_ids:
            if evidence_id not in evidence_ids:
                issues.append(
                    make_item(
                        "TRC036",
                        "error",
                        report_path,
                        f"line {offset}",
                        f"{need_id} references missing key evidence_id {evidence_id}.",
                    )
                )

    traceability_section_match = re.search(
        r"## 12\. Traceability Appendix(?P<section>.*?)(?:\n## |\Z)",
        body,
        flags=re.DOTALL,
    )
    if traceability_section_match:
        traceability_section = traceability_section_match.group("section")
        appendix_need_ids = set(NEED_ID_RE.findall(traceability_section))
        appendix_evidence_ids = set(EVIDENCE_ID_RE.findall(traceability_section))
        for need_id in appendix_need_ids:
            if need_id not in need_ids:
                issues.append(
                    make_item("TRC037", "error", report_path, "Traceability Appendix", f"Appendix references unknown need_id {need_id}.")
                )
        for evidence_id in appendix_evidence_ids:
            if evidence_id not in evidence_ids:
                issues.append(
                    make_item(
                        "TRC038",
                        "error",
                        report_path,
                        "Traceability Appendix",
                        f"Appendix references unknown evidence_id {evidence_id}.",
                    )
                )

    detailed_need_ids = set(re.findall(r"^###\s+need_id:\s*(N\d{3,})\s*$", body, flags=re.MULTILINE))
    for need_id in detailed_need_ids:
        if need_id not in need_ids:
            issues.append(
                make_item("TRC039", "error", report_path, "Detailed Findings", f"Report contains an orphan need_id {need_id}.")
            )
    report_need_ids.update(detailed_need_ids)

    for need_id, card in cards_by_id.items():
        verdict = str(card.frontmatter.get("validity_verdict", "")).strip()
        if verdict in {"validated", "conditionally_validated"} and need_id not in report_need_ids:
            issues.append(
                make_item(
                    "TRC040",
                    "error",
                    report_path,
                    "Key User Needs",
                    f"{need_id} is {verdict} in need cards but missing from the report.",
                )
            )

    return report_need_ids


def summarize(
    script_name: str,
    issues: list[ResultItem],
    summary: dict[str, Any],
    json_mode: bool,
) -> None:
    status = summary["status"]
    if json_mode:
        grouped = {"errors": [], "warnings": [], "info": []}
        for item in issues:
            grouped[f"{item.severity}s"].append(asdict(item))
        print(
            json.dumps(
                {
                    "script": script_name,
                    "status": status,
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

    status_word = {"passed": "PASS", "passed_with_warnings": "WARN", "failed": "FAIL", "internal_error": "FAIL"}[status]
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
    evidence_table_path = Path(args.evidence_table)
    need_cards_path = Path(args.need_cards)
    ranking_path = Path(args.ranking) if args.ranking else None
    report_path = Path(args.report) if args.report else None

    if not evidence_table_path.exists():
        raise ValidationFailure(f"--evidence-table path does not exist: {evidence_table_path}")
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

    need_cards = [parse_need_card(path) for path in need_card_files]
    temp_need_ids, cards_by_id = validate_need_cards(need_cards, set(), [])
    evidence_rows = validate_evidence_table(evidence_table_path, temp_need_ids, issues)
    evidence_ids = set(evidence_rows)

    need_ids, cards_by_id = validate_need_cards(need_cards, evidence_ids, issues)

    orphan_evidence_ids = [evidence_id for evidence_id, row in evidence_rows.items() if row.get("linked_need_ids", "").strip() == "unassigned"]
    orphan_need_ids: list[str] = []
    duplicate_ids = {
        "evidence_ids": sorted({item.message.split(": ", 1)[1].rstrip(".") for item in issues if item.rule_id == "TRC005"}),
        "need_ids": sorted({item.message.split(": ", 1)[1].rstrip(".") for item in issues if item.rule_id == "TRC014"}),
    }

    ranked_need_ids: set[str] = set()
    validation_queue_ids: set[str] = set()
    if ranking_path:
        ranked_need_ids, validation_queue_ids = validate_ranking(ranking_path, need_ids, issues)

    report_need_ids: set[str] = set()
    if report_path:
        report_need_ids = validate_report(report_path, need_ids, evidence_ids, cards_by_id, issues)

    supporting_map = {need_id: card.supporting_evidence_ids for need_id, card in cards_by_id.items()}
    counter_map = {need_id: card.counterevidence_ids for need_id, card in cards_by_id.items()}
    linked_map = {
        evidence_id: NEED_ID_RE.findall(row.get("linked_need_ids", ""))
        for evidence_id, row in evidence_rows.items()
        if row.get("linked_need_ids", "").strip() != "unassigned"
    }

    for need_id, card in cards_by_id.items():
        if not card.supporting_evidence_ids and need_id not in ranked_need_ids and need_id not in report_need_ids:
            orphan_need_ids.append(need_id)

    error_count = sum(1 for item in issues if item.severity == "error")
    warning_count = sum(1 for item in issues if item.severity == "warning")
    status, exit_code = compute_status(error_count, warning_count, args.strict)
    summary = {
        "status": status,
        "checked_file_count": 2 + int(bool(ranking_path)) + int(bool(report_path)),
        "error_count": error_count,
        "warning_count": warning_count,
        "evidence_id_to_linked_need_ids": linked_map,
        "need_id_to_supporting_evidence_ids": supporting_map,
        "need_id_to_counterevidence_ids": counter_map,
        "orphan_evidence_ids": orphan_evidence_ids,
        "orphan_need_ids": orphan_need_ids,
        "missing_evidence_ids": sorted(
            {
                match
                for item in issues
                if item.rule_id in {"TRC020", "TRC021", "TRC022", "TRC036", "TRC038"}
                for match in EVIDENCE_ID_RE.findall(item.message)
            }
        ),
        "missing_need_ids": sorted(
            {
                match
                for item in issues
                if item.rule_id in {"TRC009", "TRC025", "TRC034", "TRC037"}
                for match in NEED_ID_RE.findall(item.message)
            }
        ),
        "duplicate_ids": duplicate_ids,
        "validation_queue_need_ids": sorted(validation_queue_ids),
        "report_need_ids": sorted(report_need_ids),
    }
    summarize("validate_evidence_links.py", issues, summary, args.json)
    return exit_code


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return run(args)
    except ValidationFailure as exc:
        issues = [make_item("TRC001", "error", "", "path", str(exc))]
        summary = {"status": "internal_error", "checked_file_count": 0, "error_count": 1, "warning_count": 0}
        summarize("validate_evidence_links.py", issues, summary, args.json)
        return 2
    except Exception as exc:  # pragma: no cover - defensive fallback
        issues = [make_item("TRC999", "error", "", "internal", f"Unexpected internal error: {exc}")]
        summary = {"status": "internal_error", "checked_file_count": 0, "error_count": 1, "warning_count": 0}
        summarize("validate_evidence_links.py", issues, summary, args.json)
        return 2


if __name__ == "__main__":
    sys.exit(main())
