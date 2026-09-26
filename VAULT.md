# Foxe Studio — Vault & Preferensi Integrasi

Dokumentasi ini menghubungkan workspace Foxe Agent dengan **Obsidian Vault** pribadi pengguna (`C:\Users\ASUS\OneDrive\Documents\Obsidian Vault`).

---

## 1. Lokasi Dokumen Preferensi di Vault

| File Vault | Jalur Dokumen | Deskripsi |
|---|---|---|
| **Preferensi Pengguna** | `01 Profile/Preferensi Pengguna.md` | Preferensi kerja otomatis (YOLO), jadwal cron 2x sehari, dan standar format laporan Telegram. |
| **Workflow Foxe Studio** | `04 Projects/Workflow Foxe Studio.md` | Prosedur pelaporan operasional studio foto, alur trigger otomatis `ayo kerja`, dan jadwal cloud cron. |
| **Arsitektur Keuangan** | `04 Projects/Foxe Studio - Arsitektur Keuangan & Log Sistem.md` | Standar mutlak COGS/OPEX dari section Detail Neraca, layout responsif 7 kolom, dan sistem serverless GitHub Actions. |

---

## 2. Rincian Konfigurasi Cron & Otomasi

### A. Cloud Cron Serverless (GitHub Actions)
- **File Workflow**: `.github/workflows/daily_sync.yml`
- **Jadwal 1 (Pagi Buka Studio)**: `0 2 * * *` UTC = **09:00 WIB**
- **Jadwal 2 (Malam Closing Studio)**: `0 14 * * *` UTC = **21:00 WIB**
- **Kredensial**: Menggunakan GitHub Secrets `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_CHAT_ID`.
- **Aksi Otomatis**: Menjalankan `python deep_sync_foxe.py`, merakit ulang dashboard, mengunggah pembaruan ke GitHub Pages, dan mengirim notifikasi closing ke Telegram via `@NunuFxBot`.

### B. Local Task Scheduler (Windows)
- **Script Pendaftaran**: `Pasang_Jadwal_Windows_Task.bat`
- **Nama Task**: `FoxeStudioDailySync`
- **Jadwal**: Setiap hari pukul 09:00 WIB via `schtasks`.

---

## 3. Format Struk Monospace Telegram (Estimate Omzet Akhir Bulan)

Di dalam struk laporan harian closing Telegram (blok `<pre>`), tepat di bawah `ESTIMASI NETT PROFIT` dan sebelum garis penutup `============================================`, wajib disematkan:
```text
--------------------------------------------
Unrealized Cash In             Rp  4.300.000
DP (-)                         Rp  1.300.000
Total                          Rp  3.000.000

Unrealized Omzet               Rp 104.625.000
============================================
```
- **Unrealized Cash In**: Total nilai paket seluruh sesi booking terdaftar dari H+1 s.d. akhir bulan di `File 2 (Schedule)`.
- **DP (-)**: Total uang muka yang sudah diterima dari booking tersebut.
- **Total**: Sisa kas/pelunasan riil yang akan masuk saat klien datang foto.
- **Unrealized Omzet**: Estimasi total omzet akhir bulan (Omzet Realized MTD + Total Pelunasan).
- Seluruh teks diformat rata kanan sejajar 44 karakter presisi mengikuti lebar struk.

---

## 4. Keamanan Autentikasi & Master PIN Portal
- **Master PIN Aktif**: `363636`
- **Mekanisme Session Invalidation**: 
  - Token autentikasi menggunakan versi `foxe_studio_auth_token_v2`.
  - Seluruh sesi lama (`v1`, custom PIN, dan sesi tersimpan) otomatis dihapus dan dipaksa keluar (*forced logout*).
  - Siapa pun yang mengakses atau me-refresh portal web wajib memasukkan PIN baru `363636`.
- **URL Live**: 👉 **https://whynunuu.github.io/FoxeStudio/**

