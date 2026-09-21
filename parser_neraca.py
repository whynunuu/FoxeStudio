"""
=============================================================================
Foxe Studio — Parser Neraca Keuangan (File Neraca Google Drive)
=============================================================================
Parser khusus untuk mengurai pos pengeluaran dari sheet 'September 2026'
pada section 'Detail' (Kolom P s.d. U) sesuai arahan pemilik studio:
- Membaca baris per tanggal menurun ke bawah.
- Mengklasifikasikan otomatis ke:
  * COGS (Biaya Langsung Produksi / Sesi Foto)
  * OPEX (Biaya Operasional Studio)
  * NON-P&L / Lainnya
=============================================================================
"""

import os
import openpyxl

NERACA_SHEET_ID = "1dvnCNyfZI5z-12081XJjGCVLtMaQpUStYT61qU3orKM"

def classify_expense(desc):
    d = str(desc or "").lower().strip()
    
    # 1. COGS (Biaya Langsung Produksi / Paket / Sesi Foto)
    if any(k in d for k in ["cetak", "print"]):
        return "COGS", "Cetak Foto & Photo Paper"
    if "frame" in d or "bingkai" in d or "album" in d:
        return "COGS", "Frame / Album / Packaging"
    if any(k in d for k in ["batrei", "baterai", "rent batrei", "sewa batrei"]):
        return "COGS", "Properti / Consumable Sesi"
    if "rent equipment" in d or "sewa alat" in d:
        return "COGS", "Outsource / Freelancer Produksi"
    if any(k in d for k in ["freelance", "ruslan", "camera", "fg "]):
        return "COGS", "Outsource / Freelancer Produksi"
        
    # 2. OPEX (Biaya Operasional Studio Rutin)
    if "listrik" in d:
        return "OPEX", "Listrik & Air"
    if "wifi" in d or "internet" in d:
        return "OPEX", "Internet & Telekomunikasi"
    if "ads" in d or "iklan" in d:
        return "OPEX", "Marketing / Ads / KOL"
    if any(k in d for k in ["makan", "sarapan", "konsumsi", "snack"]):
        return "OPEX", "Konsumsi Crew"
    if "adobe" in d or "software" in d or "subscription" in d:
        return "OPEX", "Software / Subscription"
    if any(k in d for k in ["cat limbo", "paralon", "maintenance", "dop", "perbaikan"]):
        return "OPEX", "Maintenance Studio & Equipment"
    if any(k in d for k in ["galon", "parfum", "cleaning", "tissue", "kebersihan"]):
        return "OPEX", "Office & Cleaning Supplies"
    if "gaji" in d:
        return "OPEX", "Gaji Admin & Fotografer"
        
    # 3. Non-PL / Lainnya
    if "bon" in d:
        return "NON-P&L", "Prive / Owner Draw"
    if "pajak" in d:
        return "OPEX", "Pajak & Perizinan"
    if "amal" in d:
        return "Biaya Lainnya", "Biaya Lainnya"
        
    return "OPEX", "OPEX Lainnya"

def clean_num(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace("Rp", "").strip()
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

def parse_neraca(filepath="file_neraca.xlsx", sheet_name="September 2026"):
    if not os.path.exists(filepath):
        print(f"[WARN] File neraca {filepath} tidak ditemukan.")
        return {"expenses": [], "detail": [], "summary": {}}

    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        sheet_name = wb.sheetnames[0]
        
    ws = wb[sheet_name]

    current_tgl = None
    prev_tgl = None
    expenses = []
    detail = []
    idx = 1
    det_idx = 1

    tot_masuk = 0.0
    tot_keluar = 0.0
    last_balance = 0.0

    # Section Detail terletak pada kolom:
    # Col 16 (P): Tgl
    # Col 17 (Q): Saldo Masuk
    # Col 18 (R): Saldo Keluar
    # Col 19 (S): Balance
    # Col 20 (T): Keterangan Masuk
    # Col 21 (U): Keterangan Keluar

    for r_idx, row in enumerate(ws.iter_rows(values_only=True)):
        if r_idx < 10 or r_idx > 130 or len(row) < 21:
            continue
            
        tgl_val = row[15]
        masuk_val = row[16]
        keluar_val = row[17]
        balance_val = row[18]
        ket_masuk = row[19]
        ket_keluar = row[20]
        
        # Tanggal merge/vertikal
        if tgl_val is not None and str(tgl_val).strip() != "":
            try:
                parsed_day = int(float(str(tgl_val).strip()))
                if 1 <= parsed_day <= 31:
                    current_tgl = parsed_day
            except:
                pass
                
        # Jika satu baris kosong semua di area Detail, lewati
        if all(x is None or str(x).strip() == "" for x in [masuk_val, keluar_val, balance_val, ket_masuk, ket_keluar]):
            continue

        nominal_keluar = clean_num(keluar_val)
        nominal_masuk = clean_num(masuk_val)
        nominal_balance = clean_num(balance_val)
        desc_keluar = str(ket_keluar or "").strip()
        desc_masuk = str(ket_masuk or "").strip()
        
        # Simpan ke baris detail neraca (debit / kredit) untuk baris log harian (r_idx <= 64)
        if r_idx <= 64 and current_tgl is not None:
            first_of_day = (current_tgl != prev_tgl)
            prev_tgl = current_tgl
            
            tot_masuk += nominal_masuk
            tot_keluar += nominal_keluar
            if nominal_balance > 0:
                last_balance = nominal_balance
                
            detail.append({
                "id": f"det_nrc_{det_idx}",
                "tgl": current_tgl,
                "tanggal_iso": f"2026-09-{current_tgl:02d}",
                "first_of_day": first_of_day,
                "masuk": nominal_masuk,
                "keluar": nominal_keluar,
                "balance": nominal_balance,
                "ket_masuk": desc_masuk,
                "ket_keluar": desc_keluar
            })
            det_idx += 1

        # Abaikan subtotal / angka numerik yang bukan keterangan untuk pos expenses
        if desc_keluar.replace(".", "").replace(",", "").isdigit() or desc_keluar.lower() in ["total", "nominal", "balance"]:
            continue
            
        if nominal_keluar > 0 and desc_keluar and current_tgl is not None:
            jenis, kategori = classify_expense(desc_keluar)
            tgl_iso = f"2026-09-{current_tgl:02d}"
            expenses.append({
                "id": f"ex_nrc_{idx}",
                "tanggal": tgl_iso,
                "bulan": "2026-09",
                "jenis": jenis,
                "kategori": kategori,
                "deskripsi": desc_keluar,
                "nilai": nominal_keluar
            })
            idx += 1

    summary = {
        "total_masuk": tot_masuk,
        "total_keluar": tot_keluar,
        "ending_balance": last_balance,
        "total_rows": len(detail)
    }

    print(f"[OK] File Neraca berhasil diurai: {len(expenses)} pos pengeluaran, {len(detail)} baris log debit/kredit.")
    return {
        "expenses": expenses,
        "detail": detail,
        "summary": summary
    }

if __name__ == "__main__":
    res = parse_neraca()
    exps = res["expenses"]
    cogs_tot = sum(e["nilai"] for e in exps if e["jenis"] == "COGS")
    opex_tot = sum(e["nilai"] for e in exps if e["jenis"] == "OPEX")
    print(f"Total Pos Biaya: {len(exps)}")
    print(f"Total Baris Detail Debit/Kredit: {len(res['detail'])}")
    print(f"Total COGS: Rp {cogs_tot:,.0f}")
    print(f"Total OPEX: Rp {opex_tot:,.0f}")
    print(f"Total Saldo Masuk: Rp {res['summary']['total_masuk']:,.0f}")
    print(f"Total Saldo Keluar: Rp {res['summary']['total_keluar']:,.0f}")
    print(f"Ending Balance: Rp {res['summary']['ending_balance']:,.0f}")

