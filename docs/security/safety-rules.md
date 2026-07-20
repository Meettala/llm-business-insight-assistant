# Safety rules — LLM Business Insight Assistant

1. **No code execution from user or LLM input, ever.** Every question —
   however it's parsed — must resolve to a `QuerySpec`, validated against
   a fixed whitelist of operations (`sum`, `mean`, `count`, `min`, `max`,
   `trend`) and against the dataset's actual columns, before anything
   runs. See `src/insight/query_spec.py`.
2. CSV cell values are untrusted input. A hostile cell (formula-injection
   syntax, embedded instructions, SQL-injection-style strings) is treated
   as inert text — it can become a group label in a chart, never a
   command. See `tests/test_safety.py`.
3. Every written answer states the exact operation, column, and computed
   number it's based on — verified in tests to match an independent
   pandas computation on the same data (no-fabrication check).
4. No LLM key is required for the tool to work.
5. Public demo uses a small synthetic sample dataset only.
