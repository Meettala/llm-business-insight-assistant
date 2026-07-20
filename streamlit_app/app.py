"""
LLM Business Insight Assistant — Streamlit demo.

Run with: streamlit run streamlit_app/app.py
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.insight.data import load_csv, infer_column_types  # noqa: E402
from src.insight.parser_llm import llm_available  # noqa: E402
from src.insight.pipeline import ask  # noqa: E402

st.set_page_config(page_title="LLM Business Insight Assistant", layout="wide")
st.title("LLM Business Insight Assistant")
st.caption("Ask questions about your CSV in plain English. Every answer states the exact numbers it's based on.")

mode = "LLM-assisted parsing + validated execution" if llm_available() else "Rule-based parsing only (no API key configured)"
st.info(f"Query parsing mode: **{mode}** — either way, only a fixed set of whitelisted operations ever runs against your data.")

uploaded = st.file_uploader("Upload a CSV", type="csv")
default_path = ROOT / "data" / "sample_sales.csv"
df = load_csv(uploaded) if uploaded else load_csv(default_path)
if not uploaded:
    st.caption("Using the bundled sample sales dataset — upload your own CSV above to try it on real data.")

st.subheader("Data preview")
st.dataframe(df.head(10), use_container_width=True)
types = infer_column_types(df)
st.caption("Detected columns: " + ", ".join(f"{c} ({t})" for c, t in types.items()))

question = st.text_input("Ask a question", value="What is the total revenue by region?")
if st.button("Ask") and question:
    result = ask(df, question)
    st.markdown(f"**Answer** ({result['mode']} parsing):")
    st.text(result["explanation"])

    if result["result"]["type"] == "grouped":
        chart_df = pd.DataFrame(list(result["result"]["data"].items()), columns=["group", "value"]).set_index("group")
        st.bar_chart(chart_df)
    elif result["result"]["type"] == "timeseries":
        chart_df = pd.DataFrame(list(result["result"]["data"].items()), columns=["period", "value"]).set_index("period")
        st.line_chart(chart_df)

    with st.expander("Show the validated query spec"):
        st.json(result["spec"])
