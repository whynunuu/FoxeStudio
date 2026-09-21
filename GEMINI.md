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
  `git add foxe_full_state.json index.html assemble_app.py file1.xlsm file2.xlsx file_neraca.xlsx parser_neraca.py deep_sync_foxe.py telegram_notifier.py`
  `git commit -m "Auto-sync data update"`
  `git push origin main`
- Remote URL: `https://github.com/whynunuu/FoxeStudio.git`

### 3. Berikan Laporan Ringkas, Kirim Telegram & Tautan Live:
- Kirim notifikasi otomatis laporan harian closing ke Telegram via `@NunuFxBot` (`telegram_notifier.py`) mencakup breakdown Kas/Transfer, Total COGS, OPEX, Estimasi Nett Profit, Leads, Shift Kru, dan Jadwal Foto Besok H+1.
- Sajikan tabel ringkasan: Cut-off hari ini, total order MTD, omzet MTD (Cash vs Transfer), omzet hari ini, shift kru, dan capaian target.
- Sertakan link website resmi live (terproteksi PIN: `202688`):
  👉 **https://whynunuu.github.io/FoxeStudio/**

---

## Standar Desain Visual & Larangan Sistem:
1. **Layout Fit-In & Anti-Tabrakan:**
   - `.view` menggunakan lebar adaptif `max-width: 1600px; width: 100%; margin: 0 auto;`.
   - Tabel Biaya Neraca menggunakan format **7 kolom responsif**: `Tgl | Deskripsi | Jenis | Kategori | Nilai | Status | Aksi`. Kolom Status dan tombol ✕ wajib terlihat utuh tanpa terpotong.
   - Grid `.two` dan `.three` wajib responsif (`minmax(360px, 1fr)`) dan breakpoint di 1080px agar tidak saling bertabrakan.
   - Angka KPI besar menggunakan `clamp(20px, 1.9vw, 31px)` dengan `text-overflow: ellipsis`.
2. **Larangan Fitur Terminal:**
   - Fitur Terminal View (Bloomberg style/trading) dilarang dimasukkan ke repositori ini. Repositori Foxe Studio murni fokus pada aplikasi manajemen keuangan studio foto.
   - Topbar atas wajib bersih dan mempertahankan tag `#tbUpd` serta `#tbLive`.
   - Fungsi `render()` JavaScript wajib menyertakan guard `if(up)`.
