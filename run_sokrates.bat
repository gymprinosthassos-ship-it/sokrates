@echo off
chcp 65001 >nul
title Σωκράτης AI Tutor Γυμνασίου
echo ===================================================
echo   🏛️  Εκκίνηση: Σωκράτης AI Tutor & Πύλη Εκπαιδευτικού
echo ===================================================
echo.
cd /d "%~dp0"
timeout /t 2 >nul
start http://localhost:8501
if exist "..\..\..\antigravity\scratch\socratic-mentor\.venv\Scripts\python.exe" (
    "..\..\..\antigravity\scratch\socratic-mentor\.venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501
) else (
    streamlit run app.py --server.port 8501
)
pause
