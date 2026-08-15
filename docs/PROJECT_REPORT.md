# Project Report

## Title

AI-Powered Intelligent Web Test Automation and Analytics Platform

## Abstract

Modern web applications change frequently, which makes continuous testing important. Traditional automation requires testers to manually write scripts, maintain locators, review logs, capture evidence, and prepare reports. This project reduces that manual effort by allowing users to describe a test requirement in natural language. The system converts the requirement into structured test steps, executes them in a browser through Playwright, captures screenshots and logs, stores the execution result, and displays analytics through a simple dashboard.

## Problem Statement

Automated web testing is powerful but difficult for non-programmers because it normally requires coding knowledge, locator maintenance, separate reporting tools, and manual failure analysis. A single platform is needed to combine test generation, browser execution, evidence capture, and result analysis.

## Objectives

- Build a web-based platform for AI-assisted web testing.
- Accept website URLs and natural language testing requirements.
- Generate structured test scenarios.
- Execute workflows automatically using Playwright.
- Capture screenshots, logs, status, and duration.
- Classify results as pass, fail, or warning.
- Store previous runs for review.
- Provide analytics for test execution history.
- Keep the system simple enough for academic demonstration.

## Methodology

The project follows a modular approach:

1. FastAPI handles REST APIs and serves the dashboard.
2. The AI service converts user requirements into executable steps.
3. Playwright executes the steps in Chromium.
4. SQLAlchemy stores test cases and run records in SQLite.
5. The dashboard displays generated steps, run evidence, and analytics.
6. Pytest validates key backend endpoints.

## Implementation Summary

The platform supports actions such as page navigation, text input, button click, key press, title assertion, text assertion, wait, and screenshot capture. If Ollama/Qwen is available, the system uses the model to generate the workflow. If the model is unavailable, a deterministic fallback still creates useful test steps based on the requirement text.

## Result

The completed system can generate a test case, store it, execute it in a real browser, capture evidence, and show analytics. The backend tests pass successfully.

## Future Scope

- PostgreSQL deployment for multi-user use.
- Authentication and role-based access.
- More advanced locator healing.
- CI/CD pipeline integration.
- PDF/HTML test report export.
- Parallel browser execution.
- Visual regression comparison.
