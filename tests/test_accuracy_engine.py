import pandas as pd
import pytest

from src.insight.data import infer_column_types
from src.insight.executor import execute_query
from src.insight.explain import explain_result
from src.insight.parser_rule_based import parse_question
from src.insight.query_spec import FilterSpec, QuerySpec, validate_query_spec


@pytest.fixture
def narrow_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": [
                "2026-01-01",
                "2026-01-03",
                "2026-01-11",
                "2026-01-29",
            ],
            "region": ["East", "North", "South", "West"],
            "revenue": [4765.39, 18795.48, 668.73, 7300.13],
        }
    )


@pytest.fixture
def wide_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": [
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
                "2026-01-04",
            ],
            "region": ["East", "North", "South", "West"],
            "category": [
                "Electronics",
                "Hardware",
                "Mechanical",
                "Electronics",
            ],
            "channel": ["Online", "Wholesale", "Retail Store", "Marketplace"],
            "segment": ["Enterprise", "SMB", "Enterprise", "Consumer"],
            "product": ["Widget A", "Component Q", "Widget A", "Other"],
            "sales_rep": ["T. Brown", "J. Adams", "T. Brown", "K. Lee"],
            "revenue": [1000.0, 800.0, 600.0, 400.0],
            "net_revenue": [900.0, 700.0, 550.0, 350.0],
            "unit_price": [100.0, 80.0, 60.0, 40.0],
            "units_sold": [10, 10, 10, 10],
            "satisfaction_score": [4.0, 3.0, 3.5, 3.0],
            "returned": ["Yes", "No", "No", "Yes"],
            "gross_profit": [450.0, 300.0, 250.0, 150.0],
            "lead_time_days": [5.0, 7.0, 10.0, 8.0],
        }
    )


@pytest.fixture
def long_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": [
                "2023-01-01",
                "2024-03-01",
                "2025-03-01",
                "2024-04-01",
            ],
            "region": ["North", "South", "North", "East"],
            "product": ["Gadget X", "Gadget Y", "Gadget X", "Widget A"],
            "units_sold": [10, 20, 30, 40],
            "revenue": [100.0, 200.0, 300.0, 400.0],
        }
    )


def _parse(frame: pd.DataFrame, question: str) -> QuerySpec:
    types = infer_column_types(frame)
    spec = parse_question(
        question,
        list(frame.columns),
        types,
        data=frame,
    )
    validate_query_spec(spec, list(frame.columns), types)
    return spec


@pytest.mark.parametrize(
    ("question", "operation", "value_column", "filter_column", "filter_value"),
    [
        ("What's the total revenue?", "sum", "revenue", None, None),
        ("What's the average revenue?", "mean", "revenue", None, None),
        ("How many rows/records are there?", "count", None, None, None),
        ("What's the total revenue for North?", "sum", "revenue", "region", "North"),
        ("How many entries are from North?", "count", None, "region", "North"),
        (
            "What's the average revenue for South?",
            "mean",
            "revenue",
            "region",
            "South",
        ),
        ("What's the highest revenue value?", "max", "revenue", None, None),
        ("What's the lowest revenue value?", "min", "revenue", None, None),
        ("What regions are in the data?", "distinct", "region", None, None),
        ("What's the date range?", "date_range", None, None, None),
    ],
)
def test_narrow_question_intents(
    narrow_frame,
    question,
    operation,
    value_column,
    filter_column,
    filter_value,
):
    spec = _parse(narrow_frame, question)

    assert spec.operation == operation
    assert spec.value_column == value_column
    if filter_column is None:
        assert not spec.filters
    else:
        assert FilterSpec(filter_column, "eq", filter_value) in spec.filters


def test_narrow_distinct_and_date_range_answers(narrow_frame):
    regions = _parse(narrow_frame, "What regions are in the data?")
    regions_result = execute_query(narrow_frame, regions)
    assert regions_result["values"] == ["East", "North", "South", "West"]

    date_range = _parse(narrow_frame, "What's the date range?")
    date_result = execute_query(narrow_frame, date_range)
    assert date_result["start"] == "2026-01-01"
    assert date_result["end"] == "2026-01-29"


def test_narrow_extreme_value_includes_context(narrow_frame):
    spec = _parse(narrow_frame, "What's the highest revenue value?")
    result = execute_query(narrow_frame, spec)

    assert result["value"] == pytest.approx(18795.48)
    assert result["context"] == {
        "region": "North",
        "date": "2026-01-03",
    }


@pytest.mark.parametrize(
    ("question", "operation", "value_column"),
    [
        ("Total revenue?", "sum", "revenue"),
        ("Total net revenue (after discount)?", "sum", "net_revenue"),
        ("Average unit price?", "mean", "unit_price"),
        ("Total units sold?", "sum", "units_sold"),
        ("Average satisfaction score?", "mean", "satisfaction_score"),
        ("Total gross profit?", "sum", "gross_profit"),
        ("Average lead time (days)?", "mean", "lead_time_days"),
    ],
)
def test_wide_measure_column_selection(
    wide_frame,
    question,
    operation,
    value_column,
):
    spec = _parse(wide_frame, question)
    assert spec.operation == operation
    assert spec.value_column == value_column


@pytest.mark.parametrize(
    ("question", "column", "value"),
    [
        ("Revenue by category — Electronics?", "category", "Electronics"),
        ("Revenue by category — Hardware?", "category", "Hardware"),
        ("Revenue by category — Mechanical?", "category", "Mechanical"),
        ("Revenue by channel — Online?", "channel", "Online"),
        (
            "Revenue by channel — Wholesale (lowest)?",
            "channel",
            "Wholesale",
        ),
        ("Revenue by region — East (highest)?", "region", "East"),
        (
            "Revenue by segment — Enterprise (highest)?",
            "segment",
            "Enterprise",
        ),
    ],
)
def test_wide_specific_group_value_is_a_sum_filter(
    wide_frame,
    question,
    column,
    value,
):
    spec = _parse(wide_frame, question)

    assert spec.operation == "sum"
    assert spec.value_column == "revenue"
    assert spec.group_by_column is None
    assert FilterSpec(column, "eq", value) in spec.filters


def test_conditional_count_includes_percentage(wide_frame):
    spec = _parse(wide_frame, "How many orders were returned?")
    result = execute_query(wide_frame, spec)

    assert spec.operation == "count"
    assert spec.include_percentage is True
    assert result["value"] == 2
    assert result["total_rows"] == 4
    assert result["percentage"] == pytest.approx(50.0)
    assert explain_result("", spec, result) == "2 out of 4 (50.0%)."


@pytest.mark.parametrize(
    ("question", "group_column", "value_column", "ranking"),
    [
        (
            "Which sales rep had the highest revenue?",
            "sales_rep",
            "revenue",
            "highest",
        ),
        (
            "Which sales rep had the lowest revenue?",
            "sales_rep",
            "revenue",
            "lowest",
        ),
        (
            "Which product sold the most units?",
            "product",
            "units_sold",
            "highest",
        ),
        (
            "Which product sold the fewest units?",
            "product",
            "units_sold",
            "lowest",
        ),
    ],
)
def test_grouped_ranking_intents(
    wide_frame,
    question,
    group_column,
    value_column,
    ranking,
):
    spec = _parse(wide_frame, question)

    assert spec.operation == "sum"
    assert spec.group_by_column == group_column
    assert spec.value_column == value_column
    assert spec.ranking == ranking
    assert spec.limit == 1


def test_grouped_ranking_executes_sum_then_rank(wide_frame):
    spec = _parse(
        wide_frame,
        "Which sales rep had the highest revenue?",
    )
    result = execute_query(wide_frame, spec)

    assert result["type"] == "ranked"
    assert result["items"] == [{"label": "T. Brown", "value": 1600.0}]


def test_overall_profit_margin_uses_ratio_of_totals(wide_frame):
    spec = _parse(wide_frame, "Overall profit margin %?")
    result = execute_query(wide_frame, spec)

    assert spec.operation == "ratio"
    assert spec.derived_measure == "profit_margin_from_gross_profit"
    assert result["value"] == pytest.approx(1150.0 / 2800.0 * 100.0)


@pytest.mark.parametrize(
    ("question", "operation", "value_column"),
    [
        ("Total revenue?", "sum", "revenue"),
        ("Average revenue per row?", "mean", "revenue"),
        ("Total units sold?", "sum", "units_sold"),
        ("Average units sold?", "mean", "units_sold"),
        ("What's the max single-transaction revenue?", "max", "revenue"),
        ("What's the min single-transaction revenue?", "min", "revenue"),
    ],
)
def test_long_basic_measure_intents(
    long_frame,
    question,
    operation,
    value_column,
):
    spec = _parse(long_frame, question)
    assert spec.operation == operation
    assert spec.value_column == value_column


@pytest.mark.parametrize(
    ("question", "column", "value"),
    [
        ("Revenue by region — North (highest)?", "region", "North"),
        ("Revenue by region — South (lowest)?", "region", "South"),
        ("Revenue by product — Gadget X (highest)?", "product", "Gadget X"),
        ("Revenue by product — Gadget Y (lowest)?", "product", "Gadget Y"),
    ],
)
def test_long_named_values_become_filters(
    long_frame,
    question,
    column,
    value,
):
    spec = _parse(long_frame, question)
    assert spec.operation == "sum"
    assert FilterSpec(column, "eq", value) in spec.filters


@pytest.mark.parametrize("year", [2023, 2024, 2025])
def test_revenue_year_filters(long_frame, year):
    spec = _parse(long_frame, f"Revenue in {year}?")
    assert spec.operation == "sum"
    assert FilterSpec("date", "year_eq", year) in spec.filters


def test_row_count_year_filter(long_frame):
    spec = _parse(long_frame, "Row count in 2024?")
    result = execute_query(long_frame, spec)

    assert spec.operation == "count"
    assert result["value"] == 2


def test_highest_month_groups_by_month_then_ranks(long_frame):
    spec = _parse(long_frame, "Which month had the highest revenue?")
    result = execute_query(long_frame, spec)

    assert spec.operation == "sum"
    assert spec.date_granularity == "month"
    assert spec.ranking == "highest"
    assert result["items"] == [{"label": "April 2024", "value": 400.0}]


def test_multiple_filters_are_all_applied(long_frame):
    spec = _parse(
        long_frame,
        "Total revenue for North region + Gadget X product combined?",
    )
    result = execute_query(long_frame, spec)

    assert spec.filters == (
        FilterSpec("region", "eq", "North"),
        FilterSpec("product", "eq", "Gadget X"),
    )
    assert result["value"] == pytest.approx(400.0)
    assert result["matching_rows"] == 2


def test_derived_net_revenue_and_gross_profit_without_direct_columns():
    frame = pd.DataFrame(
        {
            "revenue": [100.0, 200.0],
            "discount_pct": [10.0, 20.0],
            "cost": [60.0, 100.0],
        }
    )
    net_spec = _parse(frame, "Total net revenue after discount?")
    gross_spec = _parse(frame, "Total gross profit?")

    net_result = execute_query(frame, net_spec)
    gross_result = execute_query(frame, gross_spec)

    assert net_spec.derived_measure == "net_revenue_percent"
    assert net_result["value"] == pytest.approx(250.0)
    assert gross_spec.derived_measure == "gross_profit_amount"
    assert gross_result["value"] == pytest.approx(140.0)
