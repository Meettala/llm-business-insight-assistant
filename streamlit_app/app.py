"""Streamlit demo for the LLM Business Insight Assistant.

Run from the repository root with:

    streamlit run streamlit_app/app.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.insight.data import infer_column_types, load_csv
from src.insight.parser_llm import llm_available
from src.insight.pipeline import ask

ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="LLM Business Insight Assistant", layout="wide")
st.title("LLM Business Insight Assistant")
st.caption(
    "Ask questions about your CSV in plain English. Every answer states the "
    "exact numbers it is based on."
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
df = load_csv(uploaded) if uploaded else load_csv(default_path)

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

if st.button("Ask") and question:
    result = ask(df, question)
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
