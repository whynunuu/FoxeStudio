@echo off
title Jadikan Google Chrome Sebagai Browser Default
echo =======================================================
echo    MENGATUR GOOGLE CHROME SEBAGAI DEFAULT BROWSER
echo =======================================================
echo.
set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if exist "%CHROME_PATH%" (
    echo Mengirim perintah ke Google Chrome...
    start "" "%CHROME_PATH%" --make-default-browser
)

echo Membuka pengaturan Default Apps Windows...
start ms-settings:defaultapps

echo.
echo =======================================================
echo [PETUNJUK]:
echo Pada jendela Pengaturan Windows yang terbuka:
echo 1. Pilih "Google Chrome"
echo 2. Klik tombol "Set default" / "Jadikan default"
echo =======================================================
timeout /t 5 >nul
exit
