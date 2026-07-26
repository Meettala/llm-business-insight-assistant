# Contributing

Thank you for considering a contribution.

## Development setup

```bash
git clone https://github.com/Meettala/llm-business-insight-assistant.git
cd llm-business-insight-assistant
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest
```

Run the tests before making changes:

```bash
python -m pytest tests/ -q
```

## Contribution principles

Changes must preserve the project's constrained-execution security model.

- Do not introduce `eval`, `exec`, unrestricted SQL generation, or dynamic pandas expression execution.
- Route every analytical request through a validated `QuerySpec`.
- Add or update tests for behavioral and security changes.
- Keep user-facing claims supported by the implementation.
- Never commit API keys, private datasets, credentials, or personal information.

## Pull requests

Keep pull requests focused and include:

- what changed
- why it changed
- security or compatibility implications
- tests performed
- screenshots for user-interface changes

## Bug reports

Include reproduction steps, sample input that contains no confidential data, expected behavior, observed behavior, and environment information.

## Feature proposals

Explain the user problem, proposed behavior, alternatives considered, and how the change preserves validation and deterministic execution.
