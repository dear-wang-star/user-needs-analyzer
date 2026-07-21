#!/usr/bin/env python3
"""Validate raw input materials before user-needs analysis.

Inputs:
- One PATH argument pointing to a file or directory.
- Supported file formats: .md, .txt, .csv, .json

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
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

SUPPORTED_SUFFIXES = {".md", ".txt", ".csv", ".json"}
SYSTEM_FILE_NAMES = {".DS_Store"}
EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?x)(?:\+?\d[\d\-\s().]{6,}\d)"
)
SENSITIVE_FILE_RE = re.compile(
    r"(email|phone|customer|client|passport|ssn|secret|confidential|姓名|邮箱|手机|电话|身份证)",
    re.IGNORECASE,
)
MINIMAL_CONTENT_CHARS = 40
SOURCE_HINT_RE = re.compile(r"\b(source|reference|ticket|interview|survey|review)\b", re.IGNORECASE)
DATE_HINT_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b(date|time|timestamp|collected)\b", re.IGNORECASE)
USER_HINT_RE = re.compile(r"\b(user|participant|customer|respondent|participant_id|user_id)\b", re.IGNORECASE)
SCENARIO_HINT_RE = re.compile(r"\b(context|scenario|workflow|stage|trigger|situation)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ResultItem:
    rule_id: str
    severity: str
    file: str
    location: str
    message: str


@dataclass(frozen=True)
class FileReport:
    path: Path
    suffix: str
    size_bytes: int
    content_hash: str
    valid: bool


class ValidationFailure(Exception):
    """Raised for operational failures that should return exit code 2."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate raw input materials before running user-needs analysis.",
    )
    parser.add_argument("path", help="Input file or directory to scan.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as a failing result (exit code 1).",
    )
    return parser


def is_hidden_path(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts if part not in {".", ".."})


def should_ignore(path: Path) -> bool:
    if path.name in SYSTEM_FILE_NAMES:
        return True
    if "__pycache__" in path.parts or ".git" in path.parts:
        return True
    if is_hidden_path(path):
        return True
    return False


def discover_files(target: Path) -> list[Path]:
    if target.is_file():
        if target.suffix.lower() in SUPPORTED_SUFFIXES:
            return [target]
        return []

    files: list[Path] = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if should_ignore(path.relative_to(target)):
            continue
        if path.suffix.lower() in SUPPORTED_SUFFIXES:
            files.append(path)
    return files


def make_item(rule_id: str, severity: str, file: Path | str, location: str, message: str) -> ResultItem:
    return ResultItem(
        rule_id=rule_id,
        severity=severity,
        file=str(file),
        location=location,
        message=message,
    )


def read_text_utf8(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValidationFailure(f"Unable to read file: {path} ({exc})") from exc
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UnicodeDecodeError(exc.encoding, exc.object, exc.start, exc.end, exc.reason)


def parse_csv_text(path: Path, text: str) -> tuple[list[str], list[list[str]]]:
    try:
        rows = list(csv.reader(text.splitlines()))
    except csv.Error as exc:
        raise ValidationFailure(f"CSV parsing failed for {path}: {exc}") from exc
    if not rows:
        return [], []
    header = rows[0]
    data_rows = rows[1:]
    return header, data_rows


def content_is_minimal(text: str) -> bool:
    return len(text.strip()) < MINIMAL_CONTENT_CHARS


def has_missing_context(text: str) -> bool:
    lowered = text.lower()
    return not (
        SOURCE_HINT_RE.search(lowered)
        and DATE_HINT_RE.search(text)
        and USER_HINT_RE.search(lowered)
        and SCENARIO_HINT_RE.search(lowered)
    )


def suspicious_filename(path: Path) -> bool:
    name = path.stem
    return bool(SENSITIVE_FILE_RE.search(name) or EMAIL_RE.search(name) or PHONE_RE.search(name))


def looks_like_phone_number(candidate: str) -> bool:
    digits = re.sub(r"\D", "", candidate)
    if len(digits) < 8 or len(digits) > 15:
        return False
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate.strip()):
        return False
    return True


def validate_json(
    path: Path,
    text: str,
    issues: list[ResultItem],
) -> None:
    try:
        top_level = json.loads(text)
    except json.JSONDecodeError as exc:
        issues.append(
            make_item(
                "INP006",
                "error",
                path,
                f"line {exc.lineno}, column {exc.colno}",
                f"Invalid JSON syntax: {exc.msg}",
            )
        )
        return
    if not isinstance(top_level, (dict, list)):
        issues.append(
            make_item(
                "INP106",
                "warning",
                path,
                "top-level",
                "Heuristic review: JSON top-level structure is neither an object nor an array.",
            )
        )


def validate_csv(
    path: Path,
    text: str,
    issues: list[ResultItem],
) -> None:
    header, data_rows = parse_csv_text(path, text)
    if not header or not any(cell.strip() for cell in header):
        issues.append(
            make_item(
                "INP007",
                "error",
                path,
                "line 1",
                "CSV file does not contain a usable header row.",
            )
        )
        return

    normalized_header = [cell.strip() for cell in header]
    duplicate_headers = [name for name, count in Counter(normalized_header).items() if name and count > 1]
    if duplicate_headers:
        issues.append(
            make_item(
                "INP107",
                "warning",
                path,
                "line 1",
                f"Heuristic review: duplicate CSV headers detected: {', '.join(sorted(duplicate_headers))}.",
            )
        )

    expected_columns = len(header)
    for index, row in enumerate(data_rows, start=2):
        if len(row) != expected_columns:
            issues.append(
                make_item(
                    "INP008",
                    "error",
                    path,
                    f"line {index}",
                    f"CSV row has {len(row)} columns; expected {expected_columns}.",
                )
            )


def validate_privacy_heuristics(path: Path, text: str, issues: list[ResultItem]) -> bool:
    privacy_flag = False
    if EMAIL_RE.search(text):
        privacy_flag = True
        issues.append(
            make_item(
                "INP103",
                "warning",
                path,
                "content",
                "Heuristic review: possible email address detected; privacy review recommended.",
            )
        )
    phone_match = next((match for match in PHONE_RE.finditer(text) if looks_like_phone_number(match.group(0))), None)
    if phone_match is not None:
        privacy_flag = True
        issues.append(
            make_item(
                "INP104",
                "warning",
                path,
                "content",
                "Heuristic review: possible phone number detected; privacy review recommended.",
            )
        )
    if suspicious_filename(path):
        privacy_flag = True
        issues.append(
            make_item(
                "INP105",
                "warning",
                path,
                "filename",
                "Heuristic review: filename may contain a real name or sensitive identifier.",
            )
        )
    return privacy_flag


def validate_file(path: Path, issues: list[ResultItem]) -> tuple[FileReport | None, bool]:
    try:
        size_bytes = path.stat().st_size
    except OSError as exc:
        raise ValidationFailure(f"Unable to stat file: {path} ({exc})") from exc

    if size_bytes == 0:
        issues.append(make_item("INP003", "error", path, "file", "File is empty."))
        return None, False

    try:
        text = read_text_utf8(path)
    except UnicodeDecodeError:
        issues.append(
            make_item(
                "INP005",
                "error",
                path,
                "file",
                "Text is not valid UTF-8.",
            )
        )
        return None, False

    privacy_flag = validate_privacy_heuristics(path, text, issues)

    if content_is_minimal(text):
        issues.append(
            make_item(
                "INP101",
                "warning",
                path,
                "content",
                "Heuristic review: file contains very little content and may lack analysis context.",
            )
        )

    if has_missing_context(text):
        issues.append(
            make_item(
                "INP108",
                "warning",
                path,
                "content",
                "Heuristic review: source, date, user identifier, or scenario context may be missing.",
            )
        )

    suffix = path.suffix.lower()
    if suffix == ".json":
        validate_json(path, text, issues)
    elif suffix == ".csv":
        validate_csv(path, text, issues)

    has_error = any(item.file == str(path) and item.severity == "error" for item in issues)
    report = FileReport(
        path=path,
        suffix=suffix,
        size_bytes=size_bytes,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        valid=not has_error,
    )
    return report, privacy_flag


def add_duplicate_content_warnings(reports: Iterable[FileReport], issues: list[ResultItem]) -> None:
    by_hash: dict[str, list[FileReport]] = defaultdict(list)
    for report in reports:
        by_hash[report.content_hash].append(report)
    for matching_reports in by_hash.values():
        if len(matching_reports) < 2:
            continue
        paths = ", ".join(str(report.path) for report in matching_reports)
        for report in matching_reports:
            issues.append(
                make_item(
                    "INP102",
                    "warning",
                    report.path,
                    "content",
                    f"Heuristic review: file content is identical to other scanned files ({paths}).",
                )
            )


def summarize(reports: list[FileReport], issues: list[ResultItem], privacy_review_recommended: bool) -> dict[str, Any]:
    suffix_counter = Counter(report.suffix for report in reports)
    error_count = sum(1 for item in issues if item.severity == "error")
    warning_count = sum(1 for item in issues if item.severity == "warning")
    overall_status = "failed" if error_count else "passed_with_warnings" if warning_count else "passed"
    return {
        "scanned_file_count": len(reports),
        "valid_file_count": sum(1 for report in reports if report.valid),
        "total_size_bytes": sum(report.size_bytes for report in reports),
        "file_types": dict(sorted(suffix_counter.items())),
        "error_count": error_count,
        "warning_count": warning_count,
        "privacy_review_recommended": privacy_review_recommended,
        "overall_status": overall_status,
    }


def to_json_payload(script_name: str, issues: list[ResultItem], summary: dict[str, Any], status: str) -> dict[str, Any]:
    grouped = {"errors": [], "warnings": [], "info": []}
    for item in issues:
        key = f"{item.severity}s"
        grouped.setdefault(key, []).append(asdict(item))
    return {
        "script": script_name,
        "status": status,
        "errors": grouped["errors"],
        "warnings": grouped["warnings"],
        "info": grouped["info"],
        "summary": summary,
    }


def emit_text(script_name: str, issues: list[ResultItem], summary: dict[str, Any]) -> None:
    status_word = {
        "passed": "PASS",
        "passed_with_warnings": "WARN",
        "failed": "FAIL",
        "internal_error": "FAIL",
    }[summary["overall_status"]]
    print(f"{status_word} {script_name}")
    print(
        f"files={summary['scanned_file_count']} valid={summary['valid_file_count']} "
        f"errors={summary['error_count']} warnings={summary['warning_count']}"
    )
    for item in issues:
        print(
            f"[{item.severity.upper()}] {item.rule_id} {item.file}:{item.location} - {item.message}"
        )
    print("Summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def compute_exit_code(summary: dict[str, Any], strict: bool) -> int:
    if summary["error_count"] > 0:
        return 1
    if strict and summary["warning_count"] > 0:
        return 1
    return 0


def run(args: argparse.Namespace) -> int:
    target = Path(args.path)
    if not target.exists():
        raise ValidationFailure(f"Input path does not exist: {target}")

    files = discover_files(target)
    if not files:
        issues = [
            make_item(
                "INP002",
                "error",
                target,
                "path",
                "No supported files were found under the provided path.",
            )
        ]
        summary = {
            "scanned_file_count": 0,
            "valid_file_count": 0,
            "total_size_bytes": 0,
            "file_types": {},
            "error_count": 1,
            "warning_count": 0,
            "privacy_review_recommended": False,
            "overall_status": "failed",
        }
        if args.json:
            print(json.dumps(to_json_payload("validate_input.py", issues, summary, "failed"), ensure_ascii=False, indent=2))
        else:
            emit_text("validate_input.py", issues, summary)
        return 1

    issues: list[ResultItem] = []
    reports: list[FileReport] = []
    privacy_flag = False
    for file_path in files:
        report, file_privacy_flag = validate_file(file_path, issues)
        privacy_flag = privacy_flag or file_privacy_flag
        if report is not None:
            reports.append(report)

    add_duplicate_content_warnings(reports, issues)
    summary = summarize(reports, issues, privacy_flag)

    if args.json:
        print(
            json.dumps(
                to_json_payload("validate_input.py", issues, summary, summary["overall_status"]),
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        emit_text("validate_input.py", issues, summary)
    return compute_exit_code(summary, args.strict)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return run(args)
    except ValidationFailure as exc:
        summary = {
            "scanned_file_count": 0,
            "valid_file_count": 0,
            "total_size_bytes": 0,
            "file_types": {},
            "error_count": 1,
            "warning_count": 0,
            "privacy_review_recommended": False,
            "overall_status": "internal_error",
        }
        issues = [make_item("INP001", "error", args.path, "path", str(exc))]
        if args.json:
            print(
                json.dumps(
                    to_json_payload("validate_input.py", issues, summary, "internal_error"),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            emit_text("validate_input.py", issues, summary)
        return 2
    except Exception as exc:  # pragma: no cover - defensive fallback
        summary = {
            "scanned_file_count": 0,
            "valid_file_count": 0,
            "total_size_bytes": 0,
            "file_types": {},
            "error_count": 1,
            "warning_count": 0,
            "privacy_review_recommended": False,
            "overall_status": "internal_error",
        }
        issues = [make_item("INP999", "error", args.path, "internal", f"Unexpected internal error: {exc}")]
        if args.json:
            print(
                json.dumps(
                    to_json_payload("validate_input.py", issues, summary, "internal_error"),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            emit_text("validate_input.py", issues, summary)
        return 2


if __name__ == "__main__":
    sys.exit(main())
