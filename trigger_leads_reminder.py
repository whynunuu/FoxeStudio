"""
Foxe Studio — CLI / Cron Trigger Follow-Up Reminder
===================================================
Script pemicu pengiriman reminder follow-up admin Foxe Studio
via WhatsApp (Fonnte) dan Telegram Bot (@NunuFxBot).
Berjalan di jam operasional 09:00 - 21:00 WIB (interval 3 jam).
"""

import sys
import datetime
from datetime import timezone, timedelta
from agentic_lead_engine import AgenticLeadEngine

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

WIB = timezone(timedelta(hours=7))
now_wib = datetime.datetime.now(WIB)
hour_label = f"{now_wib.strftime('%H:%M')} WIB"

import os
import json
import urllib.request

# Status Reminder: Aktif di jam 10:00, 14:00, 20:00 WIB
REMINDER_ENABLED = os.environ.get("ENABLE_LEADS_REMINDER", "true").lower() in ("true", "1", "yes")

if not REMINDER_ENABLED:
    print(f"[{now_wib.strftime('%Y-%m-%d %H:%M:%S')} WIB] [INFO] Follow-Up Reminder dinonaktifkan.")
    print("Pengiriman pesan reminder ke Telegram & WhatsApp dilewati.")
    sys.exit(0)

print(f"[{now_wib.strftime('%Y-%m-%d %H:%M:%S')} WIB] Menjalankan Trigger Follow-Up Reminder Foxe Studio ({hour_label})...")

try:
    engine = AgenticLeadEngine()

    # Ambil leads live terbaru dari server Railway jika tersedia
    try:
        req = urllib.request.Request("https://foxestudio.up.railway.app/api/leads", headers={"User-Agent": "FoxeReminder/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                live_data = json.loads(resp.read().decode("utf-8"))
                if live_data.get("leads"):
                    engine.leads = live_data["leads"]
                    print(f"[SYNC] Memuat {len(engine.leads)} leads live dari Railway.")
    except Exception as e:
        print(f"[WARN] Menggunakan data leads lokal: {e}")

    result = engine.send_followup_reminder(current_hour_str=hour_label)
    print("Hasil Pengiriman Reminder:", result)
    if result.get("telegram") or result.get("whatsapp"):
        print("✓ Sukses terkirim ke:", ", ".join(result.get("recipients", [])))
        sys.exit(0)
    else:
        print("[WARN] Tidak ada kanal yang berhasil terkirim.")
        sys.exit(0)
except Exception as e:
    print("[ERROR] Gagal mengeksekusi reminder:", e)
    sys.exit(1)
