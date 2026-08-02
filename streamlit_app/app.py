"""Streamlit demo for the LLM Business Insight Assistant.

Run from the repository root with:

    streamlit run streamlit_app/app.py
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from src.insight.data import (  # noqa: E402
    infer_column_types,
    load_csv,
    paginate_dataframe,
    profile_dataset,
)
from src.insight.executor import QueryExecutionError  # noqa: E402
from src.insight.parser_llm import llm_available  # noqa: E402
from src.insight.pipeline import ask  # noqa: E402
from src.insight.query_spec import InvalidQuerySpec  # noqa: E402

st.set_page_config(page_title="LLM Business Insight Assistant", layout="wide")
st.title("LLM Business Insight Assistant")
st.caption(
    "Ask questions about your CSV in plain English. Every answer is calculated "
    "from the complete uploaded dataset through a validated query specification."
)

if llm_available():
    mode = "LLM-assisted parsing with validated execution"
else:
    mode = "Rule-based parsing only (no API key configured)"

st.info(
    f"Query parsing mode: **{mode}**. Only a fixed set of validated operations "
    "can run against the uploaded data."
)

uploaded = st.file_uploader("Upload a CSV", type="csv")
default_path = ROOT / "data" / "sample_sales.csv"

try:
    df = load_csv(uploaded) if uploaded else load_csv(default_path)
except (pd.errors.ParserError, UnicodeDecodeError, OSError, ValueError):
    st.error(
        "The CSV could not be read. Check that it is a valid UTF-8 CSV with a "
        "header row and consistent columns."
    )
    st.stop()

if df.empty:
    st.error("The CSV is empty. Upload a file containing at least one data row.")
    st.stop()

if uploaded is None:
    st.caption(
        "Using the bundled sample sales dataset. Upload your own CSV above to "
        "try the assistant with another dataset."
    )

profile = profile_dataset(df)
column_types = infer_column_types(df)

st.subheader("Dataset overview")
metric_columns = st.columns(5)
metric_columns[0].metric("Rows", f"{profile.row_count:,}")
metric_columns[1].metric("Columns", f"{profile.column_count:,}")
metric_columns[2].metric("Missing cells", f"{profile.missing_cells:,}")
metric_columns[3].metric("Duplicate rows", f"{profile.duplicate_rows:,}")
metric_columns[4].metric(
    "Memory",
    f"{profile.memory_bytes / (1024 * 1024):,.2f} MB",
)

st.success(
    "All uploaded rows and columns are loaded for analysis. The table below is "
    "paginated only to keep the browser responsive; changing pages does not "
    "change the dataset used for answers."
)

st.subheader("Full data explorer")
control_col_1, control_col_2 = st.columns([1, 2])
page_size = control_col_1.selectbox(
    "Rows per page",
    options=[25, 50, 100, 250, 500, 1000],
    index=2,
)
total_pages = max(1, math.ceil(profile.row_count / page_size))
page_number = control_col_2.number_input(
    "Page",
    min_value=1,
    max_value=total_pages,
    value=1,
    step=1,
)

selected_columns = st.multiselect(
    "Columns to display",
    options=list(df.columns),
    default=list(df.columns),
    help=(
        "All columns are selected by default. Hiding a column only changes the "
        "table view; analysis still uses the complete uploaded dataset."
    ),
)

if not selected_columns:
    st.warning("Select at least one column to display in the data explorer.")
else:
    displayed_df = df.loc[:, selected_columns]
    page = paginate_dataframe(
        displayed_df,
        page_number=int(page_number),
        page_size=int(page_size),
    )
    st.caption(
        f"Showing rows {page.start_row:,}–{page.end_row:,} of "
        f"{page.total_rows:,} · Page {page.page_number:,} of {page.total_pages:,}"
    )
    st.dataframe(
        page.dataframe,
        use_container_width=True,
        hide_index=False,
        height=520,
    )

with st.expander("Column schema and detected types"):
    schema_df = pd.DataFrame(
        {
            "column": list(df.columns),
            "detected_type": [column_types[column] for column in df.columns],
            "pandas_dtype": [str(df[column].dtype) for column in df.columns],
            "non_null_rows": [int(df[column].notna().sum()) for column in df.columns],
            "missing_rows": [int(df[column].isna().sum()) for column in df.columns],
            "unique_values": [int(df[column].nunique(dropna=True)) for column in df.columns],
        }
    )
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

question = st.text_input(
    "Ask a question",
    value="What is the total revenue by region?",
)

if st.button("Ask"):
    if not question.strip():
        st.warning("Enter a question before running the analysis.")
        st.stop()

    try:
        result = ask(df, question.strip())
    except InvalidQuerySpec as exc:
        st.warning(
            "That question cannot be represented safely with the supported "
            f"operations. Details: {exc}"
        )
        st.stop()
    except QueryExecutionError as exc:
        st.warning(str(exc))
        st.stop()
    except (KeyError, TypeError, ValueError):
        st.error(
            "The analysis could not be completed for this dataset. Try a more "
            "specific question using one of the detected columns."
        )
        st.stop()

    st.markdown(f"**Answer** ({result['mode']} parsing):")
    st.text(result["explanation"])

    result_data = result["result"]
    if result_data["type"] == "grouped":
        chart_df = pd.DataFrame(
            list(result_data["data"].items()),
            columns=["group", "value"],
        ).set_index("group")
        st.bar_chart(chart_df)
    elif result_data["type"] == "timeseries":
        chart_df = pd.DataFrame(
            list(result_data["data"].items()),
            columns=["period", "value"],
        ).set_index("period")
        st.line_chart(chart_df)

    with st.expander("Show the validated query spec"):
        st.json(result["spec"])
