# Security Policy

## Supported versions

Security fixes are currently applied to the latest version on the `main` branch.

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability.

Send a private report to the repository owner through GitHub with:

- a clear description of the issue
- affected files or components
- reproduction steps or a minimal proof of concept
- expected and observed behavior
- potential impact
- any suggested mitigation

Do not include real confidential datasets, API keys, access tokens, or personal information in a report.

## Security model

The central security property of this project is constrained execution. Natural-language input may propose a candidate query, but application code validates that query against a fixed operation whitelist and the uploaded dataset schema before deterministic execution.

The project intentionally avoids:

- `eval` and `exec`
- dynamically generated Python execution
- dynamically generated SQL execution
- unrestricted pandas expression evaluation
- treating dataset cell contents as instructions

## Scope and limitations

This repository demonstrates a safety-oriented architecture, but users deploying it are responsible for environment hardening, authentication, authorization, dependency management, provider configuration, data retention, and compliance requirements.
