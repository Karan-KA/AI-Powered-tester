# Viva Questions and Answers

## What is the main problem solved by this project?

The project reduces manual effort in web testing by converting natural language requirements into executable browser test workflows and preserving execution evidence.

## Why did you use Playwright?

Playwright supports modern browser automation, screenshots, locators, keyboard actions, and headless execution. It is suitable for testing dynamic web applications.

## What is the role of AI?

AI interprets the user requirement and creates structured test steps. The system can use Ollama/Qwen, and it also has a fallback planner when the model is unavailable.

## Why SQLite instead of PostgreSQL?

SQLite keeps the academic demo simple. The code uses SQLAlchemy, so PostgreSQL can be used later by changing the database URL.

## How are failures handled?

If a required step fails, the run status becomes `failed`, the error is saved, and logs are shown. Optional generated selectors can produce warnings instead of stopping the whole run.

## What evidence is captured?

The system captures step logs, browser console messages, duration, status, errors, and screenshots.

## What are the limitations?

The current system is single-user, uses simple locator strategies, and does not yet support CI/CD integration, visual regression, or parallel execution.

## What is the future scope?

Future work includes PostgreSQL deployment, authentication, locator healing, CI/CD integration, PDF reports, visual comparison, and parallel execution.
