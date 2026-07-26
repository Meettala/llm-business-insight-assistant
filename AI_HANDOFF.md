# AI Handoff — LLM Business Insight Assistant

> Paste this file into ChatGPT, Claude, Gemini, Copilot, Perplexity, or another AI assistant to continue this repository without restarting the project. Verify the live repository, active pull request, and latest CI run before changing anything.

## Continuation instruction

You are continuing `Meettala/llm-business-insight-assistant`.

Do not replace the architecture casually or weaken the constrained-execution safety model. Read the live code, this file, `README.md`, `SECURITY.md`, `docs/architecture.md`, and Draft PR #1 before editing. Preserve verified behaviour, work through a feature branch and pull request, add tests for behavioural changes, and update this file after material code, architecture, security, deployment, documentation, licensing, or roadmap work.

Never place secrets, customer data, private keys, private prompts, production infrastructure details, or confidential commercial information in this public file or repository.

## Project identity

- Repository: `Meettala/llm-business-insight-assistant`
- Owner: Meet Tala
- Purpose: public portfolio and reference implementation
- Licence: MIT
- Base branch: `main`
- Active branch: `agent/professional-repository-foundation`
- Active PR: Draft PR #1, `Professionalize repository foundation`
- PR URL: `https://github.com/Meettala/llm-business-insight-assistant/pull/1`
- Last updated: 26 July 2026

## Product purpose

A user uploads a CSV file and asks a plain-English business question. The application infers the dataset schema, converts the question into a constrained `QuerySpec`, validates that specification, executes a fixed pandas operation, and returns chart-ready data plus an explanation grounded in the computed result.

The project demonstrates applied AI and analytics without granting a model authority to generate or execute arbitrary code.

## Core safety property

Every parser path must produce a `QuerySpec` and call `validate_query_spec` before `execute_query`.

Supported operations are restricted to:

- `sum`
- `mean`
- `count`
- `min`
- `max`
- `trend`

The project must not introduce `eval`, `exec`, generated Python, unrestricted SQL, generated pandas expressions, or direct execution of provider output.

Optional LLM output is untrusted JSON. It must pass strict response parsing and application-side schema validation. Unsupported or ambiguous requests should fail safely or fall back to the rule-based parser.

## Architecture

```text
CSV + question
      |
      v
CSV loading and column-type inference
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
Deterministic pandas executor
      |
      +--> chart-ready data
      |
      +--> grounded explanation
```

Important modules:

- `src/insight/data.py` — CSV loading and type inference.
- `src/insight/query_spec.py` — operation whitelist and schema validation.
- `src/insight/parser_rule_based.py` — no-key parser and provider fallback.
- `src/insight/parser_llm.py` — OpenAI/Anthropic calls and strict untrusted-output parsing.
- `src/insight/executor.py` — deterministic analytics and edge-case protection.
- `src/insight/explain.py` — explanations built from computed values.
- `src/insight/pipeline.py` — mandatory end-to-end orchestration path.
- `streamlit_app/app.py` — interactive interface and safe user-facing errors.

## Implemented

### Original MVP

- CSV upload and sample dataset.
- Numeric, categorical, and date-like inference.
- Rule-based parser without API keys.
- Optional OpenAI and Anthropic parsing.
- Fixed operation whitelist.
- Grouping, filtering, scalar, grouped, and monthly trend results.
- Streamlit demo.
- Safety and injection-resistance tests.

### Repository and portfolio foundation

- Recruiter-focused README.
- `docs/architecture.md` and `docs/roadmap.md`.
- `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`.
- Pull-request template.
- MIT `LICENSE`.
- Public-versus-private commercialisation policy.
- Living `AI_HANDOFF.md`.
- Portfolio architecture SVG and social-preview SVG in `docs/assets/`.

### Validation and safety improvements

- Schema-aware `QuerySpec` validation.
- Numeric operations reject non-numeric value columns.
- Trend operations require a date-classified column.
- Strict `InvalidLLMResponse` boundary.
- Rejection of empty output, malformed JSON, arrays, unknown fields, missing operations, and invalid field types.
- Plain JSON and a single JSON markdown fence supported.
- Provider failures use structured logging and rule-based fallback.
- Provider fallback tests ensure user-facing results do not expose provider exception details.
- LLM-produced specifications still pass the same application validator.

### Executor and UI hardening

- `QueryExecutionError` for valid intent that cannot produce a usable result.
- Non-count operations reject empty filtered datasets.
- Counts may safely return zero.
- Null-only numeric measures are rejected.
- Invalid-date trends are rejected.
- Non-finite analytical results are rejected.
- Grouped and trend outputs drop unusable values and verify finite numbers.
- Streamlit handles malformed CSVs, empty files, unsupported requests, execution failures, and invalid questions with safe messages.

### Engineering controls

- GitHub Actions test matrix for Python 3.10, 3.11, and 3.12.
- Ruff linting for source, application, and tests.
- `pip-audit` dependency scanning.
- `requirements-dev.txt`.
- `pyproject.toml` package metadata and central Ruff configuration.
- Non-root Docker demo image.
- `.dockerignore` excludes environment files, caches, tests, and private local configuration.

## Current validation status

Verified on recent workflow runs before the newest portfolio-readiness commits:

- Python 3.10 tests passed.
- Python 3.11 tests passed.
- Python 3.12 tests passed.
- Application Ruff now passes.
- Test Ruff was the latest remaining quality failure before central configuration and concise diagnostics were added.
- `pip-audit` had not yet run because GitHub stops the quality job at the first failed step.

The branch now contains additional provider fallback tests, executor edge-case tests, Streamlit handling, packaging, Docker, README, changelog, and visual assets. A fresh full CI result is required. Do not claim the latest branch is green until GitHub confirms tests, application Ruff, test Ruff, and `pip-audit` on the current head.

## Decisions that must be preserved

1. Safety takes priority over unrestricted analytical flexibility.
2. Every execution path validates before deterministic execution.
3. Optional provider output is untrusted input.
4. The no-key rule-based parser remains a first-class mode.
5. Provider failures fall back safely and are logged without exposing details in the UI.
6. Unknown provider fields are rejected rather than ignored.
7. Documentation claims require evidence from code, tests, CI, or measured results.
8. Public portfolio code uses MIT licensing.
9. A revenue-generating product must use a separate private proprietary repository.
10. Public code must not contain secrets, customer data, billing logic, production infrastructure details, or commercial-only IP.
11. No system should be described as completely or 100% secure.
12. Changes should use branches, pull requests, tests, and review rather than direct unreviewed edits to `main`.

## Public versus commercial product policy

This repository demonstrates the concept, safety model, engineering decisions, tests, and local demo. A future paid product should live in a separate private repository with proprietary licensing and appropriate controls for identity, least privilege, tenant isolation, encryption, secret management, audit logging, monitoring, backups, retention, abuse prevention, incident response, compliance review, and penetration testing.

See `docs/commercialisation-and-private-production.md`.

## Known limitations

- The supported analytical grammar is intentionally narrow.
- The rule-based parser may choose the first numeric column for an ambiguous question.
- Type inference is heuristic.
- Complex joins, arbitrary formulas, forecasting, and unrestricted SQL are out of scope.
- Provider timeout/retry/cost instrumentation is not yet implemented.
- Dependencies still use compatible minimum versions rather than a generated lock file.
- Docker is intended for local demonstration, not as a complete production deployment.
- A real application screenshot or demo GIF still needs to be captured from a running app; repository SVG visuals are already available.
- Accessibility testing and structured parser evaluation datasets remain future work.

## Immediate next work

1. Check CI on the newest branch head.
2. Fix any test Ruff failure with an actual code correction or narrowly justified configuration.
3. Review and fix any `pip-audit` finding.
4. Correct any failing provider fallback or executor edge-case test.
5. Run a final README, architecture, security, Docker, and packaging consistency review.
6. Add the architecture SVG to the README if presentation remains clear.
7. Update Draft PR #1 with complete scope and verified results.
8. Mark the PR ready only after all checks pass.
9. Merge intentionally into `main` only after review.
10. Capture a real Streamlit screenshot/demo after the merged version is run locally or deployed.

## Rules for another AI

Before editing:

- Inspect the live branch and PR.
- Check CI status.
- Read the implementation rather than trusting this summary alone.
- Do not ask the user to repeat information already recorded here.

When editing:

- Keep changes scoped and reviewable.
- Add tests for behaviour changes.
- Preserve the validated-query boundary.
- Avoid unnecessary frameworks and unsupported claims.
- Never print or commit secrets.

Before finishing:

- Verify tests, linting, and dependency scanning.
- Update this file with facts, not assumptions.
- Update the PR description if scope or validation status changed.

## Other repositories planned for later standardisation

Priority order:

1. `Meettala/llm-business-insight-assistant`
2. `Meettala/rag-research-assistant`
3. `Meettala/jobpilot-ai`
4. `Meettala/ai-job-market-skill-analyzer`
5. `Meettala/ml-prediction-app`
6. `Meettala/meet-tala-portfolio`
