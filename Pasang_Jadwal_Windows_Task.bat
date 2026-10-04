@echo off
title Pasang Jadwal Harian Foxe Studio di Windows
cd /d "%~dp0"
echo ==========================================================
echo    DAFTARKAN JADWAL 08:30 PAGI KE WINDOWS TASK SCHEDULER  
echo ==========================================================
echo.
echo Mendaftarkan task otomatis ke Windows...
schtasks /create /tn "FoxeStudioDailySync" /tr "\"\"%~dp0Sinkron_Laporan.bat\"\"" /sc daily /st 08:30 /f
if %errorlevel% equ 0 (
    echo.
    echo ==========================================================
    echo [BERHASIL] Task Windows 'FoxeStudioDailySync' sudah aktif!
    echo Setiap hari jam 08:30 pagi Windows akan otomatis menjalankan
    echo sinkronisasi sebelum studio buka.
    echo ==========================================================
) else (
    echo.
    echo [PERHATIAN] Jika gagal, klik kanan file ini dan pilih 'Run as administrator'.
)
echo.
pause
