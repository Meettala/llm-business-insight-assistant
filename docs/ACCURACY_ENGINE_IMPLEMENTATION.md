# Accuracy Engine Implementation

## Purpose

This change replaces first-column guessing and narrow keyword parsing with a typed, schema-aware deterministic parser. The engine still preserves the project's core safety boundary: every question becomes a validated `QuerySpec`, and the executor only performs fixed pandas operations.

## Supported intent added

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

The expanded schema adds:

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

The deterministic parser is now primary because it is reproducible, schema-aware and testable. An optional provider parser is used only as a validated fallback when deterministic intent cannot be represented safely.

The parser no longer silently selects the first numeric column. Missing or ambiguous required fields fail validation rather than producing a confident but unrelated answer.

## Benchmark coverage

The approved benchmark now contains 49 questions:

- 13 narrow CSV questions;
- 20 wide CSV questions;
- 16 long CSV questions.

Automated tests cover the intent and execution patterns represented by those questions, including filters, rankings, date logic, derived measures and percentages.

The three original raw benchmark CSV files are not stored in this public repository. Exact end-to-end comparison against their approved numeric answers must therefore be repeated through the deployed app using the owner's original files before claiming 49/49 live accuracy.

## Current validation

Before pushing the branch, 72 focused local tests passed across:

- new accuracy-engine behaviour;
- new accuracy-engine safety controls;
- existing query validation expectations;
- existing executor edge cases;
- deterministic-first pipeline behaviour.

GitHub Actions remains the authoritative branch validation before merge.

## Known limits

- categorical value matching considers columns with at most 500 unique values;
- semantic aliases are broad but not universal for every possible business schema;
- ambiguous discount columns may be rejected instead of guessed;
- arbitrary formulas, joins, forecasting and generated code remain unsupported;
- exact benchmark results still require the original narrow, wide and long CSV files;
- optional LLM fallback still uses the older simple provider schema and should not override a valid deterministic specification.
