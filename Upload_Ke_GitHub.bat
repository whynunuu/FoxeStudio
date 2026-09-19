@echo off
title Foxe Studio - Hubungkan ke GitHub
cd /d "%~dp0"
echo ==========================================================
echo       FOXE STUDIO - UPLOAD KE GITHUB (CLOUD SETUP)        
echo ==========================================================
echo.
echo Langkah mudah:
echo 1. Buka browser: https://github.com/new
echo 2. Buat repository baru (bisa Private atau Public)
echo    Contoh nama: foxe-studio-keuangan
echo 3. Salin URL HTTPS repository tersebut.
echo.
echo ==========================================================
set /p REPO_URL="Masukkan URL Repository GitHub Anda: "

if "%REPO_URL%"=="" (
    echo [ERROR] URL tidak boleh kosong.
    pause
    exit /b
)

echo.
echo Menghubungkan ke: %REPO_URL% ...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo Mengunggah file ke GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ==========================================================
    echo [BERHASIL] Repository sudah terhubung ke GitHub!
    echo GitHub Actions akan otomatis aktif dan menjalankan
    echo sinkronisasi setiap hari jam 09:00 pagi di cloud GitHub.
    echo ==========================================================
) else (
    echo.
    echo [PERHATIAN] Upload memerlukan autentikasi login GitHub.
    echo Silakan login pada jendela browser / credential manager yang muncul.
)
echo.
pause
