import pandas as pd
import pytest

from src.insight.data import paginate_dataframe, profile_dataset


def test_profile_dataset_uses_complete_dataframe() -> None:
    df = pd.DataFrame(
        {
            "name": ["A", "B", "B"],
            "value": [1.0, None, None],
            "extra": [True, False, False],
        }
    )

    profile = profile_dataset(df)

    assert profile.row_count == 3
    assert profile.column_count == 3
    assert profile.missing_cells == 2
    assert profile.duplicate_rows == 1
    assert profile.memory_bytes > 0


def test_pagination_makes_every_row_reachable() -> None:
    df = pd.DataFrame({"row_id": range(1, 251), "label": ["x"] * 250})

    first = paginate_dataframe(df, page_number=1, page_size=100)
    second = paginate_dataframe(df, page_number=2, page_size=100)
    third = paginate_dataframe(df, page_number=3, page_size=100)

    combined = pd.concat(
        [first.dataframe, second.dataframe, third.dataframe],
        ignore_index=True,
    )

    assert first.start_row == 1
    assert first.end_row == 100
    assert third.start_row == 201
    assert third.end_row == 250
    assert third.total_pages == 3
    assert combined["row_id"].tolist() == list(range(1, 251))
    assert combined.columns.tolist() == ["row_id", "label"]


def test_pagination_rejects_invalid_inputs() -> None:
    df = pd.DataFrame({"value": [1, 2, 3]})

    with pytest.raises(ValueError, match="page_size"):
        paginate_dataframe(df, page_number=1, page_size=0)

    with pytest.raises(ValueError, match="page_number"):
        paginate_dataframe(df, page_number=2, page_size=10)
