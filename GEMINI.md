# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"** (atau variasi serupa seperti "update data", "sinkronkan data"), Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri dari awal hingga selesai tanpa perlu konfirmasi manual lagi:

### 1. Eksekusi Sinkronisasi Operasional Google Drive (`deep_sync_foxe.py`):
- Unduh & parse data operasional dari 3 sumber Google Drive resmi (File 3 / Rekap Global DI-SKIP):
  * **File 1 (Log Order `.xlsm`)**: ID `1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ` (transaksi pembayaran, akumulasi total shift aktual kru, kas harian, funnel leads marketing & KPI harian).
  * **File 2 (Schedule `.xlsx`)**: ID `14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I` (jadwal booking Studio 1, 2, 3 dan deteksi jadwal foto besok H+1).
  * **File Neraca (`.xlsx`)**: ID `1dvnCNyfZI5z-12081XJjGCVLtMaQpUStYT61qU3orKM` (pengeluaran operasional & produksi dari section `Detail` sheet September 2026, diklasifikasikan ke COGS & OPEX via `parser_neraca.py`).
- **Roster Shift:** Hitung akumulasi total shift slot aktual dari Log Order s.d. tanggal sekarang/cut-off.
- **ATURAN MUTLAK BIAYA:** Pengeluaran COGS & OPEX murni diambil dari section `Detail` File Neraca (kolom P s.d. U). JANGAN mengambil pengeluaran dari File Log Order karena referensinya berbeda.
- **SECTION TERPADU:** Section COGS dan OPEX digabung menjadi satu section resmi bernama **`Neraca (COGS & OPEX)`** yang dilengkapi **Buku Detail Neraca (Debit & Kredit)**.
- Deteksi cut-off dinamis (mengikuti tanggal transaksi aktif terbaru, misal: 21 September 2026).
- Simpan state gabungan ke `foxe_full_state.json`.
- Rakit ulang file visual `index.html` dan salin ke artefak `foxe_studio_keuangan.html`.

### 2. Auto-Commit & Deploy ke GitHub:
- Otomatis commit dan push pembaruan data ke repository:
  `git add foxe_full_state.json index.html assemble_app.py file1.xlsm file2.xlsx file_neraca.xlsx parser_neraca.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md VAULT.md`
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
  - Bulan sebelum dan sesudah September 2026 (Januari–Agustus & Oktober–Desember 2026) **WAJIB DIKOSONGKAN (`—`)** dengan status badge `<span class="pill neutral">Belum Dicocokkan</span>`.
  - Jangan pernah merekayasa atau membuat angka estimasi buatan untuk bulan-bulan unverified tersebut karena belum lulus rekonsiliasi data riil oleh owner.
  - **Hanya September 2026** yang terverifikasi aktif & live (`R.omzet`, proyeksi run-rate, indikator live dot, badge `<span class="pill crit">Berjalan (Terverifikasi)</span>`).
- **Seasonality Index 12 Bulan**:
  - Matriks Seasonality Index 12 bulan (Jan–Des) tetap aktif penuh menggunakan benchmark tahun 2025 (garis tengah 1.00× rata-rata, Super Peak September 2.10×).
  - Pada chart tahunan, batang 2026 HANYA dirender untuk bulan September.
- **12 Kotak Bulan Interaktif**:
  - Setiap kotak bulan dapat diklik untuk membuka section laporan bulanan (`view = "dash"`).

### 2. Layout Fit-In & Anti-Tabrakan:
- `.view` menggunakan lebar adaptif `max-width: 1600px; width: 100%; margin: 0 auto;`.
- Tabel Biaya Neraca menggunakan format **7 kolom responsif**: `Tgl | Deskripsi | Jenis | Kategori | Nilai | Status | Aksi`. Kolom Status dan tombol ✕ wajib terlihat utuh tanpa terpotong.
- Grid `.two` dan `.three` wajib responsif (`minmax(360px, 1fr)`) dan breakpoint di 1080px agar tidak saling bertabrakan.
- Angka KPI besar menggunakan `clamp(20px, 1.9vw, 31px)` dengan `text-overflow: ellipsis`.

### 3. Tombol Update Otomatis di Web & GitHub Actions:
- Topbar dilengkapi tombol **`🔄 Update`** yang bekerja dalam dua mode:
  1. **Fast Refresh**: Memeriksa `foxe_full_state.json` terbaru di GitHub repository tanpa membebani kuota API.
  2. **Cloud Sync**: Memanggil GitHub API `workflow_dispatch` untuk memicu `.github/workflows/daily_sync.yml`. Sinkronisasi langsung berjalan di server cloud GitHub Actions tanpa perlu perangkat/laptop owner menyala.
- **Jadwal Cron Otomatis Cloud**: Workflow berjalan otomatis setiap hari pada pukul **09:00 WIB** (pagi studio buka) dan **21:00 WIB** (malam rekap closing).

### 4. Larangan Fitur Terminal:
- Fitur Terminal View (Bloomberg style/trading) dilarang dimasukkan ke repositori ini. Repositori Foxe Studio murni fokus pada aplikasi manajemen keuangan studio foto.
- Topbar atas wajib bersih dan mempertahankan tag `#tbUpd`, `#tbLive`, serta tombol `#btnSyncWeb`.
- Fungsi `render()` JavaScript wajib menyertakan guard `if(up)`.

### 5. Format Struk Telegram (Estimate Omzet Akhir Bulan):
- Di dalam struk ringkasan harian Telegram (blok `<pre>`), tepat di bawah `ESTIMASI NETT PROFIT` dan sebelum garis penutup `============================================`, wajib menyertakan section **Estimate Omzet Sampai Akhir Bulan** yang menyatu di dalam struk:
  * `Unrealized Cash In : Rp .....` (Total harga paket sesi booking terdaftar dari H+1 s.d. akhir bulan di File 2 Schedule)
  * `DP (-)             : Rp .....` (Total DP yang sudah diterima dari booking tersebut)
  * `Total              : Rp .....` (Sisa uang pelunasan yang riil akan masuk saat foto)
  * (baris kosong)
  * `Unrealized Omzet   : Rp .....` (Estimasi omzet akhir bulan = Omzet Realized MTD + Total Pelunasan)
- Format wajib rata kanan presisi 44 karakter mengikuti format struk.
