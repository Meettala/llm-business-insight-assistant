"""Utilities for exporting an auditable question-and-answer history."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping, Sequence
from typing import Any

HISTORY_COLUMNS = (
    "timestamp_utc",
    "dataset",
    "question",
    "status",
    "answer",
    "parsing_mode",
    "operation",
    "value_column",
    "group_by_column",
    "date_column",
    "filter_column",
    "filter_value",
    "validated_query_spec_json",
    "result_json",
    "error",
)


def _spreadsheet_safe(value: Any) -> str:
    """Convert a value to text and prevent spreadsheet formula injection."""
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


def history_to_csv(entries: Sequence[Mapping[str, Any]]) -> bytes:
    """Return a UTF-8 CSV containing every recorded question and response."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=HISTORY_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for entry in entries:
        writer.writerow(
            {column: _spreadsheet_safe(entry.get(column, "")) for column in HISTORY_COLUMNS}
        )
    return output.getvalue().encode("utf-8-sig")
