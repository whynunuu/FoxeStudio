"""
=============================================================================
Foxe Studio — Mesin Sinkronisasi & Integrasi Google Drive Utama
=============================================================================
Skrip utama yang mengorkestrasikan parser modular:
- parser_log_order.py (File 1)
- parser_schedule.py  (File 2)
- parser_master.py    (File 3)
Dan merakit hasilnya ke:
- foxe_full_state.json
- index.html (dan artifact foxe_studio_keuangan.html)
=============================================================================
"""

import os
import sys
import json
import datetime
import requests
import urllib3
import shutil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import parser modular (File 1, File 2, dan File Neraca)
from parser_log_order import parse_log_order
from parser_schedule import parse_schedule
from parser_neraca import parse_neraca

LOG_ORDER_FILE_ID = "1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ"
SCHEDULE_SHEET_ID = "14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I"
NERACA_SHEET_ID = "1dvnCNyfZI5z-12081XJjGCVLtMaQpUStYT61qU3orKM"

def download_gdrive(file_id, dest_path):
    session = requests.Session()
    session.verify = False
    url = "https://drive.google.com/uc?export=download"
    res = session.get(url, params={"id": file_id, "confirm": "t"}, stream=True)
    token = None
    for k, v in res.cookies.items():
        if k.startswith('download_warning'):
            token = v
            break
    if token:
        res = session.get(url, params={"id": file_id, "confirm": token}, stream=True)
    with open(dest_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
    print(f"[OK] Berhasil mengunduh {dest_path} ({os.path.getsize(dest_path)} bytes)")

def download_gsheet(sheet_id, dest_path):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    res = requests.get(url, verify=False)
    if res.status_code == 200 and len(res.content) > 1000:
        with open(dest_path, "wb") as f:
            f.write(res.content)
        print(f"[OK] Berhasil mengunduh {dest_path} ({os.path.getsize(dest_path)} bytes)")
        return True
    else:
        print(f"[WARN] Tidak dapat mengunduh Google Sheet {sheet_id} (status {res.status_code}). Memakai salinan lokal.")
        return False

def run_integration():
    print("==================================================")
    print("   FOXE STUDIO — DEEP GOOGLE DRIVE INTEGRATION   ")
    print("==================================================")
    now = datetime.datetime.now()
    now_iso = now.astimezone(datetime.timezone.utc).isoformat()
    sync_id = f"sy_{now.strftime('%Y%m%d-%H%M')}"
    print(f"Waktu mulai: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    state_file = "foxe_full_state.json"
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    if "sync" not in state:
        state["sync"] = []

    # STEP 3: Tulis sync status 'berjalan'
    current_sync = {
        "id": sync_id,
        "mulai": now_iso,
        "status": "berjalan",
        "ringkas": "Sinkronisasi sedang berlangsung..."
    }
    state["sync"].insert(0, current_sync)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    try:
        # STEP 4: Unduh sumber operasional resmi (File 1, File 2, dan File Neraca)
        print("\n[1/4] Mengunduh sumber operasional (Log Order, Schedule, dan Neraca)...")
        download_gdrive(LOG_ORDER_FILE_ID, "file1.xlsm")
        download_gsheet(SCHEDULE_SHEET_ID, "file2.xlsx")
        download_gsheet(NERACA_SHEET_ID, "file_neraca.xlsx")

        # STEP 5: Jalankan Parser File 1 (Log Order)
        print("\n[2/4] Menjalankan parser_log_order.py (File 1)...")
        res_f1 = parse_log_order("file1.xlsm", bulan="2026-09")
        print(f"[OK] File 1 terurai: {len(res_f1['orders'])} transaksi, {len(res_f1['shifts'])} shift, {len(res_f1['cashControl'])} kontrol kas, {len(res_f1['leads'])} data lead.")

        # STEP 6: Jalankan Parser File 2 (Schedule) & Merge Booking
        print("\n[3/4] Menjalankan parser_schedule.py (File 2)...")
        existing_bk = (state.get("schedule") or {}).get("bookings", [])
        res_f2_bookings = parse_schedule("file2.xlsx", bulan="2026-09", existing_bookings=existing_bk)
        print(f"[OK] File 2 terurai: {len(res_f2_bookings)} jadwal booking studio.")

        # STEP 7: Jalankan Parser File Neraca (COGS & OPEX dari Section Detail)
        print("\n[4/4] Menjalankan parser_neraca.py (File Neraca)...")
        res_neraca = parse_neraca("file_neraca.xlsx", sheet_name="September 2026")

        # STEP 8: Perbarui State Gabungan
        active_days = [int(o["tanggal"].split("-")[2]) for o in res_f1["orders"] if o["tanggal"].startswith("2026-09-") and int(o["tanggal"].split("-")[2]) <= 30]
        latest_day = max(active_days) if active_days else 19
        cutoff_date = f"2026-09-{latest_day:02d}"

        cfg = state.get("config", {})
        cfg["bulan"] = "2026-09"
        cfg["cutoff"] = cutoff_date
        cfg["status"] = "Progressive"
        if "targets" not in cfg:
            cfg["targets"] = [
                {"tier": 1, "omzet": 70000000, "persen": 0.05},
                {"tier": 2, "omzet": 85000000, "persen": 0.06},
                {"tier": 3, "omzet": 100000000, "persen": 0.07}
            ]
        state["config"] = cfg
        state["orders"] = res_f1["orders"]
        state["shifts"] = res_f1["shifts"]
        state["cashControl"] = res_f1["cashControl"]
        state["leads"] = res_f1["leads"] if res_f1["leads"] else state.get("leads", [])
        state["kpi"] = res_f1["kpi"]
        state["expenses"] = res_neraca  # COGS & OPEX terurai otomatis dari File Neraca
        state["baseline"] = state.get("baseline", {"label": "September 2025", "omzet": 88000000, "net": 35000000})
        state["history"] = state.get("history", [])
        state["ads"] = state.get("ads", [])
        state["schedule"] = {
            "bulan": "2026-09",
            "sumber": "Schedule September 2026 (Google Drive)",
            "lgPerOrang": 25000,
            "bookings": res_f2_bookings if res_f2_bookings else state.get("schedule", {}).get("bookings", [])
        }
        
        # Metadata Google Drive (File 1, File 2, dan File Neraca)
        state["gdrive"] = {
            "file1_id": LOG_ORDER_FILE_ID,
            "file2_id": SCHEDULE_SHEET_ID,
            "file_neraca_id": NERACA_SHEET_ID,
            "last_sync": now.astimezone(datetime.timezone.utc).isoformat()
        }

        # STEP 11: Tutup sync -> status 'sukses'
        current_sync["status"] = "sukses"
        current_sync["ringkas"] = f"Integrasi berhasil: {len(res_f1['orders'])} order, {len(res_f2_bookings)} jadwal, {len(res_neraca)} pos pengeluaran Neraca."

        print("\n[5/5] Menyimpan state dan merender artefak...")
        with open("foxe_full_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print("[OK] foxe_full_state.json tersimpan.")

        # Render index.html
        import subprocess
        subprocess.run([sys.executable, "assemble_app.py"], check=True)
        print("[OK] index.html berhasil dirakit ulang!")

        # Salin ke direktori artifact conversation jika ada (lingkungan lokal Antigravity)
        artifact_dir = r"C:\Users\ASUS\.gemini\antigravity\brain\cab0ebc5-5150-4303-bbe6-c97db01a1692"
        if os.path.exists(artifact_dir):
            artifact_target = os.path.join(artifact_dir, "foxe_studio_keuangan.html")
            shutil.copy("index.html", artifact_target)
            print(f"[OK] Artifact disalin ke: {artifact_target}")

        # Kirim notifikasi otomatis ke Telegram (jika bot & chat sudah terhubung)
        try:
            from telegram_notifier import send_telegram_message, build_summary_message
            tg_msg = build_summary_message(state)
            send_telegram_message(tg_msg)
        except Exception as tg_err:
            print(f"[WARN] Gagal kirim notifikasi Telegram: {tg_err}")

        print("\n==================================================")
        print("   INTEGRASI GOOGLE DRIVE BERHASIL LENGKAP!       ")
        print("==================================================")
    except Exception as e:
        print(f"\n[ERROR] Sinkronisasi terputus: {e}", file=sys.stderr)
        current_sync["status"] = "gagal"
        current_sync["ringkas"] = f"Gagal di tengah proses: {str(e)}"
        with open("foxe_full_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        raise

if __name__ == "__main__":
    run_integration()
