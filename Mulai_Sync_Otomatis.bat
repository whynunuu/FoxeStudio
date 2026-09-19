@echo off
title Foxe Studio - Sync Service Harian (09:00 Pagi)
cd /d "%~dp0"
echo ==========================================================
echo       FOXE STUDIO - SINKRONISASI OTOMATIS HARIAN         
echo ==========================================================
echo Layanan sinkronisasi disetel berjalan setiap hari jam 09:00 pagi.
echo Jendela ini dapat dibiarkan terbuka di latar belakang.
echo Tekan Ctrl+C untuk menghentikan.
echo ==========================================================
echo.
python sync_service.py --daily 09:00
pause
