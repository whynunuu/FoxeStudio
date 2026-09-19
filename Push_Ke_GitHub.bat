@echo off
title Foxe Studio - Upload Otomatis ke GitHub
cd /d "%~dp0"
echo ==========================================================
echo       FOXE STUDIO - UPLOAD KE REPOSITORY GITHUB          
echo ==========================================================
echo Target: https://github.com/whynunuu/FoxeStudio.git
echo.
git remote remove origin 2>nul
git remote add origin https://github.com/whynunuu/FoxeStudio.git
git branch -M main
echo Mengirim data dan sistem cloud ke GitHub...
echo (Jika jendela konfirmasi login muncul di browser, klik 'Sign in with your browser' / 'Authorize')
echo.
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ==========================================================
    echo [BERHASIL] Seluruh file dan sistem Cloud Sync sudah terupload!
    echo ==========================================================
) else (
    echo ==========================================================
    echo [INFO] Terjadi kendala saat upload. Periksa pesan di atas.
    echo ==========================================================
)
echo.
echo Tekan tombol apa saja untuk menutup jendela ini...
pause
