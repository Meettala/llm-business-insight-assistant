# LLM Business Insight Assistant

Upload a CSV, ask a business question in plain English, get a chart and a
written answer grounded in the actual numbers — never a plausible-sounding
guess from the model's general knowledge, and never arbitrary code
execution against your data.

## The core safety guarantee

Every question — whether parsed by the zero-key rule-based parser or an
optional LLM — must resolve to a `QuerySpec`: a fixed object naming one
of a handful of whitelisted operations (`sum`, `mean`, `count`, `min`,
`max`, `trend`) and real column names from your dataset. This is
validated (`src/insight/query_spec.py`) before anything touches your
data. There is no `eval`, no `exec`, no dynamically-constructed SQL or
pandas expression anywhere in the pipeline — see
`tests/test_safety.py` for the automated proof, including a test where a
CSV cell contains SQL-injection-style text and it's simply treated as an
inert string.

## Architecture

- `src/insight/data.py` — CSV loading + column type inference.
- `src/insight/query_spec.py` — the validated query interface (the
  safety boundary).
- `src/insight/parser_rule_based.py` — keyword-pattern question parser,
  zero API key needed.
- `src/insight/parser_llm.py` — optional LLM parser, constrained to the
  same QuerySpec shape.
- `src/insight/executor.py` — runs a validated QuerySpec with pandas.
- `src/insight/explain.py` — turns a result into a written answer that
  states its exact source numbers.
- `src/insight/pipeline.py` — the single entry point tying it together.
- `streamlit_app/app.py` — interactive demo, CSV upload supported.

## Run it

```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

## Tests

```bash
pip install pytest
python -m pytest tests/ -q
```

13 tests: QuerySpec validation, parser correctness, execution matching
independent pandas computations, and 3 dedicated injection-resistance
tests.

## Docs

- [`docs/security/safety-rules.md`](docs/security/safety-rules.md)
- [`docs/security/privacy-by-design.md`](docs/security/privacy-by-design.md)
- [`docs/testing/prompt-injection-tests.md`](docs/testing/prompt-injection-tests.md)
- [`docs/product/mvp-scope.md`](docs/product/mvp-scope.md)
