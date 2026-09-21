@echo off
title Pasang Jadwal Harian Foxe Studio di Windows
cd /d "%~dp0"
echo ==========================================================
echo    DAFTARKAN JADWAL 09:00 PAGI KE WINDOWS TASK SCHEDULER  
echo ==========================================================
echo.
echo Mendaftarkan task otomatis ke Windows...
schtasks /create /tn "FoxeStudioDailySync" /tr "\"\"%~dp0Sinkron_Laporan.bat\"\"" /sc daily /st 09:00 /f
if %errorlevel% equ 0 (
    echo.
    echo ==========================================================
    echo [BERHASIL] Task Windows 'FoxeStudioDailySync' sudah aktif!
    echo Setiap hari jam 09:00 pagi Windows akan otomatis menjalankan
    echo sinkronisasi meskipun aplikasi Antigravity ditutup total.
    echo ==========================================================
) else (
    echo.
    echo [PERHATIAN] Jika gagal, klik kanan file ini dan pilih 'Run as administrator'.
)
echo.
pause
