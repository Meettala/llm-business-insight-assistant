import pandas as pd
import pytest

from src.insight import pipeline
from src.insight.query_spec import InvalidQuerySpec, QuerySpec


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": ["North", "South"],
            "revenue": [100.0, 200.0],
        }
    )


def test_deterministic_parser_is_primary_when_it_is_valid(monkeypatch):
    monkeypatch.setattr(pipeline, "llm_available", lambda: True)
    monkeypatch.setattr(
        pipeline,
        "parse_question",
        lambda question, columns, column_types: QuerySpec(
            operation="sum",
            value_column="revenue",
        ),
    )

    def unexpected_provider_call(question, columns):
        raise AssertionError("Provider should not run for a valid deterministic spec")

    monkeypatch.setattr(
        pipeline,
        "parse_question_llm",
        unexpected_provider_call,
    )

    result = pipeline.ask(_sample_frame(), "What is total revenue?")

    assert result["mode"] == "rule_based"
    assert result["result"]["value"] == 300.0


def test_invalid_deterministic_spec_uses_validated_llm_fallback(monkeypatch):
    monkeypatch.setattr(pipeline, "llm_available", lambda: True)
    monkeypatch.setattr(
        pipeline,
        "parse_question",
        lambda question, columns, column_types: QuerySpec(
            operation="sum",
            value_column="region",
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "parse_question_llm",
        lambda question, columns: QuerySpec(
            operation="sum",
            value_column="revenue",
        ),
    )

    result = pipeline.ask(_sample_frame(), "Sum revenue")

    assert result["mode"] == "llm_fallback"
    assert result["result"]["value"] == 300.0


def test_llm_fallback_still_passes_query_spec_validation(monkeypatch):
    monkeypatch.setattr(pipeline, "llm_available", lambda: True)
    monkeypatch.setattr(
        pipeline,
        "parse_question",
        lambda question, columns, column_types: QuerySpec(
            operation="sum",
            value_column="region",
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "parse_question_llm",
        lambda question, columns: QuerySpec(
            operation="sum",
            value_column="region",
        ),
    )

    with pytest.raises(InvalidQuerySpec, match="numeric"):
        pipeline.ask(_sample_frame(), "Sum region")
