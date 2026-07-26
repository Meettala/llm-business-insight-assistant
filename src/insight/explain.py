"""
Turns a query result into a written answer. The answer sentence is built
directly from the actual computed result — never phrased by an LLM
free-form — so the stated numbers can never drift from what was actually
computed. (An optional LLM pass can be layered on top later for nicer
prose, but it would still be required to embed these exact numbers, not
invent new ones — not built in this MVP to keep the guarantee airtight.)
"""

from __future__ import annotations

from .query_spec import QuerySpec

OPERATION_LABELS = {
    "sum": "total",
    "mean": "average",
    "count": "count",
    "min": "minimum",
    "max": "maximum",
}


def explain_result(question: str, spec: QuerySpec, result: dict) -> str:
    del question  # Reserved for future contextual phrasing.

    if result["type"] == "scalar":
        operation_label = OPERATION_LABELS[result["operation"]]
        column_label = (
            f" of {result.get('column')}" if result.get("column") else ""
        )
        row_count = result.get("row_count", "the")
        formatted_value = _format_number(result["value"])
        return (
            f"The {operation_label}{column_label} is {formatted_value}, "
            f"computed from {row_count} matching rows."
        )

    if result["type"] == "grouped":
        top_items = sorted(
            result["data"].items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]
        lines = [f"- {key}: {_format_number(value)}" for key, value in top_items]
        heading = f"Breakdown by {spec.group_by_column} (top {len(lines)}):\n"
        return heading + "\n".join(lines)

    if result["type"] == "timeseries":
        points = sorted(result["data"].items())
        lines = [
            f"- {period}: {_format_number(value)}" for period, value in points
        ]
        heading = f"Trend of {spec.value_column} over time:\n"
        return heading + "\n".join(lines)

    return "Could not generate an explanation for this result type."


def _format_number(number: float) -> str:
    if isinstance(number, int) or number == int(number):
        return f"{int(number):,}"
    return f"{number:,.2f}"
