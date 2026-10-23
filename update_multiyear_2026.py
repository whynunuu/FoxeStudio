"""
Updates multiyear_cache.json and foxe_full_state.json with full daily cash/transfer
and full detailed COGS & OPEX expenses for 2026 (Jan–Okt).
"""

import json
import os

def clean_num(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace("Rp", "").replace(".", "").replace(",", ".").replace(" ", "")
    try:
        return float(s)
    except:
        return 0.0

def build_daily(orders, iso_prefix):
    days_map = {}
    for o in orders:
        t = str(o.get("tanggal", ""))
        if not t.startswith(iso_prefix):
            continue
        parts = t.split("-")
        d = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else 1
        if d not in days_map:
            days_map[d] = {"cash": 0.0, "transfer": 0.0, "total": 0.0}
        c = float(clean_num(o.get("cash", 0)))
        tr = float(clean_num(o.get("transfer", 0)))
        tot = float(clean_num(o.get("total", 0)))
        if tot == 0.0 and (c + tr) > 0:
            tot = c + tr
        days_map[d]["cash"] += c
        days_map[d]["transfer"] += tr
        days_map[d]["total"] += tot
    
    daily_res = []
    for d in sorted(days_map.keys()):
        daily_res.append({
            "tgl": f"{iso_prefix}-{d:02d}",
            "day": d,
            "cash": round(days_map[d]["cash"]),
            "transfer": round(days_map[d]["transfer"]),
            "total": round(days_map[d]["total"])
        })
    return daily_res

def norm_exp(raw_list, iso_prefix):
    norm = []
    for e in raw_list:
        tgl = str(e.get("tanggal") or e.get("tgl") or f"{iso_prefix}-01")
        parts = tgl.split("-")
        d = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else 1
        desc = str(e.get("deskripsi") or e.get("desc") or "Pengeluaran").strip()
        jenis = str(e.get("jenis") or "OPEX").strip().upper()
        kat = str(e.get("kategori") or "Lainnya").strip()
        val = round(clean_num(e.get("nilai", 0)))
        norm.append({
            "tgl": tgl,
            "day": d,
            "desc": desc,
            "jenis": jenis,
            "kategori": kat,
            "nilai": val
        })
    return norm

def main():
    print("Reading data sources...")
    with open("multiyear_cache.json", "r", encoding="utf-8") as f:
        my = json.load(f)

    with open("foxe_full_state.json", "r", encoding="utf-8") as f:
        fs = json.load(f)

    with open("historical_cache.json", "r", encoding="utf-8") as f:
        hc = json.load(f)

    nb = fs.get("neracaByMonth", {})
    ho = hc.get("historicalOrders", [])
    so = fs.get("orders", [])
    oo = fs.get("oktoberLogOrder", {}).get("orders", [])

    m_list = my["years"]["2026"]["months"]
    y_omz = 0
    y_cash = 0
    y_trf = 0
    y_cg = 0
    y_op = 0
    y_out = 0
    y_nt = 0

    for m_obj in m_list:
        m = m_obj["month"]
        iso = f"2026-{m:02d}"
        if m <= 8:
            raw_exp = nb.get(iso, {}).get("expenses", [])
            m_obj["expenses"] = norm_exp(raw_exp, iso)
            m_obj["daily"] = build_daily(ho, iso)
        elif m == 9:
            raw_exp = nb.get(iso, {}).get("expenses", [])
            m_obj["expenses"] = norm_exp(raw_exp, iso)
            m_obj["daily"] = build_daily(so, iso)
        elif m == 10:
            raw_exp = nb.get(iso, {}).get("expenses", [])
            m_obj["expenses"] = norm_exp(raw_exp, iso)
            m_obj["daily"] = build_daily(oo, iso)
        else:
            m_obj["expenses"] = []
            m_obj["daily"] = []
        
        if m <= 10:
            cg = sum(e["nilai"] for e in m_obj["expenses"] if e["jenis"] == "COGS")
            op = sum(e["nilai"] for e in m_obj["expenses"] if e["jenis"] == "OPEX")
            outc = cg + op
            omz = m_obj["omzet"]
            nt = omz - outc
            mg = (nt / omz * 100.0) if omz > 0 else 0.0
            ads = sum(e["nilai"] for e in m_obj["expenses"] if e.get("kategori") == "Marketing / Ads / KOL" or "ads" in e.get("desc", "").lower() or "iklan" in e.get("desc", "").lower())
            
            m_obj["cogs"] = cg
            m_obj["opex"] = op
            m_obj["outcome"] = outc
            m_obj["nettProfit"] = nt
            m_obj["margin"] = round(mg, 2)
            m_obj["ads"] = ads
            
            y_omz += omz
            y_cash += m_obj["cash"]
            y_trf += m_obj["transfer"]
            y_cg += cg
            y_op += op
            y_out += outc
            y_nt += nt
            
            print(f"2026 M{m:02d} ({m_obj['name']}): Omzet={omz:,.0f} | COGS={cg:,.0f} ({len([e for e in m_obj['expenses'] if e['jenis']=='COGS'])}) | OPEX={op:,.0f} ({len([e for e in m_obj['expenses'] if e['jenis']=='OPEX'])}) | Ads={ads:,.0f} | Daily={len(m_obj['daily'])}")

    y_mg = (y_nt / y_omz * 100.0) if y_omz > 0 else 0.0
    my["years"]["2026"]["omzet"] = y_omz
    my["years"]["2026"]["cash"] = y_cash
    my["years"]["2026"]["transfer"] = y_trf
    my["years"]["2026"]["cogs"] = y_cg
    my["years"]["2026"]["opex"] = y_op
    my["years"]["2026"]["outcome"] = y_out
    my["years"]["2026"]["nettProfit"] = y_nt
    my["years"]["2026"]["margin"] = round(y_mg, 2)

    # Save to multiyear_cache.json
    with open("multiyear_cache.json", "w", encoding="utf-8") as f:
        json.dump(my, f, ensure_ascii=False, indent=2)
    print("Saved multiyear_cache.json successfully.")

    # Sync to foxe_full_state.json
    fs["multiyearArsip"] = my
    with open("foxe_full_state.json", "w", encoding="utf-8") as f:
        json.dump(fs, f, ensure_ascii=False, indent=2)
    print("Synced to foxe_full_state.json successfully.")

if __name__ == "__main__":
    main()
