# v0.2.0 — Verified Accuracy Engine

These are the prepared release notes for the repository's **0.2.0 code/package version**. As of 5 September 2026, no formal GitHub `v0.2.0` Release has been published; do not treat this file as proof that a GitHub Release exists.

## Recorded Streamlit deployment

https://llm-business-insight-assistant-maubk3puyxkcbnjiad4vnr.streamlit.app/

The deployed application was successfully used for the 2 August 2026 live benchmark. JR02 could not freshly reach Streamlit from the available execution environment, so current deployment health remains to be re-verified before the URL is added to the repository Website field.

## Highlights

- 49/49 approved live benchmark questions passed across narrow, wide and 12,000-row CSV datasets on 2 August 2026.
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

Every question still resolves to a validated `QuerySpec` before execution. The 0.2.0 code does not introduce generated Python, unrestricted SQL, `eval`, `exec` or direct execution of provider output.

## Historical validation — 2 August 2026

- 85 focused local tests passed before merge.
- GitHub Actions CI run #56 passed.
- Python 3.10, 3.11 and 3.12 passed.
- Ruff source and test checks passed.
- Dependency audit passed.
- Live post-deployment audit confirmed 49/49 approved answers.

The approved expected-answer benchmark is committed at `data/validation/approved_question_answer_benchmark.csv`, but the three original raw benchmark CSV files are not public repository assets. Therefore the exact historical 49-question live run cannot be reproduced from the repository alone.

## Scope

The 49/49 result applies to the approved benchmark questions and datasets used in the dated live validation. It is not a guarantee for every possible schema, vocabulary or analytical request. Ambiguous or unsupported requests should be rejected rather than guessed.

## Merge references

Accuracy-engine PR #8 merged as `031a27cd9f6fdf655371ffff9edc2e0f6033f1ad`.
Verified release-documentation PR #10 merged as `f290f53a46d60e221c0828869ed73270dff16fad`.

## Publishing the formal GitHub Release

After JR02 is merged and the final `main` CI is green:

1. Open the repository's **Releases** page.
2. Choose **Draft a new release**.
3. Create tag `v0.2.0` from the verified JR02 `main` commit.
4. Set the title to `v0.2.0 — Verified Accuracy Engine`.
5. Use this document as the release body, preserving the dated benchmark scope and current demo qualification.
6. Review the tag target and text, then publish.
