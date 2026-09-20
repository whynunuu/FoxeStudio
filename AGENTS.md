# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"**, Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri:
1. Jalankan `python deep_sync_foxe.py` (unduh File 1, 2, 3 dari Google Drive, parse data, cut-off dinamis, COGS & OPEX tetap kosong, simpan `foxe_full_state.json`, rakit `index.html`, dan kirim notifikasi Telegram via `@NunuFxBot`).
2. Jalankan git commit & push ke `origin main` (`https://github.com/whynunuu/FoxeStudio.git`).
3. Tampilkan ringkasan metrik pembaruan hari ini dan tautan website live:
   👉 **https://whynunuu.github.io/FoxeStudio/**
