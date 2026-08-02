# Accuracy Engine Implementation

## Purpose

This release replaced first-column guessing and narrow keyword parsing with a typed, schema-aware deterministic parser. The core safety boundary remains unchanged: every question becomes a validated `QuerySpec`, and the executor performs only fixed pandas operations.

## Supported intent

- semantic column matching for revenue, net revenue, gross profit, units sold, unit price, satisfaction score and lead time;
- exact categorical value filters using values found in the uploaded dataframe;
- multiple simultaneous filters;
- year filters on validated date columns;
- distinct categorical values;
- date ranges;
- grouped aggregation followed by highest/lowest ranking;
- month and year grouping;
- conditional counts with percentages;
- row context for minimum/maximum values;
- direct or validated derived net revenue;
- direct or validated derived gross profit;
- overall profit margin calculated as a ratio of totals;
- explicit formatting hints for currency, percentages, integers and ordinary numbers.

## QuerySpec safety model

The expanded schema includes:

- `filters`: up to ten typed `FilterSpec` objects;
- filter operators limited to `eq`, `truthy` and `year_eq`;
- ranking limited to `highest` or `lowest`;
- date grouping limited to `month` or `year`;
- derived measures limited to named application-controlled formulas;
- component and return columns validated against the uploaded schema;
- result limits restricted to 1–100;
- serialisable audit output for all fields.

No generated expressions are accepted. Formula names are fixed application enums, not user-provided Python or SQL.

## Parser policy

The deterministic parser is primary because it is reproducible, schema-aware and testable. An optional provider parser is used only as a validated fallback when deterministic intent cannot be represented safely.

The optional provider parser accepts the same typed filters, rankings, date grouping, derived-measure fields and audit metadata as the deterministic `QuerySpec`. Provider output remains untrusted and is rejected when it contains unknown fields, malformed nested filters, invalid types or unsupported columns.

The parser does not silently select the first numeric column. Missing or ambiguous required fields fail validation rather than producing a confident but unrelated answer.

## Benchmark coverage

The approved benchmark contains 49 questions:

- 13 narrow CSV questions;
- 20 wide CSV questions;
- 16 long CSV questions.

Coverage includes filters, multiple filters, grouped ranking, date logic, conditional percentages, row context and derived business measures.

## Engineering validation

Before merge:

- 85 focused local tests passed;
- GitHub Actions CI run #56 passed;
- Python 3.10, 3.11 and 3.12 passed;
- Ruff source and test checks passed;
- dependency auditing passed.

Accuracy-engine PR #8 merged as `031a27cd9f6fdf655371ffff9edc2e0f6033f1ad`.

## Live validation

On 2 August 2026, the deployed application was retested using the owner's original three benchmark CSV files. Three post-update audit exports were compared with the approved expected answers.

| Dataset | Questions | Passed | Failed |
|---|---:|---:|---:|
| Narrow | 13 | 13 | 0 |
| Wide | 20 | 20 | 0 |
| Long | 16 | 16 | 0 |
| **Overall** | **49** | **49** | **0** |

All 49 approved questions matched. See [`LIVE_VALIDATION_REPORT_2026-08-02.md`](LIVE_VALIDATION_REPORT_2026-08-02.md).

## Interpretation

The result proves correct performance for the approved benchmark questions and datasets. It does not establish universal accuracy for every possible CSV, vocabulary or formula.

## Known limits

- categorical value matching considers columns with at most 500 unique values;
- semantic aliases are broad but not universal for every possible business schema;
- ambiguous discount columns may be rejected instead of guessed;
- arbitrary formulas, joins, forecasting and generated code remain unsupported;
- complete CSV files must fit available Pandas and hosting memory;
- the exact public Streamlit URL still needs to be recorded in the repository.
