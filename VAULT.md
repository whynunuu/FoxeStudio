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
| **Analisis Wisuda & Slot Orange** | `04 Projects/Foxe Studio - Analisis Wisuda & Recovery Slot Orange.md` | Analisis perbandingan performa cluster wisuda UNSOED vs UMP, evaluasi wasting deposit September vs Oktober, dan 5 rekomendasi penyelamatan booking label Orange. |
| **Foxe Sentry Security** | `04 Projects/Foxe Studio - Sentry Security & Flow Reliability Agent.md` | Agen pengawas keandalan alur sistem: audit 5 checkpoint di jam malam (21:30 & 00:00 WIB), zero-guesswork eskalasi, format struk monospace 40 karakter di Telegram, dan auto-rollback. |
| **Rekap Historis 2026** | `04 Projects/Foxe Studio - Rekap Historis 2026 & Multi-Month Sync.md` | Integrasi data 8 bulan Januari–Agustus (3.218 order) via `parser_historical.py`, caching instan `historical_cache.json`, dan isolasi background sync. |

---

## 2. Rincian Konfigurasi Cron & Otomasi 24/7 (Jadwal Selalu Up-to-Date)

### A. Cloud Cron Serverless (GitHub Actions)
- **File Workflow**: `.github/workflows/daily_sync.yml`
- **Jadwal Operasional Studio**: 08:30 WIB (Pre-Opening Sync & Sentry Audit), serta 12:00, 15:00, 18:00, 21:00 WIB (Closing), 21:30 WIB (Nightly Audit), 00:00 WIB (Midnight Check).
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
- **Jadwal**: Setiap hari pukul 08:30 WIB via `schtasks` (sebelum studio buka).

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


---

## 10. Arsitektur Pemisahan Tabel Booking di Halaman Estimasi Omzet

- **Pemisahan Sesi Booking (Oktober 2026)**:
  - Antarmuka tidak lagi mencampur sesi terjadwal dengan sesi yang sudah selesai dalam satu tabel panjang.
  - Dipisahkan menjadi **dua kartu tabel terpisah**:
    * 🟢 **Kartu Sesi Terjadwal (113 Booking)**: Nilai paket Rp 40,95 jt, estimasi kas masuk Rp 30,55 jt. Dilengkapi filter & search box mandiri (`#confSearchInput`, `#confCatFilter`).
    * 🔵 **Kartu Sesi Selesai (31 Booking)**: Nilai paket Rp 10,23 jt, pelunasan kasir masuk Rp 7,33 jt. Dilengkapi filter & search box mandiri (`#doneSearchInput`, `#doneCatFilter`).
    * 🟠 **Kartu Pipeline Recovery CRM (10 Booking)**: Menampung slot kendala/reschedule berlabel orange dengan DP aman Rp 900.000 (masa berlaku 30 hari) dan potensi pelunasan tertunda Rp 2.900.000.
  - **Master Segment Switcher (`#segOktSplit`)**:
    `[ 📋 Tampilkan Keduanya (Pisah) ]`, `[ 🟢 Sesi Terjadwal (113) ]`, `[ 🔵 Sudah Foto / Selesai (31) ]`, `[ 🟠 Reschedule (10) ]`.

---

## 11. Foxe Sentry — Flow Security, Zero-Guesswork & Nightly Audit Protocol
- **Dokumen Terkait**: `04 Projects/Foxe Studio - Sentry Security & Flow Reliability Agent.md` dan [`foxe_sentry.py`](file:///c:/Users/ASUS/OneDrive/Documents/Foxe%20Agent/foxe_sentry.py).
- **Misi**: Menjamin kelancaran seluruh aliran data (GDrive ➔ Multi-Parser ➔ Reconcile Kasir ➔ JSON State ➔ Build Web) bebas dari *silent error*.
- **Jadwal Nightly Cron (GitHub Actions)**:
  - File: `.github/workflows/nightly_sentry.yml`
  - Closing Studio: **21:30 WIB** (`30 14 * * *` UTC).
  - Midnight Readiness: **00:00 WIB** (`0 17 * * *` UTC).
- **Zero-Guesswork & Human-In-The-Loop Escalation**:
  - Jika terjadi kegagalan teknis (file corrupt/hilang, skema rusak) **ATAU agen mengalami keraguan/kebingungan** (selisih kasir gantung, kru baru tak terdaftar, partisi tanggal bocor antar-bulan), agen **DILARANG BERASUMSI**, melainkan **WAJIB LANGSUNG ESKALASI KE OWNER VIA TELEGRAM (@NunuFxBot)** dan proses auto-push otomatis **DITAHAN**.
- **Standar Desain Struk Monospace Telegram (Fit-In 40 Karakter)**:
  - Seluruh laporan audit Sentry wajib dibungkus dalam blok `<pre>...</pre>` dengan batas lebar **presisi 40 kolom karakter**.
  - Mengeliminasi problem *text-wrapping* / patah baris pada layar smartphone portrait.
  - Mempertahankan keselarasan visual dengan struk closing kasir harian studio.
- **Mekanisme Self-Healing & Rollback**:
  - Snapshot terverifikasi sehat disimpan ke `foxe_full_state.json.bak`. Jika terjadi error fatal saat audit, state otomatis di-rollback ke snapshot tersebut untuk mencegah web crash.

---

## 12. Protokol Background Sync Harian/Malam & Isolasi Bulan Aktif
- **Fokus Murni Bulan Aktif**:
  - Background process harian/malam (GitHub Actions `daily_sync.yml`, `nightly_sentry.yml`, maupun Railway scheduler) **HANYA DAN KHUSUS menyinkronkan data bulan aktif berjalan** (September rekap final & Oktober live kasir / pipeline booking).
  - Closed-books Januari–Agustus dibaca instan (< 0.01 detik) via file cache lokal `historical_cache.json`.
- **Zero-Scan Folder Google Drive Arsip**:
  - Sistem **DILARANG dan TIDAK PERNAH** melakukan screening atau download ulang semua folder arsip lama di Google Drive.
  - Akses Google Drive API dibatasi presisi ke **7 file operasional aktif**:
    1. `file1.xlsm` (Log Order September)
    2. `file1_okt.xlsm` (Log Order Oktober)
    3. `file2.xlsx` (Schedule September)
    4. `file2_okt.xlsx` (Schedule Reguler Oktober)
    5. `file_wisuda_3okt.xlsx` (Wisuda UMP Hari 1 / 3 Okt)
    6. `file_wisuda_4okt.xlsx` (Wisuda UMP Hari 2 / 4 Okt)
    7. `file_neraca.xlsx` (File Neraca Keuangan)
- **Performa Ringan & Cepat**: Durasi eksekusi sinkronisasi serverless berkisar antara **15 s.d. 25 detik**, hemat kuota API, dan bebas risiko merusak data masa lalu.

---

## 13. UI Security Modal Konfirmasi Universal & Standarisasi Format Rupiah
- **Modal Dialog Konfirmasi Interaktif (`#confModal`)**:
  - Mencegah kekeliruan input (*human error*) atau ketidaksengajaan klik tombol hapus di dashboard produksi live:
    * **Edit Data / Penggantian Status**: Memunculkan dialog konfirmasi `"Kamu yakin untuk menginput/mengubah data ini? [Yes / No]"`.
    * **Hapus Data (Tombol Silang `✕`)**: Memunculkan dialog konfirmasi `"Kamu yakin untuk menghapus data ini? [No / Yes]"`.
  - Melindungi seluruh tabel: Transaksi Kasir (`#orderTbody`), Biaya Neraca COGS & OPEX (`#neracaTable`), Funnel Leads (`#leadsTbody`), KPI Kru (`#kpiTbody`), dan Roster Gaji Kru (`#payrollTable` & `.btn-del-payroll`).
- **Standarisasi Format Mata Uang Rupiah**:
  - Seluruh nominal kas, omzet, DP, pelunasan, dan beban neraca wajib ditampilkan dalam format baku Rupiah (`Rp X.XXX.XXX`) dengan pemisah ribuan titik tanpa desimal ganjil.

---

## 14. Spesifikasi Parser Data Historis (`parser_historical.py`)
- **Modul Produksi**: `parser_historical.py` bertugas mengolah 16 file arsip operasional (8 File Log Order + 8 File Schedule) serta sheet bulanan di `file_neraca.xlsx` untuk periode Januari s.d. Agustus 2026.
- **Hasil Rekonsiliasi Kasir vs Neraca (Varians 0,017%)**:
  - Total Omzet Realized Jan–Ags: **Rp 623.973.450** (3.218 order)
  - Total Omzet YTD (Jan–Sep 2026): **Rp 741.988.450** (3.739 order)
  - Nett Profit YTD Bersih: **Rp 414.896.451** (Margin 55,9%)
- **Mekanisme Caching**: Data olahan disimpan ke `historical_cache.json` (~203 KB). Skrip harian `deep_sync_foxe.py` otomatis memakai cache ini sehingga proses sinkronisasi instan (< 0.01 detik).


