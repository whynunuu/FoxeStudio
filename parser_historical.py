"""
=============================================================================
Foxe Studio — Parser Data Historis 2026 (Januari s.d. Agustus)
=============================================================================
Parser khusus untuk mengurai data operasional bulanan (Januari–Agustus 2026):
- File 1 Log Order per bulan (file1_jan.xlsx s.d. file1_ags.xlsx)
- File 2 Schedule per bulan (file2_jan.xlsx s.d. file2_ags.xlsx)
- Section Detail & Rekap Neraca per sheet bulanan di file_neraca.xlsx
=============================================================================
"""

import os
import openpyxl
from parser_log_order import parse_log_order
from parser_schedule import parse_schedule
from parser_neraca import parse_neraca

HISTORICAL_CONFIG = [
    {
        "no": 1,
        "nama": "Januari",
        "label": "Januari 2026",
        "iso": "2026-01",
        "f_log": "file1_jan.xlsx",
        "f_sch": "file2_jan.xlsx",
        "sheet_neraca": "Januari 2026",
        "bench25": 46000000,
        "momentum": "Pasca Liburan & Tahun Baru",
        "musim": "Low Season"
    },
    {
        "no": 2,
        "nama": "Februari",
        "label": "Februari 2026",
        "iso": "2026-02",
        "f_log": "file1_feb.xlsx",
        "f_sch": "file2_feb.xlsx",
        "sheet_neraca": "Februari 2026",
        "bench25": 48000000,
        "momentum": "Couple & Valentine Session",
        "musim": "Low Season"
    },
    {
        "no": 3,
        "nama": "Maret",
        "label": "Maret 2026",
        "iso": "2026-03",
        "f_log": "file1_mar.xlsx",
        "f_sch": "file2_mar.xlsx",
        "sheet_neraca": "Maret 2026",
        "bench25": 52000000,
        "momentum": "Pra-Ramadhan & Family Portrait",
        "musim": "Normal Season"
    },
    {
        "no": 4,
        "nama": "April",
        "label": "April 2026",
        "iso": "2026-04",
        "f_log": "file1_apr.xlsx",
        "f_sch": "file2_apr.xlsx",
        "sheet_neraca": "April 2026",
        "bench25": 51000000,
        "momentum": "Hari Raya Idul Fitri & Liburan",
        "musim": "Low / Normal Season"
    },
    {
        "no": 5,
        "nama": "Mei",
        "label": "Mei 2026",
        "iso": "2026-05",
        "f_log": "file1_mei.xlsx",
        "f_sch": "file2_mei.xlsx",
        "sheet_neraca": "Mei 2026",
        "bench25": 55000000,
        "momentum": "Wisuda Gelombang 1 & Grup",
        "musim": "Normal Season"
    },
    {
        "no": 6,
        "nama": "Juni",
        "label": "Juni 2026",
        "iso": "2026-06",
        "f_log": "file1_jun.xlsx",
        "f_sch": "file2_jun.xlsx",
        "sheet_neraca": "Juni 2026",
        "bench25": 54000000,
        "momentum": "Wisuda Tengah Tahun & Liburan Sekolah",
        "musim": "High Season"
    },
    {
        "no": 7,
        "nama": "Juli",
        "label": "Juli 2026",
        "iso": "2026-07",
        "f_log": "file1_jul.xlsx",
        "f_sch": "file2_jul.xlsx",
        "sheet_neraca": "July 2026",
        "bench25": 53000000,
        "momentum": "Tahun Ajaran Baru & Mahasiswa Baru",
        "musim": "Low / Normal Season"
    },
    {
        "no": 8,
        "nama": "Agustus",
        "label": "Agustus 2026",
        "iso": "2026-08",
        "f_log": "file1_ags.xlsx",
        "f_sch": "file2_ags.xlsx",
        "sheet_neraca": "Agustus 2026",
        "bench25": 59000000,
        "momentum": "Wisuda Periode 2 & Pra-Wisuda Akbar",
        "musim": "Normal / High Season"
    }
]

def parse_historical_months(neraca_path="file_neraca.xlsx"):
    historical_months = {}
    neraca_by_month = {}
    roster_gaji_by_month = {}

    for cfg in HISTORICAL_CONFIG:
        m_no = str(cfg["no"])
        iso = cfg["iso"]
        f_log = cfg["f_log"]
        f_sch = cfg["f_sch"]
        sheet_nrc = cfg["sheet_neraca"]
        bench = cfg["bench25"]

        if not os.path.exists(f_log):
            print(f"[WARN] File Log Order {f_log} untuk {cfg['label']} tidak ditemukan, skip.")
            continue

        # 1. Parse Log Order
        res_lo = parse_log_order(f_log, bulan=iso)
        orders = res_lo.get("orders", [])
        tot_omzet = sum(o.get("total", 0) for o in orders)
        cash = sum(o.get("cash", 0) for o in orders)
        transfer = sum(o.get("transfer", 0) for o in orders)
        shifts = res_lo.get("shifts", [])
        leads = res_lo.get("leads", [])
        kpi = res_lo.get("kpi", [])

        # Top Packages
        pkg_counts = {}
        for o in orders:
            p = o.get("paket") or "Lainnya"
            pkg_counts[p] = pkg_counts.get(p, 0) + 1
        top_paket = [{"nama": p, "count": c} for p, c in sorted(pkg_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

        # Crew Shifts
        crew_shifts = {}
        for s in shifts:
            c = s.get("nama")
            if c:
                crew_shifts[c] = crew_shifts.get(c, 0) + 1

        # 2. Parse Schedule (jika ada)
        sessions_count = 0
        if os.path.exists(f_sch):
            try:
                bookings = parse_schedule(f_sch, bulan=iso)
                sessions_count = len(bookings)
            except Exception as e:
                print(f"[WARN] Gagal parse schedule {f_sch}: {e}")

        # 3. Parse Neraca
        cogs = 0.0
        opex = 0.0
        thp_gaji = 0.0
        res_nrc = {"expenses": [], "detail": [], "summary": {}, "rosterGaji": [], "rosterSummary": {}}
        if os.path.exists(neraca_path):
            try:
                res_nrc = parse_neraca(neraca_path, sheet_name=sheet_nrc)
                exps = res_nrc.get("expenses", [])
                cogs = sum(e["nilai"] for e in exps if e.get("jenis") == "COGS")
                opex = sum(e["nilai"] for e in exps if e.get("jenis") == "OPEX")
                thp_gaji = res_nrc.get("rosterSummary", {}).get("grand_total_thp", 0.0)
            except Exception as e:
                print(f"[WARN] Gagal parse neraca {sheet_nrc}: {e}")

        neraca_by_month[iso] = res_nrc
        roster_gaji_by_month[iso] = res_nrc.get("rosterGaji", [])

        nett_profit = tot_omzet - cogs - opex
        margin = (nett_profit / tot_omzet * 100) if tot_omzet > 0 else 0.0
        yoy = ((tot_omzet - bench) / bench * 100) if bench > 0 else 0.0

        historical_months[m_no] = {
            "no": cfg["no"],
            "nama": cfg["nama"],
            "label": cfg["label"],
            "iso": iso,
            "omzet": tot_omzet,
            "cash": cash,
            "transfer": transfer,
            "ordersCount": len(orders),
            "bench25": bench,
            "yoy": yoy,
            "cogs": cogs,
            "opex": opex,
            "nettProfit": nett_profit,
            "margin": margin,
            "thpGaji": thp_gaji,
            "topPaket": top_paket,
            "crewShifts": crew_shifts,
            "totalShifts": len(shifts),
            "sessionsCount": sessions_count,
            "leadsDays": len(leads),
            "kpiEntries": len(kpi),
            "hasLeadsKpi": (len(leads) > 0 or len(kpi) > 0),
            "momentum": cfg["momentum"],
            "musim": cfg["musim"],
            "status": "Terverifikasi (Real Data)"
        }

        print(f"[OK] {cfg['label']}: Omzet Rp {tot_omzet:,.0f} | Orders {len(orders)} | YoY {yoy:+.2f}% | Nett Rp {nett_profit:,.0f}")

    return {
        "historicalMonths": historical_months,
        "neracaByMonth": neraca_by_month,
        "rosterGajiByMonth": roster_gaji_by_month
    }

if __name__ == "__main__":
    res = parse_historical_months()
    print(f"\nBerhasil mengurai {len(res['historicalMonths'])} bulan historis.")
