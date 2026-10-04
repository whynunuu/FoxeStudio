@echo off
title Foxe Studio - Live Website di Chrome
echo Membuka Foxe Studio Live di Google Chrome...

set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if exist "%CHROME_PATH%" (
    start "" "%CHROME_PATH%" "https://whynunuu.github.io/FoxeStudio/"
) else (
    start chrome "https://whynunuu.github.io/FoxeStudio/" 2>nul || start "" "https://whynunuu.github.io/FoxeStudio/"
)
exit
