# AI Handoff — LLM Business Insight Assistant

> Paste this file into ChatGPT, Claude, Gemini, Copilot, Perplexity, or another AI assistant to continue this repository without restarting the project. Verify the live repository, active pull request, and latest CI run before changing anything.

## Continuation instruction

You are continuing `Meettala/llm-business-insight-assistant`.

Do not replace the architecture casually or weaken the constrained-execution safety model. Read the live code, this file, `README.md`, `SECURITY.md`, `docs/architecture.md`, and PR #1 before editing. Preserve verified behaviour, add tests for behavioural changes, and update this file after material code, architecture, security, deployment, documentation, licensing, or roadmap work.

Never place secrets, customer data, private keys, private prompts, production infrastructure details, or confidential commercial information in this public repository.

## Project identity

- Repository: `Meettala/llm-business-insight-assistant`
- Owner: Meet Tala
- Purpose: public portfolio and reference implementation
- Licence: MIT
- Base branch: `main`
- Active branch: `agent/professional-repository-foundation`
- Pull request: PR #1, `Professionalize repository foundation`
- PR URL: `https://github.com/Meettala/llm-business-insight-assistant/pull/1`
- Last updated: 26 July 2026

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
- `src/insight/parser_rule_based.py` — no-key parser and fallback.
- `src/insight/parser_llm.py` — provider calls and strict untrusted-output parsing.
- `src/insight/executor.py` — deterministic analytics and edge-case protection.
- `src/insight/explain.py` — explanations built from computed values.
- `src/insight/pipeline.py` — mandatory orchestration path.
- `streamlit_app/app.py` — interactive interface and safe user-facing errors.

## Implemented

### Safety and validation

- Fixed operation whitelist.
- Schema-aware numeric and date validation.
- Strict malformed-LLM-response handling.
- Rejection of empty output, arrays, unknown fields, invalid types, and missing operations.
- Provider fallback with structured logging.
- Injection-resistance coverage for hostile CSV values and query fields.
- Mandatory validation before deterministic pandas execution.

### Reliability

- `QueryExecutionError` for unusable analytical results.
- Protection for empty filtered data, null-only measures, invalid dates, empty grouped/trend results, and non-finite values.
- Safe Streamlit handling for malformed CSVs, empty files, unsupported questions, and execution failures.
- Provider fallback tests that avoid paid API calls and prevent exception details from reaching user-facing output.

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
- Living AI handoff.
- Architecture and social-preview SVG assets in `docs/assets/`.
- Updated PR description covering scope, safety, validation, deployment, and commercial boundaries.

## Verified validation status

Workflow run 37 on commit `a7e588a49d0695d7a263aa5cc128135046ca62aa` completed successfully:

- Python 3.10 tests: passed.
- Python 3.11 tests: passed.
- Python 3.12 tests: passed.
- Ruff application code: passed.
- Ruff tests: passed.
- `pip-audit -r requirements.txt`: passed.

A final workflow will run after this handoff update. Do not claim that newer commit is green until GitHub confirms it.

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

## Known limitations

- The analytical grammar is intentionally narrow.
- The rule-based parser may choose the first numeric column for an ambiguous question.
- Type inference is heuristic.
- Complex joins, arbitrary formulas, forecasting, and unrestricted SQL are out of scope.
- Provider timeout, retry, latency, and cost instrumentation remain future work.
- Dependencies use compatible minimum versions rather than a generated lock file.
- Docker is for local demonstration, not a complete production deployment.
- A real Streamlit screenshot or demo GIF must still be captured from a running app; repository SVG assets are available now.
- Accessibility testing and structured parser evaluation datasets remain future work.

## Next work after PR #1

1. Confirm the final CI run generated by this handoff update.
2. Mark PR #1 ready for review if it remains green and mergeable.
3. Merge intentionally into `main` after review.
4. Run the merged app locally or deploy it and capture a real screenshot/demo GIF.
5. Set `docs/assets/social-preview.svg` or a rendered PNG as the GitHub social preview manually in repository settings.
6. Add provider timeout/cost instrumentation, parser evaluation datasets, accessibility testing, and richer validated filters in later PRs.

## Public versus commercial product policy

This repository demonstrates the concept, safety model, engineering decisions, tests, and local demo. A future paid product should live in a separate private proprietary repository with identity, least privilege, tenant isolation, encryption, secret management, audit logging, monitoring, backup, retention, abuse prevention, incident response, compliance review, and penetration testing.

See `docs/commercialisation-and-private-production.md`.

## Rules for another AI

Before editing, inspect the live branch, PR, CI status, implementation, README, security policy, and architecture docs. Do not ask the user to repeat information recorded here.

When editing, keep changes reviewable, add tests, preserve the validated-query boundary, avoid unsupported claims, and never print or commit secrets.

Before finishing, verify tests, linting, dependency scanning, update this file with facts, and update the PR description when scope or validation changes.

## Other repositories planned for later standardisation

1. `Meettala/llm-business-insight-assistant`
2. `Meettala/rag-research-assistant`
3. `Meettala/jobpilot-ai`
4. `Meettala/ai-job-market-skill-analyzer`
5. `Meettala/ml-prediction-app`
6. `Meettala/meet-tala-portfolio`
