"""
Validated query schema for deterministic analytics.

Every parser path must produce this schema. The executor only performs fixed,
whitelisted operations; no generated Python, SQL, eval, or exec is permitted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

WHITELISTED_OPERATIONS = {
    "sum",
    "mean",
    "count",
    "min",
    "max",
    "trend",
    "distinct",
    "date_range",
    "ratio",
}
NUMERIC_OPERATIONS = {"sum", "mean", "min", "max", "trend", "ratio"}
ALLOWED_FILTER_OPERATORS = {"eq", "truthy", "year_eq"}
ALLOWED_RANKINGS = {"highest", "lowest"}
ALLOWED_DATE_GRANULARITIES = {"month", "year"}
ALLOWED_DERIVED_MEASURES = {
    "net_revenue_amount",
    "net_revenue_percent",
    "net_revenue_fraction",
    "net_revenue_auto",
    "gross_profit_amount",
    "gross_profit_unit_cost",
    "profit_margin_from_gross_profit",
    "profit_margin_from_cost",
    "profit_margin_from_unit_cost",
}
ALLOWED_FORMAT_HINTS = {"currency", "number", "integer", "percentage"}


@dataclass(frozen=True)
class FilterSpec:
    """One inert, validated dataframe filter."""

    column: str
    operator: str = "eq"
    value: str | int | float | bool = ""


@dataclass
class QuerySpec:
    """The only query shape accepted by the deterministic executor."""

    operation: str
    value_column: str | None = None
    group_by_column: str | None = None
    date_column: str | None = None

    # Backwards-compatible single filter fields.
    filter_column: str | None = None
    filter_value: str | int | float | bool | None = None

    # Accuracy-engine fields.
    filters: tuple[FilterSpec, ...] = field(default_factory=tuple)
    ranking: str | None = None
    limit: int | None = None
    date_granularity: str | None = None
    derived_measure: str | None = None
    component_columns: tuple[str, ...] = field(default_factory=tuple)
    return_columns: tuple[str, ...] = field(default_factory=tuple)
    include_percentage: bool = False
    include_row_count: bool = False
    format_hint: str | None = None

    def all_filters(self) -> tuple[FilterSpec, ...]:
        """Return modern and legacy filters as one immutable sequence."""
        items = list(self.filters)
        if self.filter_column is not None and self.filter_value is not None:
            legacy = FilterSpec(
                column=self.filter_column,
                operator="eq",
                value=self.filter_value,
            )
            if legacy not in items:
                items.append(legacy)
        return tuple(items)


class InvalidQuerySpec(Exception):
    """Raised when requested analytical intent is outside the safe schema."""


def _check_column(column: str | None, field_name: str, columns: list[str]) -> None:
    if column is not None and column not in columns:
        raise InvalidQuerySpec(
            f"Column '{column}' (from {field_name}) does not exist in the uploaded data"
        )


def _check_numeric_column(
    column: str,
    field_name: str,
    column_types: dict[str, str],
) -> None:
    value_type = column_types.get(column)
    if value_type != "numeric":
        if field_name == "value_column":
            raise InvalidQuerySpec(
                "Query requires a numeric value_column; "
                f"'{column}' is classified as '{value_type or 'unknown'}'"
            )
        raise InvalidQuerySpec(
            f"Field '{field_name}' requires a numeric column; "
            f"'{column}' is classified as '{value_type or 'unknown'}'"
        )


def validate_query_spec(
    spec: QuerySpec,
    columns: list[str],
    column_types: dict[str, str] | None = None,
) -> None:
    """Validate one query against operation, field, and dataframe whitelists."""
    if spec.operation not in WHITELISTED_OPERATIONS:
        raise InvalidQuerySpec(
            f"Operation '{spec.operation}' is not in the whitelist: "
            f"{sorted(WHITELISTED_OPERATIONS)}"
        )

    for field_name in (
        "value_column",
        "group_by_column",
        "date_column",
        "filter_column",
    ):
        _check_column(getattr(spec, field_name), field_name, columns)

    for index, item in enumerate(spec.all_filters()):
        if not isinstance(item, FilterSpec):
            raise InvalidQuerySpec(f"filters[{index}] must be a FilterSpec")
        _check_column(item.column, f"filters[{index}].column", columns)
        if item.operator not in ALLOWED_FILTER_OPERATORS:
            raise InvalidQuerySpec(
                f"Filter operator '{item.operator}' is not supported"
            )
        if item.operator == "year_eq":
            try:
                year = int(item.value)
            except (TypeError, ValueError) as exc:
                raise InvalidQuerySpec("year_eq filter requires an integer year") from exc
            if year < 1900 or year > 2200:
                raise InvalidQuerySpec("year_eq filter is outside the supported range")

    if len(spec.all_filters()) > 10:
        raise InvalidQuerySpec("A query may contain at most 10 filters")

    for index, column in enumerate(spec.component_columns):
        _check_column(column, f"component_columns[{index}]", columns)
    if len(spec.component_columns) > 4:
        raise InvalidQuerySpec("A derived measure may use at most 4 columns")

    for index, column in enumerate(spec.return_columns):
        _check_column(column, f"return_columns[{index}]", columns)
    if len(spec.return_columns) > 10:
        raise InvalidQuerySpec("A query may return at most 10 context columns")

    if spec.ranking is not None and spec.ranking not in ALLOWED_RANKINGS:
        raise InvalidQuerySpec(f"Unsupported ranking '{spec.ranking}'")

    if spec.limit is not None and (
        not isinstance(spec.limit, int) or not 1 <= spec.limit <= 100
    ):
        raise InvalidQuerySpec("limit must be an integer from 1 to 100")

    if spec.date_granularity is not None:
        if spec.date_granularity not in ALLOWED_DATE_GRANULARITIES:
            raise InvalidQuerySpec(
                f"Unsupported date granularity '{spec.date_granularity}'"
            )
        if spec.date_column is None:
            raise InvalidQuerySpec("date_granularity requires a date_column")

    if spec.derived_measure is not None:
        if spec.derived_measure not in ALLOWED_DERIVED_MEASURES:
            raise InvalidQuerySpec(
                f"Unsupported derived measure '{spec.derived_measure}'"
            )
        if not spec.component_columns:
            raise InvalidQuerySpec("derived_measure requires component_columns")

    if spec.format_hint is not None and spec.format_hint not in ALLOWED_FORMAT_HINTS:
        raise InvalidQuerySpec(f"Unsupported format hint '{spec.format_hint}'")

    if spec.operation == "count":
        pass
    elif spec.operation == "distinct":
        if spec.value_column is None:
            raise InvalidQuerySpec("Operation 'distinct' requires a value_column")
    elif spec.operation == "date_range":
        if spec.date_column is None:
            raise InvalidQuerySpec("Operation 'date_range' requires a date_column")
    elif spec.operation == "ratio":
        if spec.derived_measure is None:
            raise InvalidQuerySpec("Operation 'ratio' requires a derived_measure")
    else:
        if spec.value_column is None and spec.derived_measure is None:
            raise InvalidQuerySpec(
                f"Operation '{spec.operation}' requires a value_column "
                "or a validated derived_measure"
            )

    if spec.operation == "trend" and spec.date_column is None:
        raise InvalidQuerySpec("Operation 'trend' requires a date_column")

    if spec.ranking is not None and not (
        spec.group_by_column is not None or spec.date_granularity is not None
    ):
        raise InvalidQuerySpec(
            "ranking requires group_by_column or date_granularity"
        )

    if column_types is None:
        return

    if spec.date_column is not None and (
        spec.operation in {"trend", "date_range"}
        or spec.date_granularity is not None
    ):
        date_type = column_types.get(spec.date_column)
        if date_type != "date":
            raise InvalidQuerySpec(
                "Date analysis requires a date_column; "
                f"'{spec.date_column}' is classified as "
                f"'{date_type or 'unknown'}'"
            )

    for item in spec.all_filters():
        if item.operator == "year_eq":
            date_type = column_types.get(item.column)
            if date_type != "date":
                raise InvalidQuerySpec(
                    f"year_eq requires a date column; '{item.column}' "
                    f"is classified as '{date_type or 'unknown'}'"
                )

    if spec.derived_measure is not None:
        for index, column in enumerate(spec.component_columns):
            _check_numeric_column(
                column,
                f"component_columns[{index}]",
                column_types,
            )
    elif spec.operation in NUMERIC_OPERATIONS and spec.value_column is not None:
        _check_numeric_column(spec.value_column, "value_column", column_types)


def query_spec_to_dict(spec: QuerySpec) -> dict[str, Any]:
    """Return a JSON-serialisable audit representation."""
    return {
        "operation": spec.operation,
        "value_column": spec.value_column,
        "group_by_column": spec.group_by_column,
        "date_column": spec.date_column,
        "filter_column": spec.filter_column,
        "filter_value": spec.filter_value,
        "filters": [
            {
                "column": item.column,
                "operator": item.operator,
                "value": item.value,
            }
            for item in spec.filters
        ],
        "ranking": spec.ranking,
        "limit": spec.limit,
        "date_granularity": spec.date_granularity,
        "derived_measure": spec.derived_measure,
        "component_columns": list(spec.component_columns),
        "return_columns": list(spec.return_columns),
        "include_percentage": spec.include_percentage,
        "include_row_count": spec.include_row_count,
        "format_hint": spec.format_hint,
    }
