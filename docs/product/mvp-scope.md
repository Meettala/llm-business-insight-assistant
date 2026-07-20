# MVP scope — LLM Business Insight Assistant

## In scope
- CSV upload with automatic column type detection.
- Rule-based question parsing (zero API key) producing a validated
  QuerySpec.
- Optional LLM-assisted parsing, constrained to the identical QuerySpec
  shape and validated identically.
- Whitelisted execution: sum, mean, count, min, max, trend-over-time,
  with optional group-by and filter.
- Chart + written explanation stating the exact numbers used.
- Streamlit interactive app + live client-side demo on the portfolio site.

## Explicitly out of scope
- Arbitrary SQL or code generation/execution of any kind.
- Multi-file joins or relational queries (single CSV per session).
- Persisted upload history.
- CSV → Markdown business report export as a separate polished document
  (the in-app explanation covers this; a dedicated export button is a
  fast follow, not required for the core safety-proof MVP).
