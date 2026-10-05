# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"** (atau "update data", "sinkronkan data"), Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri:
1. Jalankan `python deep_sync_foxe.py`:
   - Unduh 11 File Operasional Resmi:
     * File 1 Log Order Sept: ID `1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ` (`file1.xlsm`)
     * File 1 Log Order Okt: ID `1xibgfKWJZWmcwh9lxR9Dt7IkHyMi7b75` (`file1_okt.xlsm`)
     * File 2 Schedule Sept: ID `14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I` (`file2.xlsx`)
     * File Neraca: ID `1dvnCNyfZI5z-12081XJjGCVLtMaQpUStYT61qU3orKM` (`file_neraca.xlsx`)
     * Schedule Reguler Oktober: ID `17QPAAhmPZqkomwajFhAw3JBmDyBFuklfNMqyVqlK484` (`file2_okt.xlsx`)
     * Wisuda UMP Hari 1 (3 Okt): ID `1sRILPoZD09Rm5aKn6tswNxvxOiRkSu4Z` (`file_wisuda_3okt.xlsx`)
     * Wisuda UMP Hari 2 (4 Okt): ID `1hDeuOh-6fnsP7vzWAl4HVwlYoEumu1hA` (`file_wisuda_4okt.xlsx`)
     * Wisuda UIN Saizu Hari 1 (1 Sept): ID `10ombL-MWte-Gfh9aOkBoSqRAbrA7KiNc` (`file_wisuda_uin_1sep.xlsx`)
     * Wisuda UIN Saizu Hari 2 (2 Sept): ID `1QAJ6bRYkpawktaQFSdrPXcTEou0e1RTQ` (`file_wisuda_uin_2sep.xlsx`)
     * Wisuda UNSOED Hari 1 (8 Sept): ID `14zX-ykMTFlff29otmXIlNbl9dF5Eu1vL` (`file_wisuda_unsoed_8sep.xlsx`)
     * Wisuda UNSOED Hari 2 (9 Sept): ID `17v-GjdUESuSWDFmduvweCzCe5Cg7QtNn` (`file_wisuda_unsoed_9sep.xlsx`)
   - Hitung total shift aktual kru s.d. hari ini dari Log Order, deteksi cut-off dinamis (Sept: 30 Sep, Okt: 01 Okt).
   - Parse section `Detail` File Neraca (kolom P s.d. U) untuk klasifikasi COGS & OPEX serta Buku Detail Neraca (Debit/Kredit).
   - Parse Log Order & Pipeline Oktober: Realisasi live 1 booking DP (Rp 100 rb) via AMEL (2 shift) + 164 booking terdaftar (Potensi omzet Rp 59,15 jt, estimasi pelunasan Rp 47,80 jt).
   - **Optimasi Cepat Data Historis (Closed Books Jan–Ags)**: Menggunakan cache instan `historical_cache.json` (< 0.01 detik). Sinkronisasi harian/rutin DILARANG membaca ulang 16 file arsip dari awal, melainkan fokus 100% pada bulan aktif berjalan (September rekap final & Oktober live).
   - Simpan `foxe_full_state.json`, rakit `index.html`, dan kirim notifikasi Telegram via `@NunuFxBot`.
   - Di dalam struk laporan Telegram (blok monospace), sertakan kalkulasi **Estimate Omzet Sampai Akhir Bulan** (Unrealized Cash In, DP (-), Total, dan Unrealized Omzet) yang menyatu di dalam struk di bawah Estimasi Nett Profit.
2. Jalankan git commit & push ke `origin main`:
   `git add foxe_full_state.json index.html assemble_app.py logo_foxe.png file1.xlsm file1_okt.xlsm file2.xlsx file_neraca.xlsx file2_okt.xlsx file_wisuda_3okt.xlsx file_wisuda_4okt.xlsx file_wisuda_uin_1sep.xlsx file_wisuda_uin_2sep.xlsx file_wisuda_unsoed_8sep.xlsx file_wisuda_unsoed_9sep.xlsx parser_neraca.py parser_schedule.py parser_log_order.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md VAULT.md`
   `git commit -m "Auto-sync data update"`
   `git push origin main`
3. Tampilkan ringkasan metrik pembaruan hari ini dan tautan website live:
   👉 **https://whynunuu.github.io/FoxeStudio/** (PIN: `363636`)

---

## Aturan Mutlak Desain & Arsitektur Dashboard:

### 1. Section No. 1: Laporan Tahunan & Seasonality Index
- **Posisi Prioritas #1**: `Laporan Tahunan` berada di urutan teratas pada daftar navigasi Ringkasan dan menjadi tampilan pembuka (**default landing view**) saat website pertama kali dimuat.
- **ATURAN MUTLAK DATA REAL (Anti-Fabrikasi)**:
  - Bulan sebelum September 2026 (Januari–Agustus) dan sesudah Oktober 2026 (November–Desember 2026) **WAJIB DIKOSONGKAN (`—`)** dengan status badge `<span class="pill neutral">Belum Dicocokkan</span>`.
  - **September 2026**: Menampilkan data riil live terverifikasi (`R.omzet`, proyeksi run-rate, indikator live dot berdenyut, dan badge `<span class="pill crit">Berjalan (Terverifikasi)</span>`).
  - **Oktober 2026**: Menampilkan data riil pipeline booking terdaftar (`S.oktoberPipeline`: 163 booking terdaftar dari Schedule Reguler + Wisuda UMP 3 & 4 Okt, badge `<span class="pill prog">Pipeline (163 Booking)</span>`, potensi omzet Rp 58,88 jt, dan estimasi pelunasan riil Rp 47,52 jt).
- **Benchmark Seasonality 12 Bulan**:
  - Matriks Seasonality Index 12 bulan (Januari s.d. Desember) tetap aktif penuh menggunakan benchmark tahun 2025 (garis tengah 1.00×, Super Peak September 2.10×).
  - Pada grafik tahunan dan grafik YoY, batang 2026 dirender untuk bulan September (realized) dan Oktober (pipeline terdaftar).
- **12 Kotak Bulan Interaktif & Urutan Layout**:
  - **Posisi Paling Atas**: Tepat di bawah kartu KPI, urutan pertama adalah **12 Kotak Bulan Interaktif (`.mgrid`)** dan **Tabel Komparasi 12 Bulan**.
  - **Posisi Bawah**: Banner penjelasan Seasonality Index dan Grafik Chart Seasonality diletakkan di bawah tabel bulanan.
  - Setiap kotak bulan dapat diklik: September membuka dashboard live (`view = "dash"`), Oktober langsung membuka rincian pipeline booking Oktober 2026 (`estMonth = 10; view = "est"`).

### 2. Navigasi & Integrasi Lintas Section (Cross-Section Harmony):
- **Navigasi Langsung Oktober 2026 (`estMonth = 10`)**:
  - Mengklik kotak atau tombol bulan Oktober pada Laporan Tahunan langsung membuka halaman **Oktober 2026** di Estimasi Omzet.
  - **Topbar Adaptif**: Topbar otomatis menampilkan periode *"Oktober 2026 | Pipeline 163 Booking · Reguler & Wisuda UMP"*.
  - Dilengkapi **Dual-Period Switcher**:
    - `[ 📅 Oktober 2026 (Pipeline 163 Booking) ]`
    - `[ 📅 September 2026 (Sisa Jadwal) ]`
  - Tabel 163 booking dilengkapi pencarian cepat client/paket/spot instan dan tombol filter kategori (*Semua*, *Wisuda UMP*, *Studio Reguler*).
- **Integrasi Lintas Section**:
  - **Dashboard Bulanan (`vDash`)**: Kartu forward outlook pipeline Oktober (163 booking) dengan tombol pintas ke rincian estimasi.
  - **Target & Skenario (`vTarget`)**: Kartu kesiapan target Q4 / Oktober 2026 dengan modal terkunci Rp 58,88 jt.
  - **Perbandingan YoY (`vYoy`)**: Grafik chart YoY merender batang Oktober 2026 (hijau putus-putus) berdampingan dengan September run-rate, serta kartu forward outlook YoY.
  - **Paket & Crew (`vCrew`)**: Alert operasional persiapan kru menangani 134 sesi wisuda di 5 backdrop dan 29 sesi reguler studio.
  - **Rekap Shift (`vShift`)**: Peringatan kesiapan roster shift menyambut Super Peak Wisuda UMP (70 sesi pada 3 Okt dan 64 sesi pada 4 Okt).

### 3. Struktur Section Neraca (COGS & OPEX):
- Section COGS dan OPEX digabung menjadi satu section resmi bernama **`Neraca (COGS & OPEX)`**.
- **Sumber Data Biaya:** Pengeluaran COGS & OPEX murni diambil dari section `Detail` File Neraca (kolom P s.d. U via `parser_neraca.py`). JANGAN mengambil dari File Log Order karena referensinya berbeda.
- Di bawah rekap COGS & OPEX, wajib menyertakan **Buku Detail Neraca (Debit & Kredit)** yang mencatat mutasi kas masuk, kas keluar, dan saldo berjalan per tanggal transaksi.

### 4. Standar Tampilan Fit-In & Anti-Tabrakan:
- **Lebar Kontainer (`.view`):** Gunakan `max-width: 1600px; width: 100%; margin: 0 auto; padding: 28px 32px 80px;`. JANGAN batasi ke 1200px kaku agar tidak muncul ruang hitam kosong di kanan layar.
- **Format Tabel Biaya 7 Kolom:**
  $$\text{Tgl} \ \mid\ \text{Deskripsi} \ \mid\ \text{Jenis} \ \mid\ \text{Kategori} \ \mid\ \text{Nilai} \ \mid\ \text{Status} \ \mid\ \text{Aksi}$$
  - Informasi vendor/metode bayar disatukan sebagai subteks halus di bawah Deskripsi.
  - Informasi cicilan/termin disatukan di bawah Nilai.
  - Kolom Status dan tombol hapus `✕` harus selalu terlihat utuh tanpa terpotong.
- **Pencegahan Benturan Grid (`.two` & `.three`):** Wajib menggunakan `repeat(auto-fit, minmax(360px, 1fr))` dengan breakpoint di `1080px` (otomatis menjadi 1 kolom tumpuk saat layar menyempit).
- **Tipografi KPI Adaptif:** Nilai uang besar pada `.stat .v` menggunakan `clamp(20px, 1.9vw, 31px)` dengan `text-overflow: ellipsis` agar tidak meluber keluar kotak kartu.
- **Wrapping Teks:** Jangan gunakan blanket `white-space: nowrap` pada semua `td`. Izinkan deskripsi membungkus alami (*wrap*), sementara angka `.n`, tanggal `.mono`, dan badge `.pill` tetap *nowrap*.
- **Dropdown KPI Interaktif:** Input Nama dan Posisi pada form KPI menggunakan dropdown interaktif dengan opsi kru aktif dan input kustom.


- **Standarisasi Kontainer Scrollable Tabel Panjang (`.tw.scrollable`):** Seluruh tabel data yang memuat entri panjang (Realisasi Live Log Order, Transaksi Bulanan, Buku Detail Neraca, Beban COGS/OPEX, Rekap Shift Harian, Funnel Leads, dan Sisa Jadwal) **WAJIB** dibungkus kontainer scrollable (`max-height: 460px – 520px; overflow-y: auto;`) dengan sticky table header (`thead` menempel di atas) agar seluruh halaman web tetap ringkas, tidak memanjang ke bawah, dan nyaman dijelajahi.

### 5. Kebijakan Fitur Terminal:
- Fitur Terminal View (Bloomberg/trading terminal) **DILARANG & DIHAPUS PERMANEN** dari repositori Foxe Studio utama.
- Topbar harus tetap bersih, resmi, dan menyertakan elemen `#tbUpd`, `#tbLive`, dan tombol update `#btnSyncWeb`.
- Fungsi `render()` pada JavaScript wajib menyertakan pemeriksaan defensif `if(up)` agar tidak terjadi error `TypeError: null`.

### 6. Tombol Update Otomatis di Web & GitHub Actions:
- Topbar aplikasi web dilengkapi tombol **`🔄 Update`** yang bekerja dalam dua mode:
  1. **Fast Refresh**: Memeriksa `foxe_full_state.json` terbaru di GitHub repository tanpa membebani kuota API.
  2. **Cloud Sync**: Memanggil GitHub API `workflow_dispatch` untuk memicu `.github/workflows/daily_sync.yml`. Sinkronisasi langsung berjalan di server cloud GitHub Actions tanpa perlu perangkat/laptop owner menyala.
- **Jadwal Cron Otomatis Cloud**: Workflow berjalan otomatis sebelum buka studio pukul **08:30 WIB** (`30 1 * * *` UTC) dan selama jam operasional studio pada pukul **12:00, 15:00, 18:00, dan 21:00 WIB** (`0 5,8,11,14 * * *` UTC). Dilengkapi silent background auto-polling setiap 60 detik di web client dan state sync 15 menit di Railway 24/7.
- **Jadwal Follow-Up Reminder Leads**: Workflow `.github/workflows/leads_reminder.yml` dan Railway scheduler berjalan pada pukul **10:00, 14:00, dan 20:00 WIB** (`0 3,7,13 * * *` UTC) mengirimkan rekap calon klien Hot & Warm secara mandiri ke WhatsApp Admin dan Telegram (@NunuFxBot).

### 7. Format Laporan Telegram (Estimate Omzet Akhir Bulan):
- Di dalam struk ringkasan harian Telegram (blok `<pre>`), tepat di bawah `ESTIMASI NETT PROFIT` dan sebelum garis penutup `============================================`, wajib menyertakan section **Estimate Omzet Sampai Akhir Bulan** yang menyatu di dalam struk:
  * `Unrealized Cash In : Rp .....` (Total harga paket sesi booking terdaftar dari H+1 s.d. akhir bulan di File 2 Schedule)
  * `DP (-)             : Rp .....` (Total DP yang sudah diterima dari booking tersebut)
  * `Total              : Rp .....` (Sisa uang pelunasan yang riil akan masuk saat foto)
  * (baris kosong)
  * `Unrealized Omzet   : Rp .....` (Estimasi omzet akhir bulan = Omzet Realized MTD + Total Pelunasan)
- Format harus sejajar rata kanan 44 karakter presisi mengikuti lebar struk kasir.

### 8. Kewajiban Mutlak Mengirimkan Review Pekerjaan Terstruktur:
- **Setiap kali Agent selesai bekerja** (baik melalui trigger kata kunci `'ayo kerja'`, permintaan update fitur, perbaikan bug, atau sinkronisasi data), Agent **WAJIB MENYERTAKAN REVIEW PEKERJAAN TERSTRUKTUR** di akhir responnya.
- **Format Review Pekerjaan Wajib Mencakup:**
  1. **Rincian Pekerjaan Selesai**: Poin-poin spesifik apa saja yang baru saja dituntaskan atau diubah.
  2. **File & Komponen yang Diperbarui**: Daftar file script, JSON state, visual HTML, atau dokumen Obsidian yang mengalami perubahan.
  3. **Status Integrasi & Deploy**: Konfirmasi git commit & push ke GitHub Pages, serta status pengiriman Telegram.
  4. **Metrik & Highlight Operasional Terkini**: Ringkasan data penting (omzet, order, pipeline, ads, schedule besok) agar owner dapat memantau studio secara transparan dan jelas.
  5. **Durasi Waktu Pengerjaan**: Wajib menyertakan catatan durasi pengerjaan di baris penutup dengan format: `⏱️ Waktu Pengerjaan : [X] Menit [Y] Detik`.

### 9. Integrasi Kalender Marketing & Meta Ads Tracker 2026/2027:
- Meta Ads Tracker mendukung pergantian multi-bulan dinamis: **Oktober 2026 (Live Tracker)** dan **September 2026 (Arsip)**.
- Section Marketing dilengkapi **Kalender Marketing & Boosting 2026/2027 (Agustus 2026 s.d. Juli 2027)** berisi 43 agenda momentum akademik dan seasonal kampus/sekolah (berdasarkan basis data 2.164 transaksi Semester 1 2026).
- Tabel dilengkapi filter kategori interaktif (*Semua*, *Event Day*, *Boost / Hard Push*, *H-7 Conversion*, *Awareness*) dan pencarian instan agenda/paket/kampus.

### 10. Aturan Mutlak Keselarasan Periode Bulan (Anti-Cross-Month Desync / Anti-Silang Bulan):
- **Konsistensi Bulan Tunggal (Single Source of Truth Bulan Aktif)**:
  - Bulan yang sedang aktif (`activeMonth` / `R.c.bulan`) **WAJIB MENJADI RUJUKAN TUNGGAL** untuk SELURUH section dashboard (Dashboard Utama, Neraca COGS/OPEX, Gaji Kru, Log Transaksi, Jadwal Ads, Rekap Shift, Estimasi Omzet, dll.).
  - **Prinsip Bebas Silang Bulan**:
    * Jika user memilih **Oktober 2026**, seluruh section (termasuk Jadwal Ads & Realized Ads dari Neraca) **WAJIB membuka dan menampilkan data Oktober 2026**.
    * Jika user memilih **September 2026**, seluruh section **WAJIB membuka dan menampilkan data September 2026**.
    * Begitu pula untuk bulan lainnya (Januari = Januari, Februari = Februari, dst.).
  - **DILARANG KERAS** menggunakan variabel state bulan lokal independen yang tidak tersinkronisasi (seperti `adsMonth`), ataupun melakukan fallback paksa data bulan lain jika data bulan yang dipilih belum ada (jika belum ada rencana, tampilkan status kosong / placeholder yang jujur).
  - Toggling periode pada sub-section (seperti tombol switch periode di Jadwal Ads atau Estimasi) harus otomatis memperbarui `activeMonth` dan merender ulang seluruh antarmuka secara harmonis.

### 11. Standarisasi Aturan Kode Warna Sel KHUSUS File Schedule (Anti-Ghost Slot):
- **Lingkup Eksklusif**: Kode warna ini **HANYA DAN KHUSUS BERLAKU UNTUK FILE SCHEDULE** (`file2.xlsx`, `file2_okt.xlsx`, `file_wisuda_3okt.xlsx`, `file_wisuda_4okt.xlsx`, dan jadwal studio/event lainnya). File operasional lain (Log Order `file1.xlsm` & Neraca `file_neraca.xlsx`) tetap independen mengikuti kolom kasir dan section detail masing-masing.
- **Standarisasi 5 Kode Warna Schedule**:
  1. ⚪ **Putih / No Fill** (`FFFFFFFF` / `00000000`): **Slot Kosong** (Available untuk booking baru).
  2. 🟢 **Hijau** (`FF00FF00`): **Slot Terisi (Confirmed Booking)**. Booking sah terjadwal, masuk penuh ke dalam potensi pipeline dan estimasi pelunasan (*cash-in*).
  3. 🔵 **Biru / Cyan** (`FF00FFFF`): **Selesai / Sedang Sesi / Hadir (Live Case)**. Klien sudah datang di studio, sesi berlangsung atau sudah selesai, dan uang direalisasikan di kasir.
  4. 🟠 **Orange** (`FFFF9900`): **Kendala Jadwal (Reschedule / Telat / Tidak Datang / CLOSED)**. Slot bertuliskan `CLOSED` atau pesanan yang reschedule/batal otomatis disaring dari estimasi sisa uang masuk agar tidak terjadi over-estimasi atau *double-count*.
  5. 🔴 **Merah** (`FFFF0000` / `FFF4CCCC`): **Full Slot / Batas Order**. Kuota ditutup atau penanda batas jam operasional, otomatis dikecualikan dari perhitungan booking klien.
- **Ketentuan Khusus Masa Berlaku DP Label Orange (30 Hari)**:
  - Uang DP klien pada slot bersandi **Orange (🟠)** **TETAP BERLAKU SELAMA 1 BULAN (30 HARI)** terhitung sejak tanggal sesi jadwal aslinya.
  - Sisa pelunasan pada slot Orange sementara dinetralkan (`Rp 0`) dari proyeksi cash-in hari berjalan untuk menjaga integritas pembukuan kasir harian.
  - Namun, data booking Orange wajib dialihkan ke **Pipeline Recovery CRM** agar admin aktif mem-follow up penjadwalan ulang (*re-book*) sebelum 30 hari berakhir, sehingga potensi pelunasan yang tertunda dapat terealisasi kembali.
- **Integrasi Visual Dashboard**: Menampilkan badge status sesi (🔵 *Selesai/Hadir*, 🟢 *Terjadwal*, 🟠 *Reschedule*) dan tombol filter status cepat pada tabel daftar booking.

### 12. Pemisahan Tampilan Booking di Dashboard (Terjadwal vs Sudah Selesai Hadir):
- Di section Estimasi Omzet (Oktober 2026), daftar booking tidak lagi disatukan dalam 1 tabel panjang, melainkan dipisahkan menjadi dua kartu tabel mandiri dengan Master Segment Switcher (`#segOktSplit`):
  * `[ 📋 Tampilkan Keduanya (Pisah) ]`
  * `[ 🟢 Sesi Terjadwal (113) ]`
  * `[ 🔵 Sudah Foto / Selesai (31) ]`
  * `[ 🟠 Reschedule (10) ]`
- Masing-masing tabel dilengkapi pencarian mandiri (`#confSearchInput`, `#doneSearchInput`) dan filter kategori mandiri (`#confCatFilter`, `#doneCatFilter`).

### 13. Foxe Sentry — Flow Security, Zero-Guesswork & Nightly Audit Protocol:
- **Tugas & Tanggung Jawab Utama**:
  - Menjaga seluruh flow operasional (Google Drive, Multi-Parser, Reconcile Kasir, Business Rules, dan Web Deployment) berjalan 100% bebas error.
  - Berjalan otomatis via GitHub Actions (`.github/workflows/nightly_sentry.yml`) pada jadwal pre-opening sebelum buka studio **08:30 WIB** (`30 1 * * *` UTC), closing malam **21:30 WIB** (`30 14 * * *` UTC), dan dry-run tengah malam **00:00 WIB** (`0 17 * * *` UTC).
- **Kebijakan Mutlak "Zero Guesswork & Eskalasi Human-in-the-Loop"**:
  - Jika terjadi error teknis (file corrupt, sheet hilang, JSON rusak, web down), **ATAU jika agen mengalami keraguan / anomali logika kasir yang ambigu ("bingung")** seperti:
    * Selisih angka kasir tak bertuan (Kas + Transfer ≠ Omzet),
    * Entitas kru asing aktif yang belum terdaftar di master roster,
    * Kebocoran tanggal transaksi antar-bulan (Cross-Month leak),
    * Nilai nominal negatif atau NaN.
  - **Agen DILARANG KERAS berasumsi atau menyembunyikan masalah**, melainkan **WAJIB LANGSUNG ESKALASI LAPOR KE OWNER VIA TELEGRAM (@NunuFxBot)** melalui pesan darurat terstruktur.
  - Proses `git push` otomatis wajib **DITAHAN** saat terjadi insiden untuk menjaga stabilitas data live, dan snapshot sehat `foxe_full_state.json.bak` siap digunakan untuk recovery.

### 14. UI Security — Modal Konfirmasi Universal (Edit & Hapus) & Format Rupiah:
- **Dialog Modal Universal (`#confModal`)**:
  - Mencegah human error salah ubah nilai atau ketidaksengajaan klik tombol hapus:
    * Sebelum submit form edit / ubah status: Muncul modal *"Kamu yakin untuk menginput/mengubah data ini? [Yes/No]"*.
    * Sebelum menghapus entri tabel via tombol `✕` / `.btn-del-payroll`: Muncul modal *"Kamu yakin untuk menghapus data ini? [No/Yes]"*.
  - Menjaga integritas tabel: Kasir, Biaya Neraca, Leads, KPI Kru, dan Payroll.
- **Standarisasi Format Mata Uang Rupiah**:
  - Seluruh nilai nominal di dashboard wajib diformat baku Rupiah (`Rp X.XXX.XXX`) dengan pemisah ribuan titik.

### 15. Protokol Background Sync — Isolasi Bulan Aktif & Zero-Scan Arsip Lama:
- **Fokus Murni Bulan Aktif**:
  - Seluruh sinkronisasi latar belakang harian & malam (GitHub Actions & Railway) **HANYA DAN KHUSUS menyinkronkan data bulan aktif berjalan** (September rekap final & Oktober live kasir / pipeline booking).
  - Data historis Januari–Agustus wajib dibaca instan (< 0.01 detik) via `historical_cache.json`.
- **Dilarang Scanning Folder Arsip Google Drive**:
  - Sistem DILARANG dan TIDAK PERNAH melakukan scanning/download ulang folder-folder arsip lama di Google Drive.
  - Panggilan API dibatasi presisi pada 7 file operasional aktif: `file1.xlsm`, `file1_okt.xlsm`, `file2.xlsx`, `file2_okt.xlsx`, `file_wisuda_3okt.xlsx`, `file_wisuda_4okt.xlsx`, `file_neraca.xlsx`.

### 16. Protokol Investigasi & Solusi Cepat "Desync Dashboard vs Log Order" (Tombol Update Tidak Berubah):
- **Indikasi Kasus / Keluhan Pengguna**:
  Pengguna menanyakan *"udah di pastiin sync sama log order kan?"* atau mengeluhkan *"di dashboard belum update padahal udah klik tombol Update"*.
- **Akar Masalah yang Wajib Diperiksa (Root Causes)**:
  1. **Fallback Cut-Off Statis**: Variabel cut-off di Javascript (`compute()` / `vTahunan()`) memiliki nilai tanggal fallback statis/hardcoded (misal `"2026-10-02"` atau `"2026-10-04"`), sehingga transaksi setelah tanggal tersebut otomatis terfilter dan tersembunyi dari layar.
  2. **Integritas Objek State `oktoberLogOrder`**: Properti `state["oktoberLogOrder"]` belum tersimpan atau tertimpa snapshot lama di `foxe_full_state.json`.
  3. **Fast Refresh Mode vs GitHub Push**: Tombol `🔄 Update` di website hanya memicu *Fast Refresh* (`fetch foxe_full_state.json?t=...` dari GitHub Pages). Jika commit lokal/closing belum di-push ke remote (`origin main`), atau tertimpa commit Cloud Cron yang berbeda, website tetap menyajikan data lama.
  4. **Browser Cache & `BUILD_ID`**: Browser client menyimpan cache `localStorage` dan asset HTML. `BUILD_ID` wajib di-bump agar fungsi `checkNewBuild()` otomatis mendeteksi versi baru dan me-reload browser client.
- **Standar Eksekusi Resolusi Cepat (Zero-Guesswork Fast Solving)**:
  1. **Periksa Formula Cut-Off**: Pastikan cut-off dihitung 100% dinamis dari tanggal order aktif tertinggi (`oktMaxDay` dari `S.orders`), DILARANG menggunakan tanggal fallback statis.
  2. **Jalankan Deep Sync Penuh**: Eksekusi `python deep_sync_foxe.py` untuk mengunduh 11 sumber Google Drive, mengurai seluruh transaksi Log Order, dan memperbarui `foxe_full_state.json`.
  3. **Rakit Bundel Visual & Bump Build**: Jalankan `python assemble_app.py` untuk memperbarui `BUILD_ID` dan merakit `index.html`.
  4. **Deploy ke Remote**: Jalankan `git add`, `git commit`, dan `git push origin main`.
  5. **Instruksi Pengguna**: Minta pengguna melakukan **Hard Refresh** (`Ctrl + F5` / `Ctrl + Shift + R` di PC, atau tutup dan buka kembali tab browser di HP) untuk langsung memuat data terbaru.



