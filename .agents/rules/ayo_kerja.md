# Rule: "ayo kerja" Command Pipeline

Whenever the user prompts "ayo kerja" (or "update data", "sinkronkan data"), immediately execute the full synchronization and cloud deployment pipeline for Foxe Studio:
1. Run `python deep_sync_foxe.py`:
   - Downloads File 1 Log Order, File 2 Schedule, and File Neraca (skips File 3).
   - Computes dynamic cut-off, daily omzet, roster shifts, COGS/OPEX from Neraca Detail.
   - Updates `foxe_full_state.json`, compiles `index.html`, and sends receipt notification to Telegram via `@NunuFxBot`.
2. Run git commit & push:
   `git add foxe_full_state.json index.html assemble_app.py file1.xlsm file2.xlsx file_neraca.xlsx parser_neraca.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md VAULT.md`
   `git commit -m "Auto-sync data update"`
   `git push origin main`
3. Print summary of changes (cutoff, MTD omzet, daily omzet, cash vs transfer, shifts).
4. Provide the live link: 👉 https://whynunuu.github.io/FoxeStudio/ (PIN: `363636`)
