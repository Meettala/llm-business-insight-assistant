import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.insight.data import load_csv, infer_column_types
from src.insight.parser_rule_based import parse_question
from src.insight.executor import execute_query
from src.insight.query_spec import validate_query_spec

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"


def _load():
    df = load_csv(CSV_PATH)
    types = infer_column_types(df)
    return df, types


def test_parses_total_revenue_question():
    df, types = _load()
    spec = parse_question("What is the total revenue?", list(df.columns), types)
    validate_query_spec(spec, list(df.columns))
    assert spec.operation == "sum"
    assert spec.value_column == "revenue"


def test_parses_grouped_question():
    df, types = _load()
    spec = parse_question("What is the total revenue by region?", list(df.columns), types)
    validate_query_spec(spec, list(df.columns))
    assert spec.group_by_column == "region"


def test_executor_matches_independent_pandas_computation():
    df, types = _load()
    spec = parse_question("What is the total revenue?", list(df.columns), types)
    validate_query_spec(spec, list(df.columns))
    result = execute_query(df, spec)
    # No-fabrication check: the computed number must match an
    # independently-computed pandas sum on the same data.
    assert result["value"] == df["revenue"].sum()


def test_count_question():
    df, types = _load()
    spec = parse_question("How many rows are there?", list(df.columns), types)
    validate_query_spec(spec, list(df.columns))
    result = execute_query(df, spec)
    assert result["value"] == len(df)
