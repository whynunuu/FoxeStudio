# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"**, Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri:
1. Jalankan `python deep_sync_foxe.py` (unduh File 1 Log Order, File 2 Schedule, dan File Neraca dari Google Drive, skip File 3 Rekap Global, hitung total shift aktual kru s.d. hari ini, cut-off dinamis, parse COGS & OPEX serta Buku Detail Neraca Debit/Kredit dari section Detail File Neraca, simpan `foxe_full_state.json`, rakit `index.html`, dan kirim notifikasi Telegram via `@NunuFxBot`).
2. Jalankan git commit & push ke `origin main` (`git add foxe_full_state.json index.html assemble_app.py file1.xlsm file2.xlsx file_neraca.xlsx parser_neraca.py deep_sync_foxe.py telegram_notifier.py`).
3. Tampilkan ringkasan metrik pembaruan hari ini dan tautan website live:
   👉 **https://whynunuu.github.io/FoxeStudio/** (PIN: `202688`)


