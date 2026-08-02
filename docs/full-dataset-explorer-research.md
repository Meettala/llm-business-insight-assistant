# Full-Dataset Explorer Research and Design

Last updated: 2 August 2026

## User requirement

The assistant must accept CSV files with changing schemas and make every uploaded row and column available for inspection and analysis. It must not silently analyse only a fixed preview such as `df.head(10)`.

The interface may paginate or virtualise the table to protect browser performance, but pagination must never reduce the dataframe passed to the analytical pipeline.

## Comparable product findings

### ChatGPT Data Analysis

Official OpenAI documentation describes CSV and spreadsheet analysis, interactive tables, row-and-column inspection, calculations, transformations, charts, and Python-backed analysis. Its table interface can be expanded and scrolled while analysis operates on the uploaded file rather than only the visible screen area.

Sources:

- https://help.openai.com/en/articles/8437071-advanced-data-analysis-chatgpt
- https://help.openai.com/en/articles/9213685-extracting-insights-with-chatgpt-data-analysis
- https://openai.com/academy/data-analysis/

### Julius AI

Julius provides natural-language data questions, cleaning, sorting, visualisations, statistical modelling, reports, and CSV/Excel export. Its Data Explorer uses a paginated interactive dataframe: the UI shows a limited page at a time while users can navigate through all rows. Julius documents support for CSV, Excel, JSON, Parquet, Feather, SQLite and SPSS, plus multi-tab spreadsheets and connected databases or warehouses.

Sources:

- https://julius.ai/features
- https://julius.ai/docs/data-explorer
- https://julius.ai/docs/get-started/files
- https://julius.ai/docs/faqs

### Hex

Hex combines natural-language questions with spreadsheet-style exploration, filters, pivots, drill-downs, visualisations, notebooks, SQL, Python, collaboration and governed semantic definitions. Its design separates data access and computation from the currently visible result view.

Sources:

- https://hex.tech/product/explore/
- https://hex.tech/capability/ai/

### PandasAI

PandasAI supports natural-language analysis of one or multiple dataframes and can return dataframe, chart and analytical outputs. Its multi-dataframe interface reinforces the need for schema-independent ingestion and explicit dataframe context rather than fixed columns.

Sources:

- https://docs.pandas-ai.com/v3/chat-and-output
- https://docs.pandas-ai.com/v2/library

## Product principles derived from the research

1. **Complete-data analysis** — the analytical pipeline receives the complete loaded dataframe.
2. **Responsive viewing** — large tables are paginated or virtualised instead of sending every cell to the browser at once.
3. **Dynamic schemas** — column controls and schema summaries are generated from the uploaded file.
4. **Transparent scope** — the UI states whether a result uses the complete dataset, a filter or a sample.
5. **Visible metadata** — show total rows, total columns, missing cells, duplicate rows and memory size.
6. **Column inspection** — expose inferred types, pandas dtypes, missing counts and unique-value counts.
7. **Safety boundary remains intact** — table flexibility must not introduce generated Python, SQL, `eval`, `exec` or unrestricted model-produced operations.
8. **Graceful scaling** — future versions should support chunked loading, DuckDB/Polars or warehouse connectors when a CSV no longer fits safely in memory.

## Implemented in this change

- Removed the fixed ten-row preview.
- Added total row and column metrics based on the complete dataframe.
- Added paginated navigation with selectable page sizes.
- Kept every uploaded column selected by default.
- Added optional display-column selection without changing analysis scope.
- Added a schema explorer for every column.
- Added explicit UI wording that answers use the complete dataframe.
- Added reusable dataset-profile and pagination helpers.
- Added regression tests proving every row remains reachable across pages.

## Important limitation

The current loader still uses pandas and loads the full CSV into application memory. This is appropriate for moderate datasets, but it is not an unlimited-size architecture. Very large files can exceed the memory available to Streamlit or its hosting platform.

The interface must not claim unlimited file size. The truthful guarantee is:

> No application-level row or column truncation is applied after a CSV is successfully loaded. Every loaded row and column is available to the analytical pipeline, and every row is reachable through the paginated data explorer.

## Future production improvements

- configurable upload-size and memory safeguards;
- delimiter, encoding and malformed-row diagnostics;
- chunked ingestion and row-count progress;
- DuckDB or Polars-backed querying for larger-than-memory workflows;
- server-side filtering, sorting and pagination;
- search across selected columns;
- CSV, Excel, JSON and Parquet support;
- multiple datasets and validated joins;
- dataset persistence with privacy controls;
- downloadable filtered and transformed results;
- accessibility and keyboard-navigation testing;
- performance tests at increasing row and column counts.
