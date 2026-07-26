"""Injection-resistance tests for hostile dataset and query content."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest

from src.insight.data import infer_column_types
from src.insight.executor import execute_query
from src.insight.query_spec import InvalidQuerySpec, QuerySpec, validate_query_spec

HOSTILE_DF = pd.DataFrame(
    {
        "region": [
            "North",
            "'; DROP TABLE sales;--",
            "=1+1+cmd|'/c calc'!A1",
            "South",
        ],
        "revenue": [100, 200, 300, 400],
    }
)


def test_hostile_cell_value_is_treated_as_inert_text():
    column_types = infer_column_types(HOSTILE_DF)
    spec = QuerySpec(
        operation="sum",
        value_column="revenue",
        group_by_column="region",
    )

    validate_query_spec(
        spec,
        list(HOSTILE_DF.columns),
        column_types,
    )
    result = execute_query(HOSTILE_DF, spec)

    assert "'; DROP TABLE sales;--" in result["data"]
    assert result["data"]["'; DROP TABLE sales;--"] == 200


def test_query_spec_cannot_carry_arbitrary_code_as_operation():
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(
            QuerySpec(operation="os.system('ls')"),
            list(HOSTILE_DF.columns),
        )


def test_query_spec_cannot_reference_nonexistent_injected_column():
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(
            QuerySpec(operation="sum", value_column="revenue) OR 1=1--"),
            list(HOSTILE_DF.columns),
        )
