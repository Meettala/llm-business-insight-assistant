import pytest

from src.insight.question_input import parse_batch_questions, parse_single_question


def test_single_question_trims_input():
    assert parse_single_question("  Total revenue?  ") == ["Total revenue?"]


def test_single_question_rejects_blank_input():
    assert parse_single_question("   ") == []


def test_batch_questions_use_one_non_empty_line_per_question():
    value = "Total revenue?\n\n Average revenue? \nRevenue by region?"
    assert parse_batch_questions(value) == [
        "Total revenue?",
        "Average revenue?",
        "Revenue by region?",
    ]


def test_batch_questions_preserve_order_and_duplicates():
    assert parse_batch_questions("A?\nB?\nA?") == ["A?", "B?", "A?"]


def test_batch_questions_enforce_limit():
    with pytest.raises(ValueError, match="maximum is 2"):
        parse_batch_questions("A?\nB?\nC?", limit=2)


def test_batch_questions_require_positive_limit():
    with pytest.raises(ValueError, match="at least 1"):
        parse_batch_questions("A?", limit=0)
