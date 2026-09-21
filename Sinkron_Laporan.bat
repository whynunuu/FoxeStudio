@echo off
title Sinkronisasi Penuh Foxe Studio (Google Drive & Cloud Deploy)
echo =======================================================
echo   SINKRONISASI OPERASIONAL FOXE STUDIO
echo   File 1: Log Order (.xlsm)
echo   File 2: Schedule (.xlsx)
echo   File Neraca: Keuangan (.xlsx)
echo =======================================================
echo.
cd /d "%~dp0"
python deep_sync_foxe.py
echo.
echo Mengunggah pembaruan ke live website GitHub...
git add foxe_full_state.json index.html assemble_app.py file1.xlsm file2.xlsx file_neraca.xlsx parser_neraca.py deep_sync_foxe.py telegram_notifier.py
git commit -m "Auto-sync Google Drive update (Log Order, Schedule & Neraca)" 2>nul
git push origin main
echo.
echo [BERHASIL] Website live https://whynunuu.github.io/FoxeStudio/ sudah terupdate!
timeout /t 5 >nul
