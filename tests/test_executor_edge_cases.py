import math

import pandas as pd
import pytest

from src.insight.executor import QueryExecutionError, execute_query
from src.insight.query_spec import QuerySpec


def test_non_count_query_rejects_empty_filtered_dataset():
    frame = pd.DataFrame({"region": ["North"], "revenue": [100.0]})
    spec = QuerySpec(
        operation="sum",
        value_column="revenue",
        filter_column="region",
        filter_value="South",
    )

    with pytest.raises(QueryExecutionError, match="No rows match"):
        execute_query(frame, spec)


def test_count_returns_zero_for_empty_filtered_dataset():
    frame = pd.DataFrame({"region": ["North"], "revenue": [100.0]})
    spec = QuerySpec(
        operation="count",
        filter_column="region",
        filter_value="South",
    )

    result = execute_query(frame, spec)

    assert result["value"] == 0


def test_numeric_query_rejects_all_null_values():
    frame = pd.DataFrame({"revenue": [None, None]})
    spec = QuerySpec(operation="mean", value_column="revenue")

    with pytest.raises(QueryExecutionError, match="usable numeric values"):
        execute_query(frame, spec)


def test_trend_rejects_invalid_dates():
    frame = pd.DataFrame(
        {
            "date": ["not-a-date", "still-not-a-date"],
            "revenue": [100.0, 200.0],
        }
    )
    spec = QuerySpec(
        operation="trend",
        value_column="revenue",
        date_column="date",
    )

    with pytest.raises(QueryExecutionError, match="No valid dates"):
        execute_query(frame, spec)


def test_query_rejects_non_finite_result():
    frame = pd.DataFrame({"revenue": [math.inf]})
    spec = QuerySpec(operation="sum", value_column="revenue")

    with pytest.raises(QueryExecutionError, match="non-finite"):
        execute_query(frame, spec)
