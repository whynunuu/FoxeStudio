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

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Import parser modular (File 1, File 2, dan File Neraca)
from parser_log_order import parse_log_order
from parser_schedule import parse_schedule, parse_october_pipeline
from parser_neraca import parse_neraca

LOG_ORDER_FILE_ID = "1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ"
LOG_ORDER_OKT_FILE_ID = "1xibgfKWJZWmcwh9lxR9Dt7IkHyMi7b75"
SCHEDULE_SHEET_ID = "14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I"
NERACA_SHEET_ID = "1dvnCNyfZI5z-12081XJjGCVLtMaQpUStYT61qU3orKM"

# Sumber Jadwal Oktober 2026 (Reguler & Wisuda UMP 3 & 4 Okt)
SCHEDULE_OKT_SHEET_ID = "17QPAAhmPZqkomwajFhAw3JBmDyBFuklfNMqyVqlK484"
WISUDA_3OKT_FILE_ID = "1sRILPoZD09Rm5aKn6tswNxvxOiRkSu4Z"
WISUDA_4OKT_FILE_ID = "1hDeuOh-6fnsP7vzWAl4HVwlYoEumu1hA"

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
    try:
        base, ext = os.path.splitext(dest_path)
        tmp_dest = f"{base}_temp{ext}"
        with open(tmp_dest, "wb") as f:
            for chunk in res.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        if os.path.exists(dest_path):
            try:
                os.replace(tmp_dest, dest_path)
                print(f"[OK] Berhasil mengunduh {dest_path} ({os.path.getsize(dest_path)} bytes)")
                return dest_path
            except PermissionError:
                print(f"[WARN] {dest_path} sedang dibuka oleh Excel. Memakai hasil unduh live terbaru: {tmp_dest} ({os.path.getsize(tmp_dest)} bytes)")
                return tmp_dest
        else:
            os.rename(tmp_dest, dest_path)
            print(f"[OK] Berhasil mengunduh {dest_path} ({os.path.getsize(dest_path)} bytes)")
            return dest_path
    except Exception as e:
        print(f"[WARN] Gagal mengunduh {dest_path}: {e}. Memakai salinan lokal.")
        return dest_path

def download_gsheet(sheet_id, dest_path):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    try:
        res = requests.get(url, verify=False)
        if res.status_code == 200 and len(res.content) > 1000:
            base, ext = os.path.splitext(dest_path)
            tmp_dest = f"{base}_temp{ext}"
            with open(tmp_dest, "wb") as f:
                f.write(res.content)
            if os.path.exists(dest_path):
                try:
                    os.replace(tmp_dest, dest_path)
                    print(f"[OK] Berhasil mengunduh {dest_path} ({os.path.getsize(dest_path)} bytes)")
                    return dest_path
                except PermissionError:
                    print(f"[WARN] {dest_path} sedang dibuka oleh Excel. Memakai hasil unduh live terbaru: {tmp_dest} ({os.path.getsize(tmp_dest)} bytes)")
                    return tmp_dest
            else:
                os.rename(tmp_dest, dest_path)
                print(f"[OK] Berhasil mengunduh {dest_path} ({os.path.getsize(dest_path)} bytes)")
                return dest_path
        else:
            print(f"[WARN] Tidak dapat mengunduh Google Sheet {sheet_id} (status {res.status_code}). Memakai salinan lokal.")
            return dest_path
    except Exception as e:
        print(f"[WARN] Gagal mengunduh {dest_path}: {e}. Memakai salinan lokal.")
        return dest_path

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
        # STEP 4: Unduh sumber operasional resmi (Log Order, Schedule, Wisuda, dan Neraca)
        print("\n[1/5] Mengunduh sumber operasional (Log Order, Schedule, Wisuda, dan Neraca)...")
        p_f1 = download_gdrive(LOG_ORDER_FILE_ID, "file1.xlsm") or "file1.xlsm"
        p_f1_okt = download_gdrive(LOG_ORDER_OKT_FILE_ID, "file1_okt.xlsm") or "file1_okt.xlsm"
        p_f2 = download_gsheet(SCHEDULE_SHEET_ID, "file2.xlsx") or "file2.xlsx"
        p_neraca = download_gsheet(NERACA_SHEET_ID, "file_neraca.xlsx") or "file_neraca.xlsx"
        p_f2_okt = download_gsheet(SCHEDULE_OKT_SHEET_ID, "file2_okt.xlsx") or "file2_okt.xlsx"
        p_w3 = download_gsheet(WISUDA_3OKT_FILE_ID, "file_wisuda_3okt.xlsx") or "file_wisuda_3okt.xlsx"
        p_w4 = download_gsheet(WISUDA_4OKT_FILE_ID, "file_wisuda_4okt.xlsx") or "file_wisuda_4okt.xlsx"

        # STEP 5: Jalankan Parser File 1 (Log Order September & Oktober)
        print("\n[2/5] Menjalankan parser_log_order.py (File 1 September & Oktober)...")
        res_f1 = parse_log_order(p_f1, bulan="2026-09")
        print(f"[OK] File 1 Sept terurai: {len(res_f1['orders'])} transaksi, {len(res_f1['shifts'])} shift, {len(res_f1['cashControl'])} kontrol kas, {len(res_f1['leads'])} data lead.")
        
        res_f1_okt = parse_log_order(p_f1_okt, bulan="2026-10")
        print(f"[OK] File 1 Okt terurai: {len(res_f1_okt['orders'])} transaksi, {len(res_f1_okt['shifts'])} shift, cutoff {res_f1_okt['cutoff']}.")

        # STEP 6: Jalankan Parser File 2 (Schedule) & Merge Booking
        print("\n[3/5] Menjalankan parser_schedule.py (File 2)...")
        existing_bk = (state.get("schedule") or {}).get("bookings", [])
        res_f2_bookings = parse_schedule(p_f2, bulan="2026-09", existing_bookings=existing_bk)
        print(f"[OK] File 2 terurai: {len(res_f2_bookings)} jadwal booking studio.")

        # STEP 7: Jalankan Parser File Neraca (COGS, OPEX, Log Debit Kredit & Gaji Karyawan)
        print("\n[4/5] Menjalankan parser_neraca.py (File Neraca September & Oktober)...")
        actual_shifts_sep = {}
        for s in res_f1.get("shifts", []):
            nm = str(s.get("nama") or "").upper().strip()
            if nm:
                actual_shifts_sep[nm] = actual_shifts_sep.get(nm, 0) + s.get("slot", 1)

        actual_shifts_okt = {}
        for s in res_f1_okt.get("shifts", []):
            nm = str(s.get("nama") or "").upper().strip()
            if nm:
                actual_shifts_okt[nm] = actual_shifts_okt.get(nm, 0) + s.get("slot", 1)

        res_neraca_sep = parse_neraca(p_neraca, sheet_name="September 2026", actual_shifts=actual_shifts_sep)

        # Parse Oktober 2026 jika sheet ada di spreadsheet
        import openpyxl
        wb_nrc = openpyxl.load_workbook(p_neraca, read_only=True)
        res_neraca_okt = None
        if "Oktober 2026" in wb_nrc.sheetnames:
            res_neraca_okt = parse_neraca(p_neraca, sheet_name="Oktober 2026", actual_shifts=actual_shifts_okt)
            print(f"[OK] Sheet Oktober 2026 berhasil diikat: {len(res_neraca_okt['expenses'])} pos biaya, {len(res_neraca_okt['detail'])} mutasi detail, {len(res_neraca_okt['rosterGaji'])} karyawan roster.")
        wb_nrc.close()

        # Gabungkan struktur Neraca multi-bulan
        state["neracaByMonth"] = {
            "2026-09": res_neraca_sep,
            "2026-10": res_neraca_okt if res_neraca_okt else {"expenses": [], "detail": [], "summary": {}, "rosterGaji": [], "rosterSummary": {}}
        }

        all_expenses = list(res_neraca_sep.get("expenses", []))
        if res_neraca_okt:
            all_expenses.extend(res_neraca_okt.get("expenses", []))
        state["expenses"] = all_expenses

        state["rosterGajiByMonth"] = {
            "2026-09": res_neraca_sep.get("rosterGaji", []),
            "2026-10": res_neraca_okt.get("rosterGaji", []) if res_neraca_okt else []
        }

        # Simpan default untuk kompatibilitas
        state["neracaDetail"] = res_neraca_sep.get("detail", [])
        state["neracaSummary"] = res_neraca_sep.get("summary", {})
        state["rosterGaji"] = res_neraca_sep.get("rosterGaji", [])
        state["rosterSummary"] = res_neraca_sep.get("rosterSummary", {})
        neraca_count = len(state["expenses"])
        detail_count = len(state["neracaDetail"]) + (len(res_neraca_okt["detail"]) if res_neraca_okt else 0)
        gaji_count = len(state["rosterGaji"])

        # STEP 7.5: Jalankan Parser Schedule Pipeline Oktober 2026 (Reguler + Wisuda 3 & 4 Okt)
        print("\n[5/5] Menjalankan parse_october_pipeline()...")
        okt_pipeline = parse_october_pipeline(p_f2_okt, p_w3, p_w4)
        state["oktoberPipeline"] = okt_pipeline
        print(f"[OK] Pipeline Oktober terurai: {okt_pipeline['totalBookings']} booking terdaftar (Potensi: Rp {okt_pipeline['potentialOmzet']:,.0f}, Estimasi Pelunasan: Rp {okt_pipeline['estimateCashIn']:,.0f}).")

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
        state["oktoberLogOrder"] = res_f1_okt
        state["orders"] = res_f1["orders"] + res_f1_okt["orders"]
        state["shifts"] = res_f1["shifts"] + res_f1_okt["shifts"]
        state["cashControl"] = res_f1["cashControl"] + res_f1_okt["cashControl"]
        state["leads"] = res_f1["leads"] + [l for l in res_f1_okt["leads"] if l.get("transaksi") or l.get("dp") or l.get("leads")]
        state["kpi"] = res_f1["kpi"]

        # Injeksi otomatis Bonus KPI dari Sheet 9 ke Roster Gaji (Adif, Saka, Amel, Indah)
        kpi_list = state.get("kpi", [])
        if kpi_list and state.get("rosterGaji"):
            pool = 7000000.0
            bobot = 1.0 / len(kpi_list) if len(kpi_list) else 0.25
            kpi_cair_map = {}
            for kp in kpi_list:
                nm = str(kp.get("nama", "")).strip().upper()
                basic = float(kp.get("disiplin", 0) or 0)
                in_job = ((float(kp.get("akurasi", 0) or 0) + float(kp.get("sop", 0) or 0) + float(kp.get("client", 0) or 0) + float(kp.get("produktivitas", 0) or 0)) / 4.0) * 3.0
                op = basic + in_job + float(kp.get("referral", 0) or 0)
                b_cair = round((pool * bobot) * (op / 100.0))
                kpi_cair_map[nm] = b_cair

            for r in state["rosterGaji"]:
                rn = str(r.get("nama", "")).strip().upper()
                matched_kpi = 0
                for knm, bcair in kpi_cair_map.items():
                    if knm == rn or knm in rn or rn in knm:
                        matched_kpi = bcair
                        break
                r["bonus_kpi"] = float(matched_kpi)
                tot_gaji = float(r.get("total_gaji", 0) or 0)
                add = float(r.get("additional", 0) or 0)
                bon = float(r.get("bon", 0) or 0)
                bonus = float(r.get("bonus", 0) or 0)
                huk = float(r.get("hukuman", 0) or 0)
                r["thp"] = tot_gaji + float(matched_kpi) + add + bonus - huk - bon

            if "rosterSummary" in state:
                state["rosterSummary"]["total_bonus_kpi"] = sum(r.get("bonus_kpi", 0) for r in state["rosterGaji"])
                state["rosterSummary"]["grand_total_thp"] = sum(r.get("thp", 0) for r in state["rosterGaji"])

        state["baseline"] = state.get("baseline", {"label": "September 2025", "omzet": 88000000, "net": 35000000})
        state["history"] = state.get("history", [])
        state["ads"] = state.get("ads", {})
        state["adsByMonth"] = state.get("adsByMonth", {})
        state["marketingCalendar"] = state.get("marketingCalendar", [])
        state["schedule"] = {
            "bulan": "2026-09",
            "sumber": "Schedule September 2026 (Google Drive)",
            "lgPerOrang": 25000,
            "bookings": res_f2_bookings if res_f2_bookings else state.get("schedule", {}).get("bookings", [])
        }
        
        # Metadata Google Drive (File 1, File 2, dan File Neraca)
        state["gdrive"] = {
            "file1_id": LOG_ORDER_FILE_ID,
            "file1_okt_id": LOG_ORDER_OKT_FILE_ID,
            "file2_id": SCHEDULE_SHEET_ID,
            "file_neraca_id": NERACA_SHEET_ID,
            "last_sync": now.astimezone(datetime.timezone.utc).isoformat()
        }

        # STEP 11: Tutup sync -> status 'sukses'
        current_sync["status"] = "sukses"
        current_sync["ringkas"] = f"Integrasi berhasil: {len(res_f1['orders'])} order Sep, {len(res_f1_okt['orders'])} order Okt, {len(res_f2_bookings)} jadwal, {len(res_neraca)} pos pengeluaran Neraca, {okt_pipeline['totalBookings']} pipeline Okt."

        print("\n[5/5] Menyimpan state dan merender artefak...")
        with open("foxe_full_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print("[OK] foxe_full_state.json tersimpan.")

        # Render index.html
        import subprocess
        subprocess.run([sys.executable, "assemble_app.py"], check=True)
        print("[OK] index.html berhasil dirakit ulang!")

        # Salin ke direktori artifact conversation jika ada (lingkungan lokal Antigravity)
        for c_id in ["b33216a3-0a5f-4df8-aff3-aeef2408089b", "cab0ebc5-5150-4303-bbe6-c97db01a1692"]:
            art_dir = os.path.join(r"C:\Users\ASUS\.gemini\antigravity\brain", c_id)
            if os.path.exists(art_dir):
                target_file = os.path.join(art_dir, "foxe_studio_keuangan.html")
                shutil.copy("index.html", target_file)
                print(f"[OK] Artifact disalin ke: {target_file}")

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
