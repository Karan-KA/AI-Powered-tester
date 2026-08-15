# Architecture

## System Overview

```text
User Dashboard
  -> FastAPI REST API
    -> Saved URL Workspaces
      -> Multiple generated test cases
      -> Per-workspace execution history
    -> AI Test Generator
      -> Ollama/Qwen when available
      -> Rule-based fallback when unavailable
    -> Playwright Executor
      -> Chromium browser automation
      -> Screenshots, console logs, errors
    -> SQLite Database
      -> Test cases
      -> Test runs
      -> Analytics
```

## Major Modules

| Module | Responsibility |
| --- | --- |
| `frontend/dist/index.html` | Workspace UI for saved URL sessions, generation, execution, and evidence |
| `backend/app/main.py` | Creates the FastAPI app, serves frontend, mounts artifacts, initializes DB |
| `backend/app/api/routes_tests.py` | REST endpoints for health, test cases, runs, and analytics |
| `backend/app/services/ai_service.py` | Converts natural language requirements into structured test steps |
| `backend/app/services/executor_service.py` | Executes generated steps using Playwright and stores evidence |
| `backend/app/services/llm_service.py` | Optional Ollama/Qwen communication |
| `backend/app/models.py` | SQLAlchemy models for sessions, test cases, and runs |

## Data Flow

1. User creates or opens a saved URL workspace.
2. User enters a requirement; blank input requests an exploratory suite.
3. Qwen interprets and plans the workflow using a strict JSON schema.
4. The backend validates actions, selectors, assertions, literal test data, and evidence steps.
5. Invalid AI plans fall back to deterministic site-aware generation.
6. Generated test cases are appended to the workspace instead of replacing history.
7. Playwright executes a selected case and saves logs, screenshots, duration, and status.
8. The workspace can be reopened later with its complete test and run history.

## Consistency Strategy

- Qwen output must match a strict structured schema.
- Only supported Playwright actions are accepted.
- Interactive plans require navigation, interaction, assertions, and evidence.
- Detected page selectors repair common model-generated selector mistakes.
- A failed AI validation uses deterministic generation rather than a looser second AI attempt.
- Hidden Qwen thinking tags are removed before output is consumed.

## Status Logic

| Status | Meaning |
| --- | --- |
| `passed` | All required steps completed successfully |
| `failed` | A required step failed |
| `warning` | The run completed with optional missing UI elements or missing runtime dependency |
| `running` | Temporary state while execution is in progress |

## Design Decision: SQLite First

The abstract mentions PostgreSQL, but SQLite is used in this implementation to keep setup simple for evaluation and viva. The SQLAlchemy layer keeps the application portable, so the database can be moved to PostgreSQL later by changing `DATABASE_URL`.
