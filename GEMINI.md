# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"** (atau variasi serupa seperti "update data", "sinkronkan data"), Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri dari awal hingga selesai tanpa perlu konfirmasi manual lagi:

### 1. Eksekusi Sinkronisasi Google Drive (`deep_sync_foxe.py`):
- Unduh data terbaru dari 3 sumber Google Drive resmi:
  * **File 1 (Log Order `.xlsm`)**: ID `1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ`
  * **File 2 (Schedule `.xlsx`)**: ID `14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I`
  * **File 3 (Master Kalkulasi `.xlsx`)**: ID `1ttO8updDK1_F1TZFWxQGIDYtI2tvToMg`
- Ekstraksi transaksi harian, shift kru, kontrol kas harian, funnel leads, dan evaluasi 5 pilar KPI.
- Pindai 3 blok studio (Studio 1, 2, 3) di Schedule dengan mempertahankan entri `manual: true` agar tidak pernah tertimpa.
- **ATURAN MUTLAK BIAYA:** Bagian COGS & OPEX (`expenses`) **HARUS SELALU KOSONG (`[]`)** sesuai instruksi pemilik studio.
- Deteksi cut-off dinamis (mengikuti tanggal transaksi aktif terbaru, misal: 20 September 2026).
- Simpan state gabungan ke `foxe_full_state.json`.
- Rakit ulang file visual `index.html` dan salin ke artefak `foxe_studio_keuangan.html`.

### 2. Auto-Commit & Deploy ke GitHub:
- Otomatis commit dan push pembaruan data ke repository:
  `git add foxe_full_state.json index.html file1.xlsm file2.xlsx file3_export.xlsx`
  `git commit -m "Auto-sync data update"`
  `git push origin main`
- Remote URL: `https://github.com/whynunuu/FoxeStudio.git`

### 3. Berikan Laporan Ringkas, Kirim Telegram & Tautan Live:
- Kirim notifikasi otomatis laporan harian closing ke Telegram via `@NunuFxBot` (`telegram_notifier.py`).
- Sajikan tabel ringkasan: Cut-off hari ini, total order MTD, omzet MTD (Cash vs Transfer), omzet hari ini, shift kru, dan capaian target.
- Sertakan link website resmi live:
  👉 **https://whynunuu.github.io/FoxeStudio/**
