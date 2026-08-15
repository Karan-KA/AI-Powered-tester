@echo off
cd /d "C:\Users\Acer\OneDrive\Documents\Jira-agent-AI\backend"
"C:\Users\Acer\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
