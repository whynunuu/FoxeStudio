import os
import sys
import json
import openpyxl
import re

sys.stdout.reconfigure(encoding='utf-8')

BULAN_NAMES = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

def clean_val(v):
    if v is None: return 0.0
    if isinstance(v, (int, float)): return float(v)
    s = str(v).replace('Rp', '').replace('.', '').replace(',', '.').strip()
    try: return float(s)
    except: return 0.0

def classify_expense(desc):
    dl = str(desc or '').lower().strip()
    cogs_kws = ['cetak', 'frame', 'pigura', 'album', 'kertas', 'packaging', 'paper', 'tinta', 'properti', 'backdrop', 'kostum', 'baju', 'jas', 'kebaya', 'wisuda', 'freelance', 'frelance', 'mua', 'makeup', 'vendor', 'photobook', 'kanvas', 'canvas', 'flashdisk', 'usb', 'laminasi', 'akrilik']
    if any(k in dl for k in cogs_kws):
        return 'COGS', 'Cetak Foto & Frame' if any(k in dl for k in ['cetak', 'frame', 'pigura', 'album']) else 'Packaging & Properti'
    if any(k in dl for k in ['gaji', 'bonus', 'fee', 'thp', 'honor', 'insentif']):
        return 'OPEX', 'Gaji & Honor Karyawan'
    if any(k in dl for k in ['ads', 'iklan', 'meta', 'instagram', 'facebook', 'tiktok', 'marketing', 'kol', 'promo']):
        return 'OPEX', 'Marketing / Ads / KOL'
    if any(k in dl for k in ['listrik', 'pln', 'token']):
        return 'OPEX', 'Listrik (PLN)'
    if any(k in dl for k in ['wifi', 'internet', 'indihome', 'biznet', 'folx']):
        return 'OPEX', 'Internet & Komunikasi'
    if any(k in dl for k in ['pdam', 'air']):
        return 'OPEX', 'Air (PDAM)'
    if any(k in dl for k in ['pajak', 'pph', 'amal', 'sedekah', 'zakat']):
        return 'OPEX', 'Pajak & Donasi Sosial'
    if any(k in dl for k in ['makan', 'minum', 'snack', 'kopi', 'konsumsi', 'galon']):
        return 'OPEX', 'Konsumsi & Logistik Studio'
    if any(k in dl for k in ['service', 'renov', 'perbaikan', 'beli alat', 'maintenance', 'cat', 'lampu', 'ac']):
        return 'OPEX', 'Maintenance & Peralatan Studio'
    return 'OPEX', 'Operasional & Perlengkapan'

def find_sheet_for_month(sheetnames, year_str, month_num):
    m_names_id = ["januari", "februari", "maret", "april", "mei", "juni", "juli", "agustus", "september", "oktober", "november", "desember"]
    m_names_en = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    mid = m_names_id[month_num - 1]
    men = m_names_en[month_num - 1]
    for s in sheetnames:
        sl = s.strip().lower()
        if 'master' in sl or 'copy' in sl: continue
        if year_str in sl or year_str[2:] in sl:
            if month_num == 10 and 'okrtober' in sl: return s
            if month_num == 9 and 'sept' in sl: return s
            if mid in sl or men in sl or mid[:3] in sl: return s
    return None

def main():
    print("Loading file_neraca.xlsx with read_only=True...")
    if not os.path.exists("file_neraca.xlsx"):
        print("ERROR: file_neraca.xlsx not found.")
        return
        
    wb = openpyxl.load_workbook("file_neraca.xlsx", read_only=True, data_only=True)
    sheetnames = wb.sheetnames
    print(f"Loaded workbook with {len(sheetnames)} sheets.")
    
    my = {"years": {}}
    if os.path.exists("multiyear_cache.json"):
        with open("multiyear_cache.json", "r", encoding="utf-8") as f:
            try: my = json.load(f)
            except: my = {"years": {}}
    if "years" not in my: my["years"] = {}

    for y in [2022, 2023, 2024, 2025]:
        year_str = str(y)
        print(f"\n====================== RECONCILING YEAR {year_str} ======================")
        y_omz = 0; y_cash = 0; y_trf = 0; y_cg = 0; y_op = 0; y_out = 0; y_nt = 0
        new_months = []
        
        for m in range(1, 13):
            sname = find_sheet_for_month(sheetnames, year_str, m)
            if not sname:
                print(f"  M{m:02d}: Not found")
                continue
            ws = wb[sname]
            all_rows = list(ws.iter_rows(min_row=1, max_row=150, values_only=True))
            
            # 1. Kalkulasi Resmi (Cols AT..BA, Rows 8, 9)
            kotor_kalk = 0.0; keluar_kalk = 0.0; bersih_kalk = 0.0
            div_investor = 0.0; div_modal = 0.0; div_tabungan = 0.0; div_gm = 0.0
            
            if len(all_rows) >= 9:
                r8 = all_rows[7]; r9 = all_rows[8]
                for c_idx, val in enumerate(r8):
                    v_str = str(val or '').strip().lower()
                    if 'kotor' in v_str: kotor_kalk = clean_val(r9[c_idx])
                    elif 'pengeluaran' in v_str and c_idx >= 35: keluar_kalk = clean_val(r9[c_idx])
                    elif 'bersih' in v_str: bersih_kalk = clean_val(r9[c_idx])
                    elif 'investor' in v_str: div_investor = clean_val(r9[c_idx])
                    elif 'modal' in v_str and c_idx >= 40: div_modal = clean_val(r9[c_idx])
                    elif 'tabungan' in v_str: div_tabungan = clean_val(r9[c_idx])
                    elif 'general' in v_str or 'gm' in v_str or 'manger' in v_str: div_gm = clean_val(r9[c_idx])
            
            # 2. Income Table Row Total
            sheet_cash = 0.0; sheet_trf = 0.0; sheet_tot_in = 0.0
            for r_idx in range(40, min(48, len(all_rows))):
                row = all_rows[r_idx]
                col_b = str(row[1] or '').strip().lower()
                if 'total' in col_b or 'jumlah' in col_b:
                    if row[5] and clean_val(row[5]) > 0:
                        sheet_cash = clean_val(row[2])
                        sheet_trf = clean_val(row[4]) + clean_val(row[3])
                        sheet_tot_in = clean_val(row[5])
                    elif r_idx + 1 < len(all_rows):
                        next_r = all_rows[r_idx + 1]
                        if next_r[5] and clean_val(next_r[5]) > 0:
                            sheet_cash = clean_val(next_r[2])
                            sheet_trf = clean_val(next_r[4]) + clean_val(next_r[3])
                            sheet_tot_in = clean_val(next_r[5])
                    break
                    
            # 3. Daily Cash/Transfer (Rows 11..41)
            daily = []; tot_c_daily = 0.0; tot_t_daily = 0.0
            for r_idx in range(10, min(41, len(all_rows))):
                row = all_rows[r_idx]
                d_val = row[1]
                if d_val is None: continue
                try:
                    day_int = int(float(str(d_val).strip()))
                    if not (1 <= day_int <= 31): continue
                except: continue
                c_val = clean_val(row[2])
                q_val = clean_val(row[3])
                t_val = clean_val(row[4])
                f_val = clean_val(row[5])
                if f_val == 0.0 and (c_val + q_val + t_val) > 0:
                    f_val = c_val + q_val + t_val
                tot_c_daily += c_val
                tot_t_daily += (t_val + q_val)
                daily.append({
                    "tgl": f"{y:04d}-{m:02d}-{day_int:02d}",
                    "day": day_int,
                    "cash": round(c_val),
                    "transfer": round(t_val + q_val),
                    "total": round(f_val)
                })
                
            omzet = kotor_kalk if kotor_kalk > 0 else (sheet_tot_in if sheet_tot_in > 0 else (tot_c_daily + tot_t_daily))
            cash = sheet_cash if sheet_cash > 0 else tot_c_daily
            transfer = sheet_trf if sheet_trf > 0 else tot_t_daily
            if (cash + transfer) == 0 and omzet > 0:
                cash = round(omzet * 0.35)
                transfer = round(omzet * 0.65)
                
            # 4. Rekap 18 Pos Pengeluaran (Cols AB..AE)
            rekap_cogs = 0.0; rekap_opex = 0.0; rekap_total = 0.0; rekap_items = []
            for r_idx in range(8, min(33, len(all_rows))):
                row = all_rows[r_idx]
                if len(row) >= 30:
                    pos_nama = str(row[28] or '').strip()
                    pos_nom = clean_val(row[29])
                    col_ab = str(row[27] or '').strip().lower()
                    if 'total' in col_ab or 'jumlah' in col_ab or 'total' in pos_nama.lower():
                        rekap_total = pos_nom
                        continue
                    if pos_nom > 0:
                        is_cogs = any(k in pos_nama.lower() for k in ['cetak', 'frame', 'album', 'freelance', 'frelance', 'alat'])
                        if is_cogs: rekap_cogs += pos_nom
                        else: rekap_opex += pos_nom
                        rekap_items.append({
                            "pos": pos_nama,
                            "nominal": round(pos_nom),
                            "jenis": "COGS" if is_cogs else "OPEX"
                        })
                        
            # 5. Detail Saldo Keluar (Cols P..U)
            expenses = []; current_day = 1
            for r_idx in range(10, min(135, len(all_rows))):
                row = all_rows[r_idx]
                p_val = row[15]
                if p_val is not None:
                    try:
                        d = int(float(str(p_val).strip()))
                        if 1 <= d <= 31: current_day = d
                    except: pass
                out_val = clean_val(row[17])
                desc_val = str(row[20] or row[19] or row[16] or '').strip()
                if out_val == 0.0 and not desc_val: continue
                if desc_val.lower() in ['saldo keluar', 'keterangan', 'detail', 'nominal', 'total', 'jumlah']: continue
                if any(w in desc_val.lower() for w in ['bon manajemen', 'alas', 'folx', 'tambahan / balik', 'refund out']): continue
                
                jenis, kat = classify_expense(desc_val)
                expenses.append({
                    "tgl": f"{y:04d}-{m:02d}-{current_day:02d}",
                    "day": current_day,
                    "desc": desc_val or "Pengeluaran Operasional",
                    "jenis": jenis,
                    "kategori": kat,
                    "nilai": round(out_val)
                })
                
            outcome = keluar_kalk if keluar_kalk > 0 else (rekap_total if rekap_total > 0 else (rekap_cogs + rekap_opex))
            cogs = rekap_cogs if rekap_cogs > 0 else sum(e["nilai"] for e in expenses if e["jenis"] == "COGS")
            opex = outcome - cogs if outcome >= cogs else sum(e["nilai"] for e in expenses if e["jenis"] == "OPEX")
            
            nett_profit = bersih_kalk if (bersih_kalk != 0 and kotor_kalk > 0) else (omzet - outcome)
            margin = (nett_profit / omzet * 100.0) if omzet > 0 else 0.0
            
            ads = sum(e["nilai"] for e in expenses if e.get("kategori") == "Marketing / Ads / KOL" or "ads" in e.get("desc", "").lower() or "iklan" in e.get("desc", "").lower())
            if ads == 0:
                for item in rekap_items:
                    if 'ads' in item['pos'].lower() or 'iklan' in item['pos'].lower():
                        ads = item['nominal']
                        break
                        
            m_obj = {
                "month": m,
                "name": BULAN_NAMES[m - 1],
                "omzet": round(omzet),
                "cash": round(cash),
                "transfer": round(transfer),
                "cogs": round(cogs),
                "opex": round(opex),
                "outcome": round(outcome),
                "nettProfit": round(nett_profit),
                "margin": round(margin, 2),
                "ads": round(ads),
                "rekapItems": rekap_items,
                "pembagian": {
                    "investor": round(div_investor or (nett_profit * 0.7)),
                    "modal": round(div_modal or (nett_profit * 0.15)),
                    "tabungan": round(div_tabungan or (nett_profit * 0.05)),
                    "gm": round(div_gm or (nett_profit * 0.10))
                },
                "daily": daily,
                "expenses": expenses,
                "sheetName": sname
            }
            new_months.append(m_obj)
            
            y_omz += omzet; y_cash += cash; y_trf += transfer
            y_cg += cogs; y_op += opex; y_out += outcome; y_nt += nett_profit
            print(f"  M{m:02d} ({BULAN_NAMES[m-1]:10s}): Omzet={omzet:11,.0f} | Beban={outcome:10,.0f} | Laba Bersih={nett_profit:10,.0f} ({margin:4.1f}%) | COGS={cogs:9,.0f} | OPEX={opex:9,.0f}")
            
        y_margin = (y_nt / y_omz * 100.0) if y_omz > 0 else 0.0
        my["years"][year_str] = {
            "year": year_str,
            "omzet": round(y_omz),
            "cash": round(y_cash),
            "transfer": round(y_trf),
            "cogs": round(y_cg),
            "opex": round(y_op),
            "outcome": round(y_out),
            "nettProfit": round(y_nt),
            "margin": round(y_margin, 2),
            "months": new_months
        }
        print(f"TOTAL {year_str}: Omzet={y_omz:12,.0f} | Beban={y_out:12,.0f} | Laba Bersih={y_nt:12,.0f} ({y_margin:.1f}%)")

    wb.close()
    
    with open("multiyear_cache.json", "w", encoding="utf-8") as f:
        json.dump(my, f, ensure_ascii=False, indent=2)
    print("\nSaved multiyear_cache.json successfully.")

    with open("foxe_full_state.json", "r", encoding="utf-8") as f:
        fs = json.load(f)
    fs["multiyearArsip"] = my
    with open("foxe_full_state.json", "w", encoding="utf-8") as f:
        json.dump(fs, f, ensure_ascii=False, indent=2)
    print("Synced to foxe_full_state.json successfully.")

if __name__ == "__main__":
    main()
