import pytest

from src.insight.charting import chart_types_for, palette_colors


def test_grouped_results_offer_comparison_and_share_charts():
    choices = chart_types_for("grouped")

    assert "Bar" in choices
    assert "Horizontal bar" in choices
    assert "Pie" in choices
    assert "Donut" in choices


def test_timeseries_results_offer_time_appropriate_charts():
    choices = chart_types_for("timeseries")

    assert "Line" in choices
    assert "Area" in choices
    assert "Scatter" in choices
    assert "Pie" not in choices


def test_scalar_or_unknown_results_do_not_offer_misleading_chart():
    assert chart_types_for("scalar") == ()
    assert chart_types_for("unknown") == ()


def test_known_palette_returns_fixed_safe_colours():
    colours = palette_colors("Office")

    assert colours[0] == "#4472C4"
    assert len(colours) >= 6


def test_unknown_palette_is_rejected():
    with pytest.raises(ValueError, match="Unknown colour palette"):
        palette_colors("user-controlled-css")
