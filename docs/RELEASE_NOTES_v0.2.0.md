# v0.2.0 — Verified Accuracy Engine

## Highlights

- 49/49 approved live benchmark questions passed across narrow, wide and 12,000-row CSV datasets.
- Schema-aware deterministic parsing replaces first-numeric-column guessing.
- Multiple simultaneous filters.
- Highest/lowest grouped rankings.
- Distinct values and date ranges.
- Year filters plus month/year grouping.
- Returned-order counts with percentages.
- Row context for minimum and maximum transactions.
- Application-controlled net revenue, gross profit and profit-margin calculations.
- Single-question and batch-question workflows.
- Full-dataset explorer and downloadable answer audit.
- User-selected charts and Office/Excel-style colour palettes.

## Safety

Every question still resolves to a validated `QuerySpec` before execution. The release does not introduce generated Python, unrestricted SQL, `eval`, `exec` or direct execution of provider output.

## Validation

- 85 focused local tests passed before merge.
- GitHub Actions CI run #56 passed.
- Python 3.10, 3.11 and 3.12 passed.
- Ruff source and test checks passed.
- Dependency audit passed.
- Live post-deployment audit confirmed 49/49 approved answers.

## Scope

The 49/49 result applies to the approved benchmark questions and datasets. It is not a guarantee for every possible schema, vocabulary or analytical request. Ambiguous or unsupported requests should be rejected rather than guessed.

## Merge reference

Accuracy-engine PR #8 merged as `031a27cd9f6fdf655371ffff9edc2e0f6033f1ad`.
