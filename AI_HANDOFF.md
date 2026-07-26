# AI Handoff — LLM Business Insight Assistant

> Paste this file into ChatGPT, Claude, Gemini, Perplexity, Copilot, or another AI assistant when continuing work on this repository. Treat it as the current source of project context, but verify the live repository, open pull requests, and CI status before changing anything.

## Handoff instruction for the next AI

You are continuing development of `Meettala/llm-business-insight-assistant`.

Do not restart the project, replace the architecture casually, or remove the constrained-execution safety model. First inspect the live repository, current branch, open pull requests, CI results, and this file. Preserve verified behaviour. Make changes through a feature branch and pull request, run tests and quality checks, and update this file after every material code, architecture, security, documentation, deployment, licensing, or roadmap change.

When updating this file:

1. Update the date, branch, PR, and validation status.
2. Add completed work to `Implemented so far`.
3. Record important decisions in `Decisions that must be preserved`.
4. Report only verified test and CI results.
5. Move completed items out of `Next work`.
6. Add newly discovered risks or limitations.
7. Never include secrets, private keys, customer data, or confidential production information.

## Project identity

- Repository: `Meettala/llm-business-insight-assistant`
- Owner: Meet Tala
- Project type: Public portfolio and reference implementation
- Public licence: MIT
- Base branch: `main`
- Active branch: `agent/professional-repository-foundation`
- Active pull request: Draft PR #1, `Professionalize repository foundation`
- PR URL: `https://github.com/Meettala/llm-business-insight-assistant/pull/1`
- Last updated: 26 July 2026

## Product purpose

The project is a safety-first business analytics assistant. A user uploads a CSV file and asks a plain-English business question. The application returns a calculated result, chart-ready data, and a written explanation grounded in the uploaded dataset.

The central design goal is to avoid unrestricted model-generated code. Natural language is converted into a constrained `QuerySpec`, which is validated before deterministic pandas execution.

## Core safety property

Every question, whether parsed by the rule-based parser or optional LLM parser, must become a validated `QuerySpec`.

Supported operations are restricted to `sum`, `mean`, `count`, `min`, `max`, and `trend`.

The application must not introduce `eval`, `exec`, dynamically generated Python, dynamically generated pandas expressions, unrestricted SQL, or direct execution of model output.

The `QuerySpec` validation boundary is mandatory for every execution path.

## Current architecture

```text
CSV + user question
        |
        v
CSV loading and column-type inference
        |
        v
Rule-based parser or optional LLM parser
        |
        v
Strict provider-response parsing for LLM mode
        |
        v
Validated QuerySpec
        |
        v
Deterministic pandas executor
        |
        +--> structured result/chart data
        |
        +--> grounded written explanation
```

Important modules:

- `src/insight/data.py` — CSV loading and schema/type inference.
- `src/insight/query_spec.py` — operation whitelist, column validation, and numeric/date schema validation.
- `src/insight/parser_rule_based.py` — zero-key parser and fallback.
- `src/insight/parser_llm.py` — optional provider calls plus strict parsing of untrusted provider output.
- `src/insight/executor.py` — fixed pandas operations only.
- `src/insight/explain.py` — grounded answer generation.
- `src/insight/pipeline.py` — required orchestration path and safety boundary.
- `streamlit_app/app.py` — interactive UI.

## Implemented so far

### Original MVP

- CSV upload and loading.
- Numeric, categorical, and date-like column inference.
- Rule-based parsing without an API key.
- Optional OpenAI or Anthropic parsing.
- Fixed operation whitelist.
- Grouping, filtering, scalar results, grouped results, and monthly trends.
- Streamlit interface.
- Synthetic sample sales dataset.
- Initial safety, parser, and execution tests.
- Injection-resistance tests, including malicious-looking CSV values treated as inert text.

### Professional repository foundation

- Reworked the README for global recruiters, contributors, and technical reviewers.
- Added clearer positioning, architecture, quick start, privacy, limitations, roadmap, and commercialisation guidance.
- Added `docs/architecture.md` and `docs/roadmap.md`.
- Added `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, and a pull-request template.
- Added MIT `LICENSE`.
- Added `docs/commercialisation-and-private-production.md`.
- Added this living `AI_HANDOFF.md` file.

### Quality and engineering controls

- Added GitHub Actions CI.
- Test matrix covers Python 3.10, 3.11, and 3.12.
- Added Ruff linting.
- Added `pip-audit` dependency vulnerability scanning.
- Added `requirements-dev.txt`.
- Added schema-aware `QuerySpec` validation.
- Numeric operations require a numeric value column.
- Trend operations require a numeric value column and a date-classified date column.
- Added tests for invalid categorical aggregations and invalid trend schemas.
- Cleaned and simplified the rule-based parser.
- Kept Ruff strict for application code and applied only a targeted `E402` exception to tests that intentionally bootstrap `sys.path` before imports.

### Strict LLM-response handling

- Added `InvalidLLMResponse` for malformed or unsafe provider responses.
- Added `parse_llm_response` as a dedicated untrusted-input boundary.
- Rejects empty responses.
- Rejects invalid JSON.
- Rejects arrays and other non-object JSON.
- Rejects unknown fields.
- Rejects missing or empty `operation`.
- Rejects invalid field types.
- Accepts plain JSON or a single JSON markdown fence.
- Returns a `QuerySpec` that still must pass application-side schema validation before execution.
- Added offline tests for valid JSON, fenced JSON, empty content, malformed JSON, missing operation, arrays, unknown fields, and invalid field types.
- No paid provider calls are required by these tests.

## Current validation status

Verified from GitHub Actions before the latest strict LLM parser commits:

- Python 3.10 tests: passed.
- Python 3.11 tests: passed.
- Python 3.12 tests: passed.
- Ruff initially found parser issues, which were fixed.
- A later Ruff run still failed because tests intentionally import after modifying `sys.path`.
- CI now keeps Ruff strict for application code and ignores only `E402` for the test directory.
- New commits containing the targeted Ruff configuration, strict LLM parser, and LLM parser tests require a fresh live CI check.

Do not claim the latest CI is passing until GitHub confirms the newest branch head.

## Decisions that must be preserved

1. Safety takes priority over query flexibility.
2. Every execution path must call `validate_query_spec` before `execute_query`.
3. Unsupported or malformed requests should fail safely or request clarification rather than generate code.
4. The rule-based parser must remain functional without paid API keys.
5. Optional LLM output is untrusted input and must pass strict response parsing and QuerySpec validation.
6. Unknown provider-response fields must be rejected, not silently ignored.
7. The public portfolio repository uses MIT licensing.
8. Future revenue-generating production development must occur in a separate private repository with proprietary licensing.
9. Production secrets, customer data, billing logic, private prompts, infrastructure details, and commercial-only IP must not be committed publicly.
10. Documentation claims must be supported by code, tests, CI, or measured evidence.
11. Changes should use branches and pull requests rather than direct unreviewed edits to `main`.

## Public versus commercial product policy

This public repository demonstrates the concept, architecture, safety model, and engineering quality.

A future paid product must use a separate private repository with managed secrets, least-privilege access, MFA, protected branches, separate environments, encryption, tenant isolation, audit logs, monitoring, vulnerability scanning, backups, retention controls, abuse protection, incident response, regulatory review, and appropriate penetration testing.

Do not describe any system as completely or 100% secure. Use evidence-based, defence-in-depth language.

## Known risks and limitations

- The analytical grammar is intentionally narrow.
- The rule-based parser may choose the first numeric column when the request is ambiguous.
- Strict LLM response parsing now validates structure, but the resulting `QuerySpec` still depends on the existing validator for operation and column correctness.
- Provider timeouts, authentication failures, and SDK-specific response edge cases still need structured error handling.
- Type inference is heuristic and may misclassify unusual datasets.
- Complex joins, arbitrary formulas, forecasting, and unrestricted SQL are out of scope.
- Dependencies use broad minimum versions rather than a fully reproducible lock strategy.
- Docker and deployment configuration are not yet implemented.
- User-facing error messages and observability need improvement.
- Screenshots, demo media, and a repository social-preview image are not yet added.

## Next work

Continue in this order unless live findings require reprioritisation:

1. Check GitHub Actions for the latest branch head after the strict LLM parser and test commits.
2. Fix any remaining test, Ruff, or dependency-audit failures without weakening gates unnecessarily.
3. Replace broad exception printing in `pipeline.py` with structured, safe logging and fallback behaviour.
4. Add tests proving provider failures fall back safely without exposing secrets or internal details.
5. Improve Streamlit errors so invalid questions and dataset issues are understandable but do not expose internals.
6. Review executor edge cases: empty filtered datasets, all-null numeric columns, invalid/empty trend dates, NaN, and infinite values.
7. Add packaging metadata, likely through `pyproject.toml`.
8. Add a reproducible dependency strategy.
9. Add Docker support suitable for local demonstration, with no production secrets.
10. Add screenshots, demo GIF/video, architecture visuals, and social-preview artwork.
11. Complete review of Draft PR #1, mark ready only after required checks pass, then merge intentionally.
12. After this repository is stable, reuse the standard across the user's other projects.

## Working rules for another AI

Before editing:

- Read `README.md`, `AI_HANDOFF.md`, `SECURITY.md`, `docs/architecture.md`, and the current PR.
- Inspect actual code and tests; do not rely only on this summary.
- Check the current branch and CI status.
- Do not ask the user to repeat information already present here or in the repository.

When changing code:

- Keep changes scoped and reviewable.
- Add or update tests for behaviour changes.
- Preserve the validated-query safety boundary.
- Avoid unnecessary frameworks or complexity.
- Do not insert fake metrics, users, performance claims, or unsupported security claims.
- Do not expose secrets in code, examples, logs, screenshots, issues, or documentation.

Before finishing a work session:

- Run or check tests, linting, and security scans.
- Summarise what changed and what remains.
- Update this file with verified facts.
- Update the PR description if scope has materially changed.

## Other user repositories planned for later standardisation

- `Meettala/meet-tala-portfolio`
- `Meettala/ai-job-market-skill-analyzer`
- `Meettala/ml-prediction-app`
- `Meettala/rag-research-assistant`
- `Meettala/jobpilot-ai`
- `Meettala/llm-business-insight-assistant`

Current priority order:

1. LLM Business Insight Assistant
2. RAG Research Assistant
3. JobPilot AI
4. AI Job Market Skill Analyzer
5. ML Prediction App
6. Portfolio

This ordering may be adjusted based on code quality, job relevance, dependencies, or security findings, but any change must be recorded here.
