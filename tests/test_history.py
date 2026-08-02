from __future__ import annotations

import csv
import io

from src.insight.history import HISTORY_COLUMNS, history_to_csv


def test_history_csv_contains_question_answer_and_query_spec() -> None:
    payload = history_to_csv(
        [
            {
                "timestamp_utc": "2026-08-02T08:00:00+00:00",
                "dataset": "sales.csv",
                "question": "Total revenue?",
                "status": "answered_unverified",
                "answer": "$100.00",
                "parsing_mode": "rule_based",
                "operation": "sum",
                "value_column": "revenue",
                "validated_query_spec_json": {"operation": "sum"},
                "result_json": {"type": "scalar", "value": 100.0},
            }
        ]
    )

    text = payload.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))

    assert tuple(rows[0].keys()) == HISTORY_COLUMNS
    assert rows[0]["question"] == "Total revenue?"
    assert rows[0]["answer"] == "$100.00"
    assert rows[0]["operation"] == "sum"
    assert '"operation": "sum"' in rows[0]["validated_query_spec_json"]


def test_history_csv_prevents_spreadsheet_formula_execution() -> None:
    payload = history_to_csv(
        [
            {
                "question": "=HYPERLINK(\"https://example.invalid\")",
                "answer": "+SUM(1,1)",
                "status": "answered_unverified",
            }
        ]
    )

    row = next(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))
    assert row["question"].startswith("'=")
    assert row["answer"].startswith("'+")


def test_history_csv_accepts_empty_history() -> None:
    payload = history_to_csv([])
    rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))
    assert rows == []
