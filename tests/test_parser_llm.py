import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.insight.parser_llm import InvalidLLMResponse, parse_llm_response


def test_parses_valid_json_object():
    spec = parse_llm_response(
        '{"operation":"sum","value_column":"revenue",'
        '"group_by_column":"region","date_column":null}'
    )

    assert spec.operation == "sum"
    assert spec.value_column == "revenue"
    assert spec.group_by_column == "region"
    assert spec.date_column is None


def test_accepts_json_markdown_fence():
    spec = parse_llm_response(
        '```json\n{"operation":"count","value_column":null,'
        '"group_by_column":null,"date_column":null}\n```'
    )

    assert spec.operation == "count"


@pytest.mark.parametrize("raw", ["", "   ", "not json", "{}"])
def test_rejects_empty_invalid_or_missing_operation(raw):
    with pytest.raises(InvalidLLMResponse):
        parse_llm_response(raw)


def test_rejects_json_array():
    with pytest.raises(InvalidLLMResponse, match="JSON object"):
        parse_llm_response('[{"operation":"count"}]')


def test_rejects_unknown_fields():
    with pytest.raises(InvalidLLMResponse, match="unsupported fields"):
        parse_llm_response('{"operation":"count","code":"import os"}')


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("value_column", 123),
        ("group_by_column", ["region"]),
        ("date_column", {"name": "date"}),
    ],
)
def test_rejects_invalid_field_types(field_name, value):
    raw = json.dumps({"operation": "sum", field_name: value})
    with pytest.raises(InvalidLLMResponse, match=field_name):
        parse_llm_response(raw)


def test_parses_typed_filters_and_ranking():
    spec = parse_llm_response(
        json.dumps(
            {
                "operation": "sum",
                "value_column": "revenue",
                "group_by_column": "sales_rep",
                "filters": [
                    {
                        "column": "region",
                        "operator": "eq",
                        "value": "North",
                    }
                ],
                "ranking": "highest",
                "limit": 1,
                "format_hint": "currency",
            }
        )
    )

    assert spec.filters[0].column == "region"
    assert spec.filters[0].value == "North"
    assert spec.ranking == "highest"
    assert spec.limit == 1


def test_rejects_nested_filter_value():
    raw = json.dumps(
        {
            "operation": "sum",
            "value_column": "revenue",
            "filters": [
                {
                    "column": "region",
                    "operator": "eq",
                    "value": {"$ne": None},
                }
            ],
        }
    )

    with pytest.raises(InvalidLLMResponse, match="scalar"):
        parse_llm_response(raw)
