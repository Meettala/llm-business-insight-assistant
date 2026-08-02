# AI Handoff — LLM Business Insight Assistant

> Continue this repository from its live GitHub state. Verify `main`, open pull requests, releases and GitHub Actions before making claims or edits.

## Repository

- Repository: `Meettala/llm-business-insight-assistant`
- Default branch: `main`
- Licence: MIT
- Current release work branch: `docs/verified-release-v0.2.0`
- Recommended release: `v0.2.0 — Verified Accuracy Engine`
- Accuracy design record: `docs/ACCURACY_ENGINE_IMPLEMENTATION.md`
- Live validation record: `docs/LIVE_VALIDATION_REPORT_2026-08-02.md`
- Trusted benchmark: `data/validation/approved_question_answer_benchmark.csv`

## Completed milestones

- PR #4 — dynamic full-dataset CSV explorer; merge `db22f7bbff417ee058173b7cc9593abec160c5d1`.
- PR #5 — downloadable question/answer audit and benchmark; merge `e3cbc397d257dec44c0a765eab63034158301d57`.
- PR #6 — single-question and multi-question modes; merge `10a22a663d2c2bfd405c2b8afd5dea5758544960`.
- PR #7 — fresh-audit workflow and user-selected chart types/colour palettes; merge `20337c89f00618c061280c23d1d4191308c724ea`.
- PR #8 — schema-aware accuracy engine; merge `031a27cd9f6fdf655371ffff9edc2e0f6033f1ad`.
- CI run #56 passed on the final accuracy-engine branch.
- Post-deployment live validation confirmed 49/49 approved questions passed.

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

Provider output remains untrusted. The deterministic parser is primary; optional LLM parsing is only a strictly validated fallback.

## Current capabilities

- complete CSV loading after successful upload;
- paginated full-data explorer;
- schema, missing-data, duplicates and memory summaries;
- single-question and batch-question modes;
- schema-aware measure selection;
- exact categorical filters and multiple simultaneous filters;
- grouped totals and highest/lowest ranking;
- year filters and month/year grouping;
- distinct values and date ranges;
- conditional counts with percentages;
- row context for extrema;
- application-controlled net revenue, gross profit and profit-margin calculations;
- downloadable question-and-answer audit;
- downloadable approved benchmark;
- user-selected bar, horizontal bar, line, area, scatter, pie and donut charts;
- Office/Excel-style and additional palettes.

## Validation status

### Engineering

- 85 focused local tests passed before merge.
- GitHub Actions CI run #56 passed.
- Python 3.10, 3.11 and 3.12 passed.
- Ruff checks and dependency audit passed.

### Live benchmark

On 2 August 2026, three post-update audit exports from the deployed app were compared with the owner-approved answers:

- narrow CSV: 13/13;
- wide CSV: 20/20;
- long CSV: 16/16;
- overall: 49/49.

Use this exact scope statement:

> The deployed app passed all 49 approved questions on three benchmark datasets; this is verified benchmark performance, not a claim of perfect accuracy for every possible CSV or question.

## Portfolio and release documents

- `docs/LIVE_VALIDATION_REPORT_2026-08-02.md`
- `docs/PORTFOLIO_AND_PROFILE_COPY.md`
- `docs/PORTFOLIO_MEDIA_CHECKLIST.md`
- `docs/RELEASE_NOTES_v0.2.0.md`

## Remaining release tasks

1. Merge the verified-release documentation PR after green CI.
2. Create GitHub release `v0.2.0` using `docs/RELEASE_NOTES_v0.2.0.md`.
3. Copy the exact public Streamlit URL from the deployed app or Streamlit Cloud dashboard and add it to README/repository metadata/portfolio.
4. Capture the screenshots and short demo video described in `docs/PORTFOLIO_MEDIA_CHECKLIST.md`.
5. Apply the prepared CV, LinkedIn and portfolio wording manually; no LinkedIn connector is available in this workflow.
6. Then move to the RAG Research Assistant improvement phase.

## Known limits

- semantic aliases are broad but not universal;
- categorical value matching is intentionally limited for very high-cardinality columns;
- ambiguous measures may be rejected instead of guessed;
- arbitrary formulas, joins, forecasting and unrestricted SQL remain out of scope;
- Pandas requires the complete CSV to fit available memory and hosting limits;
- the exact public Streamlit URL has not yet been recorded in the repository.

## Public/commercial boundary

This public repository is a portfolio/reference implementation. A paid production system should use a separate private repository and add identity, tenant isolation, least privilege, encryption, secrets management, monitoring, audit logs, retention controls, backup, abuse prevention, incident response and security testing.
