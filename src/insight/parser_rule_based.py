"""
Rule-based question parser: turns a plain-English question into a
QuerySpec using keyword matching against the actual column names and
common phrasing patterns. No API key needed. Always available as the
fallback when no LLM key is configured, and as the baseline the LLM
parser's output is cross-checked against isn't required to match, but
both paths produce the same QuerySpec shape and go through the same
validator.
"""

from __future__ import annotations

from .query_spec import QuerySpec

OPERATION_KEYWORDS = {
    "sum": ["total", "sum of", "how much"],
    "mean": ["average", "mean", "avg"],
    "count": ["how many", "count of", "number of"],
    "min": ["lowest", "minimum", "smallest"],
    "max": ["highest", "maximum", "largest", "biggest"],
    "trend": ["over time", "trend", "by month", "monthly"],
}

GROUP_BY_MARKERS = ["by ", "per ", "grouped by", "for each"]


def _find_operation(question_lower: str) -> str:
    for operation, keywords in OPERATION_KEYWORDS.items():
        if any(keyword in question_lower for keyword in keywords):
            return operation
    return "count"


def _find_column(question_lower: str, columns: list[str]) -> str | None:
    # Prefer the longest matching column name to avoid partial-word
    # false positives (for example, "revenue" inside "revenue_total").
    candidates = [column for column in columns if column.lower() in question_lower]
    return max(candidates, key=len) if candidates else None


def parse_question(
    question: str,
    columns: list[str],
    column_types: dict[str, str],
) -> QuerySpec:
    q_lower = question.lower()
    operation = _find_operation(q_lower)

    numeric_columns = [
        column for column in columns if column_types.get(column) == "numeric"
    ]
    date_columns = [
        column for column in columns if column_types.get(column) == "date"
    ]
    categorical_columns = [
        column for column in columns if column_types.get(column) == "categorical"
    ]

    value_column = _find_column(q_lower, numeric_columns)

    group_by_column = None
    if any(marker in q_lower for marker in GROUP_BY_MARKERS):
        group_by_column = _find_column(q_lower, categorical_columns)

    date_column = None
    if operation == "trend" and date_columns:
        date_column = _find_column(q_lower, date_columns) or date_columns[0]

    if operation != "count" and value_column is None and numeric_columns:
        value_column = numeric_columns[0]

    return QuerySpec(
        operation=operation,
        value_column=value_column,
        group_by_column=group_by_column,
        date_column=date_column,
    )
