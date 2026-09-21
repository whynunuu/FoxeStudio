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
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id_env = os.environ.get("TELEGRAM_CHAT_ID")
    chat_id = int(chat_id_env) if chat_id_env and chat_id_env.isdigit() else None

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    return {
        "token": token or cfg.get("token", DEFAULT_TOKEN),
        "chat_id": chat_id or cfg.get("chat_id")
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
    from collections import defaultdict
    cfg = state.get("config", {})
    cutoff = cfg.get("cutoff", "2026-09-20")
    try:
        cutoff_dt = datetime.datetime.strptime(cutoff, "%Y-%m-%d")
    except Exception:
        cutoff_dt = datetime.datetime.now()
    cutoff_day = cutoff_dt.day

    tomorrow_dt = cutoff_dt + datetime.timedelta(days=1)
    tomorrow_str = tomorrow_dt.strftime("%Y-%m-%d")
    tomorrow_display = tomorrow_dt.strftime("%d %b %Y").upper()

    cash_by_date = defaultdict(float)
    tf_by_date = defaultdict(float)
    tot_by_date = defaultdict(float)
    for o in state.get("orders", []):
        cash_by_date[o.get("tanggal")] += o.get("cash", 0)
        tf_by_date[o.get("tanggal")] += o.get("transfer", 0)
        tot_by_date[o.get("tanggal")] += o.get("grandTotal", o.get("total", 0))

    leads_map = {l.get("tanggal"): l for l in state.get("leads", [])}

    def fmt_k(v):
        if v <= 0:
            return "-"
        return f"{int(round(v / 1000))}k"

    table_lines = []
    table_lines.append("============================================")
    table_lines.append("        SUMMARY FOXE STUDIO (HARIAN)        ")
    table_lines.append("============================================")
    table_lines.append("Tgl     Cash  Transfer   Total  Leads   Rate")
    table_lines.append("--------------------------------------------")

    for d in range(1, 31):
        tgl = f"2026-09-{d:02d}"
        if d <= cutoff_day:
            c = cash_by_date.get(tgl, 0)
            t = tf_by_date.get(tgl, 0)
            tot = tot_by_date.get(tgl, 0)
            ld = leads_map.get(tgl)
            if ld and ld.get("leads") and ld["leads"] > 0:
                l_str = str(int(ld["leads"]))
                r_str = f"{int(round(ld.get('dp', 0) / ld['leads'] * 100))}%"
            else:
                l_str = "-"
                r_str = "-"
        else:
            c, t, tot = 0, 0, 0
            l_str = "-"
            r_str = "-"
        
        table_lines.append(f"{d:<3} {fmt_k(c):>9} {fmt_k(t):>9} {fmt_k(tot):>7} {l_str:>6} {r_str:>6}")

    table_lines.append("--------------------------------------------")

    total_cash = sum(cash_by_date.values())
    total_tf = sum(tf_by_date.values())
    grand_total = total_cash + total_tf

    def rp(n):
        return f"Rp {n:,.0f}".replace(",", ".")

    table_lines.append(f"{'TOTAL CASH':<24} {rp(total_cash):>19}")
    table_lines.append(f"{'TOTAL TRANSFER':<24} {rp(total_tf):>19}")
    table_lines.append(f"{'GRAND TOTAL OMZET':<24} {rp(grand_total):>19}")

    exps = state.get("expenses", [])
    if exps:
        cogs_tot = sum(e.get("nilai", 0) for e in exps if e.get("jenis") == "COGS")
        opex_tot = sum(e.get("nilai", 0) for e in exps if e.get("jenis") == "OPEX")
        nett_profit = grand_total - cogs_tot - opex_tot
        table_lines.append("--------------------------------------------")
        table_lines.append(f"{'TOTAL COGS (Produksi)':<24} {rp(cogs_tot):>19}")
        table_lines.append(f"{'TOTAL OPEX (Studio)':<24} {rp(opex_tot):>19}")
        table_lines.append(f"{'ESTIMASI NETT PROFIT':<24} {rp(nett_profit):>19}")

    table_lines.append("============================================")

    table_block = "\n".join(table_lines)

    # Leads s.d. cutoff
    total_leads = sum(l.get("leads", 0) for l in state.get("leads", []) if int(l.get("tanggal", "2026-09-01").split("-")[2]) <= cutoff_day)
    total_dp = sum(l.get("dp", 0) for l in state.get("leads", []) if int(l.get("tanggal", "2026-09-01").split("-")[2]) <= cutoff_day)
    conv_rate = (total_dp / total_leads * 100) if total_leads > 0 else 0

    # Roster Shift aktual s.d. cutoff (akumulasi total shift dari Log Order)
    from collections import Counter
    shift_counts = Counter()
    for sh in state.get("shifts", []):
        try:
            sh_day = int(sh.get("tanggal", "2026-09-01").split("-")[2])
            if sh_day <= cutoff_day:
                shift_counts[sh.get("nama")] += 1
        except Exception:
            pass

    shift_order = [
        ("Admin AMEL", shift_counts.get("AMEL", 0)),
        ("Admin INDAH", shift_counts.get("INDAH", 0)),
        ("Fotografer ADIF", shift_counts.get("ADIF", 0)),
        ("Fotografer SAKA", shift_counts.get("SAKA", 0))
    ]
    tot_shifts = sum(cnt for _, cnt in shift_order)

    shift_lines = []
    for label, cnt in shift_order:
        shift_lines.append(f"• {label:<17} : <b>{cnt}</b>")
    shift_lines.append(f"• <b>{'TOTAL SHIFT':<17} : {tot_shifts}</b>")
    shift_block = "\n".join(shift_lines)

    # Jadwal Foto Besok
    tomorrow_bookings = [
        b for b in state.get("schedule", {}).get("bookings", [])
        if b.get("tgl") == tomorrow_str
    ]

    booking_lines = []
    if tomorrow_bookings:
        for idx, b in enumerate(tomorrow_bookings, 1):
            nama = b.get("nama", "Klien")
            paket = b.get("paket") or b.get("paketRaw") or "Sesi Foto"
            nohp = str(b.get("noHp", "")).lower()
            if "lunas" in nohp:
                status = "Lunas"
            elif "dp" in nohp:
                status = "DP"
            else:
                status = "Confirmed"
            
            adm_code = str(b.get("admin", "")).strip().upper()
            adm_name = {"IN": "INDAH", "AM": "AMEL", "AD": "ADDEL"}.get(adm_code, adm_code) if adm_code else "-"
            waktu = b.get("waktu", "")
            studio = b.get("studio", "")
            extra_info = f" | {waktu} @ {studio}" if waktu and studio else ""
            booking_lines.append(f"{idx}. <b>{nama}</b> | {paket} (Status: {status} | Admin: {adm_name}{extra_info})")
    else:
        booking_lines.append("<i>Belum ada jadwal booking terdaftar untuk besok.</i>")

    booking_block = "\n".join(booking_lines)
    total_klien_besok = len(tomorrow_bookings)

    now_str = datetime.datetime.now().strftime("%d %B %Y, %H:%M WIB")

    full_msg = (
        f"<pre>{table_block}</pre>\n\n"
        f"🎯 <b>LEADS (s.d. {cutoff_day} Sept):</b>\n"
        f"• Leads   : <b>{int(total_leads)}</b>\n"
        f"• DP      : <b>{int(total_dp)}</b>\n"
        f"• Rate    : <b>{conv_rate:.2f}%</b>\n\n"
        f"👥 <b>ROSTER SHIFT (aktual s.d. {cutoff_day} Sept):</b>\n"
        f"{shift_block}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 <b>JADWAL FOTO BESOK ({tomorrow_display})</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{booking_block}\n\n"
        f"Total Jadwal Besok: <b>{total_klien_besok} Klien</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <i>Sumber: Foxe Studio — Schedule dan Log Order.xlsm</i>\n"
        f"🕒 <i>Last Updated: {now_str}</i>\n"
        f"👉 <a href=\"https://whynunuu.github.io/FoxeStudio/\"><b>Buka Dashboard Live Foxe Studio</b></a>"
    )
    return full_msg

if __name__ == "__main__":
    print("Testing Telegram Notifier with new format...")
    if os.path.exists("foxe_full_state.json"):
        with open("foxe_full_state.json", "r", encoding="utf-8") as f:
            st = json.load(f)
        msg = build_summary_message(st)
        send_telegram_message(msg)

