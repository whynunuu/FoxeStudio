@echo off
title Sinkronisasi Penuh Foxe Studio (Google Drive)
echo =======================================================
echo   SINKRONISASI LENGKAP GOOGLE DRIVE FOXE STUDIO
echo   File 1: Log Order (.xlsm)
echo   File 2: Schedule (.xlsx)
echo   File 3: Master Kalkulasi (.xlsx)
echo =======================================================
echo.
cd /d "%~dp0"
python deep_sync_foxe.py
echo.
echo Selesai! Tekan sembarang tombol untuk keluar...
pause >nul
