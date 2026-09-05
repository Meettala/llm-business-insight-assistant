# Portfolio Media Checklist

Use the recorded Streamlit deployment and non-sensitive synthetic/sample data only after the deployment has passed the current smoke test below.

## Fresh demo smoke test

Recorded candidate:

`https://llm-business-insight-assistant-maubk3puyxkcbnjiad4vnr.streamlit.app/`

Before calling it a current live demo, verify all seven checks:

1. The app loads without a deployment/build error.
2. The bundled sample dataset or a synthetic uploaded CSV loads and the dataset overview is visible.
3. Run one simple aggregation such as `What is the total revenue?` and confirm a grounded numerical result.
4. Run one grouped/ranked question such as `Which region had the highest revenue?` and confirm a ranked result.
5. Ask an unsupported or ambiguous question and confirm it is rejected safely rather than converted into unrestricted code.
6. Expand the validated `QuerySpec`, then confirm the question-and-answer audit and download control are visible.
7. Confirm there is no secret, private data, API key, email address or local path exposed in the UI.

JR02 could not complete this browser smoke from its available execution environment, so the URL remains a recorded/candidate deployment until the owner completes the checklist.

## Required screenshots

1. **Dataset overview**
   - Show row count, column count, missing cells, duplicates and memory.
   - Keep the synthetic/sample file name visible.

2. **Batch question mode**
   - Show several different question types in one batch.
   - Include at least one filtered total, one ranking and one date question.

3. **Verified answer and QuerySpec**
   - Show a correct answer using synthetic/sample data.
   - Expand the validated query specification so reviewers can see the constrained execution design.

4. **Charts and colours**
   - Show the chart-type selector and colour-palette selector.
   - Capture one grouped result using an Office/Excel-style palette.

5. **Audit export**
   - Show the question-and-answer audit table and download control.

## Suggested 45-second demo recording

- 0–5 seconds: project title and dataset overview.
- 5–15 seconds: enter a batch of questions.
- 15–27 seconds: show accurate scalar, ranked and date answers.
- 27–35 seconds: change chart type and colour palette.
- 35–42 seconds: expand the validated `QuerySpec`.
- 42–45 seconds: show the downloadable audit and the dated 49/49 benchmark statement with its scope note.

## Presentation rules

- Do not upload private, employer or customer data.
- Avoid exposing API keys, browser bookmarks, email addresses or local file paths.
- Use 16:9 framing for LinkedIn and portfolio video.
- Use a square or 1.91:1 crop for the GitHub social preview.
- Keep the 49/49 statement paired with the benchmark-specific scope note and 2 August 2026 date.
- Do not imply the screenshot itself reproduces the full 49-question live benchmark.

## Recommended README media order

1. Hero screenshot
2. Short demo GIF or video link
3. Architecture diagram
4. Verified benchmark summary
5. Detailed feature screenshots

## Deployment link status

The Streamlit URL is now recorded in the repository README. Current availability must still be freshly smoke-tested before it is used as the GitHub Website field or described as a presently verified live demo.
