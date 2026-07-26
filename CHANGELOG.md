# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the project intends to follow Semantic Versioning once formal releases begin.

## [Unreleased]

### Added

- Continuous integration across Python 3.10, 3.11, and 3.12.
- Ruff linting and dependency vulnerability auditing with `pip-audit`.
- `pyproject.toml` packaging and shared tool configuration.
- Strict parsing for untrusted LLM JSON responses.
- Offline tests for malformed, fenced, empty, and schema-invalid provider output.
- Provider failure fallback tests.
- Schema-aware numeric and date validation.
- Executor protection for empty data, null-only measures, invalid dates, and non-finite results.
- Safe user-facing Streamlit error messages.
- Non-root Docker demo image and `.dockerignore`.
- Security policy and private vulnerability-reporting guidance.
- Contribution guidelines focused on preserving constrained execution.
- Architecture and roadmap documentation.
- MIT licence and public-versus-private commercialisation policy.
- Living `AI_HANDOFF.md` continuation context.
- Portfolio architecture and social-preview SVG assets.

### Changed

- Reworked the README for recruiters, contributors, and technical reviewers.
- Clarified that optional LLM parsing remains subordinate to strict response parsing and application-side `QuerySpec` validation.
- Replaced broad console printing with structured provider-fallback logging.
- Improved rule-based parser readability and column selection.
- Limited quality linting to executable source, application, and test code.

### Security

- Numeric operations now reject categorical value columns before execution.
- Trend requests now require an inferred date column.
- Unknown LLM-response fields and invalid field types are rejected.
- Provider failures fall back without exposing secrets in user-facing output.
- Docker excludes local environment files and runs as a non-root user.

## [0.1.0] - 2026-07-20

### Added

- Initial safety-first CSV analytics pipeline.
- Rule-based and optional LLM-assisted parsing.
- Validated `QuerySpec` execution boundary.
- Streamlit application.
- Initial automated tests including injection-resistance checks.
- Security, privacy, testing, and MVP documentation.
