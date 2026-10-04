@echo off
title Foxe Flow - Otomasi Admin Studio
cd /d "%~dp0"

echo ===================================================
echo     FOXE FLOW - STUDIO AUTOMATION ENGINE (n8n)
echo ===================================================
echo Memulai server otomasi lokal di http://localhost:8765 ...
echo.

set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if exist "%CHROME_PATH%" (
    start "" "%CHROME_PATH%" "http://localhost:8765"
) else (
    start chrome "http://localhost:8765" 2>nul || start "" "http://localhost:8765"
)
.\.venv\Scripts\python.exe -m uvicorn foxe_flow.server:app --host 127.0.0.1 --port 8765
pause
