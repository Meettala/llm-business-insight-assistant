"""Safe presentation choices for chart-ready analytical results.

This module controls only visualization. It never changes the validated query,
filters, aggregation, or calculated answer.
"""

from __future__ import annotations

CHART_TYPES_BY_RESULT = {
    "grouped": ("Bar", "Horizontal bar", "Line", "Area", "Scatter", "Pie", "Donut"),
    "timeseries": ("Line", "Area", "Bar", "Scatter"),
}

COLOR_PALETTES = {
    "Office": ("#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5", "#70AD47"),
    "Modern": ("#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"),
    "Professional": ("#1F4E78", "#5B9BD5", "#A9D18E", "#FFD966", "#C55A11", "#7030A0"),
    "Vibrant": ("#E63946", "#F4A261", "#E9C46A", "#2A9D8F", "#457B9D", "#9B5DE5"),
    "Pastel": ("#A8DADC", "#F1FAEE", "#FFD6A5", "#FFADAD", "#BDB2FF", "#CAFFBF"),
    "Monochrome": ("#1F2937", "#4B5563", "#6B7280", "#9CA3AF", "#D1D5DB", "#E5E7EB"),
}


def chart_types_for(result_type: str) -> tuple[str, ...]:
    """Return allowed chart types for a deterministic result type."""
    return CHART_TYPES_BY_RESULT.get(result_type, ())


def palette_colors(name: str) -> tuple[str, ...]:
    """Return a known palette and reject unknown user-supplied names."""
    try:
        return COLOR_PALETTES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown colour palette: {name}") from exc
