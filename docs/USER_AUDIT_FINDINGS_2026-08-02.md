# User audit findings — 2 August 2026

Three exported application-audit CSV files were compared with the project owner's trusted answers for `narrow_sample.csv`, `wide_sample.csv`, and `long_sample.csv`.

## Observed accuracy

### Narrow sample

- Correct: total revenue, average revenue, row count.
- Numerically partial: highest and lowest revenue values were correct, but the associated region and date were omitted.
- Incorrect: four region-filtered totals, North count, South average, distinct region list, and date range.

Primary cause: filter values such as North/South/East/West were not converted into validated filters. Distinct values and date-range operations do not exist in the current QuerySpec.

### Wide sample

- Correct: total revenue and total units sold.
- Incorrect or incomplete: 18 of 20 audited questions.

Examples:

- `Average unit price?` selected `units_sold` instead of `unit_price`.
- `Revenue by category — Electronics?` used grouped row count instead of revenue sum filtered to Electronics.
- `Wholesale (lowest)` used the minimum individual transaction inside each channel rather than total revenue by channel.
- returned-order count ignored the returned flag and counted all 200 rows.
- sales-rep highest/lowest questions calculated a single transaction maximum/minimum instead of grouped revenue totals.
- gross profit, margin, lead time, segment and product rankings selected unrelated fallback operations or columns.

Primary causes: weak column matching, no explicit aggregation intent for grouped questions, no conditional count, no ranking over grouped aggregates, and no calculated-field/percentage support.

### Long sample

- Correct: total revenue and average revenue per row.
- Incorrect: units questions, region/product grouped totals, year filters, year row count, highest month, transaction extrema in the supplied audit, and the combined North + Gadget X filter.
- The supplied long audit contains 15 rows rather than all 16 trusted questions; `Revenue by product — Gadget X (highest)?` was absent from the exported audit.

Primary causes: no multiple filters, no date-period filter, no grouped-sum ranking, and weak value-column matching (`units_sold` questions fell back to `revenue`).

## System-level diagnosis

The executor safely executes the QuerySpec it receives, but safety validation does not prove semantic correctness. Most wrong answers originate in parsing and intent representation:

1. filter values are often omitted;
2. the parser falls back to the first numeric column;
3. `by <dimension>` may be interpreted as count rather than sum;
4. `highest` and `lowest` may select row-level extrema instead of ranked grouped totals;
5. the QuerySpec lacks distinct-values, date-range, multiple-filter, derived-measure, ratio, conditional-count and top/bottom aggregate operations;
6. explanations confidently describe the executed operation even when it does not match the user's question.

## Immediate UI changes in this branch

- remove the repeated yellow unverified warning from every answer;
- show one concise unverified-answer notice above the question area;
- add `Start a fresh audit for each run`, enabled by default;
- preserve an optional accumulated-history workflow;
- add user-selected chart type and colour palette controls;
- support bar, horizontal bar, line, area, scatter, pie and donut charts where appropriate;
- use fixed Office/Excel-style and other safe colour palettes;
- keep scalar answers as scalar values rather than forcing misleading charts.

## Required next accuracy PR

The next feature branch must extend QuerySpec and tests without introducing generated code. It should add:

- exact and normalised column/value matching;
- multiple typed filters;
- grouped aggregation plus top/bottom ranking;
- distinct values;
- date minimum/maximum and date-period filters;
- conditional counts and percentages;
- validated derived measures such as net revenue and gross profit;
- ratio operations such as profit margin;
- benchmark evaluation that compares all trusted expected answers with tolerances and reports pass/partial/fail.

No claim of broad question accuracy should be made until that benchmark is green.