# Testing

## Automated Tests

The test suite is located at:

```text
backend/tests/test_api.py
```

Run:

```powershell
C:\Users\Acer\AppData\Local\Programs\Python\Python311\python.exe -m pytest backend\tests
```

Verified result:

```text
26 passed
```

## What Is Covered

- Health endpoint response
- Test generation and persistence
- Blank-prompt automatic test generation
- Multi-case suite generation for detected page functionality
- Persistent URL workspaces and append-only test history
- Session-scoped test and run listing
- Session deletion with related test/run cleanup
- Semantic prompt parsing that separates test data from expected behavior
- Qwen AI intent extraction, plan generation, validation, retry, and selector grounding
- Clear saved tests and run history
- Test listing
- Analytics response shape

## Manual Test Checklist

| Test | Expected Result |
| --- | --- |
| Open `/app` | Workspace interface loads without overflow |
| Create a new URL workspace | Workspace appears in the sidebar |
| Generate test for `https://example.com` | Steps appear and remain saved |
| Add another prompt | Earlier generated tests remain in the workspace |
| Run generated test | Result appears with status and logs |
| Open `/api/analytics` | Counts and pass rate are returned |
| Open `/docs` | FastAPI Swagger UI loads |

## Limitations

The automated test suite avoids real browser execution so it can run reliably in restricted environments. Browser execution is verified manually through the dashboard and Playwright installation.
