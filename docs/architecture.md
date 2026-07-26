# Architecture

## Design objective

The application provides natural-language access to tabular business data without granting a language model authority to execute arbitrary code.

The central architectural decision is to separate **interpretation** from **execution**:

1. A user provides a CSV file and asks a question.
2. Dataset columns are inspected and typed.
3. A rule-based parser or optional LLM parser proposes a structured `QuerySpec`.
4. Application code validates the specification against a fixed operation whitelist and the real dataset schema.
5. A deterministic pandas executor performs the calculation.
6. The result is converted into chart-ready data and a grounded written explanation.

## Trust boundaries

### Untrusted inputs

- uploaded filenames and CSV contents
- column names and cell values
- natural-language questions
- optional LLM output

All of these inputs must be treated as data, never as executable instructions.

### Trusted application boundary

`src/insight/query_spec.py` defines the contract that crosses into execution. A request is executable only after validation confirms:

- the operation is supported
- referenced columns exist
- the measure is compatible with the operation
- grouping and filtering use known columns
- required fields are present

### Deterministic execution

`src/insight/executor.py` maps validated operations to explicit pandas calls. It does not execute generated source code, SQL, or expression strings.

## Component responsibilities

| Component | Responsibility |
|---|---|
| `data.py` | Load CSV data and infer useful column types |
| `parser_rule_based.py` | Translate common question patterns without an external model |
| `parser_llm.py` | Optionally propose the same constrained query shape |
| `query_spec.py` | Validate the query contract and enforce the safety boundary |
| `executor.py` | Perform deterministic aggregations and trends |
| `explain.py` | Produce a narrative based on actual result values |
| `pipeline.py` | Coordinate the end-to-end workflow |
| `streamlit_app/app.py` | Provide the interactive interface |

## Security properties

The architecture is designed to guarantee that:

- an LLM cannot select an operation outside the whitelist
- an LLM cannot reference nonexistent columns successfully
- CSV cell text cannot become executable instructions
- failed validation stops execution
- explanations are generated from computed results rather than model memory

These properties are covered by the test suite, including adversarial strings stored in CSV cells.

## Trade-offs

The constrained design intentionally sacrifices arbitrary analytical flexibility for auditability, testability, and a smaller attack surface. Queries requiring joins, custom formulas, forecasting, or unrestricted SQL are rejected or remain out of scope.

## Future evolution

New analytical capabilities should be added as explicit typed operations with:

1. a schema update
2. validation rules
3. deterministic executor logic
4. positive and negative tests
5. security review
6. user-facing documentation
