"""
=============================================================================
Foxe Studio — Parser Schedule Booking (File 2)
=============================================================================
Parser khusus untuk mengurai jadwal booking studio dari 'file2.xlsx' (Schedule).
Membaca sheet 'Tanggal 1' s.d. 'Tanggal 31':
1. Memindai 3 Blok Studio:
   - Studio 1: Kolom 1 s.d. 6  (No, Waktu, Nama, Paket, Admin, No.HP)
   - Studio 2: Kolom 7 s.d. 12 (No, Waktu, Nama, Paket, Admin, No.HP)
   - Studio 3: Kolom 13 s.d. 18 (No, Waktu, Nama, Paket, Admin, No.HP)
2. Normalisasi nama paket & penentuan harga:
   - Large Group dinamis: 'LG <n>' / 'Large Group <n>' = n × Rp25.000 (min 7)
   - Paket standar (Graduation, Couple, Photofox, Pas Foto, dsb.)
3. Mempertahankan booking berstatus manual: true jika terjadi bentrok.
=============================================================================
"""

import re
import datetime
import openpyxl

PRICING_TABLE = {
    "Graduation": 350000,
    "Graduation Premium": 500000,
    "Large Group": 25000, # per orang (min 7)
    "Single": 100000,
    "Couple A": 150000,
    "Couple B": 200000,
    "Couple C": 400000,
    "Photofox": 200000,
    "Photo Fox": 200000,
    "Family A": 350000,
    "Family B": 450000,
    "Maternity": 350000,
    "Studio Rent": 450000,
    "Pas Foto": 50000,
    "All File": 100000,
    "All Soft File": 50000,
    "Add Cetak": 25000,
    "Add Edit": 50000,
    "Packing": 20000
}

def str_time(v):
    if isinstance(v, datetime.time):
        return v.strftime("%H:%M")
    if isinstance(v, datetime.datetime):
        return v.strftime("%H:%M")
    return str(v or "").strip()

def npak(p):
    s = str(p or "").strip()
    if s.lower() == "photo fox":
        return "Photofox"
    if s.lower().startswith("pass photo"):
        return "Pas Foto"
    return s

def extract_schedule_color(cell):
    """
    Ekstraksi status warna sel KHUSUS File SCHEDULE:
    - PUTIH  : Kosong (No fill / 00000000 / FFFFFFFF)
    - HIJAU  : Isi / Confirmed Booking (FF00FF00 dsb)
    - BIRU   : Selesai / Sedang Sesi / Hadir (FF00FFFF / Cyan / Biru)
    - ORANGE : Reschedule / Telat / Tidak Datang / CLOSED (FFFF9900 dsb)
    - MERAH  : Full Slot / Batas Order (FFFF0000 dsb)
    """
    if not cell or not cell.fill or not cell.fill.start_color:
        return "PUTIH"
    sc = cell.fill.start_color
    rgb = getattr(sc, 'rgb', None)
    if not rgb:
        return "PUTIH"
    rgb_str = str(rgb).upper()
    if rgb_str in ['00000000', 'FFFFFFFF', 'NONE']:
        return "PUTIH"
    if rgb_str in ['FF00FF00', 'FF00FF7F', 'FF90EE90', 'FF00E676', 'FF93C47D']:
        return "HIJAU"
    if rgb_str in ['FF00FFFF', 'FF9FC5E8', 'FF4A86E8', 'FF6D9EEB', 'FF00B0F0', 'FF00B0FF', 'FF29B6F6', 'FF03A9F4']:
        return "BIRU"
    if rgb_str in ['FFFF9900', 'FFE69138', 'FFF9CB9C', 'FFFFB74D', 'FFFFA726', 'FFFF9800', 'FFFB8C00']:
        return "ORANGE"
    if rgb_str in ['FFFF0000', 'FFCC0000', 'FFE06666', 'FFF4CCCC', 'FFEF5350', 'FFE53935']:
        return "MERAH"
    return "PUTIH"

def parse_schedule(filepath="file2.xlsx", bulan="2026-09", existing_bookings=None):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    
    manual_map = {}
    if existing_bookings:
        for b in existing_bookings:
            if b.get("manual"):
                k = f"{b.get('tgl')}|{b.get('nama','').strip().lower()}|{b.get('waktu')}"
                manual_map[k] = b

    bookings = []
    b_idx = 1
    
    for day in range(1, 32):
        sname = f"Tanggal {day}"
        if sname not in wb.sheetnames:
            continue
        ws = wb[sname]
        tgl_str = f"{bulan}-{day:02d}"
        
        studios = [(1, "Studio 1"), (7, "Studio 2"), (13, "Studio 3")]
        for c_start, studio_name in studios:
            for r in range(3, ws.max_row + 1):
                c_nama_cell = ws.cell(r, c_start + 2)
                nama_val = c_nama_cell.value
                if not nama_val:
                    continue
                nama = str(nama_val).strip()
                if not nama or nama.lower() in ["nama", "none", "-"]:
                    continue
                
                # Deteksi warna sel schedule
                col = extract_schedule_color(c_nama_cell)
                if col == "PUTIH":
                    col = extract_schedule_color(ws.cell(r, c_start + 1))
                if col == "PUTIH":
                    col = extract_schedule_color(ws.cell(r, c_start))
                
                # Filter 1: Merah = batas order/full slot (bukan order klien)
                if col == "MERAH":
                    continue
                
                waktu = str_time(ws.cell(r, c_start + 1).value)
                paket_raw = str(ws.cell(r, c_start + 3).value or "").strip()
                admin = str(ws.cell(r, c_start + 4).value or "").strip().upper()
                hp = str(ws.cell(r, c_start + 5).value or "").strip()
                
                # Filter 2: Orange bertuliskan CLOSED/batal
                if col == "ORANGE" and (nama.lower() in ["closed", "tutup", "cancel", "batal"] or "closed" in paket_raw.lower()):
                    continue
                
                # Cek manual override
                m_key = f"{tgl_str}|{nama.lower()}|{waktu}"
                if m_key in manual_map:
                    bookings.append(manual_map[m_key])
                    continue
                
                # Status Sesi berdasarkan Kode Warna Schedule
                if col == "BIRU":
                    status_sesi = "done"
                    status_label = "Selesai / Hadir"
                    status_badge = "crit"
                elif col == "ORANGE":
                    status_sesi = "reschedule"
                    status_label = "Reschedule / Kendala"
                    status_badge = "warn"
                else:
                    status_sesi = "confirmed"
                    status_label = "Terjadwal"
                    status_badge = "prog"

                # Hitung harga paket
                paket_std = npak(paket_raw)
                harga = 0.0
                jml_orang = 1
                
                # Cek Large Group (misal: "LG 10", "Large Group 15")
                lg_match = re.search(r'(?:lg|large\s*group)\s*(\d+)', paket_raw, re.IGNORECASE)
                if lg_match:
                    paket_std = "Large Group"
                    jml_orang = int(lg_match.group(1))
                    harga = max(7, jml_orang) * 25000.0
                elif paket_std in PRICING_TABLE:
                    harga = float(PRICING_TABLE[paket_std])
                elif "wisuda" in paket_raw.lower() or "grad" in paket_raw.lower():
                    paket_std = "Graduation"
                    harga = 350000.0
                elif "couple" in paket_raw.lower():
                    paket_std = "Couple A"
                    harga = 150000.0
                elif "group" in paket_raw.lower():
                    paket_std = "Large Group"
                    harga = 175000.0
                else:
                    harga = 0.0
                
                bookings.append({
                    "id": f"sc_bk_{b_idx}",
                    "tgl": tgl_str,
                    "waktu": waktu,
                    "studio": studio_name,
                    "studioNama": studio_name,
                    "nama": nama,
                    "paket": paket_std,
                    "paketRaw": paket_raw,
                    "jmlOrang": jml_orang,
                    "harga": harga,
                    "admin": admin,
                    "noHp": hp,
                    "manual": False,
                    "color": col,
                    "statusColor": col.lower(),
                    "statusSesi": status_sesi,
                    "statusLabel": status_label,
                    "statusBadge": status_badge,
                    "isDone": col == "BIRU",
                    "isReschedule": col == "ORANGE"
                })
                b_idx += 1

    wb.close()
    return bookings

def parse_wisuda_schedule(filepath, tgl_str, kategori="Wisuda UMP", start_id=1):
    import os
    if not os.path.exists(filepath):
        return []
    
    wb = openpyxl.load_workbook(filepath, data_only=True)
    if "GRADUATION UMP" in wb.sheetnames:
        ws = wb["GRADUATION UMP"]
    else:
        ws = wb.active
    
    # Deteksi nama spot secara dinamis dari Baris 3
    spots = []
    for s_idx in range(5):
        base_c = s_idx * 6 + 1
        s_val = ws.cell(3, base_c).value
        if s_val and str(s_val).strip():
            spots.append(str(s_val).strip().upper())
        else:
            default_spots = ['LIMBO', 'WOODEN', 'CONCRETE', 'DIPAN', 'CALMBLUE']
            spots.append(default_spots[s_idx] if s_idx < len(default_spots) else f"SPOT_{s_idx+1}")
    
    bookings = []
    b_idx = start_id
    for r in range(11, ws.max_row + 1):
        for s_idx, s_name in enumerate(spots):
            base_c = s_idx * 6 + 1
            c_nama_cell = ws.cell(r, base_c + 2)
            nama_val = c_nama_cell.value
            if not nama_val:
                continue
            nama = str(nama_val).strip()
            if not nama or nama.lower() in ["nama", "none", "-", "closed"]:
                continue
            
            # Deteksi warna sel schedule
            col = extract_schedule_color(c_nama_cell)
            if col == "PUTIH":
                col = extract_schedule_color(ws.cell(r, base_c + 1))
            if col == "PUTIH":
                col = extract_schedule_color(ws.cell(r, base_c))
            
            # Filter 1: Merah = batas order/kuota
            if col == "MERAH":
                continue
            
            waktu_val = ws.cell(r, base_c + 1).value
            waktu = str_time(waktu_val)
            paket_raw = str(ws.cell(r, base_c + 3).value or "Graduation").strip()
            admin = str(ws.cell(r, base_c + 4).value or "").strip().upper()
            hp = str(ws.cell(r, base_c + 5).value or "").strip()
            
            # Filter 2: Orange bertuliskan CLOSED
            if col == "ORANGE" and (nama.lower() in ["closed", "tutup", "cancel", "batal"] or "closed" in paket_raw.lower()):
                continue
            
            # Status Sesi berdasarkan Kode Warna Schedule
            if col == "BIRU":
                status_sesi = "done"
                status_label = "Selesai / Hadir"
                status_badge = "crit"
            elif col == "ORANGE":
                status_sesi = "reschedule"
                status_label = "Reschedule / Kendala"
                status_badge = "warn"
            else:
                status_sesi = "confirmed"
                status_label = "Terjadwal"
                status_badge = "prog"

            paket_std = npak(paket_raw)
            if "prem" in paket_raw.lower():
                paket_std = "Graduation Premium"
                harga = 500000.0
            elif "lg" in paket_raw.lower() or "large" in paket_raw.lower():
                m_lg = re.search(r'(?:lg|large\s*group)\s*(\d+)', paket_raw.lower())
                if m_lg:
                    jml = int(m_lg.group(1))
                    paket_std = f"Large Group {jml}"
                    harga = max(7, jml) * 25000.0
                else:
                    paket_std = "Large Group"
                    harga = 175000.0
            elif "wisuda" in paket_raw.lower() or "grad" in paket_raw.lower():
                paket_std = "Graduation"
                harga = 350000.0
            elif paket_std in PRICING_TABLE:
                harga = float(PRICING_TABLE[paket_std])
            else:
                harga = 350000.0
            
            dp = 0.0
            m = re.search(r'dp\s*(\d+)', hp.lower())
            if m:
                dp = float(m.group(1)) * 1000
            elif "lunas" in hp.lower():
                dp = harga
            
            bookings.append({
                "id": f"sc_wisuda_{tgl_str}_{b_idx}",
                "tgl": tgl_str,
                "waktu": waktu,
                "studio": f"{kategori} ({s_name})",
                "studioNama": f"Spot {s_name}",
                "spot": s_name,
                "nama": nama,
                "paket": paket_std,
                "paketRaw": paket_raw,
                "jmlOrang": 1,
                "harga": harga,
                "dp": dp,
                "sisaPelunasan": max(0.0, harga - dp),
                "admin": admin,
                "noHp": hp,
                "manual": False,
                "kategori": kategori,
                "color": col,
                "statusColor": col.lower(),
                "statusSesi": status_sesi,
                "statusLabel": status_label,
                "statusBadge": status_badge,
                "isDone": col == "BIRU",
                "isReschedule": col == "ORANGE"
            })
            b_idx += 1
            
    wb.close()
    return bookings

def parse_september_wisuda(f_uin1="file_wisuda_uin_1sep.xlsx", f_uin2="file_wisuda_uin_2sep.xlsx", f_uns1="file_wisuda_unsoed_8sep.xlsx", f_uns2="file_wisuda_unsoed_9sep.xlsx"):
    b_uin1 = parse_wisuda_schedule(f_uin1, "2026-09-01", kategori="Wisuda UIN Saizu", start_id=1)
    b_uin2 = parse_wisuda_schedule(f_uin2, "2026-09-02", kategori="Wisuda UIN Saizu", start_id=len(b_uin1) + 1)
    b_uns1 = parse_wisuda_schedule(f_uns1, "2026-09-08", kategori="Wisuda UNSOED", start_id=len(b_uin1) + len(b_uin2) + 1)
    b_uns2 = parse_wisuda_schedule(f_uns2, "2026-09-09", kategori="Wisuda UNSOED", start_id=len(b_uin1) + len(b_uin2) + len(b_uns1) + 1)
    
    all_wisuda_sept = b_uin1 + b_uin2 + b_uns1 + b_uns2
    return {
        "bookings": all_wisuda_sept,
        "total": len(all_wisuda_sept),
        "totalNilai": sum(b["harga"] for b in all_wisuda_sept),
        "totalDp": sum(b["dp"] for b in all_wisuda_sept),
        "breakdown": {
            "uin_day1": {"sesi": len(b_uin1), "nilai": sum(b["harga"] for b in b_uin1)},
            "uin_day2": {"sesi": len(b_uin2), "nilai": sum(b["harga"] for b in b_uin2)},
            "unsoed_day1": {"sesi": len(b_uns1), "nilai": sum(b["harga"] for b in b_uns1)},
            "unsoed_day2": {"sesi": len(b_uns2), "nilai": sum(b["harga"] for b in b_uns2)}
        }
    }

def parse_october_pipeline(file_default="file2_okt.xlsx", file_w1="file_wisuda_3okt.xlsx", file_w2="file_wisuda_4okt.xlsx"):
    import os
    b_reg = []
    if os.path.exists(file_default):
        b_reg = parse_schedule(file_default, bulan="2026-10")
        for b in b_reg:
            hp = str(b.get("noHp", "")).lower()
            m = re.search(r'dp\s*(\d+)', hp)
            dp = float(m.group(1)) * 1000 if m else (b.get("harga", 0.0) if "lunas" in hp else 0.0)
            b["dp"] = dp
            b["sisaPelunasan"] = max(0.0, b.get("harga", 0.0) - dp)
            b["kategori"] = "Studio Reguler"
            
    b_w1 = parse_wisuda_schedule(file_w1, "2026-10-03", start_id=1)
    b_w2 = parse_wisuda_schedule(file_w2, "2026-10-04", start_id=len(b_w1)+1)
    
    all_okt = b_reg + b_w1 + b_w2
    total_val = sum(b.get("harga", 0.0) for b in all_okt)
    total_dp = sum(b.get("dp", 0.0) for b in all_okt)
    estimate_cash_in = max(0.0, total_val - total_dp)
    
    status_breakdown = {
        "done": {
            "sesi": len([b for b in all_okt if b.get("statusSesi") == "done"]),
            "nilai": sum(b.get("harga", 0.0) for b in all_okt if b.get("statusSesi") == "done"),
            "dp": sum(b.get("dp", 0.0) for b in all_okt if b.get("statusSesi") == "done"),
            "cashIn": sum(b.get("sisaPelunasan", 0.0) for b in all_okt if b.get("statusSesi") == "done")
        },
        "confirmed": {
            "sesi": len([b for b in all_okt if b.get("statusSesi") == "confirmed"]),
            "nilai": sum(b.get("harga", 0.0) for b in all_okt if b.get("statusSesi") == "confirmed"),
            "dp": sum(b.get("dp", 0.0) for b in all_okt if b.get("statusSesi") == "confirmed"),
            "cashIn": sum(b.get("sisaPelunasan", 0.0) for b in all_okt if b.get("statusSesi") == "confirmed")
        },
        "reschedule": {
            "sesi": len([b for b in all_okt if b.get("statusSesi") == "reschedule"]),
            "nilai": sum(b.get("harga", 0.0) for b in all_okt if b.get("statusSesi") == "reschedule"),
            "dp": sum(b.get("dp", 0.0) for b in all_okt if b.get("statusSesi") == "reschedule"),
            "cashIn": 0.0  # Rule 11: sisa pelunasan slot Orange dinetralkan Rp 0
        }
    }
    
    remaining_cash_in = status_breakdown["confirmed"]["cashIn"]

    return {
        "bulan": "2026-10",
        "totalBookings": len(all_okt),
        "potentialOmzet": total_val,
        "totalDp": total_dp,
        "estimateCashIn": remaining_cash_in,
        "remainingCashIn": remaining_cash_in,
        "totalPipelineCashIn": estimate_cash_in,
        "breakdown": {
            "reguler": {"sesi": len(b_reg), "nilai": sum(b.get("harga",0) for b in b_reg), "dp": sum(b.get("dp",0) for b in b_reg)},
            "wisudaDay1": {"sesi": len(b_w1), "nilai": sum(b.get("harga",0) for b in b_w1), "dp": sum(b.get("dp",0) for b in b_w1)},
            "wisudaDay2": {"sesi": len(b_w2), "nilai": sum(b.get("harga",0) for b in b_w2), "dp": sum(b.get("dp",0) for b in b_w2)}
        },
        "statusBreakdown": status_breakdown,
        "bookings": all_okt
    }

if __name__ == "__main__":
    res = parse_schedule()
    print(f"Hasil Parser Schedule: {len(res)} sesi foto terdata.")
