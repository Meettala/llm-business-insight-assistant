# LLM Business Insight Assistant

A safety-first analytics assistant that turns plain-English business questions into validated, reproducible insights from CSV data.

> Every request must resolve to a validated `QuerySpec`. Natural-language input and optional model output never receive authority to execute arbitrary Python, SQL or pandas expressions.

## Demo status

**Recorded Streamlit deployment:** [Open the LLM Business Insight Assistant](https://llm-business-insight-assistant-maubk3puyxkcbnjiad4vnr.streamlit.app/)

The deployed application was successfully used for the 2 August 2026 live benchmark. During the 5 September 2026 JR02 review, the available execution environment could not reach Streamlit, so this URL is retained as the recorded deployment rather than presented as a freshly smoke-tested current demo. Re-verify the seven-step workflow in `docs/PORTFOLIO_MEDIA_CHECKLIST.md` before treating current availability as confirmed.

## Verified benchmark

**Historical live validation completed on 2 August 2026: 49 of 49 approved benchmark questions passed.**

| Dataset | Questions | Passed | Accuracy |
|---|---:|---:|---:|
| Narrow CSV | 13 | 13 | 100% |
| Wide CSV | 20 | 20 | 100% |
| Long CSV — 12,000 rows | 16 | 16 | 100% |
| **Overall** | **49** | **49** | **100%** |

This is verified performance for the approved benchmark datasets and questions, not a claim of universal accuracy for every possible CSV or business request. See [`docs/LIVE_VALIDATION_REPORT_2026-08-02.md`](docs/LIVE_VALIDATION_REPORT_2026-08-02.md).

The approved question/answer benchmark is committed at `data/validation/approved_question_answer_benchmark.csv`. The original three raw benchmark CSV files are not public repository assets, so the exact 49-question live run cannot currently be reproduced from this repository alone. The automated tests cover the same supported intent classes on committed synthetic fixtures without replacing that historical live result.

## Why the architecture avoids generated code

A model is useful for interpreting intent, but giving model output authority to execute generated Python, SQL or pandas expressions would unnecessarily combine language-model uncertainty with code-execution risk. This project separates interpretation from authority:

**natural-language request → typed `QuerySpec` → application validation → fixed pandas executor**

The deterministic parser is primary. An optional provider is only a fallback parser and can return structured intent; its output is still untrusted and must pass the same application-side validation before execution.

## Portfolio highlights

- schema-aware natural-language analytics;
- deterministic execution instead of generated code;
- multiple validated filters;
- grouped highest/lowest ranking;
- date ranges, year filters and month/year analysis;
- conditional counts and percentages;
- validated net revenue, gross profit and profit-margin calculations;
- complete CSV loading with a paginated explorer;
- single-question and batch-question modes;
- downloadable question-and-answer audits;
- user-selected charts and Office/Excel-style colour palettes;
- Python 3.10–3.12 CI, Ruff and dependency auditing;
- adversarial and injection-resistance tests;
- Docker-based local deployment.

## Core safety boundary

Every parser path produces a typed `QuerySpec`. Application validation checks:

- whitelisted operation;
- referenced dataset columns;
- inferred numeric, categorical and date types;
- filter operators and values;
- ranking and date granularity;
- named application-controlled derived measures;
- limits and return fields.

The executor does **not** use:

- `eval`;
- `exec`;
- generated Python;
- generated SQL;
- generated pandas expressions;
- direct execution of provider output.

CSV text—including injection-style content—remains inert data.

## Supported analytics

- sum, mean, count, minimum and maximum;
- grouped totals, averages and counts;
- highest and lowest grouped results;
- exact categorical filters;
- multiple simultaneous filters;
- truthy/returned-order filters;
- year filters;
- monthly and yearly grouping;
- distinct values;
- date ranges;
- trend outputs;
- row context for minimum and maximum values;
- validated net revenue, gross profit and profit-margin calculations.

Unsupported or ambiguous questions fail safely rather than being converted into unrestricted code.

## Architecture

![Safety-first architecture: interpretation is untrusted, validation controls fixed pandas execution](docs/assets/architecture.svg)

```text
User question + uploaded CSV
        |
        v
Full CSV loading and schema inference
        |
        v
Deterministic parser
        |
        +----> optional constrained LLM fallback
        |
        v
Validated QuerySpec  <--- mandatory trust boundary
        |
        v
Fixed pandas executor
        |
        +----> grounded answer
        +----> chart-ready result
        +----> downloadable audit
```

Key modules:

- `src/insight/data.py` — complete CSV loading, profiling, pagination and type inference.
- `src/insight/query_spec.py` — typed query contract and validation boundary.
- `src/insight/parser_rule_based.py` — schema-aware deterministic parser.
- `src/insight/parser_llm.py` — optional provider calls and strict untrusted JSON parsing.
- `src/insight/executor.py` — fixed analytical operations and derived-measure enums.
- `src/insight/explain.py` — written answers generated from computed results.
- `src/insight/pipeline.py` — mandatory parsing, validation, execution and explanation path.
- `streamlit_app/app.py` — interactive application, charts and audit export.

## Quick start

### Requirements

- Python 3.10 or newer
- `pip`

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
python -m pip install -r requirements.txt
python -m pip check
streamlit run streamlit_app/app.py
```

The deterministic parser works without an API key.

## Docker

```bash
docker build -t llm-business-insight-assistant .
docker run --rm -p 8501:8501 llm-business-insight-assistant
```

Open `http://localhost:8501`. The image runs as a non-root user, includes the bundled sample dataset and exposes a Streamlit healthcheck. JR02 CI also builds the image and exercises the health endpoint so the documented container path is verified rather than assumed.

## Optional provider parsing

Add either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` at runtime. Provider output is treated as untrusted JSON and must pass strict field validation plus application-side `QuerySpec` validation. Uploaded row values are not included in the current provider prompt; the provider receives the question and the available column names.

## Testing

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -m pytest tests/ -q
ruff check src streamlit_app tests
pip-audit -r requirements.txt
```

On 2 August 2026, the accuracy-engine implementation passed 85 focused local tests and GitHub Actions CI run #56 across Python 3.10, 3.11 and 3.12 before merge. The deployed app then passed all 49 approved live benchmark questions. JR02 generates a new current CI result rather than treating those historical checks as current verification.

## Version and release status

The repository code/package version is **0.2.0**, matching the merged schema-aware accuracy engine and the existing changelog/release notes.

`docs/RELEASE_NOTES_v0.2.0.md` contains prepared release notes. A formal GitHub `v0.2.0` Release has not yet been published, so the repository does not claim one exists.

## Example questions

- “What is the total revenue for North?”
- “Which sales rep had the highest revenue?”
- “How many orders were returned?”
- “What is the date range?”
- “Revenue in 2024?”
- “Which month had the highest revenue?”
- “Total revenue for North region and Gadget X combined?”
- “What is the overall profit margin?”

## Presentation and professional copy

- [`docs/PORTFOLIO_MEDIA_CHECKLIST.md`](docs/PORTFOLIO_MEDIA_CHECKLIST.md)
- [`docs/PORTFOLIO_AND_PROFILE_COPY.md`](docs/PORTFOLIO_AND_PROFILE_COPY.md)
- [`docs/RELEASE_NOTES_v0.2.0.md`](docs/RELEASE_NOTES_v0.2.0.md)

## Known limitations

- semantic aliases are broad but not universal for every possible schema;
- categorical matching intentionally limits very high-cardinality columns;
- ambiguous discount fields may be rejected instead of guessed;
- joins, forecasting, arbitrary formulas and unrestricted SQL are out of scope;
- pandas requires the complete uploaded file to fit available memory;
- the original live-benchmark input CSVs are not committed, limiting exact public reproduction of the 2 August 49/49 run;
- this public repository is a portfolio/reference implementation, not a governed multi-tenant enterprise service.

## Privacy and production boundary

Uploaded CSV rows are processed inside the application runtime. The deterministic path makes no model-provider call. When optional provider parsing is enabled, the application sends the user question and available column names, but not uploaded row values. Review provider data-handling terms before enabling optional model parsing. A governed multi-tenant deployment would additionally require identity, tenant isolation, encryption, monitoring, retention controls and incident-response processes.

## Licence and author

Released under the [MIT License](LICENSE).

Built by [Meet Tala](https://github.com/Meettala) as part of a portfolio focused on safe LLM applications, applied AI, analytics and production-minded software engineering.
