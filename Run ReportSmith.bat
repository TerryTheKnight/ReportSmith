@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ReportSmith's Python environment was not found.
    echo Please follow the one-time setup steps in README.md first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m streamlit run app.py
pause
