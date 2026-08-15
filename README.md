# AI-Powered Intelligent Web Test Automation and Analytics Platform

This project is a beginner-friendly but complete implementation of the abstract topic:

> An AI-driven system for dynamic test generation, automated execution, and failure analysis of web applications.

Users create a saved workspace for a website URL and describe testing requirements in natural language. The system generates structured test steps, runs them with Playwright, captures screenshots and logs, and preserves each workspace's tests and run history in SQLite.

## Features

- Blank-prompt automatic suites for detected major page functionality
- Natural language to structured test steps for specific workflows
- Optional Ollama/Qwen integration for AI-generated workflows
- Rule-based fallback when the local model is unavailable
- Playwright browser execution with screenshots and console logs
- Pass, fail, and warning status tracking
- SQLite persistence using SQLAlchemy
- Chat-style URL workspaces with **New test**, saved history, and session restoration
- Multiple generated prompts and suites preserved inside each URL workspace
- FastAPI backend with interactive Swagger docs
- Static dashboard served at `/app`
- Backend tests with `pytest`
- Complete documentation and viva presentation

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Responsive HTML, CSS, JavaScript application |
| Backend | FastAPI |
| Automation | Playwright |
| Database | SQLite, SQLAlchemy |
| AI | Ollama with Qwen, plus deterministic fallback |
| Testing | Pytest, FastAPI TestClient |

## Project Structure

```text
backend/
  app/
    api/routes_tests.py        API routes for generation, execution, analytics
    core/config.py             Environment settings
    database.py                SQLAlchemy setup
    models.py                  TestSession, TestCase, and TestRun tables
    schemas.py                 Pydantic request/response models
    services/ai_service.py     AI and fallback test generation
    services/executor_service.py Playwright execution
    services/llm_service.py    Ollama helper
    main.py                    FastAPI app entry point
  tests/test_api.py            Backend tests
frontend/dist/index.html       Dashboard UI
docs/                          Project documentation
```

## Setup

Use the Python 3.11 interpreter installed on this machine:

```powershell
C:\Users\Acer\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r backend\requirements.txt
C:\Users\Acer\AppData\Local\Programs\Python\Python311\python.exe -m playwright install chromium
```

Optional local AI model:

```powershell
ollama pull qwen3:8b
ollama serve
```

Copy the environment file if you want to customize settings:

```powershell
Copy-Item backend\.env.example backend\.env
```

## Run

```powershell
cd backend
C:\Users\Acer\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/app
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Test

```powershell
C:\Users\Acer\AppData\Local\Programs\Python\Python311\python.exe -m pytest backend\tests
```

Current verification: `25 passed`.

## Viva Demo Flow

1. Open `/app` and choose **New test**.
2. Enter a URL and a requirement.
3. Generate one focused test, or leave the requirement blank for an exploratory suite.
4. Add more prompts to the same workspace without losing earlier tests.
5. Run any saved test and review status, logs, and screenshots.
6. Switch between saved URL workspaces from the sidebar.

## Main Learning Outcome

The project demonstrates how AI can reduce manual testing effort by converting natural language requirements into executable browser workflows, while still preserving evidence, repeatability, and analytics needed in a real software quality process.
