# API Reference

Base URL:

```text
http://127.0.0.1:8000
```

## Health

```http
GET /api/health
```

Returns backend status and Ollama availability.

## Sessions

```http
POST /api/sessions
GET /api/sessions
PATCH /api/sessions/{session_id}
DELETE /api/sessions/{session_id}
```

A session is a saved URL workspace containing generated tests and run history.

## Generate Test

```http
POST /api/tests/generate
```

Request:

```json
{
  "target_url": "https://example.com",
  "requirement": "Check that the home page loads correctly and capture evidence.",
  "session_id": 1
}
```

Response includes saved test case id, generated steps, and expected result.

## List Tests

```http
GET /api/tests?session_id=1
```

Returns all saved test cases, newest first.

## Get Test

```http
GET /api/tests/{case_id}
```

Returns one test case.

## Run Test

```http
POST /api/runs
```

Request:

```json
{
  "test_case_id": 1
}
```

Response includes status, duration, logs, screenshots, and error summary.

## List Runs

```http
GET /api/runs?session_id=1
```

Returns all previous runs.

## Analytics

```http
GET /api/analytics
```

Returns total cases, total runs, pass rate, failures, warnings, average duration, and recent runs.
