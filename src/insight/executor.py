"""Execute validated analytical operations against a DataFrame.

This module receives only a QuerySpec that has passed application validation.
Every execution branch is a fixed pandas operation; no generated code, SQL, or
expression strings are evaluated.
"""

from __future__ import annotations

import math

import pandas as pd

from .query_spec import QuerySpec


class QueryExecutionError(ValueError):
    """Raised when valid query intent cannot produce a usable result."""


def _require_rows(working: pd.DataFrame) -> None:
    if working.empty:
        raise QueryExecutionError("No rows match this query")


def _require_numeric_values(series: pd.Series, column: str) -> pd.Series:
    usable = series.dropna()
    if usable.empty:
        raise QueryExecutionError(
            f"Column '{column}' does not contain usable numeric values"
        )
    return usable


def _finite_float(value, column: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise QueryExecutionError(
            f"Column '{column}' produced a non-finite analytical result"
        )
    return number


def execute_query(df: pd.DataFrame, spec: QuerySpec) -> dict:
    """Execute one validated QuerySpec and return a serialisable result."""
    working = df
    if spec.filter_column and spec.filter_value is not None:
        matches_filter = working[spec.filter_column].astype(str) == str(
            spec.filter_value
        )
        working = working[matches_filter]

    if spec.operation == "count":
        if spec.group_by_column:
            result = (
                working.groupby(spec.group_by_column, dropna=False)
                .size()
                .sort_values(ascending=False)
            )
            return {
                "type": "grouped",
                "data": result.to_dict(),
                "operation": "count",
            }
        return {
            "type": "scalar",
            "value": int(len(working)),
            "operation": "count",
        }

    _require_rows(working)

    if spec.operation in {"sum", "mean", "min", "max"}:
        aggregation = spec.operation
        if spec.group_by_column:
            result = (
                working.groupby(spec.group_by_column)[spec.value_column]
                .agg(aggregation)
                .dropna()
                .sort_values(ascending=False)
            )
            if result.empty:
                raise QueryExecutionError(
                    f"Column '{spec.value_column}' has no usable grouped values"
                )
            data = {
                key: _finite_float(value, spec.value_column)
                for key, value in result.items()
            }
            return {
                "type": "grouped",
                "data": data,
                "operation": aggregation,
                "column": spec.value_column,
            }

        values = _require_numeric_values(
            working[spec.value_column],
            spec.value_column,
        )
        value = getattr(values, aggregation)()
        return {
            "type": "scalar",
            "value": _finite_float(value, spec.value_column),
            "operation": aggregation,
            "column": spec.value_column,
        }

    if spec.operation == "trend":
        working = working.copy()
        working[spec.date_column] = pd.to_datetime(
            working[spec.date_column],
            errors="coerce",
            format="mixed",
        )
        working = working.dropna(subset=[spec.date_column])
        if working.empty:
            raise QueryExecutionError("No valid dates are available for this trend")

        _require_numeric_values(working[spec.value_column], spec.value_column)
        periods = working[spec.date_column].dt.to_period("M")
        grouped = working.groupby(periods)[spec.value_column].sum(min_count=1).dropna()
        if grouped.empty:
            raise QueryExecutionError("No usable values are available for this trend")

        return {
            "type": "timeseries",
            "data": {
                str(key): _finite_float(value, spec.value_column)
                for key, value in grouped.items()
            },
            "operation": "trend",
            "column": spec.value_column,
        }

    raise QueryExecutionError(f"Unhandled operation: {spec.operation}")
