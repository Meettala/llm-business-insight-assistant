# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the project intends to follow Semantic Versioning once formal releases begin.

## [Unreleased]

### Added

- Continuous integration across Python 3.10, 3.11, and 3.12.
- Security policy and private vulnerability-reporting guidance.
- Contribution guidelines focused on preserving constrained execution.
- Architecture documentation covering components, trust boundaries, and trade-offs.
- Expanded README with setup, usage, privacy, limitations, roadmap, and recruiter-friendly project positioning.

### Changed

- Clarified that optional LLM parsing remains subordinate to application-side `QuerySpec` validation.

## [0.1.0] - 2026-07-20

### Added

- Initial safety-first CSV analytics pipeline.
- Rule-based and optional LLM-assisted parsing.
- Validated `QuerySpec` execution boundary.
- Streamlit application.
- Thirteen automated tests including injection-resistance checks.
- Security, privacy, testing, and MVP documentation.
