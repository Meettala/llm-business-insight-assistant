# AI Handoff — LLM Business Insight Assistant

> Paste this file into ChatGPT, Claude, Gemini, Perplexity, Copilot, or another AI assistant when continuing work on this repository. Treat it as the current project source of context, but verify the live repository, open pull requests, and CI status before making changes.

## Handoff instruction for the next AI

You are continuing development of `Meettala/llm-business-insight-assistant`.

Do not restart the project, replace the architecture casually, or remove the constrained-execution safety model. First inspect the live repository, current branch, open pull requests, CI results, and this file. Preserve verified working behaviour. Make changes through a feature branch and pull request, run tests and quality checks, and update this file after every material code, architecture, security, documentation, deployment, or roadmap change.

When updating this file:

1. Change the `Last updated` date and current branch/PR status.
2. Add completed work to `Implemented so far`.
3. Record important decisions in `Decisions that must be preserved`.
4. Update `Current validation status` with real test and CI results only.
5. Move finished items out of `Next work`.
6. Add newly discovered risks or limitations.
7. Never include secrets, private keys, customer data, or confidential production information.

## Project identity

- Repository: `Meettala/llm-business-insight-assistant`
- Owner: Meet Tala
- Project type: Public portfolio and reference implementation
- Public licence: MIT
- Current base branch: `main`
- Active development branch: `agent/professional-repository-foundation`
- Active pull request: Draft PR #1, `Professionalize repository foundation`
- PR URL: `https://github.com/Meettala/llm-business-insight-assistant/pull/1`
- Last updated: 26 July 2026

## Product purpose

The project is a safety-first business analytics assistant. A user uploads a CSV file and asks a plain-English business question. The application returns a calculated result, chart-ready data, and a written explanation grounded in the uploaded dataset.

The central design goal is to avoid unrestricted model-generated code. Natural language is converted into a constrained `QuerySpec`, which is validated before deterministic pandas execution.

## Core safety property

Every question, whether parsed by the rule-based parser or optional LLM parser, must become a validated `QuerySpec`.

Supported operations are restricted to:

- `sum`
- `mean`
- `count`
- `min`
- `max`
- `trend`

The application must not introduce:

- `eval`
- `exec`
- dynamically generated Python
- dynamically generated pandas expressions
- unrestricted SQL generation or execution
- direct execution of model output

The `QuerySpec` validation boundary is the most important architectural property and must remain mandatory for every execution path.

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
- `src/insight/query_spec.py` — query contract, operation whitelist, column validation, numeric/date schema validation.
- `src/insight/parser_rule_based.py` — zero-key question parser and fallback.
- `src/insight/parser_llm.py` — optional constrained LLM parser.
- `src/insight/executor.py` — fixed pandas operations only.
- `src/insight/explain.py` — grounded natural-language answer generation.
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
- Injection-resistance tests, including malicious-looking CSV cell values treated as inert text.

### Professional repository foundation

- Reworked the README for global recruiters, contributors, and technical reviewers.
- Added clearer product positioning, architecture, quick start, privacy, limitations, roadmap, and commercialisation guidance.
- Added `docs/architecture.md`.
- Added `docs/roadmap.md`.
- Added `SECURITY.md`.
- Added `CONTRIBUTING.md`.
- Added `CHANGELOG.md`.
- Added a pull-request template.
- Added MIT `LICENSE`.
- Added `docs/commercialisation-and-private-production.md`.

### Quality and engineering controls

- Added GitHub Actions CI.
- Test matrix covers Python 3.10, 3.11, and 3.12.
- Added Ruff linting.
- Added `pip-audit` dependency vulnerability scanning.
- Added `requirements-dev.txt`.
- Added schema-aware `QuerySpec` validation.
- Numeric operations now require a numeric value column.
- Trend operations now require a numeric value column and date-classified date column.
- Added tests for invalid categorical aggregations and invalid trend schemas.
- Cleaned and simplified the rule-based parser.

## Current validation status

Verified from GitHub Actions before the latest parser cleanup:

- Python 3.10 tests: passed.
- Python 3.11 tests: passed.
- Python 3.12 tests: passed.
- Ruff: initially failed because of actual parser lint issues.
- The parser lint issues were corrected in commit `53a48cb2a961bc523e46acde947bdeadbf2147ee`.
- A replacement CI run was started after that commit and must be checked before merging.

Do not claim the latest CI is passing until the live workflow run confirms it.

## Decisions that must be preserved

1. Safety takes priority over query flexibility.
2. Every execution path must call `validate_query_spec` before `execute_query`.
3. Unsupported questions should fail safely or request clarification rather than generate arbitrary code.
4. The rule-based parser must remain functional without paid API keys.
5. Optional LLM output is untrusted input and must be parsed and validated.
6. The public portfolio repository uses MIT licensing.
7. Future revenue-generating production development must occur in a separate private repository with proprietary licensing.
8. Production secrets, infrastructure details, customer data, billing logic, private prompts, and commercial-only IP must not be committed to the public repository.
9. Claims in documentation must be supported by actual code, tests, CI, or measured evidence.
10. Changes should use branches and pull requests rather than direct unreviewed edits to `main`.

## Public versus commercial product policy

This public repository demonstrates the concept, architecture, safety model, and engineering quality.

A future paid product must use a separate private repository. That private system should include, at minimum:

- managed secret storage
- least-privilege access
- multi-factor authentication
- protected branches and review requirements
- separate development, staging, and production environments
- encryption in transit and at rest
- tenant/data isolation
- audit logs and monitoring
- vulnerability scanning
- backups and tested recovery
- retention and deletion controls
- rate limiting and abuse protection
- incident response procedures
- privacy and regulatory review
- penetration testing appropriate to risk

Do not describe any system as completely or 100% secure. Use evidence-based, defence-in-depth language.

## Known risks and limitations

- The analytical grammar is intentionally narrow.
- The rule-based parser may choose the first numeric column when the user's request is ambiguous.
- The optional LLM parser currently relies on provider output being valid JSON before application validation.
- Malformed LLM JSON and unexpected response shapes need stronger dedicated tests and error handling.
- Type inference is heuristic and may misclassify unusual datasets.
- Complex joins, arbitrary formulas, forecasting, and unrestricted SQL are out of scope.
- Current dependencies use broad minimum versions rather than a fully reproducible lock strategy.
- Docker and production deployment configuration are not yet implemented.
- User-facing error messages and observability need improvement.
- Screenshots, demo media, and a repository social-preview image are not yet added.

## Next work

Continue in this order unless live repository findings require reprioritisation:

1. Check the latest GitHub Actions run for commit `53a48cb2a961bc523e46acde947bdeadbf2147ee`.
2. Fix any remaining Ruff, test, or dependency-audit failures without weakening the gates unnecessarily.
3. Add strict malformed-LLM-output handling:
   - invalid JSON
   - JSON arrays instead of objects
   - unknown fields
   - invalid field types
   - missing required intent
   - provider returning markdown or empty content
4. Add unit tests for the optional LLM parser without making real paid API calls.
5. Replace broad exception printing in the pipeline with structured, safe error handling and logging.
6. Improve user-facing Streamlit errors so invalid questions do not expose internal details.
7. Review executor edge cases:
   - empty filtered datasets
   - all-null numeric columns
   - invalid/empty trend dates
   - NaN and infinite values
8. Add packaging metadata, likely through `pyproject.toml`.
9. Add a reproducible dependency strategy.
10. Add Docker support suitable for local demonstration, not production secrets.
11. Add screenshots, demo GIF/video, architecture visuals, and social-preview artwork.
12. Complete review of Draft PR #1, mark ready only after all required checks pass, then merge intentionally.
13. After this repository is stable, reuse the repository standard across the user's other projects.

## Working rules for another AI

Before editing:

- Read `README.md`, `AI_HANDOFF.md`, `SECURITY.md`, `docs/architecture.md`, and the current PR.
- Inspect the actual code and tests; do not rely only on this summary.
- Check the current branch and CI status.
- Do not ask the user to repeat information already present here or in the repository.

When changing code:

- Keep changes scoped and reviewable.
- Add or update tests for behaviour changes.
- Preserve the validated-query safety boundary.
- Avoid adding unnecessary frameworks or complexity.
- Do not insert fake metrics, fake users, fake performance claims, or unsupported security claims.
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

Current priority order previously agreed:

1. LLM Business Insight Assistant
2. RAG Research Assistant
3. JobPilot AI
4. AI Job Market Skill Analyzer
5. ML Prediction App
6. Portfolio

This ordering may be adjusted based on code quality, job relevance, dependencies, or security findings, but changes should be recorded here.
