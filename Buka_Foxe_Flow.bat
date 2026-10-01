@echo off
title Foxe Flow - Otomasi Admin Studio
cd /d "%~dp0"

echo ===================================================
echo     FOXE FLOW - STUDIO AUTOMATION ENGINE (n8n)
echo ===================================================
echo Memulai server otomasi lokal di http://localhost:8765 ...
echo.

start "" "http://localhost:8765"
.\.venv\Scripts\python.exe -m uvicorn foxe_flow.server:app --host 127.0.0.1 --port 8765
pause
