"""Streamlit demo for the LLM Business Insight Assistant.

Run from the repository root with:

    streamlit run streamlit_app/app.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from src.insight.data import infer_column_types, load_csv  # noqa: E402
from src.insight.executor import QueryExecutionError  # noqa: E402
from src.insight.parser_llm import llm_available  # noqa: E402
from src.insight.pipeline import ask  # noqa: E402
from src.insight.query_spec import InvalidQuerySpec  # noqa: E402

st.set_page_config(page_title="LLM Business Insight Assistant", layout="wide")
st.title("LLM Business Insight Assistant")
st.caption(
    "Ask questions about your CSV in plain English. Every answer is calculated "
    "from the uploaded data through a validated query specification."
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

st.subheader("Data preview")
st.dataframe(df.head(10), use_container_width=True)

column_types = infer_column_types(df)
detected_columns = ", ".join(
    f"{column} ({column_type})"
    for column, column_type in column_types.items()
)
st.caption(f"Detected columns: {detected_columns}")

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
