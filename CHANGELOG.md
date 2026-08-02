# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog and the project follows Semantic Versioning for formal releases.

## [Unreleased]

### Pending

- Add the exact confirmed public Streamlit URL.
- Capture portfolio screenshots and a short demo video using synthetic data.

## [0.2.0] - 2026-08-02

### Added

- Schema-aware deterministic accuracy engine.
- Typed multiple filters using fixed operators.
- Grouped highest/lowest ranking.
- Distinct-value and date-range operations.
- Year filters and month/year grouping.
- Conditional counts with percentages.
- Row context for minimum and maximum transactions.
- Application-controlled net revenue, gross profit and profit-margin measures.
- Full-data CSV explorer with pagination and schema profiling.
- Single-question and multi-question batch modes.
- Downloadable question-and-answer audit and approved benchmark.
- User-selected bar, horizontal bar, line, area, scatter, pie and donut charts.
- Office/Excel-style and additional colour palettes.
- Live validation report, portfolio copy, media checklist and release notes.

### Changed

- Replaced first-numeric-column guessing with semantic schema matching.
- Made deterministic parsing the primary path and optional LLM parsing a constrained fallback.
- Expanded optional provider JSON to the same typed query fields while preserving strict rejection of unknown or malformed content.
- Improved README documentation for recruiters and technical reviewers.

### Validated

- 85 focused local tests passed before merge.
- GitHub Actions CI run #56 passed across Python 3.10, 3.11 and 3.12.
- Ruff source and test checks passed.
- Dependency audit passed.
- Post-deployment audit confirmed **49/49 approved benchmark questions passed** across narrow, wide and 12,000-row datasets.

### Security

- Every parser path still requires a validated `QuerySpec`.
- Filter operators, rankings, date granularities and derived measures remain fixed whitelists.
- No generated Python, unrestricted SQL, `eval`, `exec` or direct execution of model output was introduced.

## [0.1.0] - 2026-07-20

### Added

- Initial safety-first CSV analytics pipeline.
- Rule-based and optional LLM-assisted parsing.
- Validated `QuerySpec` execution boundary.
- Streamlit application.
- Initial automated tests including injection-resistance checks.
- Security, privacy, testing and MVP documentation.
