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


def explain_result(question: str, spec: QuerySpec, result: dict) -> str:
    if result["type"] == "scalar":
        op_word = {"sum": "total", "mean": "average", "count": "count", "min": "minimum", "max": "maximum"}[result["operation"]]
        col = f" of {result.get('column')}" if result.get("column") else ""
        return f"The {op_word}{col} is {_format_number(result['value'])}, computed from {result.get('row_count', 'the')} matching rows."

    if result["type"] == "grouped":
        top_items = sorted(result["data"].items(), key=lambda kv: kv[1], reverse=True)[:5]
        lines = [f"- {k}: {_format_number(v)}" for k, v in top_items]
        return f"Breakdown by {spec.group_by_column} (top {len(lines)}):\n" + "\n".join(lines)

    if result["type"] == "timeseries":
        points = sorted(result["data"].items())
        lines = [f"- {period}: {_format_number(v)}" for period, v in points]
        return f"Trend of {spec.value_column} over time:\n" + "\n".join(lines)

    return "Could not generate an explanation for this result type."


def _format_number(n: float) -> str:
    if isinstance(n, int) or n == int(n):
        return f"{int(n):,}"
    return f"{n:,.2f}"
