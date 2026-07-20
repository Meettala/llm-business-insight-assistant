"""
Executes a validated QuerySpec against a DataFrame. This module never
receives raw text or code — only a QuerySpec that has already passed
validate_query_spec(). Every branch here is a fixed pandas operation,
never an eval() or exec() of anything derived from user or LLM input.
"""

from __future__ import annotations

import pandas as pd

from .query_spec import QuerySpec


def execute_query(df: pd.DataFrame, spec: QuerySpec) -> dict:
    working = df
    if spec.filter_column and spec.filter_value is not None:
        working = working[working[spec.filter_column].astype(str) == str(spec.filter_value)]

    if spec.operation == "count":
        if spec.group_by_column:
            result = working.groupby(spec.group_by_column).size().sort_values(ascending=False)
            return {"type": "grouped", "data": result.to_dict(), "operation": "count"}
        return {"type": "scalar", "value": int(len(working)), "operation": "count"}

    if spec.operation in {"sum", "mean", "min", "max"}:
        agg_fn = spec.operation
        if spec.group_by_column:
            result = working.groupby(spec.group_by_column)[spec.value_column].agg(agg_fn).sort_values(ascending=False)
            return {"type": "grouped", "data": result.to_dict(), "operation": agg_fn, "column": spec.value_column}
        value = getattr(working[spec.value_column], agg_fn)()
        return {"type": "scalar", "value": float(value), "operation": agg_fn, "column": spec.value_column}

    if spec.operation == "trend":
        working = working.copy()
        working[spec.date_column] = pd.to_datetime(working[spec.date_column], errors="coerce", format="mixed")
        working = working.dropna(subset=[spec.date_column])
        grouped = working.groupby(working[spec.date_column].dt.to_period("M"))[spec.value_column].sum()
        return {
            "type": "timeseries",
            "data": {str(k): float(v) for k, v in grouped.items()},
            "operation": "trend",
            "column": spec.value_column,
        }

    raise ValueError(f"Unhandled operation: {spec.operation}")  # unreachable if validated first
