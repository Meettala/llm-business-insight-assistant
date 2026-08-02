"""Streamlit demo for the LLM Business Insight Assistant."""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import altair as alt  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from src.insight.charting import (  # noqa: E402
    COLOR_PALETTES,
    chart_types_for,
    palette_colors,
)
from src.insight.data import (  # noqa: E402
    infer_column_types,
    load_csv,
    paginate_dataframe,
    profile_dataset,
)
from src.insight.executor import QueryExecutionError  # noqa: E402
from src.insight.history import history_to_csv  # noqa: E402
from src.insight.parser_llm import llm_available  # noqa: E402
from src.insight.pipeline import ask  # noqa: E402
from src.insight.query_spec import InvalidQuerySpec  # noqa: E402
from src.insight.question_input import (  # noqa: E402
    MAX_BATCH_QUESTIONS,
    parse_batch_questions,
    parse_single_question,
)

st.set_page_config(page_title="LLM Business Insight Assistant", layout="wide")
st.title("LLM Business Insight Assistant")
st.caption(
    "Ask one question or test many questions together. Every answer is calculated "
    "from the complete uploaded dataset through a validated query specification."
)

if "query_history" not in st.session_state:
    st.session_state.query_history = []

mode = (
    "LLM-assisted parsing with validated execution"
    if llm_available()
    else "Rule-based parsing only (no API key configured)"
)
st.info(
    f"Query parsing mode: **{mode}**. Only a fixed set of validated operations "
    "can run against the uploaded data."
)

uploaded = st.file_uploader("Upload a CSV", type="csv")
default_path = ROOT / "data" / "sample_sales.csv"
dataset_name = uploaded.name if uploaded else default_path.name

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
    st.caption("Using the bundled sample sales dataset.")

profile = profile_dataset(df)
column_types = infer_column_types(df)

st.subheader("Dataset overview")
metric_columns = st.columns(5)
metric_columns[0].metric("Rows", f"{profile.row_count:,}")
metric_columns[1].metric("Columns", f"{profile.column_count:,}")
metric_columns[2].metric("Missing cells", f"{profile.missing_cells:,}")
metric_columns[3].metric("Duplicate rows", f"{profile.duplicate_rows:,}")
metric_columns[4].metric("Memory", f"{profile.memory_bytes / (1024 * 1024):,.2f} MB")

st.success(
    "All uploaded rows and columns are loaded for analysis. Pagination changes "
    "only the browser view, not the dataset used for answers."
)

st.subheader("Full data explorer")
control_col_1, control_col_2 = st.columns([1, 2])
page_size = control_col_1.selectbox(
    "Rows per page", options=[25, 50, 100, 250, 500, 1000], index=2
)
total_pages = max(1, math.ceil(profile.row_count / page_size))
page_number = control_col_2.number_input(
    "Page", min_value=1, max_value=total_pages, value=1, step=1
)
selected_columns = st.multiselect(
    "Columns to display",
    options=list(df.columns),
    default=list(df.columns),
    help="Hiding a column changes only the table view, not analysis scope.",
)
if not selected_columns:
    st.warning("Select at least one column to display.")
else:
    page = paginate_dataframe(
        df.loc[:, selected_columns],
        page_number=int(page_number),
        page_size=int(page_size),
    )
    st.caption(
        f"Showing rows {page.start_row:,}–{page.end_row:,} of {page.total_rows:,} "
        f"· Page {page.page_number:,} of {page.total_pages:,}"
    )
    st.dataframe(page.dataframe, use_container_width=True, height=520)

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


def record_history(question: str, status: str, **values) -> None:
    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": dataset_name,
        "question": question,
        "status": status,
        "answer": "",
        "parsing_mode": "",
        "operation": "",
        "value_column": "",
        "group_by_column": "",
        "date_column": "",
        "filter_column": "",
        "filter_value": "",
        "validated_query_spec_json": "",
        "result_json": "",
        "error": "",
    }
    row.update(values)
    st.session_state.query_history.append(row)


def run_question(question: str) -> dict:
    try:
        result = ask(df, question)
        spec = result["spec"]
        record_history(
            question,
            "answered_unverified",
            answer=result["explanation"],
            parsing_mode=result["mode"],
            operation=spec.get("operation", ""),
            value_column=spec.get("value_column", ""),
            group_by_column=spec.get("group_by_column", ""),
            date_column=spec.get("date_column", ""),
            filter_column=spec.get("filter_column", ""),
            filter_value=spec.get("filter_value", ""),
            validated_query_spec_json=json.dumps(spec, sort_keys=True),
            result_json=json.dumps(result["result"], sort_keys=True, default=str),
        )
        return {"question": question, "status": "answered_unverified", "result": result}
    except InvalidQuerySpec as exc:
        message = (
            "That question cannot be represented safely with the supported "
            f"operations. Details: {exc}"
        )
        record_history(question, "rejected", error=message)
        return {"question": question, "status": "rejected", "error": message}
    except QueryExecutionError as exc:
        message = str(exc)
        record_history(question, "execution_error", error=message)
        return {"question": question, "status": "execution_error", "error": message}
    except (KeyError, TypeError, ValueError) as exc:
        message = (
            "The analysis could not be completed for this dataset. Try a more "
            "specific question using one of the detected columns."
        )
        record_history(
            question,
            "application_error",
            error=f"{message} ({type(exc).__name__})",
        )
        return {"question": question, "status": "application_error", "error": message}


def build_chart(chart_df: pd.DataFrame, chart_type: str, palette_name: str, x_name: str):
    colors = list(palette_colors(palette_name))
    base = alt.Chart(chart_df).encode(
        x=alt.X(f"{x_name}:N", sort=None, title=x_name.replace("_", " ").title()),
        y=alt.Y("value:Q", title="Value"),
        tooltip=[alt.Tooltip(f"{x_name}:N"), alt.Tooltip("value:Q", format=",.2f")],
        color=alt.Color(
            f"{x_name}:N",
            scale=alt.Scale(range=colors),
            legend=None,
        ),
    )
    if chart_type == "Bar":
        return base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    if chart_type == "Horizontal bar":
        return alt.Chart(chart_df).mark_bar(cornerRadiusEnd=4).encode(
            y=alt.Y(f"{x_name}:N", sort="-x", title=x_name.replace("_", " ").title()),
            x=alt.X("value:Q", title="Value"),
            color=alt.Color(f"{x_name}:N", scale=alt.Scale(range=colors), legend=None),
            tooltip=[alt.Tooltip(f"{x_name}:N"), alt.Tooltip("value:Q", format=",.2f")],
        )
    if chart_type == "Line":
        return base.mark_line(point=True, strokeWidth=3).encode(color=alt.value(colors[0]))
    if chart_type == "Area":
        return base.mark_area(opacity=0.65, line=True).encode(color=alt.value(colors[0]))
    if chart_type == "Scatter":
        return base.mark_circle(size=110)
    if chart_type in {"Pie", "Donut"}:
        inner_radius = 65 if chart_type == "Donut" else 0
        return alt.Chart(chart_df).mark_arc(innerRadius=inner_radius).encode(
            theta=alt.Theta("value:Q"),
            color=alt.Color(f"{x_name}:N", scale=alt.Scale(range=colors), title=x_name),
            tooltip=[alt.Tooltip(f"{x_name}:N"), alt.Tooltip("value:Q", format=",.2f")],
        )
    raise ValueError(f"Unsupported chart type: {chart_type}")


def render_answer(item: dict, index: int | None = None) -> None:
    heading = f"Question {index}: {item['question']}" if index else item["question"]
    st.markdown(f"#### {heading}")
    if item["status"] != "answered_unverified":
        st.warning(item["error"])
        return

    result = item["result"]
    st.write(result["explanation"])
    result_data = result["result"]
    result_type = result_data["type"]
    chart_choices = chart_types_for(result_type)
    if chart_choices:
        values = list(result_data["data"].items())
        x_name = "period" if result_type == "timeseries" else "group"
        chart_df = pd.DataFrame(values, columns=[x_name, "value"])
        control_a, control_b = st.columns(2)
        chart_type = control_a.selectbox(
            "Chart type",
            options=chart_choices,
            key=f"chart_type_{index}_{item['question']}",
        )
        palette_name = control_b.selectbox(
            "Colour palette",
            options=list(COLOR_PALETTES),
            key=f"palette_{index}_{item['question']}",
        )
        st.altair_chart(
            build_chart(chart_df, chart_type, palette_name, x_name),
            use_container_width=True,
        )
    else:
        st.caption("This answer is a single value, so a comparison chart is not applicable.")

    with st.expander("Show the validated query spec"):
        st.json(result["spec"])


st.subheader("Ask questions")
st.caption(
    "Application answers are calculated safely but remain unverified until they "
    "are compared with a trusted expected answer."
)
question_mode = st.radio(
    "Choose how to ask",
    options=["One question", "Multiple questions together"],
    horizontal=True,
)
reset_before_run = st.checkbox(
    "Start a fresh audit for each run",
    value=True,
    help=(
        "When enabled, the previous audit history is cleared automatically before "
        "processing the next single question or batch. Disable it to build one "
        "combined history across several runs."
    ),
)

submitted_questions: list[str] = []
if question_mode == "One question":
    single_value = st.text_input(
        "Ask one question", value="What is the total revenue by region?"
    )
    if st.button("Ask question", type="primary"):
        submitted_questions = parse_single_question(single_value)
        if not submitted_questions:
            st.warning("Enter a question before running the analysis.")
else:
    batch_value = st.text_area(
        "Ask multiple questions",
        height=220,
        placeholder=(
            "Enter one question per line. Example:\n"
            "Total revenue?\n"
            "Average unit price?\n"
            "Revenue by region?"
        ),
        help=f"One question per line. Maximum {MAX_BATCH_QUESTIONS} questions per batch.",
    )
    if st.button("Ask all questions", type="primary"):
        try:
            submitted_questions = parse_batch_questions(batch_value)
        except ValueError as exc:
            st.warning(str(exc))
        if not submitted_questions and not batch_value.strip():
            st.warning("Enter at least one question, with one question on each line.")

if submitted_questions:
    if reset_before_run:
        st.session_state.query_history = []
    with st.spinner(f"Processing {len(submitted_questions)} question(s)..."):
        outputs = [run_question(question) for question in submitted_questions]
    st.markdown("### Results")
    for number, output in enumerate(outputs, start=1):
        render_answer(output, number if len(outputs) > 1 else None)
        st.divider()

st.subheader("Question and answer audit")
st.caption(
    "Every attempted question is recorded. Use the fresh-audit option above to "
    "replace old results automatically, or disable it to accumulate several runs."
)
history = st.session_state.query_history
if history:
    audit_table = pd.DataFrame(history)
    visible_columns = [
        column
        for column in (
            "timestamp_utc",
            "dataset",
            "question",
            "status",
            "answer",
            "operation",
            "value_column",
            "group_by_column",
            "filter_column",
            "filter_value",
            "error",
        )
        if column in audit_table.columns
    ]
    st.dataframe(audit_table[visible_columns], use_container_width=True, hide_index=True)
    download_col, clear_col = st.columns([2, 1])
    download_col.download_button(
        "Download all asked questions and app answers",
        data=history_to_csv(history),
        file_name="llm_business_insight_question_answer_audit.csv",
        mime="text/csv",
    )
    if clear_col.button("Clear history now"):
        st.session_state.query_history = []
        st.rerun()
else:
    st.info("No questions have been asked in this session yet.")

benchmark_path = ROOT / "data" / "validation" / "approved_question_answer_benchmark.csv"
if benchmark_path.exists():
    st.download_button(
        "Download approved expected-answer benchmark",
        data=benchmark_path.read_bytes(),
        file_name="approved_question_answer_benchmark.csv",
        mime="text/csv",
    )
