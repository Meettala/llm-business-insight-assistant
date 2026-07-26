import pandas as pd

from src.insight import pipeline
from src.insight.query_spec import QuerySpec


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": ["North", "South"],
            "revenue": [100.0, 200.0],
        }
    )


def test_provider_failure_falls_back_to_rule_based(monkeypatch, caplog):
    monkeypatch.setattr(pipeline, "llm_available", lambda: True)

    def fail_provider(question, columns):
        raise RuntimeError("provider unavailable: secret-token-value")

    monkeypatch.setattr(pipeline, "parse_question_llm", fail_provider)
    monkeypatch.setattr(
        pipeline,
        "parse_question",
        lambda question, columns, column_types: QuerySpec(
            operation="sum",
            value_column="revenue",
        ),
    )

    result = pipeline.ask(_sample_frame(), "What is total revenue?")

    assert result["mode"] == "rule_based"
    assert result["result"]["value"] == 300.0
    assert "secret-token-value" not in result["explanation"]
    assert "using the rule-based parser" in caplog.text


def test_llm_result_still_passes_query_spec_validation(monkeypatch):
    monkeypatch.setattr(pipeline, "llm_available", lambda: True)
    monkeypatch.setattr(
        pipeline,
        "parse_question_llm",
        lambda question, columns: QuerySpec(
            operation="sum",
            value_column="region",
        ),
    )

    try:
        pipeline.ask(_sample_frame(), "Sum region")
    except Exception as exc:
        assert "numeric" in str(exc)
    else:
        raise AssertionError("Invalid LLM QuerySpec unexpectedly executed")
