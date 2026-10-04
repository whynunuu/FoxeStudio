@echo off
setlocal
echo =======================================================
echo    Foxe Studio - Quota 5 Jam FULL Telegram Notifier
echo =======================================================
echo.
echo Pilihan:
echo  [1] Pasang Timer 5 Jam Penuh (Ketik: 5h)
echo  [2] Masukkan Target Jam Reset (Contoh: 20:22)
echo  [3] Masukkan Menit Tertentu (Contoh: 45)
echo.
set /p PILIHAN="Masukkan pilihan / waktu reset [Default: 5h]: "
if "%PILIHAN%"=="" set PILIHAN=5h
if "%PILIHAN%"=="1" set PILIHAN=5h

echo.
echo Menjalankan timer notifikasi ke Telegram (@NunuFxBot)...
python quota_notifier.py %PILIHAN%
pause
