"""
CSV loading and automatic column type detection.
"""

from __future__ import annotations

import pandas as pd


def load_csv(path_or_buffer) -> pd.DataFrame:
    df = pd.read_csv(path_or_buffer)
    return df


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
