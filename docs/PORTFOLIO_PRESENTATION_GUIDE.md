# Portfolio Presentation Guide

This guide completes the remaining presentation tasks for the LLM Business Insight Assistant after the code, tests, security checks, and repository foundation are ready.

## Files already available

- `AI_HANDOFF.md` — complete context for another AI assistant.
- `docs/assets/architecture.svg` — architecture visual for the README, portfolio, or case study.
- `docs/assets/social-preview.svg` — source artwork for the GitHub social preview.

## Task 1 — Run the Streamlit application locally

### macOS or Linux

```bash
git clone https://github.com/Meettala/llm-business-insight-assistant.git
cd llm-business-insight-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

### Windows PowerShell

```powershell
git clone https://github.com/Meettala/llm-business-insight-assistant.git
cd llm-business-insight-assistant
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

The bundled sample CSV loads automatically, so no API key is required for the first demo.

## Task 2 — Run with Docker instead

From the repository root:

```bash
docker build -t llm-business-insight-assistant .
docker run --rm -p 8501:8501 llm-business-insight-assistant
```

Open `http://localhost:8501`.

Do not place API keys inside the Dockerfile or image. Supply optional provider keys only at runtime through environment variables.

## Task 3 — Capture a professional screenshot

Use a desktop browser at approximately 1440 × 900 or 1920 × 1080.

1. Open the running Streamlit application.
2. Keep the bundled sample dataset visible.
3. Ask: `What is the total revenue by region?`
4. Wait for the answer, chart, and validated query specification to appear.
5. Collapse unrelated browser panels and remove personal bookmarks or account details from view.
6. Capture the application title, data preview, question, answer, chart, and validation evidence in one clean frame.
7. Save as `docs/assets/app-screenshot.png`.
8. Avoid including API keys, terminal windows, local usernames, private paths, customer data, or browser notifications.

Recommended screenshot names:

- `docs/assets/app-screenshot.png`
- `docs/assets/query-validation.png` for a second technical screenshot

## Task 4 — Record a short demo video or GIF

Recommended length: 30–60 seconds.

Suggested sequence:

1. Show the application title and sample dataset.
2. Ask `What is the total revenue by region?`
3. Show the calculated answer and chart.
4. Open the validated `QuerySpec` section.
5. Briefly show that the operation and columns are constrained.
6. End on the architecture visual or repository README.

Keep the recording focused and silent, or add short captions such as:

- “Plain-English CSV analytics”
- “Validated QuerySpec”
- “Deterministic pandas execution”
- “No eval, exec, or generated SQL”

Suggested output:

- MP4 for LinkedIn and portfolio use
- Optimised GIF for the GitHub README

Keep a GIF reasonably small so the repository loads quickly. Store it as `docs/assets/demo.gif` only after checking its file size and visual quality.

## Task 5 — Add the screenshot or GIF to the README

Add one of these below the project introduction.

Screenshot:

```markdown
![LLM Business Insight Assistant demo](docs/assets/app-screenshot.png)
```

GIF:

```markdown
![LLM Business Insight Assistant workflow](docs/assets/demo.gif)
```

Use real application output only. Do not use a mock screenshot that suggests unimplemented features.

## Task 6 — Prepare the GitHub social preview

GitHub social previews normally work best with a raster image rather than relying on an SVG upload.

Convert:

```text
docs/assets/social-preview.svg
```

to a PNG with a recommended 2:1 aspect ratio, commonly 1280 × 640 pixels.

Save the converted file locally as:

```text
docs/assets/social-preview.png
```

Check that the title remains readable at thumbnail size and that no text touches the edges.

## Task 7 — Set the social preview in GitHub

1. Open the GitHub repository.
2. Select **Settings**.
3. Open **General**.
4. Find **Social preview**.
5. Choose **Edit** or **Upload an image**.
6. Upload `docs/assets/social-preview.png`.
7. Save the change.
8. Share the repository link in a private message to confirm the preview appears correctly.

This setting is stored in GitHub repository settings and cannot be completed by editing a repository file alone.

## Task 8 — Final public-repository check

Before sharing with recruiters, confirm:

- The default branch is `main`.
- GitHub Actions is green.
- The README loads correctly.
- Screenshot and demo media contain no personal or confidential information.
- The MIT licence is visible.
- `AI_HANDOFF.md` contains no secrets.
- Repository description and topics accurately describe the implemented project.
- The social preview is readable.

Suggested repository description:

> Safety-first CSV analytics assistant using validated QuerySpec execution, deterministic pandas operations, Streamlit, automated tests, Ruff, pip-audit, and Docker.

Suggested GitHub topics:

```text
applied-ai
llm
python
pandas
streamlit
data-analytics
prompt-injection
secure-ai
query-validation
docker
```

## Task 9 — Use it in job applications

Suggested CV project entry:

**LLM Business Insight Assistant — Python, pandas, Streamlit, LLM safety**

Built a safety-first analytics assistant that translates plain-English CSV questions into a strictly validated query specification and deterministic pandas operations. Added malformed model-output protection, injection-resistance tests, provider fallback, edge-case handling, Python 3.10–3.12 CI, Ruff, dependency auditing, Docker, and technical documentation.

Suggested interview explanation:

> Instead of letting an LLM generate executable code or unrestricted SQL, I restricted it to a small typed QuerySpec. Application code validates the operation, columns, and schema before a fixed pandas executor runs. This gives up some flexibility but improves auditability, testability, and security.

## Instructions for another AI assistant

When continuing these presentation tasks:

1. Read `AI_HANDOFF.md` first.
2. Verify the current `main` branch and CI status.
3. Do not change the constrained-execution architecture for presentation purposes.
4. Use only real application screenshots and implemented features.
5. Do not expose secrets, local paths, personal notifications, or private data.
6. Update `AI_HANDOFF.md` after adding screenshots, demo media, deployment links, or social-preview changes.
