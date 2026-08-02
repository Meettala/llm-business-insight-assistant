# Live Accuracy Validation — 2 August 2026

## Result

The deployed LLM Business Insight Assistant was retested after the schema-aware accuracy-engine release using the owner's original three benchmark CSV files.

| Dataset | Questions | Passed | Failed | Accuracy |
|---|---:|---:|---:|---:|
| `narrow_sample.csv` | 13 | 13 | 0 | 100% |
| `wide_sample.csv` | 20 | 20 | 0 | 100% |
| `long_sample.csv` | 16 | 16 | 0 | 100% |
| **Overall** | **49** | **49** | **0** | **100%** |

All exported audit rows used the deterministic rule-based parser and completed successfully. The returned answers matched the owner-approved expected values for totals, averages, counts, category filters, multiple filters, grouped rankings, date ranges, yearly and monthly analysis, conditional percentages, row context and validated derived business measures.

## Evidence reviewed

Three post-update question-and-answer audit CSV exports were compared with `data/validation/approved_question_answer_benchmark.csv` and the owner's approved narrow-dataset answers.

The verification checked:

- final answer values;
- operation selected;
- value and grouping columns;
- categorical and year filters;
- ranking direction;
- date granularity;
- derived-measure selection;
- successful execution status.

## What this result proves

This result confirms that the deployed application answered all 49 approved questions correctly for the three benchmark datasets used during live validation.

## What this result does not prove

It is not a claim of universal accuracy for every possible CSV schema, vocabulary, formula or business question. The parser may still reject unfamiliar or ambiguous requests rather than guess. Joins, arbitrary formulas, forecasting, unrestricted SQL and generated code remain outside the supported safety boundary.

## Related engineering validation

Before merge, the accuracy-engine branch passed:

- 85 focused local tests;
- GitHub Actions CI run #56;
- Python 3.10, 3.11 and 3.12 tests;
- Ruff source and test checks;
- dependency auditing.

Accuracy-engine PR #8 was merged as commit `031a27cd9f6fdf655371ffff9edc2e0f6033f1ad`.
