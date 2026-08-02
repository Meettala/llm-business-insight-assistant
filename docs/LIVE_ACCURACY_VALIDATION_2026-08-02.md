# Live Accuracy Validation — 2 August 2026

## Result

The deployed Streamlit application was retested after the schema-aware accuracy engine from PR #8 was merged and redeployed.

**Confirmed result: 49 of 49 approved benchmark questions matched the owner-provided trusted answers.**

| Dataset | Questions | Passed | Failed | Accuracy |
|---|---:|---:|---:|---:|
| `narrow_sample.csv` | 13 | 13 | 0 | 100% |
| `wide_sample.csv` | 20 | 20 | 0 | 100% |
| `long_sample.csv` | 16 | 16 | 0 | 100% |
| **Overall** | **49** | **49** | **0** | **100%** |

## Evidence reviewed

The owner exported three post-update question-and-answer audit CSV files from the deployed application. Each audit row contained:

- the exact question;
- the rendered application answer;
- execution status;
- parsing mode;
- validated query specification;
- deterministic result JSON.

The exported answers were compared with the approved benchmark in `data/validation/approved_question_answer_benchmark.csv` and with the 13 approved narrow-dataset answers supplied by the owner.

All 49 rows had status `answered_unverified`, no row was rejected, and no execution or application error was present. The word `unverified` is the application's cautious audit label; this independent comparison verified the answers against the trusted expected values.

## Behaviours confirmed live

The audit evidence confirms correct handling for the tested datasets of:

- totals and averages;
- semantic measure selection such as revenue, unit price, units sold, satisfaction and lead time;
- exact categorical filters;
- multiple simultaneous filters;
- conditional counts and percentages;
- distinct values;
- date ranges and year filters;
- row-level minimum and maximum values with context;
- grouped highest and lowest rankings;
- month ranking;
- net revenue, gross profit and overall profit margin;
- matching-row counts for filtered results.

## Engineering validation

- Accuracy-engine PR: #8 — `Add schema-aware accuracy engine`.
- PR #8 CI run: #56 — passed.
- PR #8 merge commit: `031a27cd9f6fdf655371ffff9edc2e0f6033f1ad`.
- Focused local tests recorded before merge: 85 passed.

## Scope and limitations

This result proves **49/49 accuracy for the approved narrow, wide and long benchmark datasets and questions used in this validation**. It must not be represented as universal accuracy for every CSV schema or every possible natural-language question.

Remaining limits include:

- semantic aliases are broad but cannot cover every domain-specific column name;
- ambiguous questions or formulas may be rejected rather than guessed;
- categorical value matching is intentionally bounded;
- arbitrary formulas, joins, forecasting and unrestricted SQL are not supported;
- pandas and hosting memory limits still apply to uploaded file size.
