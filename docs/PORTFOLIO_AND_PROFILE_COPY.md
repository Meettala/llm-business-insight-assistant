# Portfolio, CV and LinkedIn Copy

## Official links

- Live application: https://llm-business-insight-assistant-maubk3puyxkcbnjiad4vnr.streamlit.app/
- GitHub repository: https://github.com/Meettala/llm-business-insight-assistant

## CV project entry

**LLM Business Insight Assistant — Python, Pandas, Streamlit, Applied AI**

Built and deployed a safety-first natural-language CSV analytics application. Designed a schema-aware query engine with validated multi-filter analysis, grouped ranking, date intelligence, conditional percentages and application-controlled derived business metrics. Preserved a strict `QuerySpec` execution boundary with no generated Python, unrestricted SQL, `eval` or `exec`. Achieved **49/49 correct answers** on a live approved benchmark across narrow, wide and 12,000-row CSV datasets.

**Live demo:** https://llm-business-insight-assistant-maubk3puyxkcbnjiad4vnr.streamlit.app/

## Short CV bullet version

- Built and deployed a safety-first natural-language CSV analytics app using Python, Pandas and Streamlit; achieved 49/49 correct results on a verified live benchmark.
- Implemented schema-aware parsing, multiple filters, grouped rankings, date analysis and validated derived metrics without arbitrary code or SQL execution.
- Added Python 3.10–3.12 CI, adversarial tests, dependency auditing, downloadable answer audits and user-controlled charts.

## LinkedIn project description

Developed a production-minded business insight assistant that lets users upload CSV files and ask questions in natural language. Instead of generating executable Python or SQL, every request is converted into a constrained and validated `QuerySpec`, then calculated through deterministic Pandas operations.

Key capabilities include full-dataset exploration, single and batch questions, multiple validated filters, grouped highest/lowest rankings, date and period analysis, conditional percentages, derived net revenue/gross profit/profit margin, downloadable audits and user-selected charts.

After a live accuracy-engine upgrade, the deployed app answered all **49 approved benchmark questions correctly** across three CSV datasets, including a 12,000-row dataset. The result is documented honestly as benchmark-specific rather than universal accuracy.

**Try the live app:** https://llm-business-insight-assistant-maubk3puyxkcbnjiad4vnr.streamlit.app/

## Portfolio card copy

**LLM Business Insight Assistant**

A safety-first applied AI analytics tool that converts natural-language business questions into validated, deterministic CSV insights. Verified at 49/49 correct answers on the approved live benchmark.

**Stack:** Python, Pandas, Streamlit, Altair, Pytest, GitHub Actions, Docker

**Live demo:** https://llm-business-insight-assistant-maubk3puyxkcbnjiad4vnr.streamlit.app/

## Interview explanation

The central design decision was to separate interpretation from execution. A rule-based or optional LLM parser may propose an analytical intent, but it never receives authority to run code. The proposal must fit a typed `QuerySpec`, reference real dataset columns and pass validation. The executor then chooses from fixed Pandas operations and application-controlled formulas. This preserves auditability and reduces injection risk while still supporting useful business questions.

## Honest scope statement

Use this sentence whenever presenting the 49/49 result:

> The deployed app passed all 49 approved questions on three benchmark datasets; this is verified benchmark performance, not a claim of perfect accuracy for every possible CSV or question.
