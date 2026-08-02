"""
Deterministic, schema-aware parser for business questions.

The parser never creates code. It maps plain English to a validated QuerySpec,
using column aliases, actual categorical values (when a dataframe is supplied),
typed filters, grouping, ranking, date intent, and approved derived measures.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import TYPE_CHECKING, Iterable

from .query_spec import FilterSpec, InvalidQuerySpec, QuerySpec

if TYPE_CHECKING:
    import pandas as pd


CONCEPT_ALIASES: dict[str, tuple[str, ...]] = {
    "revenue": (
        "revenue",
        "sales revenue",
        "sales amount",
        "gross revenue",
        "revenue amount",
    ),
    "net_revenue": (
        "net revenue",
        "revenue after discount",
        "discounted revenue",
        "net sales",
    ),
    "gross_profit": (
        "gross profit",
        "profit amount",
        "gross margin amount",
    ),
    "cost": (
        "total cost",
        "cost amount",
        "cost",
        "cogs",
        "cost of goods sold",
    ),
    "unit_cost": (
        "unit cost",
        "cost per unit",
    ),
    "discount_amount": (
        "discount amount",
        "discount value",
        "total discount",
    ),
    "discount_percent": (
        "discount pct",
        "discount percent",
        "discount percentage",
        "discount rate",
    ),
    "discount": ("discount",),
    "units_sold": (
        "units sold",
        "quantity sold",
        "sales quantity",
        "units",
        "quantity",
    ),
    "unit_price": (
        "unit price",
        "price per unit",
        "selling price",
        "price",
    ),
    "satisfaction_score": (
        "satisfaction score",
        "customer satisfaction",
        "satisfaction",
        "rating",
    ),
    "lead_time_days": (
        "lead time days",
        "lead time",
        "delivery lead time",
    ),
    "date": (
        "transaction date",
        "order date",
        "sale date",
        "date",
    ),
    "region": (
        "sales region",
        "region",
        "area",
        "territory",
    ),
    "category": (
        "product category",
        "category",
    ),
    "channel": (
        "sales channel",
        "channel",
    ),
    "segment": (
        "customer segment",
        "market segment",
        "segment",
    ),
    "product": (
        "product name",
        "product",
        "item",
    ),
    "sales_rep": (
        "sales representative",
        "sales rep",
        "representative",
        "salesperson",
        "rep",
    ),
    "returned": (
        "is returned",
        "returned order",
        "return status",
        "returned",
        "is_returned",
    ),
}

QUESTION_TERMS: dict[str, tuple[str, ...]] = {
    "revenue": ("revenue", "sales"),
    "net_revenue": ("net revenue", "after discount", "discounted revenue"),
    "gross_profit": ("gross profit",),
    "units_sold": ("units sold", "units", "quantity sold", "quantity"),
    "unit_price": ("unit price", "price per unit"),
    "satisfaction_score": ("satisfaction score", "satisfaction", "rating"),
    "lead_time_days": ("lead time",),
    "region": ("region", "regions"),
    "category": ("category", "categories"),
    "channel": ("channel", "channels"),
    "segment": ("segment", "segments"),
    "product": ("product", "products"),
    "sales_rep": (
        "sales rep",
        "sales representative",
        "representative",
        "salesperson",
    ),
    "date": ("date", "dates"),
    "returned": ("returned", "return"),
}

CURRENCY_CONCEPTS = {
    "revenue",
    "net_revenue",
    "gross_profit",
    "unit_price",
    "cost",
}


def _normalise(text: object) -> str:
    value = str(text)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = value.replace("%", " percent ")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value)


def _strip_numbering(question: str) -> str:
    return re.sub(r"^\s*\d+\s*(?:[\t.)\-:]+|\s+)", "", question).strip()


def _column_score(column: str, aliases: Iterable[str], concept: str) -> int:
    column_norm = _normalise(column)
    column_tokens = set(column_norm.split())
    best = 0
    for position, alias in enumerate(aliases):
        alias_norm = _normalise(alias)
        alias_tokens = set(alias_norm.split())
        if column_norm == alias_norm:
            best = max(best, 120 - position)
        elif alias_norm in column_norm or column_norm in alias_norm:
            best = max(best, 95 - position)
        elif alias_tokens and alias_tokens.issubset(column_tokens):
            best = max(best, 80 - position)
        elif column_tokens and column_tokens.issubset(alias_tokens):
            best = max(best, 70 - position)

    if concept == "revenue" and any(
        token in column_tokens for token in {"net", "profit", "margin", "discount"}
    ):
        best -= 60
    if concept == "net_revenue" and not (
        "net" in column_tokens or "discount" in column_tokens
    ):
        best -= 100
    if concept == "gross_profit" and "profit" not in column_tokens:
        best -= 100
    if concept == "discount_percent" and not (
        {"percent", "percentage", "pct", "rate"} & column_tokens
    ):
        best -= 80
    if concept == "discount_amount" and not (
        {"amount", "value", "total"} & column_tokens
    ):
        best -= 60
    if concept == "unit_cost" and "unit" not in column_tokens:
        best -= 80
    if concept == "unit_price" and "unit" not in column_tokens and "price" in column_tokens:
        best -= 10
    return best


def _resolve_column(
    concept: str,
    columns: list[str],
    column_types: dict[str, str],
    required_type: str | None = None,
) -> str | None:
    aliases = CONCEPT_ALIASES.get(concept, (concept,))
    candidates: list[tuple[int, str]] = []
    for column in columns:
        if required_type is not None and column_types.get(column) != required_type:
            continue
        score = _column_score(column, aliases, concept)
        if score > 0:
            candidates.append((score, column))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
    score, column = candidates[0]
    return column if score >= 45 else None


def _mentioned_concept(question_norm: str, concepts: Iterable[str]) -> str | None:
    scored: list[tuple[int, str]] = []
    for concept in concepts:
        for term in QUESTION_TERMS.get(concept, (concept,)):
            term_norm = _normalise(term)
            if term_norm and re.search(rf"\b{re.escape(term_norm)}\b", question_norm):
                scored.append((len(term_norm), concept))
    if not scored:
        return None
    scored.sort(reverse=True)
    return scored[0][1]


def _measure_intent(question_norm: str) -> str | None:
    priority = (
        "net_revenue",
        "gross_profit",
        "unit_price",
        "satisfaction_score",
        "lead_time_days",
        "units_sold",
        "revenue",
    )
    return _mentioned_concept(question_norm, priority)


def _ranking(question_norm: str) -> str | None:
    if any(term in question_norm for term in ("highest", "maximum", "most", "top")):
        return "highest"
    if any(term in question_norm for term in ("lowest", "minimum", "fewest", "bottom")):
        return "lowest"
    return None


def _base_operation(question_norm: str) -> str:
    if any(term in question_norm for term in ("average", "mean", "avg")):
        return "mean"
    if any(term in question_norm for term in ("total", "sum", "how much")):
        return "sum"
    if any(
        term in question_norm
        for term in ("how many", "row count", "record count", "number of", "count")
    ):
        return "count"
    if any(term in question_norm for term in ("maximum", "highest", "max ")):
        return "max"
    if any(term in question_norm for term in ("minimum", "lowest", "min ")):
        return "min"
    return "count"


def _categorical_value_filters(
    question_norm: str,
    columns: list[str],
    column_types: dict[str, str],
    data: "pd.DataFrame | None",
) -> tuple[FilterSpec, ...]:
    if data is None:
        return ()

    raw_matches: dict[str, list[tuple[str, object]]] = defaultdict(list)
    for column in columns:
        if column_types.get(column) != "categorical":
            continue
        series = data[column].dropna()
        unique_values = series.unique()
        if len(unique_values) > 500:
            continue
        for value in unique_values:
            value_norm = _normalise(value)
            if len(value_norm) < 2:
                continue
            if re.search(rf"\b{re.escape(value_norm)}\b", question_norm):
                raw_matches[value_norm].append((column, value))

    filters: list[FilterSpec] = []
    for value_norm, matches in raw_matches.items():
        if len(matches) == 1:
            column, value = matches[0]
            filters.append(FilterSpec(column=column, operator="eq", value=value))
            continue

        ranked: list[tuple[int, str, object]] = []
        for column, value in matches:
            column_norm = _normalise(column)
            score = 2 if column_norm in question_norm else 0
            for concept, aliases in CONCEPT_ALIASES.items():
                if _column_score(column, aliases, concept) >= 45 and any(
                    _normalise(term) in question_norm
                    for term in QUESTION_TERMS.get(concept, ())
                ):
                    score += 3
            ranked.append((score, column, value))
        ranked.sort(reverse=True)
        if ranked and ranked[0][0] > ranked[1][0]:
            _, column, value = ranked[0]
            filters.append(FilterSpec(column=column, operator="eq", value=value))

    return tuple(filters)


def _year_filters(
    question_norm: str,
    date_column: str | None,
) -> tuple[FilterSpec, ...]:
    if date_column is None:
        return ()
    years = {
        int(match)
        for match in re.findall(r"\b(?:19|20|21)\d{2}\b", question_norm)
    }
    return tuple(
        FilterSpec(column=date_column, operator="year_eq", value=year)
        for year in sorted(years)
    )


def _deduplicate_filters(filters: Iterable[FilterSpec]) -> tuple[FilterSpec, ...]:
    output: list[FilterSpec] = []
    seen: set[tuple[str, str, str]] = set()
    for item in filters:
        marker = (item.column, item.operator, _normalise(item.value))
        if marker not in seen:
            output.append(item)
            seen.add(marker)
    return tuple(output)


def _direct_or_derived_net_revenue(
    columns: list[str],
    column_types: dict[str, str],
) -> tuple[str | None, str | None, tuple[str, ...]]:
    direct = _resolve_column("net_revenue", columns, column_types, "numeric")
    if direct:
        return direct, None, ()

    revenue = _resolve_column("revenue", columns, column_types, "numeric")
    if revenue is None:
        return None, None, ()

    amount = _resolve_column("discount_amount", columns, column_types, "numeric")
    if amount:
        return None, "net_revenue_amount", (revenue, amount)

    percent = _resolve_column("discount_percent", columns, column_types, "numeric")
    if percent:
        return None, "net_revenue_percent", (revenue, percent)

    discount = _resolve_column("discount", columns, column_types, "numeric")
    if discount:
        return None, "net_revenue_auto", (revenue, discount)

    return None, None, ()


def _direct_or_derived_gross_profit(
    columns: list[str],
    column_types: dict[str, str],
) -> tuple[str | None, str | None, tuple[str, ...]]:
    direct = _resolve_column("gross_profit", columns, column_types, "numeric")
    if direct:
        return direct, None, ()

    revenue = _resolve_column("revenue", columns, column_types, "numeric")
    if revenue is None:
        return None, None, ()

    cost = _resolve_column("cost", columns, column_types, "numeric")
    if cost:
        return None, "gross_profit_amount", (revenue, cost)

    unit_cost = _resolve_column("unit_cost", columns, column_types, "numeric")
    units = _resolve_column("units_sold", columns, column_types, "numeric")
    if unit_cost and units:
        return None, "gross_profit_unit_cost", (revenue, unit_cost, units)

    return None, None, ()


def _profit_margin_spec(
    columns: list[str],
    column_types: dict[str, str],
) -> QuerySpec:
    revenue = _resolve_column("revenue", columns, column_types, "numeric")
    gross_profit = _resolve_column("gross_profit", columns, column_types, "numeric")
    if revenue and gross_profit:
        return QuerySpec(
            operation="ratio",
            value_column=revenue,
            derived_measure="profit_margin_from_gross_profit",
            component_columns=(gross_profit, revenue),
            format_hint="percentage",
        )

    cost = _resolve_column("cost", columns, column_types, "numeric")
    if revenue and cost:
        return QuerySpec(
            operation="ratio",
            value_column=revenue,
            derived_measure="profit_margin_from_cost",
            component_columns=(revenue, cost),
            format_hint="percentage",
        )

    unit_cost = _resolve_column("unit_cost", columns, column_types, "numeric")
    units = _resolve_column("units_sold", columns, column_types, "numeric")
    if revenue and unit_cost and units:
        return QuerySpec(
            operation="ratio",
            value_column=revenue,
            derived_measure="profit_margin_from_unit_cost",
            component_columns=(revenue, unit_cost, units),
            format_hint="percentage",
        )

    return QuerySpec(
        operation="ratio",
        value_column=revenue,
        derived_measure=None,
        format_hint="percentage",
    )


def _format_hint(measure_concept: str | None, operation: str) -> str:
    if operation == "count":
        return "integer"
    if measure_concept in CURRENCY_CONCEPTS:
        return "currency"
    if measure_concept == "units_sold" and operation == "sum":
        return "integer"
    return "number"


def _context_columns(
    columns: list[str],
    column_types: dict[str, str],
) -> tuple[str, ...]:
    categorical = [
        column for column in columns if column_types.get(column) == "categorical"
    ]
    dates = [column for column in columns if column_types.get(column) == "date"]
    return tuple((categorical + dates)[:4])


def parse_question(
    question: str,
    columns: list[str],
    column_types: dict[str, str],
    data: "pd.DataFrame | None" = None,
) -> QuerySpec:
    """Parse one question into a typed QuerySpec without executing anything."""
    cleaned_question = _strip_numbering(question)
    question_norm = _normalise(cleaned_question)

    date_column = _resolve_column("date", columns, column_types, "date")
    if re.search(r"\b(?:19|20|21)\d{2}\b", question_norm) and date_column is None:
        raise InvalidQuerySpec("A year-specific question requires a date column")

    if "date range" in question_norm or (
        "earliest date" in question_norm and "latest date" in question_norm
    ):
        return QuerySpec(
            operation="date_range",
            date_column=date_column,
            format_hint="number",
        )

    distinct_concept = _mentioned_concept(
        question_norm,
        ("region", "category", "channel", "segment", "product", "sales_rep"),
    )
    if distinct_concept and any(
        phrase in question_norm
        for phrase in (
            "what regions",
            "which regions",
            "what categories",
            "which categories",
            "what channels",
            "which channels",
            "what segments",
            "which segments",
            "what products",
            "which products are",
            "unique ",
            "distinct ",
            "in the data",
        )
    ):
        value_column = _resolve_column(
            distinct_concept,
            columns,
            column_types,
            "categorical",
        )
        return QuerySpec(
            operation="distinct",
            value_column=value_column,
            format_hint="number",
        )

    if "profit margin" in question_norm or "margin percent" in question_norm:
        return _profit_margin_spec(columns, column_types)

    if "returned" in question_norm and any(
        phrase in question_norm
        for phrase in ("how many", "number of", "count", "orders were returned")
    ):
        returned_column = _resolve_column("returned", columns, column_types)
        if returned_column is None:
            raise InvalidQuerySpec(
                "The question requires a returned/order-status column"
            )
        filters = (
            FilterSpec(
                column=returned_column,
                operator="truthy",
                value=True,
            ),
        )
        return QuerySpec(
            operation="count",
            filters=filters,
            include_percentage=True,
            format_hint="integer",
        )

    measure_concept = _measure_intent(question_norm)
    direct_value: str | None = None
    derived_measure: str | None = None
    component_columns: tuple[str, ...] = ()

    if measure_concept == "net_revenue":
        direct_value, derived_measure, component_columns = (
            _direct_or_derived_net_revenue(columns, column_types)
        )
    elif measure_concept == "gross_profit":
        direct_value, derived_measure, component_columns = (
            _direct_or_derived_gross_profit(columns, column_types)
        )
    elif measure_concept is not None:
        direct_value = _resolve_column(
            measure_concept,
            columns,
            column_types,
            "numeric",
        )

    operation = _base_operation(question_norm)
    rank = _ranking(question_norm)

    group_concept = _mentioned_concept(
        question_norm,
        ("sales_rep", "product", "region", "category", "channel", "segment"),
    )
    group_column = (
        _resolve_column(group_concept, columns, column_types, "categorical")
        if group_concept
        else None
    )

    filters = list(
        _categorical_value_filters(
            question_norm,
            columns,
            column_types,
            data,
        )
    )
    filters.extend(_year_filters(question_norm, date_column))
    filters = list(_deduplicate_filters(filters))
    filtered_columns = {item.column for item in filters}

    if group_column in filtered_columns:
        group_column = None

    explicit_count = any(
        phrase in question_norm
        for phrase in ("how many", "row count", "record count", "number of", "count")
    )
    explicit_average = any(
        phrase in question_norm for phrase in ("average", "mean", "avg")
    )
    if (
        measure_concept in {"revenue", "net_revenue", "gross_profit", "units_sold"}
        and filters
        and not explicit_count
        and not explicit_average
    ):
        operation = "sum"

    month_ranking = (
        "month" in question_norm
        and rank is not None
        and measure_concept in {"revenue", "net_revenue", "gross_profit"}
    )
    year_ranking = (
        "year" in question_norm
        and rank is not None
        and not any(item.operator == "year_eq" for item in filters)
    )

    date_granularity = None
    if month_ranking:
        date_granularity = "month"
        operation = "sum"
    elif year_ranking:
        date_granularity = "year"
        operation = "sum"

    ranking_query = rank is not None and (
        group_column is not None or date_granularity is not None
    )
    if ranking_query:
        if "average" in question_norm or "mean" in question_norm:
            operation = "mean"
        elif operation == "count" and direct_value is not None:
            operation = "sum"
        elif operation in {"min", "max"}:
            operation = "sum"

    single_value_query = any(
        phrase in question_norm
        for phrase in (
            "single transaction",
            "single transaction revenue",
            "revenue value",
            "highest revenue value",
            "lowest revenue value",
        )
    )
    if single_value_query and rank is not None:
        operation = "max" if rank == "highest" else "min"
        group_column = None
        date_granularity = None

    if re.search(r"\bmax\b", question_norm):
        operation = "max"
    if re.search(r"\bmin\b", question_norm):
        operation = "min"

    if (
        measure_concept in {"revenue", "net_revenue", "gross_profit", "units_sold"}
        and group_column is not None
        and not any(
            phrase in question_norm for phrase in ("average", "mean", "count")
        )
    ):
        operation = "sum"

    return_columns: tuple[str, ...] = ()
    if single_value_query and "single transaction" not in question_norm:
        return_columns = _context_columns(columns, column_types)

    include_row_count = len(filters) > 1 or "matching rows" in question_norm

    return QuerySpec(
        operation=operation,
        value_column=direct_value,
        group_by_column=group_column,
        date_column=date_column if (date_granularity or operation == "trend") else None,
        filters=tuple(filters),
        ranking=rank if ranking_query else None,
        limit=1 if ranking_query else None,
        date_granularity=date_granularity,
        derived_measure=derived_measure,
        component_columns=component_columns,
        return_columns=return_columns,
        include_row_count=include_row_count,
        format_hint=_format_hint(measure_concept, operation),
    )
