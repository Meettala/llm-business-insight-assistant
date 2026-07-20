import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.insight.query_spec import QuerySpec, InvalidQuerySpec, validate_query_spec

COLUMNS = ["date", "region", "product", "revenue", "units_sold"]


def test_valid_spec_passes():
    spec = QuerySpec(operation="sum", value_column="revenue")
    validate_query_spec(spec, COLUMNS)  # should not raise


def test_rejects_operation_outside_whitelist():
    spec = QuerySpec(operation="exec")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS)


def test_rejects_operation_that_looks_like_code():
    # Simulates an LLM (or hostile input) trying to smuggle something
    # other than a whitelisted aggregation through the operation field.
    spec = QuerySpec(operation="__import__('os').system('rm -rf /')")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS)


def test_rejects_column_not_in_dataset():
    spec = QuerySpec(operation="sum", value_column="revenue; DROP TABLE users;--")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS)


def test_trend_requires_date_column():
    spec = QuerySpec(operation="trend", value_column="revenue")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS)


def test_non_count_requires_value_column():
    spec = QuerySpec(operation="sum")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS)
