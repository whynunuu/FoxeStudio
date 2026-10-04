@echo off
setlocal
echo =======================================================
echo    Foxe Studio - Quota Reset Telegram Notifier
echo =======================================================
echo.
set /p MENIT="Masukkan estimasi waktu reset (misal: 45 atau 16:30): "
if "%MENIT%"=="" set MENIT=45
echo.
echo Menjalankan timer notifikasi ke Telegram (@NunuFxBot)...
python quota_notifier.py %MENIT%
pause
