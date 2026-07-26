# Roadmap

This roadmap prioritizes reliability, safety, usability, and reproducible evaluation. Items are proposals rather than delivery commitments.

## Near term

- Add richer validated filter operators.
- Improve error messages for unsupported or ambiguous questions.
- Add schema-aware clarification prompts.
- Expand tests for malformed CSV files and unusual column names.
- Add linting and formatting checks to continuous integration.
- Add screenshots and a short application demo.

## Medium term

- Add structured evaluation datasets for parser accuracy.
- Improve automatic chart selection while keeping it deterministic.
- Add Docker-based local deployment.
- Add provider-specific timeout, retry, cost, and latency instrumentation.
- Add accessibility checks for the Streamlit interface.
- Introduce versioned query schemas for backward compatibility.

## Longer term

- Support additional explicitly typed analytical operations.
- Add optional governed connectors for approved data sources.
- Add role-based access controls for multi-user deployment.
- Add audit logs for validated queries and result generation.
- Add deployment reference architectures for cloud environments.

## Non-goals

The project does not plan to support unrestricted source-code execution, unrestricted SQL generation, or an execution path that bypasses `QuerySpec` validation.
