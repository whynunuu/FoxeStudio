# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"** (atau "update data", "sinkronkan data"), Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri:
1. Jalankan `python deep_sync_foxe.py`:
   - Unduh 7 File Operasional Resmi:
     * File 1 Log Order Sept: ID `1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ` (`file1.xlsm`)
     * File 1 Log Order Okt: ID `1xibgfKWJZWmcwh9lxR9Dt7IkHyMi7b75` (`file1_okt.xlsm`)
     * File 2 Schedule Sept: ID `14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I` (`file2.xlsx`)
     * File Neraca: ID `1dvnCNyfZI5z-12081XJjGCVLtMaQpUStYT61qU3orKM` (`file_neraca.xlsx`)
     * Schedule Reguler Oktober: ID `17QPAAhmPZqkomwajFhAw3JBmDyBFuklfNMqyVqlK484` (`file2_okt.xlsx`)
     * Wisuda UMP Hari 1 (3 Okt): ID `1sRILPoZD09Rm5aKn6tswNxvxOiRkSu4Z` (`file_wisuda_3okt.xlsx`)
     * Wisuda UMP Hari 2 (4 Okt): ID `1hDeuOh-6fnsP7vzWAl4HVwlYoEumu1hA` (`file_wisuda_4okt.xlsx`)
   - Hitung total shift aktual kru s.d. hari ini dari Log Order, deteksi cut-off dinamis (Sept: 30 Sep, Okt: 01 Okt).
   - Parse section `Detail` File Neraca (kolom P s.d. U) untuk klasifikasi COGS & OPEX serta Buku Detail Neraca (Debit/Kredit).
   - Parse Log Order & Pipeline Oktober: Realisasi live 1 booking DP (Rp 100 rb) via AMEL (2 shift) + 164 booking terdaftar (Potensi omzet Rp 59,15 jt, estimasi pelunasan Rp 47,80 jt).
   - Simpan `foxe_full_state.json`, rakit `index.html`, dan kirim notifikasi Telegram via `@NunuFxBot`.
   - Di dalam struk laporan Telegram (blok monospace), sertakan kalkulasi **Estimate Omzet Sampai Akhir Bulan** (Unrealized Cash In, DP (-), Total, dan Unrealized Omzet) yang menyatu di dalam struk di bawah Estimasi Nett Profit.
2. Jalankan git commit & push ke `origin main`:
   `git add foxe_full_state.json index.html assemble_app.py logo_foxe.png file1.xlsm file1_okt.xlsm file2.xlsx file_neraca.xlsx file2_okt.xlsx file_wisuda_3okt.xlsx file_wisuda_4okt.xlsx parser_neraca.py parser_schedule.py parser_log_order.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md VAULT.md`
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

### 5. Kebijakan Fitur Terminal:
- Fitur Terminal View (Bloomberg/trading terminal) **DILARANG & DIHAPUS PERMANEN** dari repositori Foxe Studio utama.
- Topbar harus tetap bersih, resmi, dan menyertakan elemen `#tbUpd`, `#tbLive`, dan tombol update `#btnSyncWeb`.
- Fungsi `render()` pada JavaScript wajib menyertakan pemeriksaan defensif `if(up)` agar tidak terjadi error `TypeError: null`.

### 6. Tombol Update Otomatis di Web & GitHub Actions:
- Topbar aplikasi web dilengkapi tombol **`🔄 Update`** yang bekerja dalam dua mode:
  1. **Fast Refresh**: Memeriksa `foxe_full_state.json` terbaru di GitHub repository tanpa membebani kuota API.
  2. **Cloud Sync**: Memanggil GitHub API `workflow_dispatch` untuk memicu `.github/workflows/daily_sync.yml`. Sinkronisasi langsung berjalan di server cloud GitHub Actions tanpa perlu perangkat/laptop owner menyala.
- **Jadwal Cron Otomatis Cloud**: Workflow berjalan otomatis setiap hari pada pukul **09:00 WIB** (pagi studio buka) dan **21:00 WIB** (malam rekap closing).

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

### 9. Integrasi Kalender Marketing & Meta Ads Tracker 2026/2027:
- Meta Ads Tracker mendukung pergantian multi-bulan dinamis: **Oktober 2026 (Live Tracker)** dan **September 2026 (Arsip)**.
- Section Marketing dilengkapi **Kalender Marketing & Boosting 2026/2027 (Agustus 2026 s.d. Juli 2027)** berisi 43 agenda momentum akademik dan seasonal kampus/sekolah (berdasarkan basis data 2.164 transaksi Semester 1 2026).
- Tabel dilengkapi filter kategori interaktif (*Semua*, *Event Day*, *Boost / Hard Push*, *H-7 Conversion*, *Awareness*) dan pencarian instan agenda/paket/kampus.

