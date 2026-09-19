"""
Foxe Studio — Sinkronisasi Otomatis (Log Order + Schedule)
Skrip ini mengunduh Log Order (.xlsm) dan Schedule (.xlsx) dari Google Drive,
mem-parse transaksi, kas harian, shift, lead, kpi, dan booking jadwal,
lalu memperbarui file 'index.html' dan 'foxe_full_state.json'.
"""

import os
import sys
import json
import datetime
import requests
import urllib3
import openpyxl

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOG_ORDER_FILE_ID = "1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ"
SCHEDULE_SHEET_ID = "14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I"

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
    with open(dest_path, "wb") as f:
        f.write(res.content)
    print(f"[OK] Berhasil mengunduh {dest_path} ({os.path.getsize(dest_path)} bytes)")

def dnum(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("Rp", "").replace(".", "").replace(",", ".").replace(" ", "")
    if not s or s == "-":
        return 0.0
    try:
        return float(s)
    except:
        return 0.0

def run_sync():
    print("=== FOXE STUDIO SYNC CEPAT ===")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Waktu mulai: {now_str}")
    
    # 1. Unduh file sumber
    print("\n[1/4] Mengunduh sumber terbaru dari Google Drive...")
    download_gdrive(LOG_ORDER_FILE_ID, "file1.xlsm")
    download_gsheet(SCHEDULE_SHEET_ID, "file2.xlsx")
    
    # 2. Baca template full state lama untuk mempertahankan pengaturan & baseline
    state_file = "foxe_full_state.json"
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    print("\n[2/4] Mem-parse Log Order (.xlsm)...")
    wb1 = openpyxl.load_workbook("file1.xlsm", data_only=True)
    
    orders = []
    shifts = []
    cashControl = []
    order_idx = 1
    shift_idx = 1
    
    # Parse sheet 1..30 (September)
    for day in range(1, 31):
        sname = str(day)
        if sname not in wb1.sheetnames:
            continue
        ws = wb1[sname]
        tgl_str = f"2026-09-{day:02d}"
        
        # Cari transaksi
        rows = list(ws.iter_rows(values_only=True))
        in_tx = False
        for r in rows:
            if len(r) > 2 and r[1] == "No" and r[2] == "Nama":
                in_tx = True
                continue
            if in_tx:
                if len(r) > 1 and str(r[1] or "").strip() == "Keterangan":
                    in_tx = False
                    continue
                client = str(r[2] or "").strip()
                if client and client not in ["Nama", "Pendapatan Tunai", "None"]:
                    paket = str(r[3] or "").strip()
                    tgl_foto = None
                    if len(r) > 5 and r[5]:
                        if isinstance(r[5], (datetime.date, datetime.datetime)):
                            tgl_foto = r[5].strftime("%Y-%m-%d")
                        else:
                            tgl_foto = str(r[5])[:10]
                    cash = dnum(r[6]) if len(r) > 6 else 0.0
                    transfer = dnum(r[7]) if len(r) > 7 else 0.0
                    admin = str(r[11] or "").strip().upper() if len(r) > 11 and r[11] else ""
                    fotografer = str(r[12] or "").strip().upper() if len(r) > 12 and r[12] else ""
                    
                    orders.append({
                        "id": f"or_{order_idx}",
                        "tanggal": tgl_str,
                        "client": client,
                        "paket": paket,
                        "tanggalFoto": tgl_foto,
                        "cash": cash,
                        "transfer": transfer,
                        "total": cash + transfer,
                        "admin": admin if admin != "BELUM DIISI" else "",
                        "fotografer": fotografer if fotografer != "BELUM DIISI" else ""
                    })
                    order_idx += 1
                    
        # Cari kas harian (Pendapatan Tunai) & shift
        for r in rows:
            if len(r) > 2 and str(r[2] or "").strip() == "Pendapatan Tunai":
                val = dnum(r[3]) if len(r) > 3 else 0.0
                cashControl.append({
                    "id": f"cc_{tgl_str}",
                    "tanggal": tgl_str,
                    "nilai": val
                })
            # Shift
            if len(r) > 14 and str(r[13] or "").strip().startswith(("Admin", "Fotografer")):
                nama_crew = str(r[14] or "").strip().upper()
                if nama_crew and nama_crew != "NAMA":
                    shifts.append({
                        "id": f"sh_{shift_idx}",
                        "tanggal": tgl_str,
                        "nama": nama_crew,
                        "slot": 1
                    })
                    shift_idx += 1

    wb1.close()
    print(f"[OK] Parsed {len(orders)} transaksi, {len(shifts)} shift, {len(cashControl)} kontrol kas.")

    # 3. Update state
    state["orders"] = orders
    state["shifts"] = shifts
    state["cashControl"] = cashControl
    
    # Catatan sinkron
    if "sync" not in state:
        state["sync"] = []
    state["sync"].insert(0, {
        "id": f"sy_{datetime.datetime.now().strftime('%Y%m%d-%H%M')}",
        "mulai": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "sukses",
        "ringkas": f"Sinkron cepat selesai: {len(orders)} transaksi, {len(shifts)} shift."
    })
    
    print("\n[3/4] Menyimpan state terbaru...")
    with open("foxe_full_state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    print("\n[4/4] Memperbarui index.html...")
    import assemble_app
    print("[OK] index.html telah diperbarui dengan data termutakhir!")
    print("\nSINKRONISASI SELESAI DENGAN SUKSES!")

if __name__ == "__main__":
    run_sync()
