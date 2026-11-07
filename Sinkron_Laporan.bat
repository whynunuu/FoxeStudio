@echo off
title Sinkronisasi Penuh Foxe Studio (Google Drive & Cloud Deploy)
echo =======================================================
echo   SINKRONISASI OPERASIONAL FOXE STUDIO
echo   File 1: Log Order (.xlsm)
echo   File 2: Schedule (.xlsx)
echo   File Neraca: Keuangan (.xlsx)
echo =======================================================
echo.
cd /d "%~dp0"
python deep_sync_foxe.py
echo.
echo Mengunggah pembaruan ke live website GitHub...
git add -u
git add file*.xlsm file*.xlsx foxe_full_state.json foxe_full_state.json.bak index.html assemble_app.py logo_foxe.png leads_vault.json parser_*.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md VAULT.md
git commit -m "Auto-sync Google Drive update (Log Order, Schedule & Neraca)" 2>nul
git push origin main
echo.
echo [BERHASIL] Website live https://whynunuu.github.io/FoxeStudio/ sudah terupdate!
echo.
echo Mengirim laporan terpisah AI CRM, Leads & Performa CS ke Telegram...
python "c:\Users\ASUS\OneDrive\Documents\General\scripts\telegram_crm_notifier.py"
echo.
timeout /t 5 >nul
