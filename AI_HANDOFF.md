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
- The merged repository is ready for portfolio and job-application use.
- Presentation follow-up branch: `docs/presentation-guide`
- Presentation instructions: `docs/PORTFOLIO_PRESENTATION_GUIDE.md`

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

## Verified validation

Final workflow run 38 on commit `2d40f0ad1a6aaa98905d8c691ee6417d8f1caa07` passed:

- Python 3.10 tests.
- Python 3.11 tests.
- Python 3.12 tests.
- Ruff application code.
- Ruff tests.
- `pip-audit -r requirements.txt`.

Any later change must be validated again before being described as green.

## Presentation tasks

The remaining tasks are presentation-only and are documented in detail in `docs/PORTFOLIO_PRESENTATION_GUIDE.md`:

1. Run the Streamlit app locally or through Docker.
2. Capture a real application screenshot.
3. Record a 30–60 second demo video or GIF.
4. Add genuine demo media to the README.
5. Convert `docs/assets/social-preview.svg` to a suitable PNG.
6. Upload the PNG through GitHub repository **Settings → General → Social preview**.
7. Verify the public repository before sharing it with recruiters.

The guide also includes suggested GitHub topics, a repository description, CV wording, interview wording, and instructions for another AI assistant.

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
- A real screenshot or demo GIF still requires running the application.
- GitHub social-preview configuration must be completed through repository settings.
- Accessibility testing and structured parser evaluation datasets remain future work.

## Public versus commercial product policy

This repository demonstrates the concept, safety model, engineering decisions, tests, and local demo. A future paid product should live in a separate private proprietary repository with identity, least privilege, tenant isolation, encryption, secret management, audit logging, monitoring, backup, retention, abuse prevention, incident response, compliance review, and penetration testing.

See `docs/commercialisation-and-private-production.md`.

## Rules for another AI

Before editing, inspect the live branch, open PRs, CI status, implementation, README, security policy, architecture documentation, and presentation guide. Do not ask the user to repeat information recorded here.

When editing, keep changes reviewable, add tests where behaviour changes, preserve the validated-query boundary, avoid unsupported claims, and never print or commit secrets.

Before finishing, verify tests, linting, and dependency scanning; update this file with facts; and update PR documentation when scope or validation changes.

## Other repositories planned for later standardisation

1. `Meettala/llm-business-insight-assistant`
2. `Meettala/rag-research-assistant`
3. `Meettala/jobpilot-ai`
4. `Meettala/ai-job-market-skill-analyzer`
5. `Meettala/ml-prediction-app`
6. `Meettala/meet-tala-portfolio`
