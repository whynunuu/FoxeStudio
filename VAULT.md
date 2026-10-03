# Foxe Studio — Vault & Preferensi Integrasi

Dokumentasi ini menghubungkan workspace Foxe Agent dengan **Obsidian Vault** pribadi pengguna (`C:\Users\ASUS\OneDrive\Documents\Obsidian Vault`).

---

## 1. Lokasi Dokumen Preferensi di Vault

| File Vault | Jalur Dokumen | Deskripsi |
|---|---|---|
| **Preferensi Pengguna** | `01 Profile/Preferensi Pengguna.md` | Preferensi kerja otomatis (YOLO), jadwal cron 2x sehari, Biru Foxe, PIN 363636, dan standar struk Telegram. |
| **Workflow Foxe Studio** | `04 Projects/Workflow Foxe Studio.md` | Prosedur pelaporan studio foto, alur trigger otomatis `ayo kerja`, dan jadwal cloud cron. |
| **Arsitektur Keuangan** | `04 Projects/Foxe Studio - Arsitektur Keuangan & Log Sistem.md` | Standar mutlak COGS/OPEX dari section Detail Neraca, layout responsif 7 kolom, logo resmi, dan modul gaji karyawan. |
| **Spesifikasi Parser** | `04 Projects/Foxe Studio - Parser Specs & Data Pipeline.md` | Dokumentasi teknis mendalam 4 parser produksi (`parser_neraca.py`, `parser_schedule.py`, `parser_log_order.py`, `deep_sync_foxe.py`). |

---

## 2. Rincian Konfigurasi Cron & Otomasi 24/7 (Jadwal Selalu Up-to-Date)

### A. Cloud Cron Serverless (GitHub Actions)
- **File Workflow**: `.github/workflows/daily_sync.yml`
- **Jadwal Operasional Studio (Interval 3 Jam)**: `0 2,5,8,11,14 * * *` (UTC) = **09:00, 12:00, 15:00, 18:00, 21:00 WIB**.
- **Kredensial**: Menggunakan GitHub Secrets `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_CHAT_ID`.
- **Aksi Otomatis**: Mengunduh 7 file resmi Google Drive (termasuk Log Order Oktober file1_okt.xlsm), mengeksekusi semua parser, merakit ulang dashboard, mengunggah pembaruan ke GitHub Pages, dan mengirim notifikasi closing ke Telegram via `@NunuFxBot`.

### B. Client-Side Silent Polling (Web & Flow Builder)
- Memeriksa data terbaru secara silent setiap 60 detik (`setInterval`) dan event `visibilitychange` saat tab kembali aktif.
- Menjamin tampilan jadwal booking studio di web (`index.html` dan `flow.html`) selalu mutakhir tanpa perlu reload manual.

### C. Railway 24/7 Scheduler & Webhook Receiver (`webhook_server.py`)
- Background task `state_sync_loop()` menyinkronkan data jadwal dari GitHub Pages setiap 15 menit.
- Background task `reminder_scheduler_loop()` dan GitHub Actions (`leads_reminder.yml`) mengirimkan daftar Hot & Warm Leads yang perlu di-follow up admin pada jadwal resmi: **10:00, 14:00, dan 20:00 WIB** ke WhatsApp dan Telegram.

### D. Local Task Scheduler (Windows)
- **Script Pendaftaran**: `Pasang_Jadwal_Windows_Task.bat`
- **Nama Task**: `FoxeStudioDailySync`
- **Jadwal**: Setiap hari pukul 09:00 WIB via `schtasks`.

---

## 3. Format Struk Monospace Telegram (Estimate Omzet Akhir Bulan)

Di dalam struk laporan harian closing Telegram (blok `<pre>`), tepat di bawah `ESTIMASI NETT PROFIT` dan sebelum garis penutup `============================================`, wajib disematkan:
```text
--------------------------------------------
ESTIMATE OMZET SAMPAI AKHIR BULAN
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
- **Mekanisme Anti-Ingat Perangkat**:
  - Fitur "Ingat perangkat ini (30 hari)" dinonaktifkan dan dihapus total dari lock screen.
  - Sisa token lama di `localStorage` otomatis dibersihkan saat web dibuka.
  - Autentikasi murni berbasis tab browser (`sessionStorage`). Setiap tab/browser ditutup, pengguna wajib memasukkan ulang PIN `363636`.
  - Dilengkapi header meta `Cache-Control: no-cache, no-store, must-revalidate` untuk mencegah browser menahan cache usang.
- **URL Live**: 👉 **https://whynunuu.github.io/FoxeStudio/**

---

## 5. Kewajiban Pengiriman Review Pekerjaan Terstruktur
- Setiap kali Agent selesai bekerja (baik via trigger `ayo kerja`, modifikasi fitur, maupun perbaikan data), Agent **WAJIB menyertakan Review Pekerjaan Terstruktur** di responnya:
  1. Rincian pekerjaan & komponen yang selesai dituntaskan.
  2. Daftar file script & data yang diperbarui.
  3. Status sinkronisasi sistem (GitHub, Telegram, Obsidian).
  4. Metrik operasional penting studio & highlight yang butuh perhatian owner.

---

## 6. Kalender Marketing & Meta Ads Tracker 2026/2027
- Terintegrasi dengan artefak resmi PDF & Excel Marketing Boosting Calendar (Agustus 2026 s.d. Juli 2027).
- Berisi 43 agenda momentum akademik lengkap dengan action pill, momentum acara, paket fokus, dan alasan strategis.
- Meta Ads Tracker dilengkapi dual-switcher bulan berjalan (Oktober 2026 Live Tracker & September 2026 Arsip).

---

## 7. Aturan Mutlak Keselarasan Periode Bulan (Anti-Cross-Month Desync)
- Seluruh modul data dan rendering web mengacu pada satu variabel rujukan: `activeMonth` / `R.c.bulan`.
- Dilarang keras menggunakan variabel state bulan lokal independen yang tidak tersinkronisasi (seperti `adsMonth`) atau melakukan fallback paksa data bulan lain.
- Jika user memilih **Oktober 2026**, seluruh section (termasuk Jadwal Ads & Realized Ads dari Neraca) **WAJIB membuka dan menampilkan data Oktober 2026**.
- Jika user memilih **September 2026**, seluruh section **WAJIB membuka dan menampilkan data September 2026**.

---

## 8. Binding Multi-Sheet Neraca Oktober 2026
- `parser_neraca.py` mengikat sheet `September 2026` dan sheet `Oktober 2026` dari `file_neraca.xlsx`.
- State `neracaByMonth["2026-10"]` aktif dan siap menerima data mutasi debit/kredit finance secara real-time.
- Error boundary `try...catch` aktif pada `render()` untuk menjamin stabilitas runtime.

---

## 9. Standarisasi Aturan Kode Warna Sel KHUSUS File Schedule
- **Lingkup Eksklusif**: Aturan warna ini **HANYA DAN KHUSUS BERLAKU UNTUK FILE SCHEDULE** (`file2.xlsx`, `file2_okt.xlsx`, `file_wisuda_3okt.xlsx`, `file_wisuda_4okt.xlsx`). File Log Order dan Neraca tetap independen.
- **5 Standar Kode Warna Schedule**:
  1. ⚪ **Putih / No Fill** (`FFFFFFFF` / `00000000`): **Slot Kosong** (Available untuk booking baru).
  2. 🟢 **Hijau** (`FF00FF00`): **Slot Terisi (Confirmed Booking)**. Booking sah terjadwal, masuk penuh ke dalam potensi pipeline dan estimasi pelunasan (*cash-in*).
  3. 🔵 **Biru / Cyan** (`FF00FFFF`): **Selesai / Sedang Sesi / Hadir (Live Case)**. Klien sudah datang di studio, sesi berlangsung atau sudah selesai, dan uang direalisasikan di kasir.
  4. 🟠 **Orange** (`FFFF9900`): **Kendala Jadwal (Reschedule / Telat / Tidak Datang / CLOSED)**. Slot bertuliskan `CLOSED` atau pesanan yang reschedule/batal otomatis disaring dari estimasi sisa uang masuk agar tidak terjadi over-estimasi atau *double-count*.
  5. 🔴 **Merah** (`FFFF0000` / `FFF4CCCC`): **Full Slot / Batas Order**. Kuota ditutup atau penanda batas jam operasional, otomatis dikecualikan dari perhitungan booking klien.
- **Logika Perhitungan Warna Orange**:
  - Slot Orange menandakan sesi tidak berlanjut pada slot tersebut, sehingga **estimasi pelunasan (*cash-in*) otomatis Rp 0** agar tidak terjadi over-estimasi.
  - Jika reschedule ke tanggal baru, sesi akan dicatat di slot baru untuk mencegah *double counting*.
  - **Ketentuan Masa Berlaku DP (30 Hari)**: Uang DP klien pada slot Orange **TETAP BERLAKU SELAMA 30 HARI** sejak tanggal sesi aslinya. Booking Orange dialihkan ke **Pipeline Recovery CRM** untuk di-follow up penjadwalan ulang (*re-booking*) sebelum 30 hari berakhir demi menyelamatkan potensi pelunasan yang tertunda.

