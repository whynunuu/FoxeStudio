# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"** (atau variasi serupa seperti "update data", "sinkronkan data"), Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri dari awal hingga selesai tanpa perlu konfirmasi manual lagi:

### 1. Eksekusi Sinkronisasi Operasional Google Drive (`deep_sync_foxe.py`):
- Unduh & parse data operasional dari 7 sumber Google Drive resmi (File 3 / Rekap Global DI-SKIP):
  * **File 1 (Log Order Sept `.xlsm`)**: ID `1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ` (`file1.xlsm`).
  * **File 1 (Log Order Okt `.xlsm`)**: ID `1xibgfKWJZWmcwh9lxR9Dt7IkHyMi7b75` (`file1_okt.xlsm`).
  * **File 2 (Schedule Sept `.xlsx`)**: ID `14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I` (`file2.xlsx`).
  * **File Neraca (`.xlsx`)**: ID `1dvnCNyfZI5z-12081XJjGCVLtMaQpUStYT61qU3orKM` (`file_neraca.xlsx`).
  * **Schedule Reguler Oktober (`.xlsx`)**: ID `17QPAAhmPZqkomwajFhAw3JBmDyBFuklfNMqyVqlK484` (`file2_okt.xlsx`).
  * **Wisuda UMP Hari 1 / 3 Okt (`.xlsx`)**: ID `1sRILPoZD09Rm5aKn6tswNxvxOiRkSu4Z` (`file_wisuda_3okt.xlsx`).
  * **Wisuda UMP Hari 2 / 4 Okt (`.xlsx`)**: ID `1hDeuOh-6fnsP7vzWAl4HVwlYoEumu1hA` (`file_wisuda_4okt.xlsx`).
- **Pipeline & Realisasi Live Oktober:** Otomatis parse & merge realisasi live 1 transaksi DP (Rp 100 rb) via AMEL (2 shift) + 164 booking terdaftar (Potensi omzet Rp 59,15 jt, estimasi pelunasan Rp 47,80 jt).
- **Roster Shift:** Hitung akumulasi total shift slot aktual dari Log Order s.d. tanggal sekarang/cut-off.
- **ATURAN MUTLAK BIAYA:** Pengeluaran COGS & OPEX murni diambil dari section `Detail` File Neraca (kolom P s.d. U). JANGAN mengambil pengeluaran dari File Log Order karena referensinya berbeda.
- **SECTION TERPADU:** Section COGS dan OPEX digabung menjadi satu section resmi bernama **`Neraca (COGS & OPEX)`** yang dilengkapi **Buku Detail Neraca (Debit & Kredit)**.
- Deteksi cut-off dinamis (Sept: 30 Sep, Okt: 01 Okt).
- Simpan state gabungan ke `foxe_full_state.json`.
- Rakit ulang file visual `index.html` dan salin ke artefak `foxe_studio_keuangan.html`.

### 2. Auto-Commit & Deploy ke GitHub:
- Otomatis commit dan push pembaruan data ke repository:
  `git add foxe_full_state.json index.html assemble_app.py logo_foxe.png file1.xlsm file1_okt.xlsm file2.xlsx file_neraca.xlsx file2_okt.xlsx file_wisuda_3okt.xlsx file_wisuda_4okt.xlsx parser_neraca.py parser_schedule.py parser_log_order.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md VAULT.md`
  `git commit -m "Auto-sync data update"`
  `git push origin main`
- Remote URL: `https://github.com/whynunuu/FoxeStudio.git`

### 3. Berikan Laporan Ringkas, Kirim Telegram & Tautan Live:
- Kirim notifikasi otomatis laporan harian closing ke Telegram via `@NunuFxBot` (`telegram_notifier.py`) mencakup breakdown Kas/Transfer, Total COGS, OPEX, Estimasi Nett Profit, **Estimate Omzet Sampai Akhir Bulan (Unrealized Cash In, DP (-), Total, dan Unrealized Omzet)** yang menyatu di dalam struk, Leads, Shift Kru, dan Jadwal Foto Besok H+1.
- Sajikan tabel ringkasan: Cut-off hari ini, total order MTD, omzet MTD (Cash vs Transfer), omzet hari ini, shift kru, dan capaian target.
- Sertakan link website resmi live (terproteksi PIN: `363636`):
  👉 **https://whynunuu.github.io/FoxeStudio/**

---

## Standar Desain Visual & Larangan Sistem:

### 1. Section No. 1: Laporan Tahunan & Seasonality Index
- **Urutan Navigasi Teratas**: `Laporan Tahunan` berposisi di urutan pertama (paling atas) pada sidebar ringkasan dan menjadi landing view bawaan (**default view**) saat web pertama kali dibuka.
- **ATURAN MUTLAK DATA REAL (Anti-Spekulasi)**:
  - Bulan sebelum September 2026 (Jan–Ags) dan sesudah Oktober 2026 (Nov–Des) **WAJIB DIKOSONGKAN (`—`)** dengan status badge `<span class="pill neutral">Belum Dicocokkan</span>`.
  - **September 2026**: Menampilkan data riil live terverifikasi (`R.omzet`, proyeksi run-rate, indikator live dot, badge `<span class="pill crit">Berjalan (Terverifikasi)</span>`).
  - **Oktober 2026**: Menampilkan data riil pipeline booking terdaftar (`S.oktoberPipeline`: 163 booking terdaftar dari Schedule Reguler + Wisuda UMP 3 & 4 Okt, badge `<span class="pill prog">Pipeline (163 Booking)</span>`, potensi omzet Rp 58,88 jt, dan estimasi pelunasan riil Rp 47,52 jt).
- **Seasonality Index 12 Bulan**:
  - Matriks Seasonality Index 12 bulan (Jan–Des) tetap aktif penuh menggunakan benchmark tahun 2025 (garis tengah 1.00× rata-rata, Super Peak September 2.10×).
  - Pada chart tahunan dan chart YoY, batang 2026 dirender untuk bulan September (realized) dan Oktober (pipeline terdaftar).
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

### 3. Layout Fit-In & Anti-Tabrakan:
- `.view` menggunakan lebar adaptif `max-width: 1600px; width: 100%; margin: 0 auto; padding: 28px 32px 80px;`. JANGAN batasi ke 1200px kaku agar tidak muncul ruang hitam kosong di kanan layar.
- Tabel Biaya Neraca menggunakan format **7 kolom responsif**: `Tgl | Deskripsi | Jenis | Kategori | Nilai | Status | Aksi`. Kolom Status dan tombol ✕ wajib terlihat utuh tanpa terpotong.
- Grid `.two` dan `.three` wajib responsif (`minmax(360px, 1fr)`) dan breakpoint di 1080px agar tidak saling bertabrakan.
- Angka KPI besar menggunakan `clamp(20px, 1.9vw, 31px)` dengan `text-overflow: ellipsis`.
- **Dropdown KPI Interaktif:** Input Nama dan Posisi pada form KPI menggunakan dropdown interaktif dengan opsi kru aktif dan input kustom.

### 4. Tombol Update Otomatis di Web & GitHub Actions:
- Topbar dilengkapi tombol **`🔄 Update`** yang bekerja dalam dua mode:
  1. **Fast Refresh**: Memeriksa `foxe_full_state.json` terbaru di GitHub repository tanpa membebani kuota API.
  2. **Cloud Sync**: Memanggil GitHub API `workflow_dispatch` untuk memicu `.github/workflows/daily_sync.yml`. Sinkronisasi langsung berjalan di server cloud GitHub Actions tanpa perlu perangkat/laptop owner menyala.
- **Jadwal Cron Otomatis Cloud**: Workflow berjalan otomatis setiap 3 jam selama jam operasional studio pada pukul **09:00, 12:00, 15:00, 18:00, dan 21:00 WIB** (`0 2,5,8,11,14 * * *` UTC). Dilengkapi silent background auto-polling setiap 60 detik di web client dan state sync 15 menit di Railway 24/7.

### 5. Larangan Fitur Terminal:
- Fitur Terminal View (Bloomberg style/trading) dilarang dimasukkan ke repositori ini. Repositori Foxe Studio murni fokus pada aplikasi manajemen keuangan studio foto.
- Topbar atas wajib bersih dan mempertahankan tag `#tbUpd`, `#tbLive`, serta tombol `#btnSyncWeb`.
- Fungsi `render()` JavaScript wajib menyertakan guard `if(up)`.

### 6. Format Struk Telegram (Estimate Omzet Akhir Bulan):
- Di dalam struk ringkasan harian Telegram (blok `<pre>`), tepat di bawah `ESTIMASI NETT PROFIT` dan sebelum garis penutup `============================================`, wajib menyertakan section **Estimate Omzet Sampai Akhir Bulan** yang menyatu di dalam struk:
  * `Unrealized Cash In : Rp .....` (Total harga paket sesi booking terdaftar dari H+1 s.d. akhir bulan di File 2 Schedule)
  * `DP (-)             : Rp .....` (Total DP yang sudah diterima dari booking tersebut)
  * `Total              : Rp .....` (Sisa uang pelunasan yang riil akan masuk saat foto)
  * (baris kosong)
  * `Unrealized Omzet   : Rp .....` (Estimasi omzet akhir bulan = Omzet Realized MTD + Total Pelunasan)
- Format wajib rata kanan presisi 44 karakter mengikuti format struk.

### 7. Kewajiban Mutlak Mengirimkan Review Pekerjaan Terstruktur:
- **Setiap kali Agent selesai bekerja** (baik melalui trigger kata kunci `'ayo kerja'`, permintaan update fitur, perbaikan bug, atau sinkronisasi data), Agent **WAJIB MENYERTAKAN REVIEW PEKERJAAN TERSTRUKTUR** di akhir responnya.
- **Format Review Pekerjaan Wajib Mencakup:**
  1. **Rincian Pekerjaan Selesai**: Poin-poin spesifik apa saja yang baru saja dituntaskan atau diubah.
  2. **File & Komponen yang Diperbarui**: Daftar file script, JSON state, visual HTML, atau dokumen Obsidian yang mengalami perubahan.
  3. **Status Integrasi & Deploy**: Konfirmasi git commit & push ke GitHub Pages, serta status pengiriman Telegram.
  4. **Metrik & Highlight Operasional Terkini**: Ringkasan data penting (omzet, order, pipeline, ads, schedule besok) agar owner dapat memantau studio secara transparan dan jelas.

### 8. Integrasi Kalender Marketing & Meta Ads Tracker 2026/2027:
- Meta Ads Tracker mendukung pergantian multi-bulan dinamis: **Oktober 2026 (Live Tracker)** dan **September 2026 (Arsip)**.
- Section Marketing dilengkapi **Kalender Marketing & Boosting 2026/2027 (Agustus 2026 s.d. Juli 2027)** berisi 43 agenda momentum akademik dan seasonal kampus/sekolah (berdasarkan basis data 2.164 transaksi Semester 1 2026).
- Tabel dilengkapi filter kategori interaktif (*Semua*, *Event Day*, *Boost / Hard Push*, *H-7 Conversion*, *Awareness*) dan pencarian instan agenda/paket/kampus.

### 9. Aturan Mutlak Keselarasan Periode Bulan (Anti-Cross-Month Desync / Anti-Silang Bulan):
- **Konsistensi Bulan Tunggal (Single Source of Truth Bulan Aktif)**:
  - Bulan yang sedang aktif (`activeMonth` / `R.c.bulan`) **WAJIB MENJADI RUJUKAN TUNGGAL** untuk SELURUH section dashboard (Dashboard Utama, Neraca COGS/OPEX, Gaji Kru, Log Transaksi, Jadwal Ads, Rekap Shift, Estimasi Omzet, dll.).
  - **Prinsip Bebas Silang Bulan**:
    * Jika user memilih **Oktober 2026**, seluruh section (termasuk Jadwal Ads & Realized Ads dari Neraca) **WAJIB membuka dan menampilkan data Oktober 2026**.
    * Jika user memilih **September 2026**, seluruh section **WAJIB membuka dan menampilkan data September 2026**.
    * Begitu pula untuk bulan lainnya (Januari = Januari, Februari = Februari, dst.).
  - **DILARANG KERAS** menggunakan variabel state bulan lokal independen yang tidak tersinkronisasi (seperti `adsMonth`), ataupun melakukan fallback paksa data bulan lain jika data bulan yang dipilih belum ada (jika belum ada rencana, tampilkan status kosong / placeholder yang jujur).
  - Toggling periode pada sub-section (seperti tombol switch periode di Jadwal Ads atau Estimasi) harus otomatis memperbarui `activeMonth` dan merender ulang seluruh antarmuka secara harmonis.


