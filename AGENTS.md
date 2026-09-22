# Foxe Studio Keuangan — Memory & Workflow Rules

## Trigger Kata Kunci: "ayo kerja"
Jika USER mengirimkan instruksi **"ayo kerja"** (atau "update data", "sinkronkan data"), Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri:
1. Jalankan `python deep_sync_foxe.py`:
   - Unduh File 1 Log Order, File 2 Schedule, dan File Neraca dari Google Drive (File 3 Rekap Global DI-SKIP).
   - Hitung total shift aktual kru s.d. hari ini dari Log Order, deteksi cut-off dinamis.
   - Parse section `Detail` File Neraca (kolom P s.d. U) untuk klasifikasi COGS & OPEX serta Buku Detail Neraca (Debit/Kredit).
   - Simpan `foxe_full_state.json`, rakit `index.html`, dan kirim notifikasi Telegram via `@NunuFxBot`.
   - Di dalam struk laporan Telegram (blok monospace), sertakan kalkulasi **Estimate Omzet Sampai Akhir Bulan** (Unrealized Cash In, DP (-), Total, dan Unrealized Omzet) yang menyatu di dalam struk di bawah Estimasi Nett Profit.
2. Jalankan git commit & push ke `origin main`:
   `git add foxe_full_state.json index.html assemble_app.py file1.xlsm file2.xlsx file_neraca.xlsx parser_neraca.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md`
   `git commit -m "Auto-sync data update"`
   `git push origin main`
3. Tampilkan ringkasan metrik pembaruan hari ini dan tautan website live:
   👉 **https://whynunuu.github.io/FoxeStudio/** (PIN: `202688`)

---

## Aturan Mutlak Desain & Arsitektur Dashboard:

### 1. Struktur Section Neraca (COGS & OPEX):
- Section COGS dan OPEX digabung menjadi satu section resmi bernama **`Neraca (COGS & OPEX)`**.
- **Sumber Data Biaya:** Pengeluaran COGS & OPEX murni diambil dari section `Detail` File Neraca (kolom P s.d. U via `parser_neraca.py`). JANGAN mengambil dari File Log Order karena referensinya berbeda.
- Di bawah rekap COGS & OPEX, wajib menyertakan **Buku Detail Neraca (Debit & Kredit)** yang mencatat mutasi kas masuk, kas keluar, dan saldo berjalan per tanggal transaksi.

### 2. Standar Tampilan Fit-In & Anti-Tabrakan:
- **Lebar Kontainer (`.view`):** Gunakan `max-width: 1600px; width: 100%; margin: 0 auto; padding: 28px 32px 80px;`. JANGAN batasi ke 1200px kaku agar tidak muncul ruang hitam kosong di kanan layar.
- **Format Tabel Biaya 7 Kolom:**
  $$\text{Tgl} \ \mid\ \text{Deskripsi} \ \mid\ \text{Jenis} \ \mid\ \text{Kategori} \ \mid\ \text{Nilai} \ \mid\ \text{Status} \ \mid\ \text{Aksi}$$
  - Informasi vendor/metode bayar disatukan sebagai subteks halus di bawah Deskripsi.
  - Informasi cicilan/termin disatukan di bawah Nilai.
  - Kolom Status dan tombol hapus `✕` harus selalu terlihat utuh tanpa terpotong.
- **Pencegahan Benturan Grid (`.two` & `.three`):** Wajib menggunakan `repeat(auto-fit, minmax(360px, 1fr))` dengan breakpoint di `1080px` (otomatis menjadi 1 kolom tumpuk saat layar menyempit).
- **Tipografi KPI Adaptif:** Nilai uang besar pada `.stat .v` menggunakan `clamp(20px, 1.9vw, 31px)` dengan `text-overflow: ellipsis` agar tidak meluber keluar kotak kartu.
- **Wrapping Teks:** Jangan gunakan blanket `white-space: nowrap` pada semua `td`. Izinkan deskripsi membungkus alami (*wrap*), sementara angka `.n`, tanggal `.mono`, dan badge `.pill` tetap *nowrap*.

### 3. Kebijakan Fitur Terminal:
- Fitur Terminal View (Bloomberg/trading terminal) **DILARANG & DIHAPUS PERMANEN** dari repositori Foxe Studio utama.
- Topbar harus tetap bersih, resmi, dan menyertakan elemen `#tbUpd` dan `#tbLive`.
- Fungsi `render()` pada JavaScript wajib menyertakan pemeriksaan defensif `if(up)` agar tidak terjadi error `TypeError: null`.

### 4. Format Laporan Telegram (Estimate Omzet Akhir Bulan):
- Di dalam struk ringkasan harian Telegram (blok `<pre>`), tepat di bawah `ESTIMASI NETT PROFIT` dan sebelum garis penutup `============================================`, wajib menyertakan section **Estimate Omzet Sampai Akhir Bulan** yang menyatu di dalam struk:
  * `Unrealized Cash In : Rp .....` (Total harga paket sesi booking terdaftar dari H+1 s.d. akhir bulan di File 2 Schedule)
  * `DP (-)             : Rp .....` (Total DP yang sudah diterima dari booking tersebut)
  * `Total              : Rp .....` (Sisa uang pelunasan yang riil akan masuk saat foto)
  * (baris kosong)
  * `Unrealized Omzet   : Rp .....` (Estimasi omzet akhir bulan = Omzet Realized MTD + Total Pelunasan)
- Format harus sejajar rata kanan 44 karakter presisi mengikuti lebar struk kasir.
