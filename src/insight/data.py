"""
CSV loading, dataset profiling, pagination, and automatic column type detection.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DatasetProfile:
    """Small, safe metadata summary for an uploaded dataframe."""

    row_count: int
    column_count: int
    missing_cells: int
    duplicate_rows: int
    memory_bytes: int


@dataclass(frozen=True)
class DataPage:
    """One page from a dataframe while preserving access to the full dataset."""

    dataframe: pd.DataFrame
    page_number: int
    page_size: int
    total_pages: int
    start_row: int
    end_row: int
    total_rows: int


def load_csv(path_or_buffer) -> pd.DataFrame:
    """Load the complete CSV into a dataframe without truncating rows or columns."""

    return pd.read_csv(path_or_buffer)


def profile_dataset(df: pd.DataFrame) -> DatasetProfile:
    """Return metadata calculated from the complete dataframe."""

    return DatasetProfile(
        row_count=len(df),
        column_count=len(df.columns),
        missing_cells=int(df.isna().sum().sum()),
        duplicate_rows=int(df.duplicated().sum()),
        memory_bytes=int(df.memory_usage(index=True, deep=True).sum()),
    )


def paginate_dataframe(
    df: pd.DataFrame,
    *,
    page_number: int,
    page_size: int,
) -> DataPage:
    """Return a validated page while keeping every dataframe row reachable.

    Page numbers are one-based. Empty dataframes return one empty page so callers
    can render a stable control without special arithmetic.
    """

    if page_size <= 0:
        raise ValueError("page_size must be greater than zero")

    total_rows = len(df)
    total_pages = max(1, math.ceil(total_rows / page_size))
    if page_number < 1 or page_number > total_pages:
        raise ValueError(
            f"page_number must be between 1 and {total_pages}, got {page_number}"
        )

    start_index = (page_number - 1) * page_size
    end_index = min(start_index + page_size, total_rows)
    page_df = df.iloc[start_index:end_index]

    return DataPage(
        dataframe=page_df,
        page_number=page_number,
        page_size=page_size,
        total_pages=total_pages,
        start_row=0 if total_rows == 0 else start_index + 1,
        end_row=end_index,
        total_rows=total_rows,
    )


def infer_column_types(df: pd.DataFrame) -> dict[str, str]:
    """
    Returns a mapping of column name -> "numeric" | "date" | "categorical".
    Used both to describe the dataset to the user and to guide the
    rule-based parser's column matching.
    """
    types: dict[str, str] = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            types[col] = "numeric"
            continue
        parsed = pd.to_datetime(df[col], errors="coerce", format="mixed")
        if parsed.notna().mean() > 0.8:
            types[col] = "date"
        else:
            types[col] = "categorical"
    return types
