# AI Handoff — LLM Business Insight Assistant

> Continue this repository from its live GitHub state. Verify `main`, open pull requests and GitHub Actions before making claims or edits.

## Repository

- Repository: `Meettala/llm-business-insight-assistant`
- Default branch: `main`
- Licence: MIT
- Current feature branch: `feat/accuracy-engine`
- Current work: replace incorrect first-column/keyword guessing with a typed, schema-aware accuracy engine.
- Design record: `docs/ACCURACY_ENGINE_IMPLEMENTATION.md`
- Trusted benchmark: `data/validation/approved_question_answer_benchmark.csv`

## Recently merged

- PR #4 — dynamic full-dataset CSV explorer; merge `db22f7bbff417ee058173b7cc9593abec160c5d1`.
- PR #5 — downloadable question/answer audit and benchmark; merge `e3cbc397d257dec44c0a765eab63034158301d57`.
- PR #6 — single-question and multi-question modes; merge `10a22a663d2c2bfd405c2b8afd5dea5758544960`.
- PR #7 — fresh-audit workflow and user-selected chart types/colour palettes; merge `20337c89f00618c061280c23d1d4191308c724ea`.

## Product purpose

A user uploads a CSV and asks plain-English business questions. The application loads the complete dataframe, infers its schema, creates a constrained `QuerySpec`, validates it, performs fixed pandas operations and returns deterministic answers plus auditable query details.

## Mandatory safety property

Every question must resolve to a validated `QuerySpec` before execution.

Never introduce:

- `eval` or `exec`;
- generated Python or pandas expressions;
- unrestricted SQL;
- direct execution of provider output;
- invented columns or unvalidated formulas.

Provider output remains untrusted. The deterministic parser is primary; optional LLM parsing is only a validated fallback when deterministic intent cannot be represented.

## Accuracy-engine branch

### Expanded QuerySpec

The branch adds:

- operations: `distinct`, `date_range` and `ratio` alongside existing fixed aggregations;
- up to ten typed filters;
- filter operators limited to `eq`, `truthy` and `year_eq`;
- highest/lowest grouped ranking;
- month/year date grouping;
- named, application-controlled derived measures;
- contextual columns for row-level minimum/maximum results;
- conditional count percentages;
- row-count metadata;
- currency, percentage, integer and number formatting hints;
- complete JSON audit serialisation.

### Parser behaviour

The parser now:

- matches business concepts to the correct column instead of selecting the first numeric column;
- uses actual low-cardinality categorical values from the uploaded dataframe to build filters;
- supports multiple simultaneous filters;
- distinguishes row-level extrema from grouped totals and rankings;
- handles year filters and highest month/year questions;
- handles distinct values and date ranges;
- supports direct or validated derived net revenue and gross profit;
- calculates overall profit margin as a ratio of totals;
- rejects missing or ambiguous required fields instead of giving an unrelated confident answer.

### Executor behaviour

The executor performs only fixed operations for:

- exact categorical filters;
- truthy returned-order filters;
- year filters;
- grouped aggregation and ranking;
- month/year grouping;
- distinct values;
- date ranges;
- conditional counts and percentages;
- net revenue, gross profit and profit-margin formulas selected from fixed enums;
- row context for min/max answers.

### Tests

New files:

- `tests/test_accuracy_engine.py` — 50 behaviour tests.
- `tests/test_accuracy_engine_safety.py` — safety tests for new fields.

Before branch push, 72 focused local tests passed, including existing query-validation and executor edge expectations. GitHub Actions is authoritative before merge.

## Benchmark facts

The approved benchmark contains 49 questions:

- 13 narrow CSV questions;
- 20 wide CSV questions;
- 16 long CSV questions.

The original raw narrow, wide and long CSV files are not stored in this public repository. Therefore, do not claim 49/49 exact live accuracy until the owner retests the deployed app using those original files and exports a fresh audit.

## Existing application features

- complete CSV loading with no application-level row/column truncation after successful load;
- paginated full-data explorer;
- schema and missing/duplicate/memory summaries;
- one-question and batch-question modes;
- downloadable question/answer audit;
- downloadable approved benchmark;
- fresh audit per run by default, with optional accumulated history;
- user-selected bar, horizontal bar, line, area, scatter, pie and donut charts where applicable;
- Office/Excel-style and other palettes.

Do not claim unlimited file size. Pandas still requires the complete CSV to fit available memory and hosting limits.

## Known limits

- semantic aliases are broad but not universal for every possible schema;
- categorical value matching is intentionally limited to columns with at most 500 unique values;
- ambiguous discount columns may be rejected instead of guessed;
- arbitrary formulas, joins, forecasting and unrestricted SQL remain out of scope;
- optional provider schema is still simpler than the new deterministic QuerySpec;
- exact user benchmark values require the original raw CSV files;
- Streamlit deployment must be manually retested after merge.

## Required next steps

1. Wait for the accuracy-engine PR CI result.
2. Fix any failing Python-version, Ruff or dependency jobs without weakening validation.
3. Review the full diff and merge only after green CI.
4. Reboot/redeploy the Streamlit app.
5. Retest all 49 questions with the original three CSV files.
6. Download and compare the new audit against the trusted benchmark.
7. Record exact pass/fail counts and remaining mismatches in documentation.
8. Update this handoff with the PR number, CI run and merge SHA.

## Public/commercial boundary

This public repository is a portfolio/reference implementation. A paid production system should use a separate private repository and add identity, tenant isolation, least privilege, encryption, secrets management, monitoring, audit logs, retention controls, backup, abuse prevention, incident response and security testing.
