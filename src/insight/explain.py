"""Build deterministic written answers from computed results."""

from __future__ import annotations

from .query_spec import QuerySpec

OPERATION_LABELS = {
    "sum": "total",
    "mean": "average",
    "count": "count",
    "min": "minimum",
    "max": "maximum",
    "ratio": "ratio",
}


def _format_number(number: float, hint: str | None = None) -> str:
    if hint == "currency":
        return f"${number:,.2f}"
    if hint == "percentage":
        return f"{number:,.2f}%"
    if hint == "integer":
        return f"{int(round(number)):,}"
    if isinstance(number, int) or float(number).is_integer():
        return f"{int(number):,}"
    return f"{number:,.2f}"


def _format_context(context: dict[str, object]) -> str:
    if not context:
        return ""
    return ", ".join(str(value) for value in context.values())


def explain_result(question: str, spec: QuerySpec, result: dict) -> str:
    del question

    if result["type"] == "conditional_count":
        return (
            f"{result['value']:,} out of {result['total_rows']:,} "
            f"({result['percentage']:.1f}%)."
        )

    if result["type"] == "distinct":
        values = ", ".join(result["values"])
        return values or "No distinct values were found."

    if result["type"] == "date_range":
        return f"{result['start']} to {result['end']}."

    if result["type"] == "ranked":
        lines = [
            f"{item['label']} — "
            f"{_format_number(item['value'], result.get('format_hint'))}"
            for item in result["items"]
        ]
        return "\n".join(lines)

    if result["type"] == "scalar":
        formatted_value = _format_number(
            result["value"],
            result.get("format_hint"),
        )

        if result["operation"] == "ratio":
            return f"The overall profit margin is {formatted_value}."

        column = result.get("column") or result.get("derived_measure")
        operation_label = OPERATION_LABELS[result["operation"]]
        derived_labels = {
            "net_revenue_amount": "net revenue",
            "net_revenue_percent": "net revenue",
            "net_revenue_fraction": "net revenue",
            "net_revenue_auto": "net revenue",
            "gross_profit_amount": "gross profit",
            "gross_profit_unit_cost": "gross profit",
        }
        readable_column = derived_labels.get(
            str(column),
            str(column).replace("_", " ") if column else "",
        )
        label = f" {readable_column}" if readable_column else ""

        context = _format_context(result.get("context", {}))
        context_text = f" ({context})" if context else ""

        matching_rows = result.get("matching_rows")
        row_text = (
            f" ({matching_rows:,} matching rows)"
            if matching_rows is not None
            else ""
        )

        return (
            f"The {operation_label}{label} is {formatted_value}"
            f"{context_text}{row_text}."
        )

    if result["type"] == "grouped":
        lines = [
            f"- {key}: {_format_number(value, result.get('format_hint'))}"
            for key, value in result["data"].items()
        ]
        heading = f"Breakdown by {spec.group_by_column}:\n"
        return heading + "\n".join(lines)

    if result["type"] == "timeseries":
        lines = [
            f"- {period}: {_format_number(value, result.get('format_hint'))}"
            for period, value in result["data"].items()
        ]
        return "\n".join(lines)

    return "Could not generate an explanation for this result type."
