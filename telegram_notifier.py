"""
=============================================================================
Foxe Studio — Telegram Notifier Module
=============================================================================
Modul pengiriman notifikasi otomatis ke Telegram via Bot API.
Bot Name: NunuFx (@NunuFxBot)
Token: 8809193335:AAER1t9MAnVSyIRJSWqHpFwaoFe4hYmcZ1s
=============================================================================
"""

import os
import json
import urllib.request
import urllib.parse
import datetime

DEFAULT_TOKEN = "8809193335:AAER1t9MAnVSyIRJSWqHpFwaoFe4hYmcZ1s"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "telegram_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "token": DEFAULT_TOKEN,
        "chat_id": None
    }

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def detect_chat_id(token=None):
    if not token:
        cfg = load_config()
        token = cfg.get("token", DEFAULT_TOKEN)
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FoxeStudio/1.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            if data.get("ok") and data.get("result"):
                # Ambil update terbaru yang ada message / chat
                for item in reversed(data["result"]):
                    msg = item.get("message") or item.get("my_chat_member") or item.get("channel_post")
                    if msg and "chat" in msg:
                        chat_id = msg["chat"]["id"]
                        first_name = msg["chat"].get("first_name", msg["chat"].get("title", "User"))
                        cfg = load_config()
                        cfg["chat_id"] = chat_id
                        save_config(cfg)
                        print(f"[OK] Ditemukan Chat ID: {chat_id} ({first_name})")
                        return chat_id
    except Exception as e:
        print(f"[WARN] Gagal detect chat_id: {e}")
    return None

def send_telegram_message(text, chat_id=None, parse_mode="HTML"):
    cfg = load_config()
    token = cfg.get("token", DEFAULT_TOKEN)
    target_chat_id = chat_id or cfg.get("chat_id")

    if not target_chat_id:
        target_chat_id = detect_chat_id(token)
        if not target_chat_id:
            print("[WARN] Belum ada Chat ID terdaftar. Buka @NunuFxBot di Telegram lalu klik Start.")
            return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "FoxeStudio/1.0"})
        with urllib.request.urlopen(req, timeout=15) as res:
            resp_data = json.loads(res.read().decode("utf-8"))
            if resp_data.get("ok"):
                print(f"[OK] Notifikasi Telegram berhasil terkirim ke {target_chat_id}!")
                return True
            else:
                print(f"[WARN] Telegram API error: {resp_data}")
                return False
    except Exception as e:
        print(f"[ERROR] Gagal kirim pesan Telegram: {e}")
        return False

def build_summary_message(state):
    cfg = state.get("config", {})
    cutoff = cfg.get("cutoff", "2026-09-20")
    orders = state.get("orders", [])
    shifts = state.get("shifts", [])

    # Order & Omzet MTD
    total_mtd = sum(o.get("grandTotal", 0) for o in orders)
    cash_mtd = sum(o.get("cash", 0) for o in orders)
    tf_mtd = sum(o.get("transfer", 0) for o in orders)
    count_mtd = len(orders)

    # Order & Omzet Hari Cut-off (Hari Ini)
    today_orders = [o for o in orders if o.get("tanggal") == cutoff]
    today_omzet = sum(o.get("grandTotal", 0) for o in today_orders)
    today_count = len(today_orders)

    # Shift Kru Hari Ini
    today_shifts = [s for s in shifts if s.get("tanggal") == cutoff]
    crew_list = []
    for s in today_shifts:
        crew_list.append(f"• <b>Studio {s.get('studio')}</b>: {s.get('kru', '-')} ({s.get('jam', '-')})")
    crew_str = "\n".join(crew_list) if crew_list else "• <i>Tidak ada log shift terjadwal</i>"

    # Target
    target_tier3 = 100000000
    persen_t3 = (total_mtd / target_tier3) * 100 if target_tier3 else 0
    sisa_t3 = max(0, target_tier3 - total_mtd)

    def rp(n):
        return f"Rp {n:,.0f}".replace(",", ".")

    # Format Pesan
    msg = (
        f"🦊 <b>Foxe Studio — Laporan Harian Closing</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 <b>Cut-off:</b> {cutoff}\n"
        f"🕒 <b>Update:</b> {datetime.datetime.now().strftime('%H:%M WIB')}\n\n"
        f"💰 <b>Kinerja Hari Ini:</b>\n"
        f"• Transaksi: <b>{today_count} Order</b>\n"
        f"• Omzet: <b>{rp(today_omzet)}</b>\n\n"
        f"📈 <b>Akumulasi Bulan Ini (MTD):</b>\n"
        f"• Total Order: <b>{count_mtd} Order</b>\n"
        f"• Total Omzet: <b>{rp(total_mtd)}</b>\n"
        f"  ├ Tunai (Cash): {rp(cash_mtd)}\n"
        f"  └ Non-Tunai (TF): {rp(tf_mtd)}\n"
        f"• Progress Target Tier 3 (100 Juta): <b>{persen_t3:.1f}%</b>\n"
        f"  └ Sisa ke Target: {rp(sisa_t3)}\n\n"
        f"👥 <b>Shift Kru Hari Ini:</b>\n"
        f"{crew_str}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>Dashboard Live:</b>\n"
        f"https://whynunuu.github.io/FoxeStudio/\n"
    )
    return msg

if __name__ == "__main__":
    import sys
    print("Testing Telegram Notifier...")
    cid = detect_chat_id()
    if cid:
        print(f"Chat ID terdeteksi: {cid}")
        send_telegram_message("🦊 <b>Halo Bos!</b> Bot notifikasi Foxe Studio sudah siap terhubung ke sistem cron!", cid)
    else:
        print("Menunggu user klik /start pada @NunuFxBot...")
