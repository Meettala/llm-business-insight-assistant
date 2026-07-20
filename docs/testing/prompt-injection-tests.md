# Injection resistance tests — LLM Business Insight Assistant

This project's main risk isn't "prompt injection" in the RAG/chatbot
sense — it's **code injection via uploaded data**, since the premise is
"let an LLM turn a question into a query against arbitrary user data."
`tests/test_safety.py` (3 tests, all passing) covers this directly:

| # | Scenario | Result |
|---|---|---|
| 1 | CSV cell contains a SQL-injection-style string (`'; DROP TABLE sales;--`) | Treated as an ordinary group label; aggregation is still correct |
| 2 | QuerySpec's `operation` field is set to something like `os.system(...)` | Rejected by `validate_query_spec` — never reaches the executor |
| 3 | QuerySpec references a column name containing injection syntax | Rejected — column must exist in the actual dataset |

The deeper guarantee: the executor (`executor.py`) only ever calls a
fixed set of pandas methods selected by a whitelisted `operation` string
— there is no `eval`, `exec`, or dynamic code path anywhere in the
pipeline, so there's no code-injection surface to defend even if a future
LLM parser were compromised or hallucinated something unexpected.
