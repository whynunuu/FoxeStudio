# Rule: "ayo kerja" Command Pipeline

Whenever the user prompts "ayo kerja", immediately execute the full synchronization and cloud deployment pipeline for Foxe Studio:
1. Run `python deep_sync_foxe.py` (includes auto-dispatching Telegram notification via `@NunuFxBot`)
2. Run `git add foxe_full_state.json index.html file1.xlsm file2.xlsx file3_export.xlsx && git commit -m "Auto-sync update" && git push origin main`
3. Print summary of changes (cutoff, MTD omzet, daily omzet, cash vs transfer, shifts)
4. Provide the live link: https://whynunuu.github.io/FoxeStudio/
