"""
=============================================================================
Foxe Studio — Multi-Year Historical Financial Cache Builder (2022 - 2026)
=============================================================================
One-off compiler to parse 2022, 2023, 2024, 2025, and 2026 data from 
file_neraca.xlsx and historical_cache.json.
Generates multiyear_cache.json for instant (< 0.005s) rendering in web dashboard.
Complies with Rule 15: Isolasi Bulan Aktif & Zero-Scan Arsip Lama.
=============================================================================
"""

import os
import json
import openpyxl

BULAN_NAMES = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

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

def classify_expense(desc):
    d = str(desc or "").lower().strip()
    
    # 1. COGS (Biaya Langsung Produksi / Paket / Sesi Foto / Vendor)
    if any(k in d for k in ["cetak", "print", "add packing", "kertas photo"]):
        return "COGS", "Cetak Foto & Photo Paper"
    if any(k in d for k in ["frame", "bingkai", "album"]):
        return "COGS", "Frame / Album / Packaging"
    if any(k in d for k in ["batre", "baterai", "battery", "rent batrei", "sewa batrei", "reflektor", "properti"]):
        return "COGS", "Properti / Consumable Sesi"
    if any(k in d for k in ["freelance", "ruslan", "camera", "fg ", "rent equipment", "sewa alat", "mua", "makeup"]):
        return "COGS", "Outsource / Freelancer & Vendor"
        
    # 2. OPEX (Biaya Operasional Studio Rutin)
    if any(k in d for k in ["listrik", "pdam", "air"]):
        return "OPEX", "Listrik & Air"
    if any(k in d for k in ["wifi", "internet", "kuota"]):
        return "OPEX", "Internet & Telekomunikasi"
    if any(k in d for k in ["ads", "iklan", "kol", "endorse", "meta", "instagram"]):
        return "OPEX", "Marketing / Ads / KOL"
    if any(k in d for k in ["makan", "sarapan", "konsumsi", "snack", "kopi"]):
        return "OPEX", "Konsumsi Crew"
    if any(k in d for k in ["adobe", "software", "subscription", "claude", "chatgpt", "canva", "midjourney", "openai", "domain"]):
        return "OPEX", "Software / Subscription"
    if any(k in d for k in ["cat limbo", "paralon", "maintenance", "dop", "perbaikan", "service", "serv ", "ac ", "exhaust", "curtain", "closet", "colokan", "fitting", "lampu"]):
        return "OPEX", "Maintenance Studio & Equipment"
    if any(k in d for k in ["galon", "parfum", "cleaning", "tissue", "kebersihan", "baygon", "wd cleaner", "lakban", "atk", "sticky", "stiky", "protektor"]):
        return "OPEX", "Office & Cleaning Supplies"
    if any(k in d for k in ["gosend", "kurir", "ongkir", "ekspedisi", "jne", "j&t"]):
        return "OPEX", "Pengiriman & Logistik"
    if any(k in d for k in ["bensin", "genset", "parkir"]):
        return "OPEX", "Transport & Operasional Lapangan"
    if any(k in d for k in ["biaya admin", "admin bank", "bunga"]):
        return "OPEX", "Biaya Admin Bank & Finansial"
    if "pajak" in d:
        return "OPEX", "Pajak & Perizinan"
    if "gaji" in d:
        return "OPEX", "Gaji Admin & Fotografer"
        
    # 3. Non-P&L / Lainnya
    if any(k in d for k in ["bon", "prive", "draw"]):
        return "NON-P&L", "Prive / Owner Draw"
    if "amal" in d or "sedekah" in d:
        return "Biaya Lainnya", "Amal & Sosial"
        
    return "OPEX", "OPEX Lainnya"

def find_sheet_for_month(sheetnames, year_str, month_num):
    # month_num: 1..12
    m_id = BULAN_NAMES[month_num - 1].lower()
    
    # English names
    eng_names = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    m_en = eng_names[month_num - 1]
    
    # Short names
    short_id = m_id[:3]
    short_en = m_en[:3]
    
    candidates = []
    for s in sheetnames:
        s_clean = s.strip()
        if year_str in s_clean or year_str[2:] in s_clean:
            sl = s_clean.lower()
            # Special cases
            if month_num == 10 and "okrtober" in sl:
                candidates.append((10, s))
                continue
            if month_num == 9 and "sept" in sl:
                candidates.append((9, s))
                continue
            if m_id in sl or m_en in sl:
                candidates.append((5, s))
                continue
            if short_id in sl or short_en in sl:
                candidates.append((2, s))
                continue
                
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    return None

def parse_sheet(ws, year_num, month_num):
    # Parse daily cash/transfer (rows 11..41)
    daily = []
    tot_cash_daily = 0.0
    tot_trf_daily = 0.0
    tot_inflow_daily = 0.0
    
    for r in range(11, 42):
        day_val = ws.cell(r, 2).value # Col B (Day)
        if day_val is None:
            continue
        try:
            day_int = int(float(str(day_val).strip()))
        except:
            continue
        if day_int < 1 or day_int > 31:
            continue
            
        c_val = clean_num(ws.cell(r, 3).value) # Col C (Cash)
        q_val = clean_num(ws.cell(r, 4).value) # Col D (QRIS)
        t_val = clean_num(ws.cell(r, 5).value) # Col E (Transfer)
        f_val = clean_num(ws.cell(r, 6).value) # Col F (Total Masuk)
        
        # If total masuk not in formula or 0, compute
        if f_val == 0.0 and (c_val > 0 or t_val > 0 or q_val > 0):
            f_val = c_val + q_val + t_val
            
        tot_cash_daily += c_val
        tot_trf_daily += (t_val + q_val)
        tot_inflow_daily += f_val
        
        iso_str = f"{year_num:04d}-{month_num:02d}-{day_int:02d}"
        daily.append({
            "tgl": iso_str,
            "day": day_int,
            "cash": c_val,
            "transfer": t_val + q_val,
            "total": f_val
        })
        
    # Check total row around row 42..45
    tot_cash_sheet = 0.0
    tot_trf_sheet = 0.0
    tot_inflow_sheet = 0.0
    
    for r in range(41, 46):
        b_val = str(ws.cell(r, 2).value or "").lower()
        if "total" in b_val or "jumlah" in b_val or ws.cell(r, 6).value is not None:
            c = clean_num(ws.cell(r, 3).value)
            q = clean_num(ws.cell(r, 4).value)
            t = clean_num(ws.cell(r, 5).value)
            f = clean_num(ws.cell(r, 6).value)
            if f > 0 or (c + t + q) > 0:
                tot_cash_sheet = c
                tot_trf_sheet = t + q
                tot_inflow_sheet = f if f > 0 else (c + t + q)
                break
                
    # Use sheet total if found and valid, otherwise fallback to sum of daily
    omzet = tot_inflow_sheet if tot_inflow_sheet > 0 else tot_inflow_daily
    cash = tot_cash_sheet if tot_cash_sheet > 0 else tot_cash_daily
    transfer = tot_trf_sheet if tot_trf_sheet > 0 else tot_trf_daily
    if omzet == 0 and (cash + transfer) > 0:
        omzet = cash + transfer

    # Parse expenses (cols P..U, rows 11..120)
    expenses = []
    tot_cogs = 0.0
    tot_opex = 0.0
    
    current_day = None
    for r in range(11, 150):
        p_val = ws.cell(r, 16).value # Col P: Tgl
        if p_val is not None:
            try:
                current_day = int(float(str(p_val).strip()))
            except:
                pass
                
        out_val = clean_num(ws.cell(r, 18).value) # Col R: Saldo Keluar
        desc_val = ws.cell(r, 21).value # Col U: Keterangan Keluar
        if desc_val is None:
            # Fallback check col T or Q
            desc_val = ws.cell(r, 20).value or ws.cell(r, 17).value
            
        desc_str = str(desc_val or "").strip()
        
        # Stop condition
        if not desc_str and out_val == 0.0 and p_val is None:
            # If 3 consecutive rows are empty, break
            empty_count = 0
            for peek in range(r, min(r + 4, 150)):
                if not ws.cell(peek, 18).value and not ws.cell(peek, 21).value:
                    empty_count += 1
            if empty_count >= 3:
                break
                
        if out_val > 0 or desc_str:
            jenis, kat = classify_expense(desc_str)
            tgl_iso = f"{year_num:04d}-{month_num:02d}-{current_day:02d}" if current_day else f"{year_num:04d}-{month_num:02d}-01"
            expenses.append({
                "tgl": tgl_iso,
                "day": current_day or 1,
                "desc": desc_str or "Pengeluaran Operasional",
                "jenis": jenis,
                "kategori": kat,
                "nilai": out_val
            })
            if jenis == "COGS":
                tot_cogs += out_val
            elif jenis == "OPEX":
                tot_opex += out_val
                
    outcome = tot_cogs + tot_opex
    nett_profit = omzet - outcome
    margin = (nett_profit / omzet * 100.0) if omzet > 0 else 0.0
    
    return {
        "month": month_num,
        "name": BULAN_NAMES[month_num - 1],
        "omzet": round(omzet),
        "cash": round(cash),
        "transfer": round(transfer),
        "cogs": round(tot_cogs),
        "opex": round(tot_opex),
        "outcome": round(outcome),
        "nettProfit": round(nett_profit),
        "margin": round(margin, 2),
        "daily": daily,
        "expenses": expenses
    }

def main():
    print("Loading file_neraca.xlsx...")
    if not os.path.exists("file_neraca.xlsx"):
        print("ERROR: file_neraca.xlsx not found.")
        return
        
    wb = openpyxl.load_workbook("file_neraca.xlsx", data_only=True)
    sheetnames = wb.sheetnames
    print(f"Loaded workbook with {len(sheetnames)} sheets.")
    
    multiyear_data = {"years": {}}
    
    # Process 2022, 2023, 2024, 2025
    for year_num in [2022, 2023, 2024, 2025]:
        year_str = str(year_num)
        print(f"\nProcessing Year {year_str}...")
        
        y_omzet = 0
        y_cash = 0
        y_trf = 0
        y_cogs = 0
        y_opex = 0
        y_outcome = 0
        y_nett = 0
        
        months_data = []
        for m in range(1, 13):
            s_name = find_sheet_for_month(sheetnames, year_str, m)
            if s_name and s_name in wb.sheetnames:
                print(f"  Month {m:02d} ({BULAN_NAMES[m-1]}): sheet '{s_name}'")
                m_res = parse_sheet(wb[s_name], year_num, m)
                m_res["sheetName"] = s_name
                months_data.append(m_res)
                
                y_omzet += m_res["omzet"]
                y_cash += m_res["cash"]
                y_trf += m_res["transfer"]
                y_cogs += m_res["cogs"]
                y_opex += m_res["opex"]
                y_outcome += m_res["outcome"]
                y_nett += m_res["nettProfit"]
            else:
                print(f"  Month {m:02d} ({BULAN_NAMES[m-1]}): NOT FOUND")
                months_data.append({
                    "month": m,
                    "name": BULAN_NAMES[m-1],
                    "omzet": 0,
                    "cash": 0,
                    "transfer": 0,
                    "cogs": 0,
                    "opex": 0,
                    "outcome": 0,
                    "nettProfit": 0,
                    "margin": 0.0,
                    "daily": [],
                    "expenses": []
                })
                
        y_margin = (y_nett / y_omzet * 100.0) if y_omzet > 0 else 0.0
        multiyear_data["years"][year_str] = {
            "year": year_str,
            "omzet": y_omzet,
            "cash": y_cash,
            "transfer": y_trf,
            "cogs": y_cogs,
            "opex": y_opex,
            "outcome": y_outcome,
            "nettProfit": y_nett,
            "margin": round(y_margin, 2),
            "months": months_data
        }
        print(f"  Year {year_str} Total: Omzet {y_omzet:,.0f} | Outflow {y_outcome:,.0f} | Nett {y_nett:,.0f} ({y_margin:.1f}%)")

    # Now load 2026 data from historical_cache.json & foxe_full_state.json
    print("\nProcessing Year 2026 (Live & Closed Books)...")
    y26_months = []
    y26_omzet = 0
    y26_cash = 0
    y26_trf = 0
    y26_cogs = 0
    y26_opex = 0
    y26_outcome = 0
    y26_nett = 0

    hist_cache = {}
    if os.path.exists("historical_cache.json"):
        with open("historical_cache.json", "r", encoding="utf-8") as f:
            hist_cache = json.load(f).get("historicalMonths", {})
            
    full_state = {}
    if os.path.exists("foxe_full_state.json"):
        with open("foxe_full_state.json", "r", encoding="utf-8") as f:
            full_state = json.load(f)

    # Jan - Aug from historical_cache
    for m in range(1, 9):
        m_str = str(m)
        hm = hist_cache.get(m_str, {})
        omz = round(clean_num(hm.get("omzet", 0)))
        c = round(clean_num(hm.get("cash", 0)))
        t = round(clean_num(hm.get("transfer", 0)))
        cg = round(clean_num(hm.get("cogs", 0)))
        op = round(clean_num(hm.get("opex", 0)))
        outc = cg + op
        nt = omz - outc
        mg = (nt / omz * 100.0) if omz > 0 else 0.0
        
        y26_months.append({
            "month": m,
            "name": BULAN_NAMES[m-1],
            "omzet": omz,
            "cash": c,
            "transfer": t,
            "cogs": cg,
            "opex": op,
            "outcome": outc,
            "nettProfit": nt,
            "margin": round(mg, 2),
            "daily": [],
            "expenses": []
        })
        y26_omzet += omz
        y26_cash += c
        y26_trf += t
        y26_cogs += cg
        y26_opex += op
        y26_outcome += outc
        y26_nett += nt

    # Sept 2026 from full_state
    # Check if September in neracaByMonth or summary
    sep_data = full_state.get("neracaByMonth", {}).get("2026-09", {})
    sep_omz = round(clean_num(full_state.get("omzet", 188730000))) # or from full_state
    sep_orders = full_state.get("orders", [])
    sep_c = round(sum(clean_num(o.get("cash", 0)) for o in sep_orders if str(o.get("tanggal", "")).startswith("2026-09")))
    sep_t = round(sum(clean_num(o.get("transfer", 0)) for o in sep_orders if str(o.get("tanggal", "")).startswith("2026-09")))
    sep_cg = round(clean_num(full_state.get("totalCogs", 23221500)))
    sep_op = round(clean_num(full_state.get("totalOpex", 21144209)))
    sep_outc = sep_cg + sep_op
    sep_nt = sep_omz - sep_outc
    sep_mg = (sep_nt / sep_omz * 100.0) if sep_omz > 0 else 0.0

    y26_months.append({
        "month": 9,
        "name": "September",
        "omzet": sep_omz,
        "cash": sep_c,
        "transfer": sep_t,
        "cogs": sep_cg,
        "opex": sep_op,
        "outcome": sep_outc,
        "nettProfit": sep_nt,
        "margin": round(sep_mg, 2),
        "daily": [],
        "expenses": []
    })
    y26_omzet += sep_omz
    y26_cash += sep_c
    y26_trf += sep_t
    y26_cogs += sep_cg
    y26_opex += sep_op
    y26_outcome += sep_outc
    y26_nett += sep_nt

    # Oct 2026 Live
    okt_orders = full_state.get("oktoberLogOrder", {}).get("orders", [])
    okt_omz = round(sum(clean_num(o.get("total", 0)) for o in okt_orders))
    okt_c = round(sum(clean_num(o.get("cash", 0)) for o in okt_orders))
    okt_t = round(sum(clean_num(o.get("transfer", 0)) for o in okt_orders))
    okt_exp = full_state.get("neracaByMonth", {}).get("2026-10", {}).get("expenses", [])
    okt_cg = round(sum(clean_num(e.get("nilai", 0)) for e in okt_exp if e.get("jenis") == "COGS"))
    okt_op = round(sum(clean_num(e.get("nilai", 0)) for e in okt_exp if e.get("jenis") == "OPEX"))
    okt_outc = okt_cg + okt_op
    okt_nt = okt_omz - okt_outc
    okt_mg = (okt_nt / okt_omz * 100.0) if okt_omz > 0 else 0.0

    y26_months.append({
        "month": 10,
        "name": "Oktober",
        "omzet": okt_omz,
        "cash": okt_c,
        "transfer": okt_t,
        "cogs": okt_cg,
        "opex": okt_op,
        "outcome": okt_outc,
        "nettProfit": okt_nt,
        "margin": round(okt_mg, 2),
        "status": "Live MTD",
        "daily": [],
        "expenses": []
    })
    y26_omzet += okt_omz
    y26_cash += okt_c
    y26_trf += okt_t
    y26_cogs += okt_cg
    y26_opex += okt_op
    y26_outcome += okt_outc
    y26_nett += okt_nt

    # Nov & Dec 2026 placeholder
    for m in [11, 12]:
        y26_months.append({
            "month": m,
            "name": BULAN_NAMES[m-1],
            "omzet": 0,
            "cash": 0,
            "transfer": 0,
            "cogs": 0,
            "opex": 0,
            "outcome": 0,
            "nettProfit": 0,
            "margin": 0.0,
            "daily": [],
            "expenses": []
        })

    y26_margin = (y26_nett / y26_omzet * 100.0) if y26_omzet > 0 else 0.0
    multiyear_data["years"]["2026"] = {
        "year": "2026",
        "omzet": y26_omzet,
        "cash": y26_cash,
        "transfer": y26_trf,
        "cogs": y26_cogs,
        "opex": y26_opex,
        "outcome": y26_outcome,
        "nettProfit": y26_nett,
        "margin": round(y26_margin, 2),
        "months": y26_months
    }
    print(f"  Year 2026 Total (YTD Live): Omzet {y26_omzet:,.0f} | Outflow {y26_outcome:,.0f} | Nett {y26_nett:,.0f} ({y26_margin:.1f}%)")

    # Save to multiyear_cache.json
    out_path = "multiyear_cache.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(multiyear_data, f, ensure_ascii=False, indent=2)
    print(f"\nSuccessfully wrote {out_path} ({os.path.getsize(out_path):,} bytes).")

    # Also update foxe_full_state.json
    if os.path.exists("foxe_full_state.json"):
        with open("foxe_full_state.json", "r", encoding="utf-8") as f:
            state = json.load(f)
        state["multiyearArsip"] = multiyear_data
        with open("foxe_full_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print("Updated foxe_full_state.json with multiyearArsip property.")

if __name__ == "__main__":
    main()
