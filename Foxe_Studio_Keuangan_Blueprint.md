# 📘 FOXE STUDIO KEUANGAN — MASTER REPLICA BLUEPRINT & SYSTEM SPECIFICATION
> **Dokumentasi Komprehensif Arsitektur Sistem, SOP Operasional, R-C-T-O Framework, Flow Kerja, Project Tree, dan PRD**  
> **Versi:** 3.2.0 (Production Master) | **Klasifikasi:** Sistem Keuangan & Otomasi Studio Foto  
> **Target Penggunaan:** Deployment Ulang Cabang / Kloning Repositori / Integrasi AI Agent

---

## DAFTAR ISI
1. [Executive Summary](#1-executive-summary)
2. [MD: Master Operational & Autonomous Workflow Rules](#2-md-master-operational--autonomous-workflow-rules)
3. [R-C-T-O Framework (Kerangka Kerja Prompt AI Agent)](#3-r-c-t-o-framework-kerangka-kerja-prompt-ai-agent)
4. [Gambaran Flow Kerja & Arsitektur Pipeline (End-to-End)](#4-gambaran-flow-kerja--arsitektur-pipeline-end-to-end)
5. [Project Tree & Penjelasan Modul Repositori](#5-project-tree--penjelasan-modul-repositori)
6. [Product Requirement Document (PRD) Resmi](#6-product-requirement-document-prd-resmi)
7. [Panduan Langkah-Demi-Langkah Duplikasi & Setup Proyek](#7-panduan-langkah-demi-langkah-duplikasi--setup-proyek)

---

## 1. EXECUTIVE SUMMARY
**Foxe Studio Keuangan** adalah sistem automasi pelaporan keuangan, rekonsiliasi kasir, pemantauan pipeline jadwal, dan *CRM lead follow-up* berbasis serverless static web application. Sistem ini dirancang untuk studio foto komersial profesional dengan karakteristik perputaran kas cepat, skema Down Payment (DP) berjangka, multi-kategori layanan (Studio Reguler vs Event Wisuda Massal), dan manajemen honor shift kru lapangan.

### Pilar Utama Solusi:
- **Biaya Infrastruktur Nol (Zero Hosting Cost)**: Frontend static SPA di-host di GitHub Pages dengan kompilasi state JSON tunggal (*Single Source of Truth*).
- **Automasi Tanpa Perangkat Lokal Menyala**: Workflow dijalankan di cloud via GitHub Actions crons (08:30, 12:00, 15:00, 18:00, 21:00, 21:30 WIB) dan background worker Railway 24/7.
- **Integritas Kasir "Zero-Guesswork"**: Mengaudit keselarasan $\text{Kas Tunai} + \text{Transfer Bank} = \text{Total Omzet}$ dengan batas toleransi selisih maksimum Rp 1.000.
- **Anti-Ghost Slot & Recovery DP**: Menyaring slot jadwal batal/reschedule (label Orange) agar sisa pelunasan tidak *double-count*, namun mempertahankan masa aktif DP klien selama 30 hari di CRM.

---

## 2. MD: MASTER OPERATIONAL & AUTONOMOUS WORKFLOW RULES

Dokumen ini berfungsi sebagai aturan memori mutlak (`AGENTS.md` / `SYSTEM_RULES.md`) bagi Autonomous AI Agent:

### A. Trigger Kata Kunci Eksekusi: "ayo kerja"
Jika pengguna mengirimkan perintah `"ayo kerja"`, `"update data"`, atau `"sinkronkan data"`, Agent **HARUS LANGSUNG mengeksekusi pipeline kerja lengkap** secara mandiri tanpa memerlukan konfirmasi manual tambahan:
1. **Jalankan Ingestion & Parser Pipeline (`python deep_sync_foxe.py`)**:
   - Unduh berkas operasional Google Drive (Log Order, Schedule Reguler, Schedule Wisuda, Neraca Biaya).
   - Hitung total shift aktual kru s.d. cut-off hari ini dari Log Order kasir.
   - Parse section `Detail` File Neraca (kolom P s.d. U) untuk klasifikasi COGS & OPEX serta Buku Detail Neraca (Debet/Kredit).
   - Parse Log Order & Pipeline Booking: Hitung omzet cash/transfer, uang muka DP, dan sisa pelunasan terverifikasi.
   - **Optimasi Data Historis**: Gunakan cache instan `historical_cache.json` (< 0.01 detik) untuk bulan closed-books (Januari s.d. Agustus). Dilarang men-scan ulang arsip lama.
   - Satukan seluruh data ke dalam file `foxe_full_state.json`.
   - Rakit ulang antarmuka web visual via `python assemble_app.py` -> `index.html`.
   - Kirim notifikasi ringkasan struk closing ke Telegram Bot (@NunuFxBot).
2. **Auto-Deploy ke Remote Repository**:
   ```bash
   git add foxe_full_state.json index.html assemble_app.py file*.xlsx file*.xlsm parser_*.py deep_sync_foxe.py telegram_notifier.py AGENTS.md GEMINI.md PRD.md
   git commit -m "Auto-sync data update"
   git push origin main
   ```
3. **Tampilkan Ringkasan Metrik Hari Berjalan & Tautan Live Web**:
   - URL Dashboard: `https://[username].github.io/[repo]/` (Terproteksi PIN Default: `363636`).

### B. Aturan Mutlak Desain & Arsitektur Dashboard
1. **Laporan Tahunan & Seasonality Index (Landing View #1)**:
   - Berposisi di urutan teratas navigasi dan menjadi tampilan pembuka default saat web pertama kali dimuat.
   - **Anti-Fabrikasi Data**: Bulan sebelum periode aktif (Januari–Agustus) dan sesudah bulan berjalan (November–Desember) WAJIB DIKOSONGKAN (`—`) dengan status badge `Belum Dicocokkan`.
   - Bulan aktif berjalan menampilkan data riil live terverifikasi (`R.omzet`, run-rate, live dot berdenyut, badge `Berjalan (Terverifikasi)`).
   - Bulan pipeline menampilkan booking terdaftar (badge `Pipeline`, potensi omzet, estimasi pelunasan).
   - Matriks Seasonality Index 12 bulan menggunakan benchmark historis studio (garis tengah 1.00×, Super Peak 2.10×).
2. **Konsistensi Periode Bulan Tunggal (Anti-Cross-Month Desync)**:
   - Bulan yang sedang aktif (`activeMonth`) WAJIB menjadi rujukan tunggal untuk seluruh section dashboard (Dashboard Utama, Neraca COGS/OPEX, Gaji Kru, Log Transaksi, Jadwal Ads, Rekap Shift, Estimasi Omzet).
   - Dilarang keras menampilkan data bulan silang tanpa perpindahan konteks eksplisit oleh pengguna.
3. **Standar Tata Letak Fit-In & Anti-Tabrakan (Rule 4)**:
   - Kontainer utama `.view`: `max-width: 1600px; width: 100%; margin: 0 auto; padding: 28px 32px 80px;`.
   - Grid layout: Responsif `repeat(auto-fit, minmax(360px, 1fr))` dengan breakpoint di `1080px`.
   - Tipografi angka KPI besar: `clamp(20px, 1.9vw, 31px)` dengan `text-overflow: ellipsis`.
   - Kontainer Scrollable: Seluruh tabel panjang (Log Order, Detail Neraca, Leads, Jadwal) **WAJIB dibungkus kontainer scrollable** (`max-height: 460px – 520px; overflow-y: auto;`) dengan sticky table header (`thead`).
4. **Standarisasi 5 Kode Warna Sel Schedule (Anti-Ghost Slot)**:
   - ⚪ **Putih / No Fill** (`FFFFFFFF` / `00000000`): **Slot Kosong** (Available untuk booking baru).
   - 🟢 **Hijau** (`FF00FF00`): **Slot Terisi (Confirmed Booking)**. Booking sah terjadwal, masuk penuh ke dalam potensi pipeline dan estimasi pelunasan (*cash-in*).
   - 🔵 **Cyan / Biru** (`FF00FFFF`): **Selesai / Sedang Sesi / Hadir (Live Case)**. Klien sudah datang di studio, sesi berlangsung atau sudah selesai, uang direalisasikan di kasir.
   - 🟠 **Orange** (`FFFF9900`): **Kendala Jadwal (Reschedule / Telat / CLOSED)**. Sisa pelunasan dinetralkan (`Rp 0`), namun **DP TETAP BERLAKU 30 HARI** sejak tanggal aslinya dan dialihkan ke Pipeline Recovery CRM.
   - 🔴 **Merah** (`FFFF0000` / `FFF4CCCC`): **Full Slot / Batas Operasional**. Kuota ditutup atau penanda batas jam kerja studio.
5. **Kebijakan Keamanan UI (Modal Konfirmasi Universal & Format Rupiah)**:
   - Seluruh aksi simpan edit dan tombol hapus (`✕`) wajib memunculkan dialog konfirmasi universal (`#confModal`).
   - Format mata uang baku: `Rp X.XXX.XXX`.

### C. Protokol Foxe Sentry & Eskalasi Jam Malam
- **Jadwal Audit**: Pre-opening (08:30 WIB), Closing (21:30 WIB), Dry-run (00:00 WIB).
- **Kebijakan Zero-Guesswork**: Jika terjadi error teknis, file korup, atau anomali kasir (selisih Kas + Transfer ≠ Omzet > Rp 1.000, kru asing tak dikenal, kebocoran tanggal), agen **DILARANG MENEBAK**. Agen wajib menahan `git push` dan mengirim laporan insiden darurat ke Telegram Owner (@NunuFxBot).

---

## 3. R-C-T-O FRAMEWORK (KERANGKA KERJA PROMPT AI AGENT)

Struktur prompt sistem terstandarisasi untuk mengontrol agen AI otonom:

| Komponen | Definisi & Spesifikasi Teknis |
| :--- | :--- |
| **[R] ROLE** | **Autonomous Financial CFO & Systems Architect AI.** Bertanggung jawab menjaga integritas pembukuan kasir, akuntansi biaya, kalkulasi sisa pelunasan jadwal, penyusunan dashboard visual, automasi CI/CD, dan eskalasi krisis operasional studio foto. |
| **[C] CONTEXT** | Studio foto beroperasi dengan 11 file Google Drive (Log Order harian, Schedule Reguler, Schedule Wisuda multi-backdrop, dan Neraca). Pembayaran klien terdiri dari DP saat booking dan pelunasan di hari foto. Studio memiliki periode normal dan Super Peak Wisuda (ratusan sesi/hari). Arsitektur serverless memanfaatkan Python CLI, JSON single source of truth, GitHub Pages, dan bot Telegram. |
| **[T] TASK** | 1. **Ingest & Parse**: Unduh file GDrive, ekstrak transaksi kasir, deteksi cut-off dinamis, parsing 5 warna sel jadwal, dan baca COGS/OPEX dari Neraca kolom P-U.<br/>2. **Audit & Reconcile**: Validasi $\text{Kas} + \text{Transfer} = \text{Omzet}$. Karantina slot reschedule Orange.<br/>3. **Compile State**: Susun `foxe_full_state.json` terpadu.<br/>4. **Render UI**: Jalankan `assemble_app.py` menghasilkan `index.html` dan `flow.html`.<br/>5. **Deploy & Notify**: Push ke GitHub Pages dan kirim struk monospace 44 karakter Telegram.<br/>6. **Sentry Nightly**: Audit konsistensi data jam malam. |
| **[O] OUTPUT** | 1. Berkas data: `foxe_full_state.json` bebas anomali.<br/>2. Antarmuka web: `index.html` interaktif sesuai Rule 4 Fit-in 1600px.<br/>3. Struk Telegram: Format monospace 44 karakter presisi dilengkapi section "Estimate Omzet Sampai Akhir Bulan".<br/>4. Review Pekerjaan Terstruktur: 5 poin wajib (Rincian Selesai, File Terupdate, Status Deploy, Highlight Metrik, dan Catatan Durasi Pengerjaan). |

---

## 4. GAMBARAN FLOW KERJA & ARSITEKTUR PIPELINE (END-TO-END)

### Arsitektur Pemrosesan Data:
```text
[Sumber Eksternal]
  ├─ Google Drive 11 File Excel (Log Order, Schedule, Wisuda, Neraca)
  └─ WhatsApp / CRM Prospek Masuk (Hot, Warm, Cold, Closed)
         │
         ▼
[Tahap 1: Ingestion Engine] -> deep_sync_foxe.py
  ├─ Unduh file live via Google Drive File ID
  ├─ Isolated Historical Reader -> historical_cache.json (Jan-Ags <0.01 detik)
  └─ Snapshot Fallback -> foxe_full_state.json.bak
         │
         ▼
[Tahap 2: Specialized Parser Matrix]
  ├─ parser_log_order.py   : Kas, Transfer, Booking DP, Diskon, Roster Shift Aktual
  ├─ parser_schedule.py    : Ekstraksi 5 Sandi Warna Sel (⚪, 🟢, 🔵, 🟠, 🔴)
  ├─ parser_neraca.py      : Klasifikasi COGS & OPEX (Kolom P-U), Debet/Kredit Kas
  └─ agentic_lead_engine.py: Perhitungan MTD Leads, Win Rate, Demand Analytics
         │
         ▼
[Tahap 3: Foxe Sentry Quality Gate] -> foxe_sentry.py
  ├─ Validasi Matematika   : Kas + Transfer == Total Omzet (Toleransi <= Rp 1.000)
  ├─ Validasi Warna        : Sisa Pelunasan Orange == Rp 0, Masa Aktif DP <= 30 Hari
  └─ Validasi Periode      : Anti-Cross-Month leak check
         │
         ├─── (Jika Anomali Terdeteksi) ───► [🚨 TELEGRAM ALERT: HOLD DEPLOY]
         │
         ▼ (Jika 100% Valid / All-Clear)
[Tahap 4: State Store & UI Compiler]
  ├─ Database Statis       : foxe_full_state.json (Single Source of Truth)
  └─ Compiler Visual       : assemble_app.py -> index.html (Dashboard Utama)
                                             -> flow.html (CRM Leads Engine)
         │
         ▼
[Tahap 5: Multi-Channel Distribution]
  ├─ GitHub Actions        : Git commit & push otomatis ke origin main (GitHub Pages)
  ├─ Telegram Bot          : Kirim struk closing harian (@NunuFxBot)
  ├─ Leads Auto-Reminder   : Kirim rekap Hot & Warm leads (10:00, 14:00, 20:00 WIB)
  └─ Railway 24/7 Worker   : Background polling & webhook standby
```

---

## 5. PROJECT TREE & PENJELASAN MODUL REPOSITORI

```text
FoxeStudio-Clone/
├── .github/
│   └── workflows/
│       ├── daily_sync.yml             # Cron sync 5x sehari (08:30, 12, 15, 18, 21 WIB)
│       ├── leads_reminder.yml         # Cron reminder follow-up leads (10, 14, 20 WIB)
│       └── nightly_sentry.yml         # Cron audit jam malam (21:30 & 00:00 WIB)
│
├── core_engine/
│   ├── deep_sync_foxe.py              # Orkestrator utama: download GDrive, parse, & trigger build
│   ├── build_full_state.py            # Penggabung objek JSON state terpadu
│   ├── assemble_app.py                # Compiler frontend visual HTML/CSS/JS & bumper BUILD_ID
│   └── foxe_sentry.py                 # Engine keamanan, audit kasir gantung & dispatcher krisis
│
├── parsers/
│   ├── parser_log_order.py            # Parser Log Order Kasir (Kas, Transfer, Shift kru, Cut-off)
│   ├── parser_schedule.py             # Parser Jadwal Reguler & Wisuda (Evaluasi 5 sandi warna)
│   ├── parser_neraca.py               # Parser Neraca (COGS, OPEX, Buku Detail Kas kolom P-U)
│   ├── parser_historical.py           # Parser kompilasi arsip closed-books (Jan–Ags)
│   └── agentic_lead_engine.py         # Engine analisis funnel CRM leads WhatsApp
│
├── notifiers/
│   ├── telegram_notifier.py           # Generator struk kasir monospace 44 kolom & Telegram API
│   ├── trigger_leads_reminder.py      # Pengirim pesan pengingat follow-up prospek studio
│   └── quota_notifier.py              # Monitor kuota booking & peringatan kapasitas shift
│
├── web/
│   ├── index.html                     # Dashboard Keuangan Utama (GitHub Pages Live SPA)
│   ├── flow.html                      # Dashboard CRM Prospek Leads & Analisis Permintaan
│   ├── logo_foxe.png                  # Identitas visual studio foto
│   └── favicon.ico                    # Ikon peramban web
│
├── state_and_cache/
│   ├── foxe_full_state.json           # Single Source of Truth live state
│   ├── foxe_full_state.json.bak       # Cadangan snapshot untuk pemulihan instan jika insiden
│   ├── historical_cache.json          # Cache arsip instan Jan–Ags (< 0.01 detik)
│   ├── marketing_calendar_2026.json   # Kalender momentum akademik 12 bulan & panduan boosting
│   └── leads_vault.json               # Basis data penyimpanan status prospek CRM
│
├── automation_scripts/
│   ├── Mulai_Sync_Otomatis.bat        # Skrip sekali klik untuk deep sync lokal
│   ├── Buka_Laporan_Foxe.bat          # Pintasan membuka web di Google Chrome
│   ├── Push_Ke_GitHub.bat             # Skrip deploy commit & push cepat
│   └── Set_Default_Browser_Chrome.bat # Utilitas konfigurasi lingkungan lokal
│
├── config_and_secrets/
│   ├── requirements.txt               # Dependensi pustaka Python
│   ├── railway.json                   # Konfigurasi container deploy 24/7 Railway
│   ├── Procfile                       # Spesifikasi proses runtime server
│   ├── .gitignore                     # Filter file rahasia agar tidak terunggah ke Git
│   └── telegram_config.example.json   # Template konfigurasi kredensial bot Telegram
│
└── docs_and_memory/
    ├── AGENTS.md                      # Aturan kerja agen AI & SOP operasional
    ├── GEMINI.md                      # Memori sistem & standarisasi anti-desync
    ├── PRD.md                         # Product Requirement Document resmi
    ├── FOXE_SENTRY.md                 # Spesifikasi teknis Foxe Sentry
    └── VAULT.md                       # Daftar Google Drive File ID & konstanta bisnis
```

---

## 6. PRODUCT REQUIREMENT DOCUMENT (PRD) RESMI

### 1. Document Control
- **Nama Produk**: Foxe Studio Keuangan & Operational Intelligence System
- **Versi**: 3.2.0 (Production Master)
- **Status**: Active / Production

### 2. Kebutuhan Fungsional (Functional Requirements)
- **FR-1 (Laporan Tahunan & Seasonality Index)**:
  * Menjadi landing view utama saat pertama kali membuka aplikasi.
  * Menghitung indeks musiman 12 bulan berpatokan pada garis tengah rata-rata 1.00×.
  * Menegakkan aturan anti-fabrikasi: bulan non-aktif wajib berstatus `Belum Dicocokkan`.
- **FR-2 (Rekonsiliasi Kasir & Log Order Real-Time)**:
  * Mengaudit formula: $\text{Omzet Realized} = \text{Kas Tunai} + \text{Transfer Bank}$.
  * Membedakan transaksi Down Payment (DP) dan pelunasan di studio.
- **FR-3 (Standarisasi 5 Warna Sel Jadwal & Anti-Ghost Slot)**:
  * ⚪ Putih: Slot kosong tersedia.
  * 🟢 Hijau: Booking terkonfirmasi (masuk estimasi pelunasan).
  * 🔵 Biru/Cyan: Hadir/Selesai di studio (terealisasi di kasir).
  * 🟠 Orange: Reschedule/Batal. Pelunasan dinetralkan Rp 0, **uang DP tetap berlaku 30 hari** dan dialihkan ke CRM Recovery.
  * 🔴 Merah: Penanda tutup sesi atau batas kuota.
- **FR-4 (Neraca COGS & OPEX Terpadu)**:
  * Mengambil biaya murni dari File Neraca kolom P s.d. U.
  * Memisahkan COGS (biaya cetak, pigura, honor fotografer) dan OPEX (listrik, sewa, ads, wifi).
  * Melampirkan Buku Detail Neraca mutasi debit/kredit per tanggal transaksi.
- **FR-5 (Roster Kru & Shift Payroll)**:
  * Menghitung total shift aktual fotografer dan asisten dari Log Order harian.
  * Mengalikan total shift dengan standar upah kru untuk estimasi pencadangan kas payroll.
- **FR-6 (CRM Leads & Analisis Permintaan)**:
  * Memetakan funnel konversi: Total Leads, Hot, Warm, Cold, Closed, dan Win Rate MTD.
  * Modul Demand Analytics memeringkat paket foto paling diminati (Wisuda, Family, Large Group, Self Photo).
- **FR-7 (Notifikasi Struk Telegram & Estimasi Omzet Akhir Bulan)**:
  * Mengirim struk monospace 44 karakter dengan format:
    - `Unrealized Cash In`: Total harga paket sesi booking terdaftar H+1 s.d. akhir bulan.
    - `DP (-)`: Total DP yang sudah masuk dari booking tersebut.
    - `Total`: Sisa uang pelunasan yang riil akan masuk saat sesi foto.
    - `Unrealized Omzet`: $\text{Omzet MTD Realized} + \text{Total Sisa Pelunasan}$.

### 3. Logika & Formula Finansial Baku
$$\begin{aligned}
\textbf{Omzet Realized (MTD)} &= \sum \text{Kas Tunai} + \sum \text{Transfer Bank} \\[4pt]
\textbf{Unrealized Cash-In} &= \sum_{\text{Slot Hijau}} \text{Harga Paket Booking H+1 s.d. Akhir Bulan} \\[4pt]
\textbf{Sisa Pelunasan Riil} &= \textbf{Unrealized Cash-In} - \sum_{\text{Slot Hijau}} \text{DP yang Diterima} \\[4pt]
\textbf{Estimasi Omzet Akhir Bulan} &= \textbf{Omzet Realized} + \textbf{Sisa Pelunasan Riil} \\[4pt]
\textbf{Estimasi Nett Profit} &= \textbf{Omzet Realized} - (\textbf{COGS} + \textbf{OPEX} + \textbf{Beban Shift Kru})
\end{aligned}$$

---

## 7. PANDUAN LANGKAH-DEMI-LANGKAH DUPLIKASI & SETUP PROYEK

1. **Buat Repositori Baru di GitHub**:
   - Beri nama (misal: `StudioKeuangan-Cabang2`).
   - Clone ke komputer lokal atau workspace agent.
2. **Setup Secrets & Environment Variables**:
   - Di tab **Settings > Secrets and variables > Actions**, tambahkan:
     * `TELEGRAM_BOT_TOKEN`: Token bot Telegram dari `@BotFather`.
     * `TELEGRAM_CHAT_ID`: ID grup/akun Telegram penerima notifikasi.
3. **Konfigurasi Berkas Spreadsheet Google Drive**:
   - Buat salinan 4 file utama: Log Order (`.xlsm`), Schedule Reguler (`.xlsx`), Schedule Wisuda (`.xlsx`), dan Neraca (`.xlsx`).
   - Ambil ID masing-masing file dari URL Google Drive:
     `https://docs.google.com/spreadsheets/d/[ID_FILE_DISINI]/edit`
   - Buka file `core_engine/deep_sync_foxe.py` dan sesuaikan pemetaan ID.
4. **Instal Dependensi & Jalankan Uji Coba Sinkronisasi**:
   ```bash
   pip install -r config_and_secrets/requirements.txt
   python core_engine/deep_sync_foxe.py
   python core_engine/assemble_app.py
   ```
5. **Aktifkan GitHub Pages**:
   - Masuk ke **Settings > Pages**.
   - Pilih Build and deployment: `Deploy from a branch` -> Branch `main` -> Folder `/ (root)`.
   - Simpan. Website dashboard Anda akan live dalam 1 menit!
