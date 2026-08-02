"""Coordinate parsing, validation, execution, and explanation."""

from __future__ import annotations

import inspect
import logging

import pandas as pd

from .data import infer_column_types
from .executor import execute_query
from .explain import explain_result
from .parser_llm import InvalidLLMResponse, llm_available, parse_question_llm
from .parser_rule_based import parse_question
from .query_spec import (
    InvalidQuerySpec,
    QuerySpec,
    query_spec_to_dict,
    validate_query_spec,
)

LOGGER = logging.getLogger(__name__)


def _parse_rule_based(
    df: pd.DataFrame,
    question: str,
    columns: list[str],
    column_types: dict[str, str],
) -> QuerySpec:
    """Call the live parser while preserving compatibility with test doubles."""
    parameters = inspect.signature(parse_question).parameters
    if "data" in parameters:
        return parse_question(
            question,
            columns,
            column_types,
            data=df,
        )
    return parse_question(question, columns, column_types)


def ask(df: pd.DataFrame, question: str) -> dict:
    """Answer one question through the validated deterministic pipeline."""
    columns = list(df.columns)
    column_types = infer_column_types(df)

    mode = "rule_based"
    rule_error: Exception | None = None

    try:
        spec = _parse_rule_based(
            df,
            question,
            columns,
            column_types,
        )
        validate_query_spec(spec, columns, column_types)
    except (InvalidQuerySpec, ValueError) as exc:
        rule_error = exc
        if not llm_available():
            raise

        try:
            spec = parse_question_llm(question, columns)
            validate_query_spec(spec, columns, column_types)
            mode = "llm_fallback"
        except (InvalidLLMResponse, InvalidQuerySpec, RuntimeError, ValueError):
            LOGGER.warning(
                "Both deterministic and LLM parsing failed",
                exc_info=True,
            )
            raise rule_error

    result = execute_query(df, spec)
    explanation = explain_result(question, spec, result)

    return {
        "question": question,
        "mode": mode,
        "spec": query_spec_to_dict(spec),
        "result": result,
        "explanation": explanation,
    }
