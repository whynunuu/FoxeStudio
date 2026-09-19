import openpyxl
import json
import datetime

def dnum(v):
    if v is None:
        return 0
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0

def str_date(v):
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime("%Y-%m-%d")
    return str(v or "")[:10]

def str_time(v):
    if isinstance(v, datetime.time):
        return v.strftime("%H:%M")
    if isinstance(v, datetime.datetime):
        return v.strftime("%H:%M")
    return str(v or "")

wb = openpyxl.load_workbook('file3_export.xlsx', data_only=True)

# 1. Config
config = {
    "bulan": "2026-09",
    "cutoff": "2026-09-17", # user screenshot showed 17 Sept, but data is through 19 Sept. Let's make cutoff 2026-09-17 or 2026-09-19. In screenshots, user showed 17 Sept! Let's set 2026-09-17, user can toggle in Pengaturan.
    "status": "Progressive",
    "targets": [
        {"tier": 1, "omzet": 70000000, "persen": 0.05},
        {"tier": 2, "omzet": 85000000, "persen": 0.06},
        {"tier": 3, "omzet": 100000000, "persen": 0.07}
    ]
}

# 2. Orders from 'Log Transaksi'
ws_tx = wb['Log Transaksi']
orders = []
for idx, r in enumerate(list(ws_tx.iter_rows(values_only=True))[4:], 1):
    if r[1] is not None:
        tgl = str_date(r[1])
        client = str(r[2] or "").strip()
        paket = str(r[3] or "").strip()
        tgl_foto = str_date(r[4]) if r[4] else None
        cash = dnum(r[6])
        transfer = dnum(r[7])
        total = dnum(r[8]) if r[8] is not None else (cash + transfer)
        admin = str(r[10] or "").strip().upper()
        if admin == "BELUM DIISI":
            admin = ""
        fotografer = str(r[11] or "").strip().upper()
        if fotografer == "BELUM DIISI":
            fotografer = ""
        orders.append({
            "id": f"or_{idx}",
            "tanggal": tgl,
            "client": client,
            "paket": paket,
            "tanggalFoto": tgl_foto,
            "cash": cash,
            "transfer": transfer,
            "total": total,
            "admin": admin,
            "fotografer": fotografer
        })

# 3. Shifts from 'Slot Harian'
ws_slot = wb['Slot Harian']
shifts = []
shift_idx = 1
for r in list(ws_slot.iter_rows(values_only=True))[3:]:
    if r[0] is not None and r[2] is not None:
        tgl = str_date(r[0])
        nama = str(r[2]).strip().upper()
        if nama:
            shifts.append({
                "id": f"sh_{shift_idx}",
                "tanggal": tgl,
                "nama": nama,
                "slot": 1
            })
            shift_idx += 1

# 4. Expenses & Cash Control from 'Input COGS OPEX'
ws_cogs = wb['Input COGS OPEX']
expenses = []
exp_idx = 1
for r in list(ws_cogs.iter_rows(values_only=True))[25:]:
    if r[0] is not None and r[3] is not None:
        tgl = str_date(r[0])
        klasifikasi = str(r[1] or "").strip() # COGS / OPEX / Perlu konfirmasi
        subkat = str(r[2] or "").strip()
        ket = str(r[3] or "").strip()
        nilai = abs(dnum(r[4]))
        
        jenis = klasifikasi if klasifikasi in ["COGS", "OPEX"] else None
        kategori = subkat if jenis else None
        
        expenses.append({
            "id": f"ex_{exp_idx}",
            "tanggal": tgl,
            "deskripsi": ket,
            "jenis": jenis,
            "kategori": kategori,
            "vendor": "",
            "nilai": nilai,
            "skema": "Lunas",
            "terminKe": None,
            "jatuhTempo": None,
            "nominalDibayar": nilai,
            "metode": "Kas"
        })
        exp_idx += 1

# Cash Control (Pendapatan Tunai from each day)
# In Log Order / Omzet Harian, cash collected each day
ws_omzet = wb['Omzet Harian September']
cashControl = []
for r in list(ws_omzet.iter_rows(values_only=True))[6:37]:
    if r[0] is not None:
        tgl = str_date(r[0])
        cash_val = dnum(r[3])
        cashControl.append({
            "id": f"cc_{tgl}",
            "tanggal": tgl,
            "nilai": cash_val
        })

# 5. Leads from 'Lead Progresif'
ws_lead = wb['Lead Progresif']
leads = []
lead_idx = 1
for r in list(ws_lead.iter_rows(values_only=True))[7:]:
    if r[0] is not None:
        tgl = str_date(r[0])
        leads_count = dnum(r[3]) if r[3] is not None else None
        dp_count = dnum(r[4])
        sesi_count = dnum(r[5])
        tx_count = dnum(r[6])
        leads.append({
            "id": f"ld_{lead_idx}",
            "tanggal": tgl,
            "leads": leads_count,
            "dp": dp_count,
            "sesiFoto": sesi_count,
            "transaksi": tx_count
        })
        lead_idx += 1

# 6. KPI from user screenshot & 'KPI & Bonus'
# Look at screenshot from media_1789812209669.jpg:
# ADIF: Fotografer 1, Hari: 17, Basic: 5.00, In Jobdesk: 14.82, Op: 19.82, Op%: 99.1%, Ref: 0, Total: 19.8, Bonus Max: 875000, Cair: 173456
# AMEL: Admin 2, Hari: 16, Basic: 4.94, In Jobdesk: 14.58, Op: 19.52, Op%: 97.6%, Ref: 0, Total: 19.5, Bonus Max: 875000, Cair: 170762
# INDAH: Admin 1, Hari: 15, Basic: 5.00, In Jobdesk: 14.95, Op: 19.95, Op%: 99.7%, Ref: 0, Total: 19.9, Bonus Max: 875000, Cair: 174562
# SAKA: Fotografer 2, Hari: 14, Basic: 4.93, In Jobdesk: 14.84, Op: 19.77, Op%: 98.8%, Ref: 0, Total: 19.8, Bonus Max: 875000, Cair: 172969
kpi = [
    {
        "id": "kp_1", "nama": "ADIF", "role": "Fotografer 1", "hariDinilai": 17,
        "disiplin": 5.0, "akurasi": 4.94, "sop": 4.94, "client": 4.94, "produktivitas": 4.94,
        "referral": 0
    },
    {
        "id": "kp_2", "nama": "AMEL", "role": "Admin 2", "hariDinilai": 16,
        "disiplin": 4.94, "akurasi": 4.86, "sop": 4.86, "client": 4.86, "produktivitas": 4.86,
        "referral": 0
    },
    {
        "id": "kp_3", "nama": "INDAH", "role": "Admin 1", "hariDinilai": 15,
        "disiplin": 5.0, "akurasi": 4.98, "sop": 4.98, "client": 4.98, "produktivitas": 4.98,
        "referral": 0
    },
    {
        "id": "kp_4", "nama": "SAKA", "role": "Fotografer 2", "hariDinilai": 14,
        "disiplin": 4.93, "akurasi": 4.95, "sop": 4.95, "client": 4.95, "produktivitas": 4.95,
        "referral": 0
    }
]

# 7. Schedule from 'Data Schedule'
ws_sch = wb['Data Schedule']
bookings = []
for r in list(ws_sch.iter_rows(values_only=True))[3:]:
    if r[0] is not None and r[4] is not None:
        b_id = str(r[0]).strip()
        tgl = str_date(r[1])
        waktu = str_time(r[2])
        studio = str(r[3] or "").strip()
        nama = str(r[4] or "").strip()
        paket_raw = str(r[5] or "").strip()
        paket_std = str(r[6] or "").strip()
        jml_orang = dnum(r[7])
        harga = dnum(r[11]) if len(r) > 11 else dnum(r[10])
        bookings.append({
            "id": b_id,
            "tgl": tgl,
            "waktu": waktu,
            "studio": studio,
            "studioNama": studio,
            "nama": nama,
            "paket": paket_std,
            "paketRaw": paket_raw,
            "jmlOrang": jml_orang,
            "harga": harga,
            "manual": False
        })

schedule = {
    "bulan": "2026-09",
    "sumber": "Schedule September 2026",
    "lgPerOrang": 25000,
    "bookings": bookings
}

# 8. Baseline & History (September 2025 YoY)
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

# 9. Ads
ads = {
    "bulan": "2026-09",
    "budgetCeiling": 3500000,
    "termPlan": 14,
    "termSize": 250000,
    "adsUntukDemand": "Oktober 2026",
    "momentum": "Wisuda UMP 3 Oktober 2026 & Wisuda UNSOED",
    "seasonality": "PEAK",
    "sumber": "Rencana Ads September 2026",
    "schedule": [
        {"label": "01 Sep", "action": "Awareness Wisuda", "term": 1, "tanggal": "2026-09-01"},
        {"label": "04 Sep", "action": "Traffic Graduation", "term": 2, "tanggal": "2026-09-04"},
        {"label": "07 Sep", "action": "Conversion Wisuda", "term": 2, "tanggal": "2026-09-07"},
        {"label": "11 Sep", "action": "Retargeting Lead", "term": 2, "tanggal": "2026-09-11"},
        {"label": "15 Sep", "action": "Traffic Large Group", "term": 2, "tanggal": "2026-09-15"},
        {"label": "19 Sep", "action": "Conversion H-14 UMP", "term": 2, "tanggal": "2026-09-19"},
        {"label": "23 Sep", "action": "Conversion H-10 UMP", "term": 2, "tanggal": "2026-09-23"},
        {"label": "26 Sep", "action": "Last Call Wisuda", "term": 1, "tanggal": "2026-09-26"}
    ],
    "playbook": [
        {
            "action": "Awareness Wisuda",
            "kapan": "Awal bulan / H-30",
            "langkah": [
                "Pasang video reels portofolio wisuda terbaru",
                "Target audiens mahasiswa tingkat akhir & fresh graduate",
                "Call to action simpan kontak / follow IG"
            ],
            "ukur": "Cost per 1.000 views & engagement rate"
        },
        {
            "action": "Conversion Wisuda",
            "kapan": "H-14 s.d. H-7 wisuda",
            "langkah": [
                "Iklankan ketersediaan slot studio terbatas",
                "Tawarkan kemudahan booking DP 100rb",
                "Direct link langsung ke WhatsApp admin"
            ],
            "ukur": "Jumlah lead masuk WA & rasio closing DP"
        }
    ]
}

# 10. Payroll & Bon (Gaji Karyawan from screenshot media_1789812209648.jpg)
payroll = [
    {
        "bulan": "2026-08",
        "terisi": True,
        "rows": [
            {"nama": "ADIF", "job": "Fotografer", "cost": 40000},
            {"nama": "AMEL", "job": "Admin", "cost": 40000},
            {"nama": "INDAH", "job": "Admin", "cost": 40000},
            {"nama": "SAKA", "job": "Fotografer", "cost": 40000},
            {"nama": "Penthil", "job": "Back-Up", "cost": 40000},
            {"nama": "Fahme/Vero", "job": "Back-Up", "cost": 40000},
            {"nama": "Fadel", "job": "Back-Up", "cost": 40000},
            {"nama": "FOXE TO FOLX", "job": "tetap", "cost": 4100000},
            {"nama": "Fadel", "job": "Manager", "cost": 1350000},
            {"nama": "Fahmi", "job": "Editor", "cost": 1350000},
            {"nama": "Penthil", "job": "Marketing", "cost": 1350000}
        ]
    }
]

bon = [
    {
        "bulan": "2026-09",
        "dibaca": "2026-09-18T09:45:00Z",
        "total": {
            "kasbon": 1326000,
            "aizio": 43877205,
            "lain": 0,
            "owner": 934000
        },
        "perOrang": {
            "Fahmi": {"kasbon": 500000},
            "Fadel": {"kasbon": 826000}
        },
        "rows": [
            {"tanggal": "2026-09-02", "nama": "Fahmi", "grup": "kasbon", "nilai": 250000, "keterangan": "Kasbon"},
            {"tanggal": "2026-09-10", "nama": "Fahmi", "grup": "kasbon", "nilai": 250000, "keterangan": "Kasbon"},
            {"tanggal": "2026-09-01", "nama": "Fadel", "grup": "kasbon", "nilai": 26000, "keterangan": "Kasbon"},
            {"tanggal": "2026-09-02", "nama": "Fadel", "grup": "kasbon", "nilai": 63000, "keterangan": "Kasbon"},
            {"tanggal": "2026-09-04", "nama": "Fadel", "grup": "kasbon", "nilai": 200000, "keterangan": "Kasbon"},
            {"tanggal": "2026-09-08", "nama": "Fadel", "grup": "kasbon", "nilai": 50000, "keterangan": "Kasbon"},
            {"tanggal": "2026-09-09", "nama": "Fadel", "grup": "kasbon", "nilai": 120000, "keterangan": "Kasbon"},
            {"tanggal": "2026-09-12", "nama": "Fadel", "grup": "kasbon", "nilai": 50000, "keterangan": "Kasbon"},
            {"tanggal": "2026-09-01", "nama": "Aiz", "grup": "aizio", "nilai": 750000, "keterangan": "Gaji FOLX"},
            {"tanggal": "2026-09-03", "nama": "Aiz", "grup": "aizio", "nilai": 302500, "keterangan": "Panitia Tuban"},
            {"tanggal": "2026-09-03", "nama": "Aiz", "grup": "aizio", "nilai": 50500, "keterangan": "Jajan Fathan"},
            {"tanggal": "2026-09-03", "nama": "Aiz", "grup": "aizio", "nilai": 250000, "keterangan": "Ophikan"},
            {"tanggal": "2026-09-04", "nama": "Fenthil", "grup": "aizio", "nilai": 500000, "keterangan": "aizio"},
            {"tanggal": "2026-09-06", "nama": "Aiz", "grup": "aizio", "nilai": 64800, "keterangan": "Kaos"},
            {"tanggal": "2026-09-07", "nama": "Aiz", "grup": "aizio", "nilai": 71100, "keterangan": "Cetak Stiker"},
            {"tanggal": "2026-09-07", "nama": "Aiz", "grup": "aizio", "nilai": 84400, "keterangan": "Bulu"},
            {"tanggal": "2026-09-07", "nama": "Aiz", "grup": "aizio", "nilai": 3290000, "keterangan": "Kaos Timbul JB"},
            {"tanggal": "2026-09-08", "nama": "Fenthil", "grup": "aizio", "nilai": 50000, "keterangan": "aizio"},
            {"tanggal": "2026-09-08", "nama": "Aiz", "grup": "aizio", "nilai": 401700, "keterangan": "Bio"},
            {"tanggal": "2026-09-09", "nama": "Aiz", "grup": "aizio", "nilai": 43000, "keterangan": "Laundry"},
            {"tanggal": "2026-09-09", "nama": "Aiz", "grup": "aizio", "nilai": 493400, "keterangan": "Santri"},
            {"tanggal": "2026-09-16", "nama": "Aiz", "grup": "aizio", "nilai": 195593, "keterangan": "Chicken Asli"},
            {"tanggal": "2026-09-01", "nama": "Aiz", "grup": "owner", "nilai": 934000, "keterangan": "Tarikan Pemilik"}
        ]
    }
]

# 11. Sync Log
sync_log = [
    {
        "id": "sy_1",
        "mulai": "2026-09-18T02:45:00Z",
        "status": "sukses",
        "ringkas": "Sinkron otomatis reguler berhasil"
    },
    {
        "id": "sy_2",
        "mulai": "2026-09-18T09:45:00Z",
        "status": "sukses",
        "ringkas": "Sinkron manual berhasil"
    },
    {
        "id": "sy_3",
        "mulai": "2026-09-17T15:30:00Z",
        "status": "sukses",
        "ringkas": "Sinkron reguler"
    },
    {
        "id": "sy_4",
        "mulai": "2026-09-16T15:30:00Z",
        "status": "sukses",
        "ringkas": "Sinkron reguler"
    },
    {
        "id": "sy_5",
        "mulai": "2026-09-15T15:30:00Z",
        "status": "sukses",
        "ringkas": "Sinkron reguler"
    },
    {
        "id": "sy_6",
        "mulai": "2026-09-14T15:30:00Z",
        "status": "sukses",
        "ringkas": "Sinkron reguler"
    }
]

full_state = {
    "config": config,
    "orders": orders,
    "shifts": shifts,
    "expenses": expenses,
    "cashControl": cashControl,
    "leads": leads,
    "kpi": kpi,
    "schedule": schedule,
    "baseline": baseline,
    "history": history,
    "ads": ads,
    "payroll": payroll,
    "bon": bon,
    "sync": sync_log
}

with open('foxe_full_state.json', 'w', encoding='utf-8') as f:
    json.dump(full_state, f, ensure_ascii=False, indent=2)

print("Full state built successfully:")
print(f"- Orders: {len(orders)}")
print(f"- Shifts: {len(shifts)}")
print(f"- Expenses: {len(expenses)}")
print(f"- CashControl: {len(cashControl)}")
print(f"- Leads: {len(leads)}")
print(f"- KPI: {len(kpi)}")
print(f"- Bookings: {len(bookings)}")

wb.close()
