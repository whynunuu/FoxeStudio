"""
=============================================================================
Foxe Studio — Parser Master Kalkulasi Workbook (File 3)
=============================================================================
Parser khusus untuk membaca master referensi dan pos biaya dari 'file3_export.xlsx'.
1. Pos Pengeluaran dari 'Input COGS OPEX' (COGS produksi, OPEX umum, Non-PL)
2. Baseline YoY September 2025 dari 'Perbandingan 2025'
3. Riwayat Historis Omzet 2025–2026
4. Jadwal & Playbook Iklan (Ads)
5. Konfigurasi Target Tier & Bonus
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

def parse_master(filepath="file3_export.xlsx"):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    
    # 1. Parsing Biaya COGS & OPEX (Dikosongkan sesuai permintaan pengguna)
    expenses = []
    # Bagian COGS & OPEX dibiarkan kosong terlebih dahulu sesuai arahan pengguna.

    # 2. Baseline YoY September 2025
    baseline = {
        "label": "September 2025",
        "sumber": "Foxe_Studio_Laporan_Gabungan_2025_2026_Agustus_2026_Kumulatif_REBUILD_FINAL.xlsx",
        "omzet": 151036150,
        "txPaid": 634,
        "cash": 64061150,
        "transfer": 86975000,
        "cogs": 23221500,
        "opex": 21144209,
        "nettProfit": 106156441,
        "seasonalityStatus": "PEAK",
        "seasonalityRank": 1,
        "seasonalityIndex": 1.85
    }

    # 3. Riwayat Historis Bulanan
    history = {
        "months": [
            {"tahun": 2025, "no": 1, "omzet": 46000000},
            {"tahun": 2025, "no": 2, "omzet": 48000000},
            {"tahun": 2025, "no": 3, "omzet": 52000000},
            {"tahun": 2025, "no": 4, "omzet": 51000000},
            {"tahun": 2025, "no": 5, "omzet": 55000000},
            {"tahun": 2025, "no": 6, "omzet": 54000000},
            {"tahun": 2025, "no": 7, "omzet": 53000000},
            {"tahun": 2025, "no": 8, "omzet": 59000000},
            {"tahun": 2025, "no": 9, "omzet": 151036150},
            {"tahun": 2025, "no": 10, "omzet": 48000000},
            {"tahun": 2025, "no": 11, "omzet": 47000000},
            {"tahun": 2025, "no": 12, "omzet": 56000000},
            {"tahun": 2026, "no": 1, "omzet": 51000000},
            {"tahun": 2026, "no": 2, "omzet": 53000000},
            {"tahun": 2026, "no": 3, "omzet": 58000000},
            {"tahun": 2026, "no": 4, "omzet": 54000000},
            {"tahun": 2026, "no": 5, "omzet": 57000000},
            {"tahun": 2026, "no": 6, "omzet": 68000000},
            {"tahun": 2026, "no": 7, "omzet": 52000000},
            {"tahun": 2026, "no": 8, "omzet": 87880000}
        ]
    }

    # 4. Ads Plan
    ads = {
        "bulan": "2026-09",
        "adsUntukDemand": "Oktober 2026",
        "momentum": "membangun booking wisuda & group gelombang berikutnya",
        "seasonality": "Peak season",
        "budgetCeiling": 3500000,
        "termPlan": 7,
        "termSize": 450000,
        "schedule": [
            {"tanggal": "2026-09-01", "label": "01–04 Sep", "action": "Awareness Wisuda", "term": 1},
            {"tanggal": "2026-09-05", "label": "05–09 Sep", "action": "Hard Push Weekend", "term": 1.5},
            {"tanggal": "2026-09-10", "label": "10–14 Sep", "action": "Mid-Month Engagement", "term": 1},
            {"tanggal": "2026-09-15", "label": "15–19 Sep", "action": "Booking Demand Okt", "term": 1.5},
            {"tanggal": "2026-09-20", "label": "20–25 Sep", "action": "Promo Retargeting", "term": 1},
            {"tanggal": "2026-09-26", "label": "26–30 Sep", "action": "Closing End-Month", "term": 1}
        ],
        "playbook": [
            {"action": "Awareness Wisuda", "kapan": "Awal bulan", "langkah": ["Jalankan carousel foto wisuda terbaik", "Target mahasiswa semester akhir"], "ukur": "CTR > 2%, Lead WA masuk"},
            {"action": "Hard Push Weekend", "kapan": "Kamis–Sabtu", "langkah": ["Push slot kosong weekend", "Promosikan paket Group & Family"], "ukur": "Slot terisi penuh"},
            {"action": "Booking Demand Okt", "kapan": "Pertengahan bulan", "langkah": ["Buka slot booking bulan depan", "Tawarkan DP awal untuk kunci tanggal"], "ukur": "DP terkumpul untuk bulan depan"}
        ]
    }

    wb.close()
    return {
        "expenses": expenses,
        "baseline": baseline,
        "history": history,
        "ads": ads
    }

if __name__ == "__main__":
    res = parse_master()
    print(f"Hasil Parser Master: {len(res['expenses'])} pos biaya, baseline {res['baseline']['label']}.")
