# Answer Accuracy and Verification Roadmap

## Problem statement

The application currently validates every analytical request against a safe `QuerySpec`, but a valid query specification is not the same as a correct interpretation of the user's question.

The current grammar supports only:

- `sum`
- `mean`
- `count`
- `min`
- `max`
- `trend`
- one optional equality filter
- one optional grouping column

This is insufficient for several real-world questions in the approved benchmark. The parser can therefore select the wrong measure, ignore part of a question, or return a grouped result when the user requested one ranked item.

## Audit feature added

The Streamlit application now keeps an in-session audit history containing:

- timestamp
- dataset name
- exact question
- status
- application answer
- parsing mode
- complete validated query specification
- raw deterministic result
- error information

Users can download the history as `llm_business_insight_question_answer_audit.csv`.

The answer is explicitly marked `answered_unverified` because execution safety does not prove semantic correctness.

CSV exports defend against spreadsheet formula injection from question or dataset-derived text.

## Approved benchmark

`data/validation/approved_question_answer_benchmark.csv` records the user-approved questions and expected answers for:

- a wide business dataset covering revenue, discounts, category, channel, region, satisfaction, returns, representatives, gross profit, margin, lead time, segment and products;
- `long_sample.csv`, containing 12,000 rows across 2023–2025.

These expected answers are trusted regression targets supplied by the project owner. They must not be silently changed to make tests pass. Any correction requires the owner's approval or a reproducible independent calculation from the benchmark dataset.

## Missing capabilities to implement next

1. Multiple simultaneous equality filters.
2. Date-year and date-month filters.
3. Grouped ranking: highest, lowest, most and fewest.
4. Calculated measures such as net revenue and gross profit.
5. Validated ratio and percentage operations such as return rate and profit margin.
6. Conditional counts with denominator reporting.
7. Explicit row-count questions.
8. Ranking over time periods such as highest-revenue month or year.
9. Clarification when multiple columns could represent revenue, price, profit or units.
10. A parser confidence or coverage result that prevents unsupported partial interpretations from being presented as answers.

## Safety requirements

Future flexibility must remain declarative and validated. Do not add:

- `eval`
- `exec`
- generated Python
- unrestricted SQL
- generated pandas expressions
- direct execution of LLM output

Extend `QuerySpec` using typed, allow-listed operations and validated expression structures. Every referenced column, operator, filter, aggregation, ratio component and ranking direction must be checked before deterministic execution.

## Verification design

The next accuracy PR should add a benchmark runner that:

1. loads the exact benchmark dataset;
2. runs every approved question through the public pipeline;
3. records parsed specification and actual answer;
4. compares numeric results with explicit tolerances;
5. compares labels and ranked entities exactly after safe normalisation;
6. reports pass, fail, rejected or unsupported;
7. never treats a rejected unsupported question as a correct answer;
8. produces a machine-readable CSV or JSON report;
9. fails CI only for benchmark cases declared supported by the current version.

## Definition of done

Answer accuracy work is complete only when:

- every supported benchmark question passes automatically;
- unsupported benchmark questions are clearly rejected rather than partially interpreted;
- application answers show whether they were benchmark-verified, unverified or unsupported;
- the full test, lint and dependency-audit workflow passes;
- the live Streamlit deployment is tested using the original benchmark CSV files.
