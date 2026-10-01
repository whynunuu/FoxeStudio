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
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from agentic_lead_engine import AgenticLeadEngine, FOXE_PAYMENT_INFO, FONNTE_TOKEN

app = FastAPI(
    title="Foxe Studio AI Lead Webhook",
    description="Webhook listener & AI Lead Assistant for Foxe Studio WhatsApp",
    version="1.0.0"
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

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Foxe Studio Agentic AI Lead Engine",
        "studio": "Foxe Studio (Purwokerto)",
        "whatsapp_device": "0851-5921-0021 (Foxe Admin)",
        "gemini_ai": "Connected",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/leads")
def get_leads():
    """Mengambil daftar leads tersimpan untuk disinkronkan ke dashboard."""
    return engine.get_leads_summary()

@app.post("/webhook")
@app.post("/api/webhook")
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
