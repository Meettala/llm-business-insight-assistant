# LLM Business Insight Assistant

A safety-first analytics assistant that turns plain-English business questions into validated, reproducible insights from CSV data.

> Natural-language input never receives authority to execute arbitrary code. Every request must resolve to a validated `QuerySpec` using a fixed operation whitelist and real columns from the uploaded dataset.

## Why this project exists

Many natural-language analytics demos generate SQL, Python, or pandas expressions dynamically. That is flexible, but it expands the attack surface and makes behaviour harder to audit. This project separates interpretation from execution: a parser proposes a constrained analytical intent, application code validates it, and deterministic pandas operations perform the calculation.

## Portfolio highlights

This repository demonstrates practical skills relevant to applied AI, AI engineering, data products, backend development, and secure software engineering:

- constrained LLM integration with untrusted-output validation
- deterministic analytics instead of model-generated code execution
- schema-aware request validation
- provider failure fallback without paid API calls in tests
- adversarial and injection-resistance testing
- Python 3.10–3.12 continuous integration
- Ruff linting and dependency vulnerability auditing
- safe runtime and user-facing error handling
- packaging metadata and Docker-based local deployment
- architecture, security, contribution, roadmap, and commercialisation documentation

## Core capabilities

- Upload and inspect CSV datasets.
- Infer numeric, categorical, and date-like columns.
- Parse common questions without an API key.
- Optionally use OpenAI or Anthropic to propose the same constrained `QuerySpec`.
- Execute only `sum`, `mean`, `count`, `min`, `max`, and `trend`.
- Apply validated grouping and filtering.
- Reject invalid column types before pandas execution.
- Return chart-ready data and written explanations grounded in calculated values.
- Handle malformed provider output, empty data, unusable dates, null-only measures, and non-finite results safely.

## Safety boundary

Every parser path produces a `QuerySpec`. Application validation checks the operation, referenced columns, required fields, and inferred dataset types before the executor is called.

The execution layer does not use:

- `eval`
- `exec`
- generated Python
- generated SQL
- generated pandas expressions
- direct execution of model output

The safety suite includes adversarial operation names, nonexistent columns, malformed LLM JSON, unsupported response fields, and injection-style text stored in CSV cells. Dataset text remains inert data.

Read [`docs/architecture.md`](docs/architecture.md), [`docs/security/safety-rules.md`](docs/security/safety-rules.md), and [`SECURITY.md`](SECURITY.md) for the full model.

## Architecture

```text
User question + CSV
        |
        v
CSV loading and column-type inference
        |
        v
Rule-based parser or optional LLM parser
        |
        v
Strict LLM-response parsing
        |
        v
Validated QuerySpec  <--- mandatory trust boundary
        |
        v
Deterministic pandas executor
        |
        +----> chart-ready result
        |
        +----> grounded explanation
```

Key modules:

- `src/insight/data.py` — CSV loading and column-type inference.
- `src/insight/query_spec.py` — constrained query contract and validation boundary.
- `src/insight/parser_rule_based.py` — zero-key parser and provider fallback.
- `src/insight/parser_llm.py` — provider calls and strict untrusted-response parsing.
- `src/insight/executor.py` — fixed analytical operations and edge-case protection.
- `src/insight/explain.py` — written answers derived from computed values.
- `src/insight/pipeline.py` — required end-to-end orchestration path.
- `streamlit_app/app.py` — interactive application with safe user-facing errors.

## Quick start

### Requirements

- Python 3.10 or newer
- `pip`

### Local installation

```bash
git clone https://github.com/Meettala/llm-business-insight-assistant.git
cd llm-business-insight-assistant
python -m venv .venv
```

Activate the environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install and run:

```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

The bundled rule-based parser works without any API key.

## Docker demo

```bash
docker build -t llm-business-insight-assistant .
docker run --rm -p 8501:8501 llm-business-insight-assistant
```

Open `http://localhost:8501`. The image runs as a non-root user and does not include `.env` files, tests, private keys, or production configuration.

For optional provider parsing, pass a key at runtime rather than baking it into the image:

```bash
docker run --rm -p 8501:8501 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  llm-business-insight-assistant
```

## Optional LLM parsing

Copy the environment example:

```bash
cp .env.example .env
```

Then add either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`. The provider may propose a candidate query, but its output is treated as untrusted JSON and must pass strict response parsing plus application-side `QuerySpec` validation.

Only schema information and the user question are sent by the current parser implementation; uploaded row values are not included in the provider prompt.

## Testing and quality

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the same core checks used in CI:

```bash
python -m pytest tests/ -q
ruff check src streamlit_app tests
pip-audit -r requirements.txt
```

The suite covers:

- operation and column validation
- numeric/date schema enforcement
- rule-based parsing
- strict LLM-response parsing
- deterministic execution correctness
- provider failure fallback
- empty, null-only, invalid-date, and non-finite edge cases
- adversarial and injection-resistance scenarios

GitHub Actions runs tests on Python 3.10, 3.11, and 3.12 and performs linting plus dependency auditing for every pull request.

## Example questions

Depending on the uploaded schema:

- “What is total revenue by region?”
- “What is the average units sold by product?”
- “Show the revenue trend over time.”
- “Which region has the highest revenue?”

Unsupported requests fail safely rather than being converted into unrestricted code.

## Repository structure

```text
.
├── .github/workflows/      # CI test and quality gates
├── data/                   # Synthetic sample dataset
├── docs/                   # Architecture, product, testing, and security docs
├── src/insight/            # Core application package
├── streamlit_app/          # Interactive Streamlit demo
├── tests/                  # Behavioural, safety, and edge-case tests
├── AI_HANDOFF.md           # Living cross-AI project continuation context
├── Dockerfile              # Non-root local demo image
├── pyproject.toml          # Package and tool configuration
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

## Privacy

CSV processing remains local when the rule-based parser is used. When provider parsing is enabled, review the provider's data-handling terms and avoid sensitive schemas unless the deployment has appropriate privacy controls. See [`docs/security/privacy-by-design.md`](docs/security/privacy-by-design.md).

## Known limitations

- The analytical grammar is intentionally narrow.
- Type inference is heuristic and may require refinement for unusual datasets.
- Complex joins, arbitrary formulas, forecasting, and unrestricted SQL are out of scope.
- This public repository is a portfolio/reference implementation, not a governed multi-tenant enterprise platform.
- A production commercial product would require additional identity, isolation, monitoring, compliance, and operational controls.

## Roadmap

Planned work includes richer validated filters, clarification prompts, parser evaluation datasets, deterministic chart selection, accessibility testing, provider timeout/cost instrumentation, and versioned query schemas. See [`docs/roadmap.md`](docs/roadmap.md).

## Project continuation

[`AI_HANDOFF.md`](AI_HANDOFF.md) is a living project record designed to be pasted into ChatGPT, Claude, Gemini, Copilot, or another AI assistant. It documents the architecture, completed work, decisions, risks, validation status, and next actions so development can continue without re-explaining the project from the beginning.

## Public and commercial use

This public portfolio repository is MIT licensed. A future revenue-generating product should be developed in a separate private proprietary repository with production controls. See [`docs/commercialisation-and-private-production.md`](docs/commercialisation-and-private-production.md).

## Contributing and security

Review [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Report suspected vulnerabilities privately using [`SECURITY.md`](SECURITY.md); do not place secrets or confidential datasets in public issues.

## Licence

Released under the [MIT License](LICENSE).

## Author

Built by [Meet Tala](https://github.com/Meettala) as part of a portfolio focused on safe LLM applications, applied AI, analytics, and production-minded software engineering.
