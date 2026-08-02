"""Coordinate parsing, validation, execution, and explanation.

This module is the required application entry point so every analytical request
passes through the same validation boundary before deterministic execution.
"""

from __future__ import annotations

import logging

import pandas as pd

from .data import infer_column_types
from .executor import execute_query
from .explain import explain_result
from .parser_llm import InvalidLLMResponse, llm_available, parse_question_llm
from .parser_rule_based import parse_question
from .query_spec import QuerySpec, validate_query_spec

LOGGER = logging.getLogger(__name__)


def ask(df: pd.DataFrame, question: str) -> dict:
    """Answer a dataset question through the validated execution pipeline."""
    columns = list(df.columns)
    column_types = infer_column_types(df)

    spec: QuerySpec
    mode = "rule_based"

    if llm_available():
        try:
            spec = parse_question_llm(question, columns)
            mode = "llm"
        except (InvalidLLMResponse, RuntimeError, ValueError):
            LOGGER.warning(
                "LLM parsing failed; using the rule-based parser instead",
                exc_info=True,
            )
            spec = parse_question(question, columns, column_types)
    else:
        spec = parse_question(question, columns, column_types)

    # This validation call is the mandatory safety boundary for every parser.
    validate_query_spec(spec, columns, column_types)

    result = execute_query(df, spec)
    explanation = explain_result(question, spec, result)

    return {
        "question": question,
        "mode": mode,
        "spec": {
            "operation": spec.operation,
            "value_column": spec.value_column,
            "group_by_column": spec.group_by_column,
            "date_column": spec.date_column,
            "filter_column": spec.filter_column,
            "filter_value": spec.filter_value,
        },
        "result": result,
        "explanation": explanation,
    }
