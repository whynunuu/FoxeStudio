"""
=============================================================================
Foxe Studio — Foxe Sentry (System Reliability, Data Integrity & Security Agent)
=============================================================================
Tugas & Fungsi:
1. Memastikan semua flow operasional bebas error (GDrive, Parser, Math, Rules, Web).
2. Mengevaluasi integritas logika kasir (Anti-Silang Bulan, Anti-Ghost Slot, Balance).
3. "Zero Guesswork": Jika ada error atau agen bingung (anomali data ambigu),
   WAJIB langsung eskalasi lapor ke Owner lewat Telegram (@NunuFxBot).
4. Berjalan otomatis pada jadwal malam (21:30 WIB & 00:00 WIB) via GitHub Actions.
=============================================================================
"""

import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Import modul telegram resmi
try:
    from telegram_notifier import send_telegram_message, load_config
except ImportError:
    send_telegram_message = None
    load_config = lambda: {"token": "8809193335:AAER1t9MAnVSyIRJSWqHpFwaoFe4hYmcZ1s", "chat_id": 1608969830}

# 7 File Operasional Wajib
REQUIRED_OPERATIONAL_FILES = [
    ("file1.xlsm", "Log Order September 2026"),
    ("file1_okt.xlsm", "Log Order Oktober 2026"),
    ("file2.xlsx", "Schedule September 2026"),
    ("file_neraca.xlsx", "Neraca & Buku Kas Studio"),
    ("file2_okt.xlsx", "Schedule Reguler Oktober 2026"),
    ("file_wisuda_3okt.xlsx", "Schedule Wisuda UMP Hari 1 (3 Okt)"),
    ("file_wisuda_4okt.xlsx", "Schedule Wisuda UMP Hari 2 (4 Okt)"),
]

STATE_FILE = "foxe_full_state.json"
BACKUP_STATE_FILE = "foxe_full_state.json.bak"
INDEX_HTML = "index.html"
LIVE_URL = "https://whynunuu.github.io/FoxeStudio/"

# Master Roster Kru Dikenal Foxe
KNOWN_CREW_ROSTER = {
    "AMEL", "NUNU", "VINA", "NABILA", "FAUZAN", "FARID", "DWI", "BAGAS",
    "RIFKY", "REZA", "DIMAS", "KASIR", "ADMIN", "OWNER"
}


class FoxeSentry:
    def __init__(self, mode="audit"):
        self.mode = mode
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.critical_errors = []
        self.confusions_anomalies = []
        self.warnings = []
        self.passed_checks = []

    def log(self, tag, msg):
        print(f"[{tag}] {msg}")

    # =========================================================================
    # CHECKPOINT 1: Ingestion & Raw Excel Files Integrity
    # =========================================================================
    def check_cp1_files_integrity(self):
        self.log("CP-1", "Memeriksa integritas 7 File Operasional Resmi...")
        import openpyxl

        for fname, desc in REQUIRED_OPERATIONAL_FILES:
            if not os.path.exists(fname):
                self.critical_errors.append({
                    "cp": "CP-1 (Ingestion)",
                    "file": fname,
                    "desc": f"File operasional hilang: '{desc}' ({fname}) tidak ditemukan di disk.",
                    "action": "Jalankan 'python deep_sync_foxe.py' untuk mengunduh ulang dari Google Drive."
                })
                continue

            sz = os.path.getsize(fname)
            if sz < 1000:
                self.critical_errors.append({
                    "cp": "CP-1 (Ingestion)",
                    "file": fname,
                    "desc": f"Ukuran file mencurigakan / korup: {fname} hanya {sz} bytes (kemungkinan gagal download / 0 KB).",
                    "action": "Cek Google Drive API quota atau unduh ulang manual file tersebut."
                })
                continue

            # Verifikasi apakah file bisa dibuka openpyxl (read-only)
            try:
                wb = openpyxl.load_workbook(fname, read_only=True, data_only=True)
                sheets = wb.sheetnames
                wb.close()
                if not sheets:
                    self.critical_errors.append({
                        "cp": "CP-1 (Ingestion)",
                        "file": fname,
                        "desc": f"Workbook kosong tanpa sheet: {fname}.",
                        "action": "Verifikasi isi file excel."
                    })
                else:
                    self.passed_checks.append(f"File {fname} ({desc}) valid ({len(sheets)} sheets).")
            except Exception as e:
                self.critical_errors.append({
                    "cp": "CP-1 (Ingestion)",
                    "file": fname,
                    "desc": f"Gagal membaca format Excel pada {fname}: {str(e)}",
                    "action": "Pastikan file tidak terkunci oleh Excel desktop dan format xlsx/xlsm valid."
                })

    # =========================================================================
    # CHECKPOINT 2: State JSON & Schema Integrity
    # =========================================================================
    def check_cp2_state_integrity(self):
        self.log("CP-2", "Memeriksa skema dan konsistensi foxe_full_state.json...")
        if not os.path.exists(STATE_FILE):
            self.critical_errors.append({
                "cp": "CP-2 (State)",
                "file": STATE_FILE,
                "desc": "File state utama 'foxe_full_state.json' tidak ditemukan di direktori root.",
                "action": "Jalankan pipeline 'python deep_sync_foxe.py' untuk menghasilkan state."
            })
            return None

        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception as e:
            self.critical_errors.append({
                "cp": "CP-2 (State)",
                "file": STATE_FILE,
                "desc": f"File JSON corrupt atau sintaks rusak: {str(e)}",
                "action": "Gunakan backup foxe_full_state.json.bak atau generate ulang."
            })
            return None

        # Mandatory keys check
        required_keys = ["config", "orders", "shifts", "neracaDetail", "oktoberPipeline", "oktoberLogOrder"]
        missing_keys = [k for k in required_keys if k not in state]
        if missing_keys:
            self.critical_errors.append({
                "cp": "CP-2 (State)",
                "file": STATE_FILE,
                "desc": f"Kunci state wajib hilang: {', '.join(missing_keys)}",
                "action": "Sinkronkan ulang state via deep_sync_foxe.py."
            })
        else:
            self.passed_checks.append(f"Skema foxe_full_state.json lengkap ({len(state)} keys terdaftar).")

        return state

    # =========================================================================
    # CHECKPOINT 3: Reconcile Kasir & Math Sanity ("Anti-Broken Math")
    # =========================================================================
    def check_cp3_reconcile_and_math(self, state):
        if not state:
            return

        self.log("CP-3", "Mengaudit rekonsiliasi kasir dan matematika keuangan...")
        
        # 1. Audit September Orders
        sep_orders = state.get("orders", [])
        if sep_orders:
            tot_sep_omzet = 0
            tot_sep_cash = 0
            tot_sep_transfer = 0
            anomalous_orders = 0

            for o in sep_orders:
                tot = o.get("total", 0) or 0
                c = o.get("cash", 0) or 0
                t = o.get("transfer", 0) or 0

                if tot < 0:
                    anomalous_orders += 1

                tot_sep_omzet += tot
                tot_sep_cash += c
                tot_sep_transfer += t

            selisih_sep = abs(tot_sep_omzet - (tot_sep_cash + tot_sep_transfer))
            if selisih_sep > 1000:
                self.confusions_anomalies.append({
                    "cp": "CP-3 (Reconcile Sep)",
                    "type": "SELISIH KASIR GANTUNG",
                    "desc": (f"September: Total Omzet (Rp {tot_sep_omzet:,.0f}) tidak sinkron dengan "
                             f"Kas+Transfer (Rp {(tot_sep_cash + tot_sep_transfer):,.0f}). "
                             f"Selisih tidak bertuan: Rp {selisih_sep:,.0f}."),
                    "action": "Periksa kolom pembayaran kasir di file1.xlsm (Log Order Sept)."
                })
            else:
                self.passed_checks.append(f"September Reconciled: Rp {tot_sep_omzet:,.0f} (Selisih Rp {selisih_sep:,.0f}).")

            if anomalous_orders > 0:
                self.confusions_anomalies.append({
                    "cp": "CP-3 (Math Sanity)",
                    "type": "OMZET MINUS",
                    "desc": f"Ditemukan {anomalous_orders} order dengan nominal negatif di September.",
                    "action": "Cek input order apakah ada salah tanda minus."
                })

        # 2. Audit Oktober Orders
        okt_lo = state.get("oktoberLogOrder", {})
        okt_orders = okt_lo.get("orders", [])
        if okt_orders:
            tot_okt_omzet = 0
            tot_okt_cash = 0
            tot_okt_transfer = 0
            for o in okt_orders:
                tot = o.get("total", 0) or 0
                tot_okt_omzet += tot
                tot_okt_cash += (o.get("cash", 0) or 0)
                tot_okt_transfer += (o.get("transfer", 0) or 0)

            selisih_okt = abs(tot_okt_omzet - (tot_okt_cash + tot_okt_transfer))
            if selisih_okt > 1000:
                self.confusions_anomalies.append({
                    "cp": "CP-3 (Reconcile Okt)",
                    "type": "SELISIH KASIR OKTOBER",
                    "desc": (f"Oktober: Total Omzet (Rp {tot_okt_omzet:,.0f}) beda dengan "
                             f"Kas+Transfer (Rp {(tot_okt_cash + tot_okt_transfer):,.0f}). "
                             f"Selisih: Rp {selisih_okt:,.0f}."),
                    "action": "Periksa input pembayaran di file1_okt.xlsm."
                })
            else:
                self.passed_checks.append(f"Oktober Reconciled: Rp {tot_okt_omzet:,.0f} (Selisih Rp {selisih_okt:,.0f}).")

        # 3. Audit Neraca Detail Mutasi
        neraca_detail = state.get("neracaDetail", [])
        corrupted_neraca = 0
        for item in neraca_detail:
            debet = item.get("debet", 0) or 0
            kredit = item.get("kredit", 0) or 0
            if not isinstance(debet, (int, float)) or not isinstance(kredit, (int, float)):
                corrupted_neraca += 1

        if corrupted_neraca > 0:
            self.confusions_anomalies.append({
                "cp": "CP-3 (Neraca Audit)",
                "type": "DATA BIAYA CORRUPT",
                "desc": f"Terdapat {corrupted_neraca} baris di Neraca dengan debet/kredit non-numerik.",
                "action": "Periksa kolom nominal di file_neraca.xlsx (Sheet Detail)."
            })
        else:
            self.passed_checks.append(f"Buku Neraca Detail Valid ({len(neraca_detail)} mutasi tercatat).")

    # =========================================================================
    # CHECKPOINT 4: Business Logic & Schedule Rule Enforcement
    # =========================================================================
    def check_cp4_business_rules(self, state):
        if not state:
            return

        self.log("CP-4", "Mengaudit aturan bisnis, anti-silang bulan, dan anti-ghost slot...")
        
        # 1. Anti-Cross-Month Desync Check
        sep_orders = state.get("orders", [])
        leaked_to_sep = 0
        for o in sep_orders:
            tgl = str(o.get("tanggal", ""))
            # Jika ada tanggal berawalan 2026-10 di dalam order September
            if "2026-10" in tgl or "/10/2026" in tgl:
                leaked_to_sep += 1

        if leaked_to_sep > 0:
            self.confusions_anomalies.append({
                "cp": "CP-4 (Anti-Silang Bulan)",
                "type": "CROSS-MONTH DATA LEAK",
                "desc": f"Ditemukan {leaked_to_sep} transaksi bertanggal Oktober masuk ke tabel September!",
                "action": "Pisahkan data transaksi Oktober ke file1_okt.xlsm."
            })
        else:
            self.passed_checks.append("Anti-Silang Bulan: Nol kebocoran transaksi antar-bulan.")

        # 2. Anti-Ghost Slot & Standard Schedule Color Audit (Oktober Pipeline)
        pipeline = state.get("oktoberPipeline", {})
        bookings = pipeline.get("bookings", [])
        valid_statuses = {"terjadwal", "selesai", "hadir", "reschedule", "confirmed", "done"}
        unknown_status_count = 0
        leaked_orange_pelunasan = 0

        for b in bookings:
            st = str(b.get("status", "")).lower()
            if not any(v in st for v in valid_statuses):
                unknown_status_count += 1
            
            # Label Orange wajib dinetralkan sisa pelunasannya (tidak boleh dihitung cash-in hari berjalan)
            if "reschedule" in st or "orange" in st:
                sisa = b.get("sisa", 0) or 0
                if sisa > 0:
                    leaked_orange_pelunasan += sisa

        if leaked_orange_pelunasan > 0:
            self.confusions_anomalies.append({
                "cp": "CP-4 (Schedule Rule)",
                "type": "ORANGE SLOT OVERESTIMATION",
                "desc": (f"Booking berstatus Orange (Reschedule) masih memiliki estimasi pelunasan aktif "
                         f"sebesar Rp {leaked_orange_pelunasan:,.0f} yang belum dinetralkan."),
                "action": "Netralkan sisa pelunasan slot Orange menjadi Rp 0 sesuai Aturan 11."
            })
        else:
            self.passed_checks.append("Anti-Ghost Slot: Aturan proteksi DP 30 hari slot Orange patuh.")

        # 3. Unknown Crew Detection (Roster Sentry)
        shifts = state.get("shifts", [])
        for sh in shifts:
            nama = str(sh.get("nama", "")).strip().upper()
            if nama and nama not in KNOWN_CREW_ROSTER and (sh.get("total_shift", 0) or 0) > 0:
                self.warnings.append({
                    "cp": "CP-4 (Roster Kru)",
                    "type": "NAMA KRU BARU TERDETEKSI",
                    "desc": f"Kru '{nama}' aktif memiliki shift ({sh.get('total_shift')} shift) tapi belum ada di master roster.",
                    "action": "Tambahkan kru ke master gaji jika merupakan anggota tim resmi baru."
                })

    # =========================================================================
    # CHECKPOINT 5: Web Assembly & Live Deployment Ping
    # =========================================================================
    def check_cp5_web_and_live_ping(self):
        self.log("CP-5", "Memeriksa build index.html dan live endpoint...")

        # 1. Cek index.html lokal
        if not os.path.exists(INDEX_HTML):
            self.critical_errors.append({
                "cp": "CP-5 (Web Build)",
                "file": INDEX_HTML,
                "desc": "File frontend 'index.html' tidak ditemukan di root repositori.",
                "action": "Jalankan 'python assemble_app.py' untuk merakit ulang tampilan."
            })
        else:
            sz = os.path.getsize(INDEX_HTML)
            if sz < 20000:
                self.critical_errors.append({
                    "cp": "CP-5 (Web Build)",
                    "file": INDEX_HTML,
                    "desc": f"Ukuran index.html terlalu kecil ({sz} bytes). Kemungkinan gagal render.",
                    "action": "Rakit ulang via assemble_app.py."
                })
            else:
                self.passed_checks.append(f"Frontend index.html siap ({sz:,} bytes).")

        # 2. Ping Live GitHub Pages
        try:
            req = urllib.request.Request(LIVE_URL, headers={"User-Agent": "FoxeSentry/1.0"})
            with urllib.request.urlopen(req, timeout=10) as res:
                code = res.getcode()
                if code == 200:
                    self.passed_checks.append(f"Live Web Endpoint: HTTP {code} OK ({LIVE_URL}).")
                else:
                    self.warnings.append({
                        "cp": "CP-5 (Live Ping)",
                        "type": f"HTTP {code}",
                        "desc": f"Live URL mengembalikan status code tidak biasa: {code}",
                        "action": "Periksa tab deployment GitHub Pages."
                    })
        except Exception as e:
            self.warnings.append({
                "cp": "CP-5 (Live Ping)",
                "type": "CONNECTION TIMEOUT",
                "desc": f"Gagal ping ke live URL ({LIVE_URL}): {str(e)}",
                "action": "Periksa status internet atau server GitHub Pages."
            })

    # =========================================================================
    # DISPATCHER: Eskalasi Laporan ke Telegram (@NunuFxBot)
    # =========================================================================
    def dispatch_incident_report(self):
        if not send_telegram_message:
            self.log("SENTRY", "Modul send_telegram_message tidak tersedia.")
            return

        has_critical = len(self.critical_errors) > 0
        has_anomalies = len(self.confusions_anomalies) > 0

        # SKENARIO A: TECHNICAL CRITICAL FAILURE
        if has_critical:
            text = (
                "🚨 <b>[FOXE SENTRY: TECHNICAL FAILURE]</b> 🚨\n"
                f"<b>Waktu:</b> <code>{self.timestamp}</code>\n"
                "<b>Status:</b> CRITICAL ERROR DETECTED ❌\n\n"
                "<b>Rincian Masalah:</b>\n"
            )
            for err in self.critical_errors:
                text += f"• <b>[{err['cp']}]</b> {err['desc']}\n  👉 <i>Saran: {err['action']}</i>\n"

            text += (
                "\n<b>Tindakan Otomatis Agen:</b>\n"
                "⛔ <i>Auto-push DITAHAN untuk melindungi stabilitas website live.</i>\n"
                "Mohon periksa repository atau hubungi developer! 🛠️"
            )
            send_telegram_message(text)
            self.log("ALERT", "Pesan darurat Technical Failure terkirim ke Telegram.")
            return False

        # SKENARIO B: LOGIC ANOMALY / AGEN BINGUNG (HUMAN-IN-THE-LOOP)
        if has_anomalies:
            text = (
                "🤔 <b>[FOXE SENTRY: LOGIC ANOMALY / BINGUNG]</b> 🤔\n"
                f"<b>Waktu:</b> <code>{self.timestamp}</code>\n"
                "<b>Kategori:</b> KETIDAKSESUAIAN LOGIKA KASIR / DATA AMBIGU ⚖️\n\n"
                "<b>Temuan Sentry:</b>\n"
            )
            for anom in self.confusions_anomalies:
                text += f"• <b>[{anom['type']}]</b> {anom['desc']}\n  👉 <i>Perbaikan: {anom['action']}</i>\n"

            text += (
                "\n<b>Pertanyaan Sentry ke Owner:</b>\n"
                "<i>\"Apakah ada koreksi manual atau transaksi yang belum selesai input?\"</i>\n\n"
                "⏸️ <i>Update ditahan sementara agar angka kasir tidak saling bertabrakan.</i>"
            )
            send_telegram_message(text)
            self.log("ALERT", "Pesan eskalasi Anomali Kasir terkirim ke Telegram.")
            return False

        # SKENARIO C: ALL GREEN (NIGHTLY AUDIT PASSED)
        if self.mode in ["nightly", "verbose"]:
            text = (
                "🛡️ <b>[FOXE SENTRY: NIGHTLY AUDIT PASSED]</b> 🟢\n"
                f"<b>Waktu:</b> <code>{self.timestamp}</code>\n"
                "<b>Status:</b> SEMUA FLOW SEHAT & SIAP OPERASIONAL BESOK ✨\n\n"
                "<b>Checklist Keamanan:</b>\n"
            )
            for p in self.passed_checks:
                text += f" [OK] {p}\n"

            if self.warnings:
                text += "\n<b>Catatan Ringan:</b>\n"
                for w in self.warnings:
                    text += f" ⚠️ {w['desc']}\n"

            text += "\n<i>Semua sistem terjaga aman. Selamat beristirahat! 🌙</i>"
            send_telegram_message(text)
            self.log("ALERT", "Pesan konfirmasi All-Clear terkirim ke Telegram.")

        return True

    # =========================================================================
    # BACKUP & SELF-HEALING ENGINE
    # =========================================================================
    def execute_backup_state(self):
        """Membuat backup foxe_full_state.json.bak saat state dinyatakan 100% sehat."""
        if os.path.exists(STATE_FILE) and len(self.critical_errors) == 0 and len(self.confusions_anomalies) == 0:
            shutil.copy(STATE_FILE, BACKUP_STATE_FILE)
            self.log("BACKUP", f"Snapshot sehat tersimpan ke '{BACKUP_STATE_FILE}'.")

    def rollback_state_if_needed(self):
        """Mengembalikan backup jika state rusak."""
        if os.path.exists(BACKUP_STATE_FILE) and (len(self.critical_errors) > 0 or len(self.confusions_anomalies) > 0):
            shutil.copy(BACKUP_STATE_FILE, STATE_FILE)
            self.log("ROLLBACK", f"State dikembalikan dari '{BACKUP_STATE_FILE}' demi keselamatan kasir.")

    # =========================================================================
    # RUN AUDIT FLOW LENGKAP
    # =========================================================================
    def run_full_audit(self):
        print("=================================================================")
        print(f"🛡️  MEMULAI FOXE SENTRY AUDIT FLOW [{self.timestamp}]")
        print("=================================================================")

        # 1. CP-1 File Check
        self.check_cp1_files_integrity()

        # 2. CP-2 State Check
        state = self.check_cp2_state_integrity()

        # 3. CP-3 Math & Reconcile Check
        self.check_cp3_reconcile_and_math(state)

        # 4. CP-4 Business Rules & Schedule Guard
        self.check_cp4_business_rules(state)

        # 5. CP-5 Web & Live Ping
        self.check_cp5_web_and_live_ping()

        # Print Summary Console
        print("\n-----------------------------------------------------------------")
        print(f"Hasil Audit: Passed: {len(self.passed_checks)} | Warnings: {len(self.warnings)} | Anomalies: {len(self.confusions_anomalies)} | Critical: {len(self.critical_errors)}")
        print("-----------------------------------------------------------------")

        # Eskalasi Telegram jika ada masalah atau jika mode nightly
        success = self.dispatch_incident_report()

        if success:
            self.execute_backup_state()
            print("\n[OK] SENTRY STATUS: ALL CLEAR 🟢")
            return 0
        else:
            self.rollback_state_if_needed()
            print("\n[ALERT] SENTRY STATUS: INCIDENT ESCALATED 🚨")
            return 1


if __name__ == "__main__":
    mode_arg = "audit"
    if "--nightly" in sys.argv:
        mode_arg = "nightly"
    elif "--verbose" in sys.argv:
        mode_arg = "verbose"

    sentry = FoxeSentry(mode=mode_arg)
    exit_code = sentry.run_full_audit()
    sys.exit(exit_code)
