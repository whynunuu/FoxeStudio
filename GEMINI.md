# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"** (atau variasi serupa seperti "update data", "sinkronkan data"), Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri dari awal hingga selesai tanpa perlu konfirmasi manual lagi:

### 1. Eksekusi Sinkronisasi Operasional Google Drive (`deep_sync_foxe.py`):
- Unduh & parse data operasional HANYA dari 2 sumber Google Drive resmi (File 3 / Rekap Global DI-SKIP):
  * **File 1 (Log Order `.xlsm`)**: ID `1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ` (transaksi pembayaran, akumulasi total shift aktual kru, kas harian, funnel leads marketing & KPI harian).
  * **File 2 (Schedule `.xlsx`)**: ID `14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I` (jadwal booking Studio 1, 2, 3 dan deteksi jadwal foto besok H+1).
- **Roster Shift:** Hitung akumulasi total shift slot aktual dari Log Order s.d. tanggal sekarang/cut-off.
- **ATURAN MUTLAK BIAYA:** Bagian COGS & OPEX (`expenses`) **HARUS SELALU KOSONG (`[]`)** sesuai instruksi pemilik studio.
- Deteksi cut-off dinamis (mengikuti tanggal transaksi aktif terbaru, misal: 20 September 2026).
- Simpan state gabungan ke `foxe_full_state.json`.
- Rakit ulang file visual `index.html` dan salin ke artefak `foxe_studio_keuangan.html`.

### 2. Auto-Commit & Deploy ke GitHub:
- Otomatis commit dan push pembaruan data ke repository:
  `git add foxe_full_state.json index.html file1.xlsm file2.xlsx`
  `git commit -m "Auto-sync data update"`
  `git push origin main`
- Remote URL: `https://github.com/whynunuu/FoxeStudio.git`

### 3. Berikan Laporan Ringkas, Kirim Telegram & Tautan Live:
- Kirim notifikasi otomatis laporan harian closing ke Telegram via `@NunuFxBot` (`telegram_notifier.py`).
- Sajikan tabel ringkasan: Cut-off hari ini, total order MTD, omzet MTD (Cash vs Transfer), omzet hari ini, shift kru, dan capaian target.
- Sertakan link website resmi live:
  👉 **https://whynunuu.github.io/FoxeStudio/**
