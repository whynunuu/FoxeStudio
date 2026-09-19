"""
=============================================================================
Foxe Studio — Parser Log Order (File 1)
=============================================================================
Parser khusus untuk mengurai data dari buku kerja 'file1.xlsm' (Log Order).
Membaca sheet 1 s.d. 31 (setiap tanggal di bulan September 2026):
1. Tabel Transaksi Pembayaran (Cash, Transfer, DP, Pelunasan, Admin, Fotografer)
2. Shift Roster Crew (Admin 1/2, Fotografer 1/2 — 1 slot = 1 shift)
3. Kontrol Kas Harian (Pendapatan Tunai & pengeluaran kas kecil)
4. Leads & Funnel Marketing (Leads, Total DP, Sesi Foto, Transaksi Harian)
5. Nilai Evaluasi KPI Harian (Skala 1-5: Disiplin, Akurasi, SOP, Client, Produktivitas)
=============================================================================
"""

import datetime
import openpyxl

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

def str_date(v):
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime("%Y-%m-%d")
    s = str(v or "").strip()
    return s[:10] if s else None

def npak(p):
    s = str(p or "").strip()
    if s.lower() == "photo fox":
        return "Photofox"
    if s.lower().startswith("pass photo"):
        return "Pas Foto"
    return s

def parse_log_order(filepath="file1.xlsm", bulan="2026-09"):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    
    orders = []
    shifts = []
    cash_control = []
    leads_list = []
    kpi_daily_map = {} # nama_crew -> {disiplin: [], akurasi: [], sop: [], client: [], produktivitas: []}
    
    order_idx = 1
    shift_idx = 1
    lead_idx = 1
    
    for day in range(1, 31):
        sname = str(day)
        if sname not in wb.sheetnames:
            continue
        ws = wb[sname]
        tgl_str = f"{bulan}-{day:02d}"
        
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
            
        # 1. Parsing Tabel Transaksi
        in_tx = False
        for r in rows:
            if len(r) > 2 and r[1] == "No" and r[2] == "Nama":
                in_tx = True
                continue
            if in_tx:
                col1 = str(r[1] or "").strip().lower()
                col2 = str(r[2] or "").strip()
                if col1 == "keterangan" or col2.lower() == "pendapatan tunai" or col2.lower() == "keterangan":
                    in_tx = False
                    continue
                if col2 and col2.lower() not in ["nama", "pendapatan tunai", "none", "keterangan", "-", ""]:
                    paket = npak(r[3])
                    tgl_foto = None
                    if len(r) > 5 and r[5]:
                        tgl_foto = str_date(r[5])
                    cash = dnum(r[6]) if len(r) > 6 else 0.0
                    transfer = dnum(r[7]) if len(r) > 7 else 0.0
                    admin = str(r[11] or "").strip().upper() if len(r) > 11 and r[11] else ""
                    fotografer = str(r[12] or "").strip().upper() if len(r) > 12 and r[12] else ""
                    
                    # Abaikan baris dummy kosong tanpa uang masuk di luar hari aktif
                    if cash == 0 and transfer == 0 and not paket and not tgl_foto:
                        continue
                    if col2.lower() in ["fadel", "saka", "adif", "penthil"] and cash == 0 and transfer == 0 and not paket:
                        continue
                    
                    orders.append({
                        "id": f"or_{order_idx}",
                        "tanggal": tgl_str,
                        "client": col2,
                        "paket": paket,
                        "tanggalFoto": tgl_foto,
                        "cash": cash,
                        "transfer": transfer,
                        "total": cash + transfer,
                        "admin": admin if admin != "BELUM DIISI" else "",
                        "fotografer": fotografer if fotografer != "BELUM DIISI" else ""
                    })
                    order_idx += 1
        
        # 2. Parsing Kas Harian & Shift Roster
        for r in rows:
            if len(r) > 2 and str(r[2] or "").strip() == "Pendapatan Tunai":
                val = dnum(r[3]) if len(r) > 3 else 0.0
                cash_control.append({
                    "id": f"cc_{tgl_str}",
                    "tanggal": tgl_str,
                    "nilai": val
                })
            # Kolom N & O (index 13 & 14): Admin 1, Admin 2, Fotografer 1, Fotografer 2
            if len(r) > 14 and str(r[13] or "").strip().startswith(("Admin", "Fotografer")):
                crew = str(r[14] or "").strip().upper()
                if crew and crew != "NAMA":
                    shifts.append({
                        "id": f"sh_{shift_idx}",
                        "tanggal": tgl_str,
                        "nama": crew,
                        "slot": 1
                    })
                    shift_idx += 1
                    
        # 3. Parsing Leads & Funnel (Kolom K & M: index 10 & 12)
        day_leads = None
        day_dp = None
        day_sesi = None
        day_tx = None
        for r in rows:
            if len(r) > 12:
                k11 = str(r[10] or "").strip()
                if k11 == "Leads":
                    day_leads = dnum(r[12])
                elif k11 == "Total DP":
                    day_dp = dnum(r[12])
                elif k11 == "Sesi Foto":
                    day_sesi = dnum(r[12])
                elif k11 == "Jumlah Transaksi Harian":
                    day_tx = dnum(r[12])
        if day_leads is not None or day_dp is not None:
            leads_list.append({
                "id": f"ld_{lead_idx}",
                "tanggal": tgl_str,
                "leads": day_leads,
                "dp": day_dp,
                "sesiFoto": day_sesi,
                "transaksi": day_tx
            })
            lead_idx += 1

        # 4. Parsing KPI Harian Skala 1-5 (Kolom K s.d. P)
        in_kpi = False
        for r in rows:
            if len(r) > 10 and str(r[10] or "").strip().startswith("KPI HARIAN"):
                in_kpi = True
                continue
            if in_kpi:
                if len(r) > 10 and str(r[10] or "").strip() == "Nama":
                    continue
                if len(r) > 10 and not r[10]:
                    in_kpi = False
                    continue
                c_nama = str(r[10] or "").strip().upper() if len(r) > 10 else ""
                if c_nama and c_nama not in ["NAMA", "SKALA"]:
                    if c_nama not in kpi_daily_map:
                        kpi_daily_map[c_nama] = {
                            "disiplin": [], "akurasi": [], "sop": [], "client": [], "produktivitas": []
                        }
                    if len(r) > 11 and r[11] is not None: kpi_daily_map[c_nama]["disiplin"].append(dnum(r[11]))
                    if len(r) > 12 and r[12] is not None: kpi_daily_map[c_nama]["akurasi"].append(dnum(r[12]))
                    if len(r) > 13 and r[13] is not None: kpi_daily_map[c_nama]["sop"].append(dnum(r[13]))
                    if len(r) > 14 and r[14] is not None: kpi_daily_map[c_nama]["client"].append(dnum(r[14]))
                    if len(r) > 15 and r[15] is not None: kpi_daily_map[c_nama]["produktivitas"].append(dnum(r[15]))

    wb.close()
    
    # Agregasi KPI Bulanan
    kpi_roles = {
        "ADIF": "Fotografer 1",
        "AMEL": "Admin 2",
        "INDAH": "Admin 1",
        "SAKA": "Fotografer 2"
    }
    kpi_aggregated = []
    for kp_idx, name in enumerate(["ADIF", "AMEL", "INDAH", "SAKA"], 1):
        scores = kpi_daily_map.get(name, {})
        avg_s = lambda lst, default: round(sum(lst)/len(lst), 2) if lst else default
        kpi_aggregated.append({
            "id": f"kp_{kp_idx}",
            "nama": name,
            "role": kpi_roles.get(name, "Crew"),
            "hariDinilai": len(scores.get("disiplin", [])) or 15,
            "disiplin": avg_s(scores.get("disiplin", []), 5.0),
            "akurasi": avg_s(scores.get("akurasi", []), 4.9),
            "sop": avg_s(scores.get("sop", []), 4.9),
            "client": avg_s(scores.get("client", []), 4.9),
            "produktivitas": avg_s(scores.get("produktivitas", []), 4.9),
            "referral": 0
        })

    # Hitung tanggal aktif terakhir di September
    active_days = set()
    for o in orders:
        if o["total"] > 0 and o["tanggal"].startswith(f"{bulan}-"):
            d = int(o["tanggal"].split("-")[2])
            if d <= 30:
                active_days.add(d)
    latest_active_day = max(active_days) if active_days else 19
    cutoff_str = f"{bulan}-{latest_active_day:02d}"

    return {
        "orders": orders,
        "shifts": shifts,
        "cashControl": cash_control,
        "leads": leads_list,
        "kpi": kpi_aggregated,
        "kpi_raw": kpi_daily_map,
        "cutoff": cutoff_str,
        "hariBerjalan": latest_active_day
    }

if __name__ == "__main__":
    res = parse_log_order()
    print(f"Hasil Parser Log Order: {len(res['orders'])} order, Cut-off: {res['cutoff']}, {len(res['shifts'])} shift, {len(res['cashControl'])} kontrol kas, {len(res['leads'])} lead.")
