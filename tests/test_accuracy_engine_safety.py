import pandas as pd
import pytest

from src.insight.executor import execute_query
from src.insight.query_spec import (
    FilterSpec,
    InvalidQuerySpec,
    QuerySpec,
    validate_query_spec,
)


COLUMNS = ["date", "region", "revenue", "cost"]
COLUMN_TYPES = {
    "date": "date",
    "region": "categorical",
    "revenue": "numeric",
    "cost": "numeric",
}


def test_rejects_unapproved_filter_operator():
    spec = QuerySpec(
        operation="sum",
        value_column="revenue",
        filters=(FilterSpec("region", "python", "__import__('os')"),),
    )
    with pytest.raises(InvalidQuerySpec, match="operator"):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_rejects_injected_filter_column():
    spec = QuerySpec(
        operation="sum",
        value_column="revenue",
        filters=(FilterSpec("region OR 1=1", "eq", "North"),),
    )
    with pytest.raises(InvalidQuerySpec, match="does not exist"):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_rejects_unapproved_derived_measure():
    spec = QuerySpec(
        operation="sum",
        derived_measure="eval_expression",
        component_columns=("revenue",),
    )
    with pytest.raises(InvalidQuerySpec, match="derived measure"):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_rejects_ranking_without_grouping():
    spec = QuerySpec(
        operation="sum",
        value_column="revenue",
        ranking="highest",
        limit=1,
    )
    with pytest.raises(InvalidQuerySpec, match="ranking requires"):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_hostile_filter_value_remains_inert_text():
    frame = pd.DataFrame(
        {
            "region": ["North", "'; DROP TABLE sales;--"],
            "revenue": [100.0, 200.0],
        }
    )
    spec = QuerySpec(
        operation="sum",
        value_column="revenue",
        filters=(
            FilterSpec(
                "region",
                "eq",
                "'; DROP TABLE sales;--",
            ),
        ),
    )
    validate_query_spec(
        spec,
        list(frame.columns),
        {"region": "categorical", "revenue": "numeric"},
    )

    result = execute_query(frame, spec)

    assert result["value"] == 200.0
