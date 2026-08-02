# AI Handoff — LLM Business Insight Assistant

> Paste this file into ChatGPT, Claude, Gemini, Copilot, Perplexity, or another AI assistant to continue this repository without restarting the project. Verify the live `main` branch, open pull requests, and latest CI before changing anything.

## Continuation instruction

You are continuing `Meettala/llm-business-insight-assistant`, a public MIT-licensed portfolio and reference implementation owned by Meet Tala.

Do not replace the architecture casually or weaken the constrained-execution safety model. Read the live code, this file, `README.md`, `SECURITY.md`, `docs/architecture.md`, and `docs/PORTFOLIO_PRESENTATION_GUIDE.md` before editing. Add tests for behavioural changes and update this file after material code, architecture, security, deployment, documentation, licensing, roadmap, screenshot, demo, or social-preview work.

Never place secrets, customer data, private keys, private prompts, production infrastructure details, or confidential commercial information in this public repository.

## Repository state

- Repository: `Meettala/llm-business-insight-assistant`
- Default branch: `main`
- Licence: MIT
- PR #1, `Professionalize repository foundation`, was squash-merged on 26 July 2026.
- Merge commit: `bef5c22d1fc5702dbe8facf25169ea86310779dc`
- Presentation follow-up branch: `docs/presentation-guide`
- Presentation instructions: `docs/PORTFOLIO_PRESENTATION_GUIDE.md`
- Current feature branch: `feat/dynamic-full-csv-explorer`
- Current feature purpose: remove fixed-row preview behaviour and provide access to every successfully loaded CSV row and column.
- Research and design record: `docs/full-dataset-explorer-research.md`

## Product purpose

A user uploads a CSV file and asks a plain-English business question. The application infers the schema, converts the question into a constrained `QuerySpec`, validates it, executes a fixed pandas operation, and returns chart-ready data plus an explanation grounded in computed values.

The project demonstrates applied AI and analytics without granting a model authority to generate or execute arbitrary code.

## Core safety property

Every parser path must produce a `QuerySpec` and call `validate_query_spec` before `execute_query`.

Supported operations are restricted to `sum`, `mean`, `count`, `min`, `max`, and `trend`.

The project must not introduce `eval`, `exec`, generated Python, unrestricted SQL, generated pandas expressions, or direct execution of provider output.

Optional LLM output is untrusted JSON. It must pass strict response parsing and application-side schema validation. Provider failures fall back to the rule-based parser and still use the same validation boundary.

## Architecture

```text
CSV + question
      |
      v
Complete CSV loading and column-type inference
      |
      +--> full-data profile and paginated browser view
      |
      v
Rule-based parser or optional provider parser
      |
      v
Strict provider-response parsing
      |
      v
Validated QuerySpec  <--- mandatory trust boundary
      |
      v
Deterministic pandas executor using the complete loaded dataframe
      |
      +--> chart-ready data
      |
      +--> grounded explanation
```

Important modules:

- `src/insight/data.py` — CSV loading, dataset profiling, pagination, and type inference.
- `src/insight/query_spec.py` — operation whitelist and schema validation.
- `src/insight/parser_rule_based.py` — no-key parser and fallback.
- `src/insight/parser_llm.py` — provider calls and strict untrusted-output parsing.
- `src/insight/executor.py` — deterministic analytics and edge-case protection.
- `src/insight/explain.py` — explanations built from computed values.
- `src/insight/pipeline.py` — mandatory orchestration path.
- `streamlit_app/app.py` — interactive interface, complete-dataset explorer, and safe user-facing errors.

## Implemented

### Safety and reliability

- Fixed operation whitelist.
- Schema-aware numeric and date validation.
- Strict malformed-LLM-response handling.
- Rejection of empty output, arrays, unknown fields, invalid types, and missing operations.
- Provider fallback with structured logging.
- Injection-resistance coverage for hostile CSV values and query fields.
- `QueryExecutionError` for unusable analytical results.
- Protection for empty filtered data, null-only measures, invalid dates, empty grouped/trend results, and non-finite values.
- Safe Streamlit handling for malformed CSVs, empty files, unsupported questions, and execution failures.

### Full-dataset explorer work

The old UI used `df.head(10)`, which displayed only ten rows and could lead users to believe the application used only that preview. The analytical pipeline already received the complete dataframe, but the UI did not make this clear or let the user inspect all rows.

The feature branch now:

- loads the complete CSV without application-level row or column truncation;
- reports complete row and column counts;
- reports missing cells, duplicate rows, and dataframe memory usage;
- provides paginated access to every loaded row;
- selects every uploaded column by default;
- allows display-only column selection without changing analysis scope;
- shows per-column inferred type, pandas dtype, non-null count, missing count, and unique-value count;
- explicitly states that pagination affects only the browser view and not the dataframe used for answers;
- adds reusable `DatasetProfile`, `DataPage`, `profile_dataset`, and `paginate_dataframe` code;
- adds regression tests proving rows across all pages reconstruct the complete dataframe.

Truthful guarantee:

> No application-level row or column truncation is applied after a CSV is successfully loaded. Every loaded row and column is available to the analytical pipeline, and every loaded row is reachable through the paginated data explorer.

Do not claim that files of unlimited size are supported. The current pandas/Streamlit design still requires the CSV to fit within available application memory and hosting upload limits.

### Engineering quality

- GitHub Actions tests on Python 3.10, 3.11, and 3.12.
- Ruff linting for source, application, and tests.
- `pip-audit` dependency scanning.
- `requirements-dev.txt` and `pyproject.toml`.
- Non-root Docker image with health check.
- `.dockerignore` excluding environment files, caches, tests, and private local configuration.

### Portfolio and documentation

- Recruiter-focused README.
- Architecture, roadmap, security, contribution, changelog, and commercialisation documentation.
- MIT licence.
- Architecture and social-preview SVG assets in `docs/assets/`.
- Step-by-step portfolio presentation guide.
- Living AI handoff.
- Current competitor and architecture research in `docs/full-dataset-explorer-research.md`.

## Competitor research summary

Official product documentation was reviewed for ChatGPT Data Analysis, Julius AI, Hex, and PandasAI.

Common patterns to preserve or consider:

- natural-language data questions;
- interactive or paginated tables rather than rendering every cell simultaneously;
- complete-data computation separated from the visible page;
- dynamic schemas;
- cleaning, sorting, filtering, charts, statistics, and export;
- multiple files or dataframes;
- database and warehouse connectors for larger datasets;
- transparency about data scope and practical memory limits.

See `docs/full-dataset-explorer-research.md` for links and detailed findings.

## Verified validation

Historical workflow run 38 on commit `2d40f0ad1a6aaa98905d8c691ee6417d8f1caa07` passed the original project checks.

The `feat/dynamic-full-csv-explorer` branch must receive a new green CI result before merge. Do not describe this feature as merged or deployed until that is verified.

Required checks:

- Python 3.10 tests.
- Python 3.11 tests.
- Python 3.12 tests.
- Ruff application code.
- Ruff tests.
- `pip-audit -r requirements.txt`.

## Future full-data improvements

The current feature addresses fixed display truncation, not unlimited-scale data infrastructure. Future work should include:

1. configurable upload-size and memory safeguards;
2. encoding, delimiter, quote, and malformed-row diagnostics;
3. chunked ingestion and progress reporting;
4. DuckDB or Polars-backed analysis for larger datasets;
5. server-side filtering, sorting, search, and pagination;
6. CSV, Excel, JSON, and Parquet support;
7. multiple datasets and validated joins;
8. downloads for filtered or transformed results;
9. persistence with privacy, deletion, and retention controls;
10. accessibility and performance tests across increasing rows and columns.

These improvements must preserve the validated `QuerySpec` execution boundary. Do not introduce unrestricted generated code merely to increase flexibility.

## Presentation tasks

The remaining presentation tasks are documented in detail in `docs/PORTFOLIO_PRESENTATION_GUIDE.md`:

1. Run the Streamlit app locally or through Docker.
2. Capture a real application screenshot.
3. Record a 30–60 second demo video or GIF.
4. Add genuine demo media to the README.
5. Convert `docs/assets/social-preview.svg` to a suitable PNG.
6. Upload the PNG through GitHub repository **Settings → General → Social preview**.
7. Verify the public repository before sharing it with recruiters.

## Decisions that must be preserved

1. Safety takes priority over unrestricted analytical flexibility.
2. Every execution path validates before deterministic execution.
3. Provider output is untrusted input.
4. The no-key rule-based parser remains a first-class mode.
5. Provider failures fall back safely without exposing details in the UI.
6. Unknown provider fields are rejected rather than ignored.
7. Documentation claims require evidence from code, tests, CI, or measured results.
8. Public portfolio code uses MIT licensing.
9. A revenue-generating product must use a separate private proprietary repository.
10. Public code must not contain secrets, customer data, billing logic, production infrastructure details, or commercial-only IP.
11. No system should be described as completely or 100% secure.
12. Changes should use branches, pull requests, tests, and review rather than direct unreviewed edits to `main`.
13. A visible table page is not the same as the analytical dataset; never pass only the displayed page to `ask`.
14. Never silently truncate successfully loaded rows or columns.
15. Never claim unlimited file-size support while pandas loads the complete file into memory.

## Known limitations

- The analytical grammar is intentionally narrow.
- The rule-based parser may choose the first numeric column for an ambiguous question.
- Type inference is heuristic.
- Complex joins, arbitrary formulas, forecasting, and unrestricted SQL are out of scope.
- The current loader requires the complete CSV to fit in memory.
- Streamlit hosting may impose upload-size and resource limits.
- Provider timeout, retry, latency, and cost instrumentation remain future work.
- Dependencies use compatible minimum versions rather than a generated lock file.
- Docker is for local demonstration, not a complete production deployment.
- A real screenshot or demo GIF still requires running the application.
- GitHub social-preview configuration must be completed through repository settings.
- Accessibility testing and structured parser evaluation datasets remain future work.

## Public versus commercial product policy

This repository demonstrates the concept, safety model, engineering decisions, tests, and local demo. A future paid product should live in a separate private proprietary repository with identity, least privilege, tenant isolation, encryption, secret management, audit logging, monitoring, backup, retention, abuse prevention, incident response, compliance review, and penetration testing.

See `docs/commercialisation-and-private-production.md`.

## Rules for another AI

Before editing, inspect the live branch, open PRs, CI status, implementation, README, security policy, architecture documentation, presentation guide, and `docs/full-dataset-explorer-research.md`. Do not ask the user to repeat information recorded here.

When editing, keep changes reviewable, add tests where behaviour changes, preserve the validated-query boundary, avoid unsupported claims, and never print or commit secrets.

Before finishing, verify tests, linting, and dependency scanning; update this file with facts; and update PR documentation when scope or validation changes.

## Other repositories planned for later standardisation

1. `Meettala/llm-business-insight-assistant`
2. `Meettala/rag-research-assistant`
3. `Meettala/jobpilot-ai`
4. `Meettala/ai-job-market-skill-analyzer`
5. `Meettala/ml-prediction-app`
6. `Meettala/meet-tala-portfolio`
