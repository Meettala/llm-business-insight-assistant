"""Helpers for normalising single-question and batch-question input."""

from __future__ import annotations

MAX_BATCH_QUESTIONS = 100


def parse_single_question(value: str) -> list[str]:
    """Return one trimmed question, or an empty list for blank input."""
    question = value.strip()
    return [question] if question else []


def parse_batch_questions(value: str, *, limit: int = MAX_BATCH_QUESTIONS) -> list[str]:
    """Return non-empty questions from a one-question-per-line text block.

    Blank lines are ignored. Order and duplicate questions are preserved because
    both can be useful when validating repeatability. A bounded batch protects
    the interactive app from accidental very large submissions.
    """
    if limit < 1:
        raise ValueError("Batch question limit must be at least 1")

    questions = [line.strip() for line in value.splitlines() if line.strip()]
    if len(questions) > limit:
        raise ValueError(
            f"Batch contains {len(questions)} questions; the maximum is {limit}."
        )
    return questions
