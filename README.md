# LLM Business Insight Assistant

A safety-first analytics assistant that turns plain-English business questions into validated, reproducible insights from CSV data.

> The model never receives permission to execute arbitrary code. Every request must resolve to a validated `QuerySpec` using a fixed whitelist of supported operations and real columns from the uploaded dataset.

## Why this project exists

Many natural-language analytics demos rely on dynamically generated SQL, Python, or pandas expressions. That approach is flexible, but it also creates serious reliability and security risks. This project takes the opposite approach: natural language is only used to select a constrained analytical operation, while deterministic application code performs the calculation.

## Core capabilities

- Upload and inspect CSV datasets.
- Infer numeric, categorical, and date-like columns.
- Parse questions with a zero-key rule-based parser.
- Optionally use an LLM to produce the same constrained `QuerySpec` shape.
- Execute only whitelisted operations: `sum`, `mean`, `count`, `min`, `max`, and `trend`.
- Apply validated grouping and filtering.
- Generate charts and written explanations grounded in the calculated values.
- Run the complete workflow through a Streamlit interface.

## Safety boundary

Every question must resolve to a `QuerySpec` before execution. Validation checks the requested operation, referenced columns, grouping, filters, and dataset schema. The execution layer does not use `eval`, `exec`, dynamically generated SQL, or dynamically generated pandas expressions.

The automated safety tests include adversarial text stored inside CSV cells. Injection-style strings remain inert data values and are never interpreted as executable instructions.

Read the full security model in [`docs/security/safety-rules.md`](docs/security/safety-rules.md) and [`SECURITY.md`](SECURITY.md).

## Architecture

```text
User question + CSV
        |
        v
Column inference
        |
        v
Rule-based parser or optional LLM parser
        |
        v
Validated QuerySpec  <--- trust boundary
        |
        v
Deterministic pandas executor
        |
        +----> chart data
        |
        +----> grounded explanation
```

Key modules:

- `src/insight/data.py` — CSV loading and column type inference.
- `src/insight/query_spec.py` — validated query contract and safety boundary.
- `src/insight/parser_rule_based.py` — zero-key parser.
- `src/insight/parser_llm.py` — optional constrained LLM parser.
- `src/insight/executor.py` — deterministic analytics execution.
- `src/insight/explain.py` — grounded written responses.
- `src/insight/pipeline.py` — end-to-end orchestration.
- `streamlit_app/app.py` — interactive application.

See [`docs/architecture.md`](docs/architecture.md) for design decisions and trust boundaries.

## Quick start

### Prerequisites

- Python 3.10 or newer
- `pip`

### Installation

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

Install dependencies and run the app:

```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

The rule-based parser works without an API key.

## Optional LLM parsing

Copy the example environment file:

```bash
cp .env.example .env
```

Then add either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`. The LLM may help translate a question into a candidate `QuerySpec`, but the same application-side validation is always applied before execution.

## Testing

```bash
pip install pytest
python -m pytest tests/ -q
```

The current suite contains 13 tests covering:

- `QuerySpec` validation
- parser behavior
- execution correctness against independent pandas calculations
- injection resistance
- inert handling of adversarial CSV values

GitHub Actions runs the test suite on supported Python versions for every push and pull request.

## Example questions

Depending on the uploaded dataset, supported questions include:

- “What is total revenue by region?”
- “What is the average units sold by product?”
- “Show the revenue trend over time.”
- “Which region has the highest revenue?”

Questions outside the supported operation set are rejected rather than converted into unrestricted code.

## Repository structure

```text
.
├── data/                  # Synthetic sample data and generator
├── docs/                  # Product, testing, security, and architecture docs
├── src/insight/           # Core application package
├── streamlit_app/         # Interactive user interface
├── tests/                 # Unit and safety tests
├── .github/workflows/     # Continuous integration
├── .env.example           # Optional provider configuration
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── requirements.txt
```

## Privacy

CSV processing is designed to remain local when the rule-based parser is used. When optional external LLM parsing is enabled, review provider behavior and avoid sending sensitive column values unless the implementation and provider configuration explicitly support your privacy requirements. See [`docs/security/privacy-by-design.md`](docs/security/privacy-by-design.md).

## Known limitations

- The supported analytical grammar is intentionally narrow.
- Complex joins, arbitrary formulas, forecasting, and unrestricted SQL are out of scope.
- Automatic type inference can require refinement for unusual datasets.
- The project is an educational and portfolio-grade reference implementation, not a substitute for a governed enterprise analytics platform.

## Roadmap

Planned improvements include:

- richer validated filtering operators
- schema-aware clarification prompts
- structured evaluation datasets
- improved chart selection
- Docker-based local deployment
- cost and latency instrumentation for optional LLM providers
- expanded accessibility and error messaging

See [`docs/roadmap.md`](docs/roadmap.md).

## Contributing

Contributions are welcome. Review [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening an issue or pull request.

## Security

Please do not disclose suspected vulnerabilities publicly. Follow the process in [`SECURITY.md`](SECURITY.md).

## License

A license file will define permitted reuse and distribution. Until one is added, no additional rights are granted beyond those provided by GitHub's Terms of Service.

## Author

Built by [Meet Tala](https://github.com/Meettala) as part of a portfolio focused on safe LLM applications, applied AI, analytics, and production-minded software engineering.
