"""
Ties parsing, validation, execution, and explanation together — the
single entry point both the Streamlit app and any future API route
should use, so the safety guarantees can't be bypassed by calling the
pieces directly in the wrong order.
"""

from __future__ import annotations

import pandas as pd

from .data import infer_column_types
from .executor import execute_query
from .explain import explain_result
from .parser_llm import llm_available, parse_question_llm
from .parser_rule_based import parse_question
from .query_spec import QuerySpec, validate_query_spec


def ask(df: pd.DataFrame, question: str) -> dict:
    columns = list(df.columns)
    column_types = infer_column_types(df)

    spec: QuerySpec
    mode = "rule_based"
    if llm_available():
        try:
            spec = parse_question_llm(question, columns)
            mode = "llm"
        except Exception as exc:
            print(f"[ask] LLM parsing failed, falling back to rule-based: {exc}")
            spec = parse_question(question, columns, column_types)
    else:
        spec = parse_question(question, columns, column_types)

    # Every path — rule-based or LLM — goes through the same validator
    # before touching the data. This line is the actual safety boundary.
    validate_query_spec(spec, columns)

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
        },
        "result": result,
        "explanation": explanation,
    }
