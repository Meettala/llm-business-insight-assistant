"""Execute validated analytical operations against a DataFrame.

Every branch is a fixed pandas operation. No generated code, SQL, or expression
strings are evaluated.
"""

from __future__ import annotations

import math

import pandas as pd

from .query_spec import FilterSpec, QuerySpec


class QueryExecutionError(ValueError):
    """Raised when valid query intent cannot produce a usable result."""


def _normalise_text(value: object) -> str:
    return " ".join(str(value).strip().casefold().split())


def _require_rows(working: pd.DataFrame) -> None:
    if working.empty:
        raise QueryExecutionError("No rows match this query")


def _require_numeric_values(series: pd.Series, column: str) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        raise QueryExecutionError(
            f"Column '{column}' does not contain usable numeric values"
        )
    return values


def _finite_float(value: object, column: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise QueryExecutionError(
            f"Column '{column}' produced a non-finite analytical result"
        )
    return number


def _apply_filter(working: pd.DataFrame, item: FilterSpec) -> pd.DataFrame:
    series = working[item.column]

    if item.operator == "eq":
        if pd.api.types.is_numeric_dtype(series):
            target = pd.to_numeric(pd.Series([item.value]), errors="coerce").iloc[0]
            if pd.notna(target):
                numeric = pd.to_numeric(series, errors="coerce")
                return working[numeric == target]
        target_text = _normalise_text(item.value)
        matches = series.map(_normalise_text) == target_text
        return working[matches]

    if item.operator == "truthy":
        truthy_tokens = {
            "1",
            "true",
            "yes",
            "y",
            "returned",
            "return",
            "returned order",
        }
        if pd.api.types.is_bool_dtype(series):
            return working[series.fillna(False)]
        if pd.api.types.is_numeric_dtype(series):
            numeric = pd.to_numeric(series, errors="coerce").fillna(0)
            return working[numeric != 0]
        return working[series.map(_normalise_text).isin(truthy_tokens)]

    if item.operator == "year_eq":
        parsed = pd.to_datetime(series, errors="coerce", format="mixed")
        return working[parsed.dt.year == int(item.value)]

    raise QueryExecutionError(f"Unhandled filter operator: {item.operator}")


def _apply_filters(df: pd.DataFrame, spec: QuerySpec) -> pd.DataFrame:
    working = df
    for item in spec.all_filters():
        working = _apply_filter(working, item)
    return working


def _discount_factor(discount: pd.Series, mode: str) -> pd.Series:
    values = pd.to_numeric(discount, errors="coerce")
    if mode == "net_revenue_fraction":
        return values
    if mode == "net_revenue_percent":
        return values / 100.0
    if mode == "net_revenue_auto":
        usable = values.dropna()
        if usable.empty:
            return values
        maximum = float(usable.abs().max())
        if maximum <= 1.0:
            return values
        if maximum <= 100.0:
            return values / 100.0
        raise QueryExecutionError(
            "The discount column is ambiguous; use an amount or percentage-specific column"
        )
    raise QueryExecutionError(f"Unsupported discount mode: {mode}")


def _measure_series(working: pd.DataFrame, spec: QuerySpec) -> pd.Series:
    if spec.derived_measure is None:
        if spec.value_column is None:
            raise QueryExecutionError("A numeric value column is required")
        return pd.to_numeric(working[spec.value_column], errors="coerce")

    columns = spec.component_columns
    measure = spec.derived_measure

    if measure == "net_revenue_amount":
        revenue, discount = columns
        return pd.to_numeric(working[revenue], errors="coerce") - pd.to_numeric(
            working[discount], errors="coerce"
        )

    if measure in {
        "net_revenue_percent",
        "net_revenue_fraction",
        "net_revenue_auto",
    }:
        revenue, discount = columns
        revenue_values = pd.to_numeric(working[revenue], errors="coerce")
        factor = _discount_factor(working[discount], measure)
        return revenue_values * (1.0 - factor)

    if measure == "gross_profit_amount":
        revenue, cost = columns
        return pd.to_numeric(working[revenue], errors="coerce") - pd.to_numeric(
            working[cost], errors="coerce"
        )

    if measure == "gross_profit_unit_cost":
        revenue, unit_cost, units = columns
        return pd.to_numeric(working[revenue], errors="coerce") - (
            pd.to_numeric(working[unit_cost], errors="coerce")
            * pd.to_numeric(working[units], errors="coerce")
        )

    raise QueryExecutionError(
        f"Derived measure '{measure}' is not a direct aggregation measure"
    )


def _profit_margin(working: pd.DataFrame, spec: QuerySpec) -> float:
    columns = spec.component_columns
    measure = spec.derived_measure

    if measure == "profit_margin_from_gross_profit":
        gross_profit, revenue = columns
        numerator = pd.to_numeric(working[gross_profit], errors="coerce").sum(
            min_count=1
        )
        denominator = pd.to_numeric(working[revenue], errors="coerce").sum(
            min_count=1
        )
    elif measure == "profit_margin_from_cost":
        revenue, cost = columns
        revenue_total = pd.to_numeric(working[revenue], errors="coerce").sum(
            min_count=1
        )
        cost_total = pd.to_numeric(working[cost], errors="coerce").sum(
            min_count=1
        )
        numerator = revenue_total - cost_total
        denominator = revenue_total
    elif measure == "profit_margin_from_unit_cost":
        revenue, unit_cost, units = columns
        revenue_total = pd.to_numeric(working[revenue], errors="coerce").sum(
            min_count=1
        )
        cost_total = (
            pd.to_numeric(working[unit_cost], errors="coerce")
            * pd.to_numeric(working[units], errors="coerce")
        ).sum(min_count=1)
        numerator = revenue_total - cost_total
        denominator = revenue_total
    else:
        raise QueryExecutionError(
            f"Unsupported ratio measure: {spec.derived_measure}"
        )

    if pd.isna(numerator) or pd.isna(denominator) or float(denominator) == 0.0:
        raise QueryExecutionError("The profit margin denominator is zero or unavailable")
    return _finite_float(float(numerator) / float(denominator) * 100.0, "ratio")


def _period_labels(
    dates: pd.Series,
    granularity: str,
) -> tuple[pd.Series, dict[object, str]]:
    if granularity == "month":
        periods = dates.dt.to_period("M")
        labels = {
            period: period.to_timestamp().strftime("%B %Y")
            for period in periods.dropna().unique()
        }
        return periods, labels

    years = dates.dt.year
    labels = {year: str(int(year)) for year in years.dropna().unique()}
    return years, labels


def _rank_series(
    series: pd.Series,
    ranking: str,
    limit: int,
) -> pd.Series:
    ascending = ranking == "lowest"
    return series.sort_values(ascending=ascending).head(limit)


def _context_for_index(
    working: pd.DataFrame,
    index: object,
    columns: tuple[str, ...],
) -> dict[str, object]:
    context: dict[str, object] = {}
    for column in columns:
        value = working.loc[index, column]
        if isinstance(value, pd.Series):
            value = value.iloc[0]
        if pd.isna(value):
            continue
        if pd.api.types.is_datetime64_any_dtype(working[column]):
            value = pd.Timestamp(value).date().isoformat()
        else:
            parsed = pd.to_datetime(
                pd.Series([value]), errors="coerce", format="mixed"
            )
            if column.lower().endswith("date") and parsed.notna().iloc[0]:
                value = parsed.iloc[0].date().isoformat()
        context[column] = value
    return context


def execute_query(df: pd.DataFrame, spec: QuerySpec) -> dict:
    """Execute one validated QuerySpec and return a serialisable result."""
    original_count = int(len(df))
    working = _apply_filters(df, spec)

    if spec.operation == "count":
        if spec.group_by_column:
            result = working.groupby(spec.group_by_column, dropna=False).size()
            if spec.ranking:
                result = _rank_series(result, spec.ranking, spec.limit or 1)
                return {
                    "type": "ranked",
                    "items": [
                        {"label": str(key), "value": int(value)}
                        for key, value in result.items()
                    ],
                    "operation": "count",
                    "ranking": spec.ranking,
                    "format_hint": spec.format_hint or "integer",
                }
            result = result.sort_values(ascending=False)
            return {
                "type": "grouped",
                "data": {str(key): int(value) for key, value in result.items()},
                "operation": "count",
                "format_hint": spec.format_hint or "integer",
            }

        if spec.date_granularity and spec.date_column:
            dates = pd.to_datetime(
                working[spec.date_column],
                errors="coerce",
                format="mixed",
            )
            periods, labels = _period_labels(dates, spec.date_granularity)
            counts = working.groupby(periods).size()
            if spec.ranking:
                counts = _rank_series(counts, spec.ranking, spec.limit or 1)
                return {
                    "type": "ranked",
                    "items": [
                        {"label": labels.get(key, str(key)), "value": int(value)}
                        for key, value in counts.items()
                    ],
                    "operation": "count",
                    "ranking": spec.ranking,
                    "format_hint": spec.format_hint or "integer",
                }

        value = int(len(working))
        if spec.include_percentage:
            percentage = (value / original_count * 100.0) if original_count else 0.0
            return {
                "type": "conditional_count",
                "value": value,
                "total_rows": original_count,
                "percentage": percentage,
                "operation": "count",
                "format_hint": "integer",
            }
        return {
            "type": "scalar",
            "value": value,
            "operation": "count",
            "row_count": value,
            "format_hint": spec.format_hint or "integer",
        }

    if spec.operation == "distinct":
        _require_rows(working)
        values = (
            working[spec.value_column]
            .dropna()
            .map(str)
            .drop_duplicates()
            .sort_values(key=lambda series: series.str.casefold())
            .tolist()
        )
        return {
            "type": "distinct",
            "values": values,
            "column": spec.value_column,
            "operation": "distinct",
        }

    if spec.operation == "date_range":
        _require_rows(working)
        dates = pd.to_datetime(
            working[spec.date_column],
            errors="coerce",
            format="mixed",
        ).dropna()
        if dates.empty:
            raise QueryExecutionError("No valid dates are available")
        return {
            "type": "date_range",
            "start": dates.min().date().isoformat(),
            "end": dates.max().date().isoformat(),
            "column": spec.date_column,
            "operation": "date_range",
        }

    _require_rows(working)

    if spec.operation == "ratio":
        value = _profit_margin(working, spec)
        return {
            "type": "scalar",
            "value": value,
            "operation": "ratio",
            "row_count": int(len(working)),
            "format_hint": spec.format_hint or "percentage",
        }

    measure = _measure_series(working, spec)
    usable_measure = measure.dropna()
    if usable_measure.empty:
        label = spec.value_column or spec.derived_measure or "measure"
        raise QueryExecutionError(
            f"Measure '{label}' does not contain usable numeric values"
        )

    if spec.date_granularity and spec.date_column:
        dates = pd.to_datetime(
            working[spec.date_column],
            errors="coerce",
            format="mixed",
        )
        if dates.notna().sum() == 0:
            raise QueryExecutionError("No valid dates are available for this analysis")
        periods, labels = _period_labels(dates, spec.date_granularity)
        temp = working.assign(_measure=measure, _period=periods).dropna(
            subset=["_measure", "_period"]
        )
        aggregation = "sum" if spec.operation == "trend" else spec.operation
        grouped = temp.groupby("_period")["_measure"].agg(aggregation).dropna()
        if grouped.empty:
            raise QueryExecutionError("No usable date-grouped values are available")
        if spec.ranking:
            grouped = _rank_series(grouped, spec.ranking, spec.limit or 1)
            return {
                "type": "ranked",
                "items": [
                    {
                        "label": labels.get(key, str(key)),
                        "value": _finite_float(
                            value, spec.value_column or "measure"
                        ),
                    }
                    for key, value in grouped.items()
                ],
                "operation": aggregation,
                "ranking": spec.ranking,
                "format_hint": spec.format_hint,
            }
        return {
            "type": "timeseries",
            "data": {
                labels.get(key, str(key)): _finite_float(
                    value, spec.value_column or "measure"
                )
                for key, value in grouped.items()
            },
            "operation": aggregation,
            "column": spec.value_column,
            "format_hint": spec.format_hint,
        }

    if spec.operation == "trend":
        if spec.date_column is None:
            raise QueryExecutionError("Trend requires a date column")
        dates = pd.to_datetime(
            working[spec.date_column],
            errors="coerce",
            format="mixed",
        )
        if dates.notna().sum() == 0:
            raise QueryExecutionError("No valid dates are available for this trend")
        periods, labels = _period_labels(dates, "month")
        temp = working.assign(_measure=measure, _period=periods).dropna(
            subset=["_measure", "_period"]
        )
        grouped = temp.groupby("_period")["_measure"].sum(min_count=1).dropna()
        return {
            "type": "timeseries",
            "data": {
                labels.get(key, str(key)): _finite_float(
                    value, spec.value_column or "measure"
                )
                for key, value in grouped.items()
            },
            "operation": "trend",
            "column": spec.value_column,
            "format_hint": spec.format_hint,
        }

    if spec.operation in {"sum", "mean", "min", "max"}:
        aggregation = spec.operation
        temp = working.assign(_measure=measure)

        if spec.group_by_column:
            grouped = (
                temp.groupby(spec.group_by_column, dropna=False)["_measure"]
                .agg(aggregation)
                .dropna()
            )
            if grouped.empty:
                raise QueryExecutionError("No usable grouped values are available")
            if spec.ranking:
                grouped = _rank_series(grouped, spec.ranking, spec.limit or 1)
                return {
                    "type": "ranked",
                    "items": [
                        {
                            "label": str(key),
                            "value": _finite_float(
                                value, spec.value_column or "measure"
                            ),
                        }
                        for key, value in grouped.items()
                    ],
                    "operation": aggregation,
                    "ranking": spec.ranking,
                    "format_hint": spec.format_hint,
                }
            grouped = grouped.sort_values(ascending=False)
            return {
                "type": "grouped",
                "data": {
                    str(key): _finite_float(
                        value, spec.value_column or "measure"
                    )
                    for key, value in grouped.items()
                },
                "operation": aggregation,
                "column": spec.value_column,
                "format_hint": spec.format_hint,
            }

        values = _require_numeric_values(
            temp["_measure"],
            spec.value_column or spec.derived_measure or "measure",
        )
        value = getattr(values, aggregation)()
        result = {
            "type": "scalar",
            "value": _finite_float(
                value,
                spec.value_column or spec.derived_measure or "measure",
            ),
            "operation": aggregation,
            "column": spec.value_column,
            "derived_measure": spec.derived_measure,
            "row_count": int(len(working)),
            "format_hint": spec.format_hint,
        }

        if aggregation in {"min", "max"} and spec.return_columns:
            index = values.idxmax() if aggregation == "max" else values.idxmin()
            result["context"] = _context_for_index(
                working,
                index,
                spec.return_columns,
            )

        if spec.include_row_count:
            result["matching_rows"] = int(len(working))

        return result

    raise QueryExecutionError(f"Unhandled operation: {spec.operation}")
