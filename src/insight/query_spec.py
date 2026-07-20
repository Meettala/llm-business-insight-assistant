"""
QuerySpec: the single safe interface between "a question" (from a human
or an LLM) and "code that touches the uploaded data".

Neither the rule-based parser nor the optional LLM parser is ever allowed
to generate or execute arbitrary code against the DataFrame. Both must
produce a QuerySpec, which is validated against a fixed whitelist of
operations and against the DataFrame's actual columns before anything
runs. This is the single most important safety property of this project.
"""

from __future__ import annotations

from dataclasses import dataclass, field

WHITELISTED_OPERATIONS = {"sum", "mean", "count", "min", "max", "trend"}


@dataclass
class QuerySpec:
    operation: str
    value_column: str | None = None
    group_by_column: str | None = None
    date_column: str | None = None
    filter_column: str | None = None
    filter_value: str | None = None


class InvalidQuerySpec(Exception):
    pass


def validate_query_spec(spec: QuerySpec, columns: list[str]) -> None:
    if spec.operation not in WHITELISTED_OPERATIONS:
        raise InvalidQuerySpec(f"Operation '{spec.operation}' is not in the whitelist: {WHITELISTED_OPERATIONS}")

    for field_name in ("value_column", "group_by_column", "date_column", "filter_column"):
        value = getattr(spec, field_name)
        if value is not None and value not in columns:
            raise InvalidQuerySpec(f"Column '{value}' (from {field_name}) does not exist in the uploaded data")

    if spec.operation != "count" and spec.value_column is None:
        raise InvalidQuerySpec(f"Operation '{spec.operation}' requires a value_column")

    if spec.operation == "trend" and spec.date_column is None:
        raise InvalidQuerySpec("Operation 'trend' requires a date_column")
