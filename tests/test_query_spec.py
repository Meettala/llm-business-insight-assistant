import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.insight.query_spec import InvalidQuerySpec, QuerySpec, validate_query_spec

COLUMNS = ["date", "region", "product", "revenue", "units_sold"]
COLUMN_TYPES = {
    "date": "date",
    "region": "categorical",
    "product": "categorical",
    "revenue": "numeric",
    "units_sold": "numeric",
}


def test_valid_spec_passes():
    spec = QuerySpec(operation="sum", value_column="revenue")
    validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_rejects_operation_outside_whitelist():
    spec = QuerySpec(operation="exec")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_rejects_operation_that_looks_like_code():
    spec = QuerySpec(operation="__import__('os').system('rm -rf /')")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_rejects_column_not_in_dataset():
    spec = QuerySpec(operation="sum", value_column="revenue; DROP TABLE users;--")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_trend_requires_date_column():
    spec = QuerySpec(operation="trend", value_column="revenue")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_non_count_requires_value_column():
    spec = QuerySpec(operation="sum")
    with pytest.raises(InvalidQuerySpec):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_numeric_operation_rejects_categorical_value_column():
    spec = QuerySpec(operation="sum", value_column="product")
    with pytest.raises(InvalidQuerySpec, match="requires a numeric value_column"):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_trend_rejects_non_date_column():
    spec = QuerySpec(
        operation="trend",
        value_column="revenue",
        date_column="region",
    )
    with pytest.raises(InvalidQuerySpec, match="requires a date_column"):
        validate_query_spec(spec, COLUMNS, COLUMN_TYPES)


def test_count_allows_categorical_grouping():
    spec = QuerySpec(operation="count", group_by_column="region")
    validate_query_spec(spec, COLUMNS, COLUMN_TYPES)
