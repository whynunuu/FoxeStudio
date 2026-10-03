# 🛡️ FOXE SENTRY — FLOW RELIABILITY & SECURITY AGENT BLUEPRINT
> **Misi Utama:** Memastikan seluruh rantai pipeline data Foxe Studio bebas error, menjaga integritas angka kasir, dan secara proaktif mengeskalasi anomali/kebingungan langsung ke Telegram Owner (@NunuFxBot) pada jadwal jam malam.

---

## 1. 📂 PROJECT TREE (Struktur Berkas Repositori)

```text
Foxe Agent/
├── 🤖 SENTRY CORE & PIPELINE
│   ├── foxe_sentry.py               # Engine Utama: Sentry Validator, JEV RAG Evaluator & Incident Dispatcher
│   ├── deep_sync_foxe.py            # Pipeline sinkronisasi data & build 7 file
│   ├── assemble_app.py              # Generator perakit file visual index.html
│   └── telegram_notifier.py         # Notifier resmi integrasi bot Telegram (@NunuFxBot)
│
├── ⚙️ PARSER MATRIX (Target Validasi)
│   ├── parser_log_order.py          # Parser Log Order Sept & Okt (Kas, Transfer, Booking)
│   ├── parser_schedule.py           # Parser Jadwal Reguler & Wisuda UMP (Deteksi Warna Sel)
│   └── parser_neraca.py             # Parser COGS, OPEX & Buku Detail Neraca (Debet/Kredit)
│
├── 📊 STATE & DEPLOYMENT ARTIFACTS
│   ├── foxe_full_state.json         # Single source of truth state data aktif
│   ├── foxe_full_state.json.bak     # Fallback snapshot jika terdeteksi anomali di jam malam
│   └── index.html                   # Dashboard web frontend resmi (GitHub Pages)
│
├── ⏰ AUTOMATION & SCHEDULE (Jam Malam)
│   └── .github/workflows/
│       ├── daily_sync.yml           # Auto-sync jam kerja (09:00, 12:00, 15:00, 18:00, 21:00 WIB)
│       ├── leads_reminder.yml       # Reminder leads hot/warm (10:00, 14:00, 20:00 WIB)
│       └── nightly_sentry.yml       # Audit Jam Malam Sentry (21:30 WIB & 00:00 WIB)
│
├── 📑 ATURAN BISNIS & MEMORY
│   ├── AGENTS.md                    # Aturan workflow & trigger operasional
│   ├── GEMINI.md                    # SOP & larangan sistem studio
│   └── FOXE_SENTRY.md               # Dokumentasi resmi arsitektur Sentry
│
└── 📁 OPERATIONAL RAW EXCEL (7 Sumber Data)
    ├── file1.xlsm                   # Log Order September 2026
    ├── file1_okt.xlsm               # Log Order Oktober 2026
    ├── file2.xlsx                   # Schedule September 2026
    ├── file2_okt.xlsx               # Schedule Reguler Oktober 2026
    ├── file_wisuda_3okt.xlsx        # Schedule Wisuda UMP Hari 1 (3 Okt)
    ├── file_wisuda_4okt.xlsx        # Schedule Wisuda UMP Hari 2 (4 Okt)
    └── file_neraca.xlsx             # Neraca Keuangan, Biaya COGS/OPEX & Kas
```

---

## 2. 🗺️ ARSITEKTUR ALUR KERJA (n8n Node & Sistem JEV RAG)

```text
[⏰ Cron Trigger: 21:30 & 00:00 WIB]
               │
               ▼
[Node 1: GDrive Ingestion Guard] ──────────(Error/Corrupt?)──────────► [📢 TELEGRAM ALERT]
               │ (Valid)
               ▼
[Node 2: Multi-Parser Syntax Guard] ───────(Sheet/Kolom Patah?)──────► [📢 TELEGRAM ALERT]
               │ (Valid)
               ▼
[Node 3: JEV RAG Anomaly Evaluator]
  ├─ Audit Matematika (Kas + Trf vs Omzet)
  ├─ Audit Standar Warna Sel Schedule (Anti-Ghost)
  ├─ Audit Masa Aktif DP Orange (30 Hari)
  └─ Audit Anti-Silang Bulan (Single Source)
               │
        ┌──────┴────────────────────────┐
   (Ada Selisih /                (Confidence 100%
    Agen Bingung)                   All Clear)
        │                               │
        ▼                               ▼
[📢 TELEGRAM ALERT:              [Node 4: Assembly & State Compiler]
 INCIDENT REPORT]                               │
(Eksekusi di-HOLD                               ▼
 Rollback ke .bak)               [Node 5: GitHub Pages & HTTP Ping]
                                                │
                                                ▼
                                 [Node 6: Nightly All-Green Log]
```

---

## 3. 🔍 5 CHECKPOINT AUDIT SENTRY

| Checkpoint | Target yang Diperiksa | Indikator Masalah (Trigger Alert) | Tindakan Sentry |
| :--- | :--- | :--- | :--- |
| **CP-1: GDrive Ingestion** | 7 File Resmi Google Drive | File 0 Byte, download time-out, file berubah jadi halaman HTML login GDrive | Stop pipeline, alert ke Telegram. |
| **CP-2: Parser Matrix** | Skema `foxe_full_state.json` | JSON rusak, kunci utama hilang, format array tidak valid | Tangkap exception, sebutkan file & baris error ke Telegram. |
| **CP-3: Reconcile Kasir** | Angka Uang & Mutasi | Total Omzet ≠ (Kas Tunai + Transfer Bank), selisih kasir gantung > Rp 1.000 | Tahan auto-commit, laporkan selisih nominal uang gantung. |
| **CP-4: Business Rules** | Jadwal & Roster Kru | Ada kebocoran transaksi antar-bulan, slot Orange bocor ke cash-in, kru asing tak dikenal | Flag anomali data, minta konfirmasi owner via Telegram. |
| **CP-5: Live Web Ping** | `https://whynunuu.github.io/FoxeStudio/` | Web mengembalikan status selain HTTP 200, atau file HTML lokal kosong | Laporkan status link web down ke Telegram. |

---

## 4. 🧠 MATRIKS "KONDISI AGEN BINGUNG" (Zero Guesswork Policy)

Agen dilarang keras mengarang atau berasumsi jika menjumpai kondisi berikut:
1. **Selisih Angka Kasir Tak Bertuan:**
   * Contoh: Log Order mencatat total transaksi Rp 1.500.000, namun rincian kasir Kas + Transfer hanya Rp 1.200.000 (Selisih Rp 300.000 tidak jelas).
2. **Entitas Kru Baru di Lapangan:**
   * Muncul kru baru di kolom jadwal yang tidak cocok dengan master data honor shift kasir.
3. **Penyusupan Booking Antar Bulan (Cross-Month Clash):**
   * Transaksi berlabel Oktober tanpa sengaja tersimpan di sheet September atau sebaliknya.
4. **Fluktuasi Omzet Ekstrem Tanpa Catatan:**
   * Omzet harian anjlok drastis ke 0 atau melonjak ratusan persen tanpa adanya jadwal event wisuda.

---

## 5. 📢 FORMAT TEMPLATE PESAN TELEGRAM (@NunuFxBot)

### Skenario A: Terjadi Error Teknis / Crash
```text
🚨 [FOXE SENTRY: TECHNICAL FAILURE] 🚨
Waktu: 2026-10-03 21:32:10 WIB
Status: CRITICAL ERROR DETECTED ❌

Rincian Masalah:
• [CP-1 (Ingestion)] File operasional hilang: 'Neraca & Buku Kas Studio' (file_neraca.xlsx).
  👉 Saran: Jalankan 'python deep_sync_foxe.py' untuk mengunduh ulang.

Tindakan Otomatis Agen:
⛔ Auto-push DITAHAN untuk melindungi stabilitas website live.
Mohon periksa repository atau hubungi developer! 🛠️
```

### Skenario B: Terjadi Anomali Logika / "Agen Bingung"
```text
🤔 [FOXE SENTRY: LOGIC ANOMALY / BINGUNG] 🤔
Waktu: 2026-10-03 21:35:45 WIB
Kategori: KETIDAKSESUAIAN LOGIKA KASIR / DATA AMBIGU ⚖️

Temuan Sentry:
• [SELISIH KASIR GANTUNG] September: Total Omzet (Rp 2.450.000) tidak sinkron dengan Kas+Transfer (Rp 2.150.000). Selisih tidak bertuan: Rp 300.000.
  👉 Perbaikan: Periksa kolom pembayaran kasir di file1.xlsm.

Pertanyaan Sentry ke Owner:
"Apakah ada koreksi manual atau transaksi yang belum selesai input?"

⏸️ Update ditahan sementara agar angka kasir tidak saling bertabrakan.
```

### Skenario C: Status Malam Sempurna (All-Clear)
```text
🛡️ [FOXE SENTRY: NIGHTLY AUDIT PASSED] 🟢
Waktu: 2026-10-03 22:00:00 WIB
Status: SEMUA FLOW SEHAT & SIAP OPERASIONAL BESOK ✨

Checklist Keamanan:
 [OK] File file1.xlsm (Log Order September 2026) valid.
 [OK] Skema foxe_full_state.json lengkap.
 [OK] September Reconciled: Rp 47,800,000.
 [OK] Anti-Silang Bulan: Nol kebocoran transaksi antar-bulan.
 [OK] Anti-Ghost Slot: Aturan proteksi DP 30 hari slot Orange patuh.
 [OK] Live Web Endpoint: HTTP 200 OK (https://whynunuu.github.io/FoxeStudio/).

Semua sistem terjaga aman. Selamat beristirahat! 🌙
```

---

## 6. ⏰ JADWAL CRON MALAM (GitHub Actions)

File: `.github/workflows/nightly_sentry.yml`
* **Jadwal 1 (21:30 WIB / 14:30 UTC):** Audit closing harian Foxe Studio.
* **Jadwal 2 (00:00 WIB / 17:00 UTC):** Midnight dry-run & kesiapan operasional hari berikutnya.

---

## 7. 🛡️ SELF-HEALING & SAFETY ROLLBACK

Jika audit menemukan error atau ketidakcocokan logika kasir:
1. `foxe_sentry.py` mengembalikan exit code 1 dan membatalkan push commit.
2. Snapshot `foxe_full_state.json.bak` siap dikembalikan jika file JSON utama korup.
3. Website kasir `index.html` terproteksi 100% dari *blank page* atau *unhandled exception*.
