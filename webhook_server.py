"""
Foxe Studio — Railway Webhook Receiver & Agentic AI Lead Service
===============================================================
Layanan backend siap deploy di Railway untuk menerima webhook chat WhatsApp (Fonnte),
mencocokkan data transaksi di Log Order / state, mengklasifikasi tier (Hot/Warm/Cold),
dan meracik balasan humanis via Google Gemini API secara real-time.
"""

import os
import json
import time
import datetime
import asyncio
from datetime import timezone, timedelta
from typing import Optional
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import urllib.parse
from agentic_lead_engine import (
    AgenticLeadEngine, FOXE_PAYMENT_INFO, FONNTE_TOKEN, STATE_FILE,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
)

WIB = timezone(timedelta(hours=7))
REMINDER_HOURS = [10, 14, 20] # Jam pengiriman reminder Foxe Studio (10:00, 14:00, 20:00 WIB)
last_reminder_slot = ""

app = FastAPI(
    title="Foxe Studio AI Lead Webhook & Follow-Up Reminder",
    description="Webhook listener, 3-hour Follow-up Reminder & AI Lead Assistant for Foxe Studio WhatsApp",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi engine
engine = AgenticLeadEngine()

def sync_state_from_remote():
    """Mengambil foxe_full_state.json terkini dari GitHub Pages agar data studio selalu up-to-date."""
    url = f"https://whynunuu.github.io/FoxeStudio/foxe_full_state.json?t={int(time.time())}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FoxeRailway/1.0"})
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status == 200:
                raw_data = json.loads(res.read().decode("utf-8"))
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(raw_data, f, ensure_ascii=False, indent=2)
                engine.state = raw_data
                orders_count = len(raw_data.get("orders", []))
                sched_count = len(raw_data.get("schedule", []))
                print(f"[STATE SYNC] Berhasil sinkronisasi jadwal dari GitHub Pages ({orders_count} orders, {sched_count} bookings).")
                return {"status": "success", "orders": orders_count, "schedules": sched_count}
    except Exception as e:
        print(f"[STATE SYNC WARN] Gagal sinkronisasi dari GitHub Pages: {e}")
        return {"status": "error", "message": str(e)}

async def state_sync_loop():
    """
    Background Task Scheduler di Railway:
    Sinkronisasi berkala jadwal & transaksi dari GitHub Pages setiap 15 menit.
    """
    print("[SCHEDULER] Auto-Sync State Jadwal Aktif (Interval 15 Menit)")
    while True:
        try:
            sync_state_from_remote()
        except Exception as e:
            print(f"[STATE LOOP ERROR] {e}")
        await asyncio.sleep(900) # 15 menit

REMINDER_ENABLED = os.environ.get("ENABLE_LEADS_REMINDER", "true").lower() in ("true", "1", "yes")

async def reminder_scheduler_loop():
    """
    Background Task Scheduler 24/7 di Railway:
    Mengecek waktu lokal WIB setiap menit. Jika berada di jadwal reminder studio
    (10:00, 14:00, 20:00 WIB), kirim reminder follow-up ke WhatsApp & Telegram.
    Hanya dikirim TEPAT SATU KALI per slot jam.
    """
    global last_reminder_slot
    if not REMINDER_ENABLED:
        print("[SCHEDULER] Background Reminder Scheduler DINONAKTIFKAN.")
        return
    print("[SCHEDULER] Background Reminder Scheduler Aktif (10:00, 14:00, 20:00 WIB)")
    while True:
        try:
            now_wib = datetime.datetime.now(WIB)
            current_hour = now_wib.hour
            current_slot = f"{now_wib.strftime('%Y-%m-%d')}_{current_hour:02d}"

            if current_hour in REMINDER_HOURS and current_slot != last_reminder_slot:
                hour_label = f"{current_hour:02d}:00 WIB"
                print(f"[{now_wib.strftime('%H:%M:%S')} WIB] Mengeksekusi trigger reminder ({hour_label})...")
                last_reminder_slot = current_slot
                res = engine.send_followup_reminder(current_hour_str=hour_label)
                print(f"[SCHEDULER SELESAI] Hasil: {res}")
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")

        await asyncio.sleep(40)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(state_sync_loop())
    asyncio.create_task(reminder_scheduler_loop())

@app.get("/")
def root():
    now_wib = datetime.datetime.now(WIB)
    return {
        "status": "online",
        "service": "Foxe Studio Agentic AI Lead & Reminder Engine",
        "studio": "Foxe Studio (Purwokerto)",
        "whatsapp_device": "0851-5921-0021 (Foxe Admin)",
        "gemini_ai": "Connected",
        "operational_hours": "09:00 - 21:00 WIB",
        "reminder_schedule": "Pukul 10:00, 14:00, dan 20:00 WIB (Kirim ke WhatsApp & Telegram)",
        "current_time_wib": now_wib.strftime("%Y-%m-%d %H:%M:%S WIB")
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/leads")
def get_leads():
    """Mengambil daftar leads tersimpan untuk disinkronkan ke dashboard."""
    return engine.get_leads_summary()

@app.get("/api/trigger-reminder")
@app.post("/api/trigger-reminder")
def trigger_reminder_endpoint(hour: Optional[str] = None):
    """
    Endpoint pemicu reminder manual/tes via WhatsApp & Telegram.
    """
    now_wib = datetime.datetime.now(WIB)
    hour_label = hour or f"{now_wib.strftime('%H:%M')} WIB"
    result = engine.send_followup_reminder(current_hour_str=hour_label)
    return result

@app.get("/api/reminder-status")
def reminder_status():
    """Status scheduler reminder untuk verifikasi dan sinkronisasi dengan GitHub Actions."""
    now_wib = datetime.datetime.now(WIB)
    return {
        "status": "active" if REMINDER_ENABLED else "disabled",
        "schedule": ["10:00 WIB", "14:00 WIB", "20:00 WIB"],
        "last_reminder_slot": last_reminder_slot,
        "current_time_wib": now_wib.strftime("%Y-%m-%d %H:%M:%S WIB")
    }

@app.get("/api/sync-state")
@app.post("/api/sync-state")
def trigger_sync_state_endpoint():
    """
    Endpoint manual/remote untuk memaksa sinkronisasi state terbaru dari GitHub Pages.
    """
    return sync_state_from_remote()

@app.get("/webhook")
@app.get("/webhook/whatsapp")
@app.get("/webhook/fonnte")
@app.get("/api/webhook")
@app.get("/api/webhook/whatsapp")
def webhook_test_get():
    return {"status": "ready", "message": "Foxe Webhook endpoint is active and listening for POST requests from Fonnte"}

def send_telegram_instant_lead(lead: dict, raw_msg: str):
    """
    Mengirimkan alert real-time ke Telegram (@NunuFxBot) saat ada chat WhatsApp masuk:
    - Nama & Nomor Client
    - Klasifikasi Tier (Hot/Warm/Cold)
    - Pesan asli
    - Draft balasan AI siap copy-paste langsung
    """
    token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return

    tier = lead.get("tier", "WARM")
    badge = {
        "HOT": "🔥 [HOT LEAD - MINTA REKENING / LOCK SLOT]",
        "WARM": "⚡ [WARM LEAD - KONSULTASI PAKET]",
        "COLD": "❄️ [COLD LEAD - TANYA UMUM/PRICELIST]",
        "CLOSED": "✅ [DEAL - TERDAFTAR DI SPREADSHEET]"
    }.get(tier, "📌 [PROSPEK BARU]")

    name = lead.get("display_name", "Klien")
    phone = lead.get("phone", "")
    draft = lead.get("ai_recommendation", "")

    text = (
        f"🚨 <b>CHAT WHATSAPP MASUK (0851-5921-0021)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Klien:</b> {name} (<code>{phone}</code>)\n"
        f"🎯 <b>Klasifikasi:</b> {badge}\n"
        f"💬 <b>Pesan Klien:</b>\n<i>\"{raw_msg}\"</i>\n\n"
        f"🤖 <b>Rekomendasi Balasan AI (Siap Kirim):</b>\n"
        f"<blockquote>{draft}</blockquote>\n\n"
        f"👉 <a href=\"https://whynunuu.github.io/FoxeStudio/flow.html\"><b>Buka CRM & Kirim Balasan</b></a>"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload, headers={"User-Agent": "FoxeStudio/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            pass
        print(f"[OK] Notifikasi prospek live terkirim ke Telegram ({name})")
    except Exception as e:
        print(f"[WARN] Gagal kirim instant alert Telegram: {e}")

@app.post("/webhook")
@app.post("/webhook/whatsapp")
@app.post("/webhook/fonnte")
@app.post("/api/webhook")
@app.post("/api/webhook/whatsapp")
async def receive_fonnte_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint penangkap webhook dari Fonnte WhatsApp Gateway.
    Payload Fonnte:
    {
        "device": "6285159210021",
        "sender": "6281234567890",
        "message": "Kak mau booking wisuda tgl 3 Okt",
        "name": "Cantika Dewi",
        "timestamp": 1727756400
    }
    """
    try:
        # Coba ambil json atau form-data
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "error", "message": f"Invalid payload: {str(e)}"})

    sender = str(payload.get("sender") or "").strip()
    message = str(payload.get("message") or "").strip()
    name = str(payload.get("name") or payload.get("pushName") or "Client").strip()

    # Abaikan pesan kosong atau pesan dari sistem sendiri
    if not sender or not message:
        return {"status": "ignored", "reason": "Empty sender or message"}

    # Proses pesan lewat engine AI
    result = engine.ingest_fonnte_message(payload)

    # PERHATIAN: Alert instan per chat dinonaktifkan secara default agar Telegram tidak dibanjiri pesan.
    # Seluruh notifikasi dikirimkan terpadu sesuai jadwal resmi (10:00, 14:00, 20:00 WIB).
    ENABLE_INSTANT_ALERT = os.environ.get("ENABLE_INSTANT_TELEGRAM_ALERT", "false").lower() in ("true", "1", "yes")
    if ENABLE_INSTANT_ALERT and result.get("status") == "success" and result.get("lead"):
        background_tasks.add_task(send_telegram_instant_lead, result["lead"], message)

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Webhook Masuk: {name} ({sender}) -> Tier: {result.get('tier')}")
    print(f"  AI Draft: {result.get('ai_recommendation')}")

    return {
        "status": "success",
        "client_name": name,
        "phone": sender,
        "tier": result.get("tier"),
        "lead_status": result.get("lead_status") or result.get("lead", {}).get("status"),
        "ai_recommendation": result.get("ai_recommendation")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=port, reload=False)
