# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"**, Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri:
1. Jalankan `python deep_sync_foxe.py` (unduh File 1 Log Order & File 2 Schedule dari Google Drive, skip File 3, hitung total shift aktual kru s.d. hari ini, cut-off dinamis, COGS & OPEX tetap kosong, simpan `foxe_full_state.json`, rakit `index.html`, dan kirim notifikasi Telegram via `@NunuFxBot`).
2. Jalankan git commit & push ke `origin main` (`git add foxe_full_state.json index.html file1.xlsm file2.xlsx`).
3. Tampilkan ringkasan metrik pembaruan hari ini dan tautan website live:
   👉 **https://whynunuu.github.io/FoxeStudio/**
