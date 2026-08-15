# User Manual

## Start the Application

```powershell
cd backend
C:\Users\Acer\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/app
```

## Create a URL Workspace

1. Click `New test`.
2. Enter a website URL.
3. Enter a requirement for one focused workflow, or leave it blank for an exploratory suite.
4. Click `Generate`.
5. Continue entering requirements to append more tests to the same saved workspace.
6. Select any earlier workspace from the sidebar to restore its tests and run history.

Example requirement:

```text
Check that the home page loads correctly and capture evidence.
```

## Run a Test Case

Click `Run` beside any generated test. The result drawer shows status, summary, screenshots, and logs.

## Understand Results

| Field | Meaning |
| --- | --- |
| Status | Pass, fail, warning, or running |
| Duration | Browser execution time |
| Logs | Step logs, console messages, and errors |
| Screenshots | Evidence captured during execution |

## Troubleshooting

| Issue | Fix |
| --- | --- |
| Playwright warning | Run `python -m playwright install chromium` |
| Ollama unavailable | Start Ollama or use fallback mode |
| Website blocks automation | Try another URL or use a local test page |
| Port already used | Run uvicorn with another port: `--port 8001` |
| Changed to another website | Click `New test` before entering the new URL |
