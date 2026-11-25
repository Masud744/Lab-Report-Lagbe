---
title: Lab Report Lagbe
colorFrom: green
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Lab Report Lagbe? — AI Academic Programming Lab Report Workspace

An AI-powered, full-stack academic web workspace for programming lab reports. Enter your course metadata and task descriptions (or write/test your own code in the built-in Code Workspace), attach output screenshots, and compile a publication-grade LaTeX PDF report complete with institutional cover page, methodology, syntax-highlighted code, 2x2 visualization grids, and result discussion.

---

## Key Features

- **Academic Workspace UI**: Clean dashboard with live KPI stats, recent reports table, built-in PDF preview modal, interactive calendar, quick-start templates, activity history, and `Ctrl+K` global search.
- **AI Report Generation**: Generates structured Problem Description, 5-point Methodology, runnable source code (or analyzes your own custom code), and Result & Discussion via Groq API (`qwen/qwen3.8-27b` with automatic model fallback).
- **Interactive Code Workspace**: Write and execute code directly inside the browser (local runtime for Python, C, C++, Java, Dart, JavaScript, Bash, plus Piston/Judge0/AI simulation fallback) and send verified code straight into a new lab report.
- **22 Programming Languages**: Python, C++, C, Java, Dart, JavaScript, TypeScript, SQL, Go, Rust, Kotlin, C#, PHP, Ruby, Swift, R, Bash, MATLAB/Octave, Arduino (C++), Lua, Perl, and Scala.
- **Publication-Grade LaTeX PDF**: Official UFTB crest (with optional custom university logo upload in Settings), TikZ double-border cover page, single-task and multi-task numbering, dual-column code listing for longer files, and 2x2 screenshot figure grids.
- **Lab Sheet Auto-Fill**: Upload a teacher's lab manual PDF, question screenshot (PNG/JPG), or text file to automatically extract course metadata, lab title, language, tasks, and requirements into the form.
- **Review & Edit Studio + Overleaf Export**: Inspect and refine AI-generated Problem Overview, Methodology points, Source Code, Output, Figure Captions, and Discussion before compiling the final PDF, and download an Overleaf-ready `.zip` bundle (`main.tex` + logo + figures) for any report.
- **Self-Healing Code Execution**: Automatically detects compiler or runtime errors during local/sandboxed execution, feeds stderr back to Groq AI to repair the code, and re-executes to verify runnable output.
- **Headless Matplotlib Plot Capture**: Automatically captures Python `matplotlib` charts (`Agg` backend) both in the live Code Workspace and inside Section 4 (Output Visualization) of generated PDFs.
- **Smart Auto-Visualization**: Automatically generates 4-angle wireframe renders for 3D OpenGL cuboid tasks and 2D pixel coordinate grids for DDA / Bresenham / Midpoint Circle tasks when no screenshots are uploaded.
- **Zero-Cost Stack**: Runs completely on free-tier infrastructure (Groq API + local/Docker LaTeX).

---

## Architecture

```
Browser (Emerald Academic Workspace SPA)
       |
       +-- POST /api/execute   ---> CodeRunner (Local / Piston / Judge0 / AI)
       |
       +-- GET  /api/dashboard ---> ReportStorage (JSON metadata + PDF files)
       |
       +-- POST /api/generate  ---> FastAPI Backend (app.py)
                                        |
                                        +--> 1. AIService (Groq API): Overview, Methodology, Code, Discussion
                                        +--> 2. CodeRunner: Live execution or AI terminal simulation
                                        +--> 3. VisualRunner: Uploaded screenshots or 2D/3D auto-renders
                                        +--> 4. LaTeXGenerator (pdflatex): Compiles & persists PDF
```

---

## Project Structure

```
Lab Report Generator/
|-- app.py                      # FastAPI web server and REST API endpoints
|-- services/
|   |-- auth_guard.py           # Firebase ID token verification & sliding-window rate limiter
|   |-- ai_service.py           # Groq API integration, JSON parser, model fallback
|   |-- code_runner.py          # Local runtime, Piston, and Judge0 code execution
|   |-- latex_generator.py      # Jinja2-to-LaTeX renderer, sanitizer, pdflatex builder
|   |-- visual_runner.py        # 3D wireframe and 2D raster auto-visualization renderer
|   `-- storage.py              # Report metadata and activity persistence
|-- templates/
|   `-- report_template.tex     # Master LaTeX academic report template
|-- static/
|   |-- index.html              # Single-page workspace UI
|   |-- css/style.css           # Emerald Academic Workspace design system
|   |-- js/app.js               # Dashboard, report builder, code workspace, drafts, settings
|   `-- images/                 # UFTB seal and application assets
|-- firestore.rules             # Strict owner-isolated Firestore Security Rules
|-- Dockerfile                  # Production Docker image (Hugging Face Spaces ready)
|-- .dockerignore               # Excludes secrets, venv, and local outputs from image
|-- docker-compose.yml          # Local Docker Compose setup with optional Piston container
|-- requirements.txt            # Python dependencies
|-- .env.example                # Sample environment variables
`-- README.md
```

---

## Quick Start (Local Setup)

### 1. Prerequisites

- Python 3.10+
- `pdflatex` installed locally:
  ```bash
  sudo apt update && sudo apt install -y texlive-base texlive-latex-extra texlive-fonts-recommended
  ```
- A free Groq API key from [console.groq.com/keys](https://console.groq.com/keys)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/Masud744/Lab-Report-Lagbe-.git
cd Lab-Report-Lagbe-

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set GROQ_API_KEY
```

### 3. Run the Server

```bash
uvicorn app:app --reload --port 7860
```

Open [http://localhost:7860](http://localhost:7860) in your browser.

---

## Docker Setup

### Option A: Standalone Docker

```bash
docker build -t lab-report-lagbe .
docker run -p 7860:7860 --env-file .env lab-report-lagbe
```

### Option B: Docker Compose (with local Piston runner)

```bash
docker compose up --build
```

Note: When deploying publicly, set `ENABLE_LOCAL_RUNNER=false` in your environment so untrusted user code runs only in sandboxed Piston/Judge0 or AI simulation mode.

---

## Cloud Deployment (Hugging Face Spaces)

1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces) with **Docker** as the SDK (CPU basic - 16 GB RAM free tier).
2. Push this repository to your Space:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/<your-space-name>
   git push space main
   ```
3. In Space **Settings -> Variables and secrets**, configure:
   - **Secret** `GROQ_API_KEY`: Your Groq API key
   - **Variables** (from `.env`):
     - `FIREBASE_API_KEY`
     - `FIREBASE_AUTH_DOMAIN`
     - `FIREBASE_PROJECT_ID` (`lab-report-lagbe`)
     - `FIREBASE_STORAGE_BUCKET`
     - `FIREBASE_MESSAGING_SENDER_ID`
     - `FIREBASE_APP_ID`
     - `FIREBASE_MEASUREMENT_ID`
     - `ENABLE_LOCAL_RUNNER`: `true` (safe sandboxed env; or `false` to route code to external Piston/AI simulation)
4. In Firebase Console -> **Authentication -> Settings -> Authorized domains**, add your Space hostname (for example `<your-username>-<your-space-name>.hf.space`) so Google Sign-In works on the live URL.
5. Hugging Face Spaces builds the `Dockerfile` automatically and serves the application on port `7860`. Note that local files in `output/` and `data/` reset when the Space rebuilds or sleeps, while user profiles, drafts, and metadata stay persisted in Firestore.

---

## License

MIT License. Designed and maintained by Shahriar Alom Masud.
