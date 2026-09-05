# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog. Versioned code follows Semantic Versioning; GitHub Releases are a separate publication artifact and must not be inferred from this file alone.

## [Unreleased]

### Job-readiness maintenance — 2026-09-05

- Align `pyproject.toml` with the existing v0.2.0 accuracy-engine code and documentation.
- Re-verify the current Python 3.10–3.12 install/test matrix, Ruff, dependency audit and Docker run path.
- Qualify the Streamlit URL as a candidate/currently unverified deployment until a fresh browser smoke test succeeds.
- Clarify that the 49/49 result is the dated 2 August 2026 live benchmark result; the original three raw benchmark CSV files are not committed, so that exact live run is not reproducible from the public repository alone.
- Surface the existing architecture asset for recruiter review.

### Remaining external evidence work

- Publish a formal GitHub `v0.2.0` Release from `docs/RELEASE_NOTES_v0.2.0.md` after the JR02 technical gate is green.
- Freshly smoke-test the recorded Streamlit deployment before adding it to the GitHub Website field.
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
- Live validation report, portfolio copy, media checklist and prepared release notes.

### Changed

- Replaced first-numeric-column guessing with semantic schema matching.
- Made deterministic parsing the primary path and optional LLM parsing a constrained fallback.
- Expanded optional provider JSON to the same typed query fields while preserving strict rejection of unknown or malformed content.
- Improved README documentation for recruiters and technical reviewers.

### Validated on 2 August 2026

- 85 focused local tests passed before merge.
- GitHub Actions CI run #56 passed across Python 3.10, 3.11 and 3.12.
- Ruff source and test checks passed.
- Dependency audit passed.
- Post-deployment audit confirmed **49/49 approved benchmark questions passed** across narrow, wide and 12,000-row datasets.

The 49/49 figure applies only to the approved benchmark datasets and questions used in that dated validation.

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
