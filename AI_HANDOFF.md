# AI Handoff — LLM Business Insight Assistant

> Continue this repository from its live GitHub state. Verify `main`, open pull requests and GitHub Actions before making claims or edits.

## Repository

- Repository: `Meettala/llm-business-insight-assistant`
- Default branch: `main`
- Licence: MIT
- Accuracy-engine implementation: `docs/ACCURACY_ENGINE_IMPLEMENTATION.md`
- Live validation record: `docs/LIVE_ACCURACY_VALIDATION_2026-08-02.md`
- Trusted benchmark: `data/validation/approved_question_answer_benchmark.csv`

## Recently merged

- PR #4 — dynamic full-dataset CSV explorer; merge `db22f7bbff417ee058173b7cc9593abec160c5d1`.
- PR #5 — downloadable question/answer audit and benchmark; merge `e3cbc397d257dec44c0a765eab63034158301d57`.
- PR #6 — single-question and multi-question modes; merge `10a22a663d2c2bfd405c2b8afd5dea5758544960`.
- PR #7 — fresh-audit workflow and user-selected chart types/colour palettes; merge `20337c89f00618c061280c23d1d4191308c724ea`.
- PR #8 — schema-aware accuracy engine; CI run #56 passed; merge `031a27cd9f6fdf655371ffff9edc2e0f6033f1ad`.

## Confirmed live validation

After PR #8 was merged and the Streamlit app was redeployed, the owner reran the full approved benchmark using the original CSV files and exported three fresh audit files.

Independent comparison confirmed:

- narrow dataset: 13/13 passed;
- wide dataset: 20/20 passed;
- long dataset: 16/16 passed;
- overall: **49/49 passed**.

All 49 rows were answered without rejection or execution/application errors. See `docs/LIVE_ACCURACY_VALIDATION_2026-08-02.md` for details.

The 49/49 result is limited to the approved benchmark datasets and questions. Do not describe it as universal accuracy for all CSV schemas or all natural-language requests.

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

## Accuracy engine

### Expanded QuerySpec

The engine supports:

- `sum`, `mean`, `count`, `min`, `max`, `trend`, `distinct`, `date_range` and `ratio` operations;
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

The parser:

- matches business concepts to the correct column instead of selecting the first numeric column;
- uses actual low-cardinality categorical values from the uploaded dataframe to build filters;
- supports multiple simultaneous filters;
- distinguishes row-level extrema from grouped totals and rankings;
- handles year filters and highest month/year questions;
- handles distinct values and date ranges;
- supports direct or validated derived net revenue and gross profit;
- calculates overall profit margin as a ratio of totals;
- rejects missing or ambiguous required fields instead of giving an unrelated confident answer.

The optional LLM parser supports the same typed filters, ranking, date grouping, derived-measure and audit fields. Its JSON remains untrusted and must pass both strict response parsing and `validate_query_spec`.

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

- `tests/test_accuracy_engine.py` — behaviour coverage for narrow, wide and long benchmark intents.
- `tests/test_accuracy_engine_safety.py` — safety tests for new fields.
- 85 focused local tests passed before PR #8 merge.
- GitHub Actions CI run #56 passed on the final PR #8 head.

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

- the confirmed 49/49 result applies only to the approved benchmark;
- semantic aliases are broad but not universal for every possible schema;
- categorical value matching is intentionally limited to columns with at most 500 unique values;
- ambiguous discount columns may be rejected instead of guessed;
- arbitrary formulas, joins, forecasting and unrestricted SQL remain out of scope.

## Recommended next steps

1. Merge the documentation PR that records the live 49/49 validation after its CI passes.
2. Preserve the current safety boundary when adding any future analytical intent.
3. Add new regression questions whenever a real unsupported or incorrect interpretation is found.
4. Consider storing privacy-safe synthetic benchmark datasets in the repository for fully reproducible end-to-end CI.
5. Confirm and document the production Streamlit URL before using it in portfolio materials.

## Public/commercial boundary

This public repository is a portfolio/reference implementation. A paid production system should use a separate private repository and add identity, tenant isolation, least privilege, encryption, secrets management, monitoring, audit logs, retention controls, backup, abuse prevention, incident response and security testing.
