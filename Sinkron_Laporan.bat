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
git add foxe_full_state.json index.html assemble_app.py logo_foxe.png file1.xlsm file1_okt.xlsm file2.xlsx file_neraca.xlsx file2_okt.xlsx file_wisuda_3okt.xlsx file_wisuda_4okt.xlsx file_wisuda_uin_1sep.xlsx file_wisuda_uin_2sep.xlsx file_wisuda_unsoed_8sep.xlsx file_wisuda_unsoed_9sep.xlsx parser_neraca.py parser_schedule.py parser_log_order.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md VAULT.md
git commit -m "Auto-sync Google Drive update (Log Order, Schedule & Neraca)" 2>nul
git push origin main
echo.
echo [BERHASIL] Website live https://whynunuu.github.io/FoxeStudio/ sudah terupdate!
echo.
echo Mengirim laporan terpisah AI CRM, Leads & Performa CS ke Telegram...
python "c:\Users\ASUS\OneDrive\Documents\General\scripts\telegram_crm_notifier.py"
echo.
timeout /t 5 >nul
