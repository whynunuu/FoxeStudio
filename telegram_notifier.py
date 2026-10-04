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
import sys
import datetime
import re
from collections import defaultdict, Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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

def build_summary_message(state, bulan=None):
    BULAN_NAMA = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    cfg = state.get("config", {})
    ok_lo = state.get("oktoberLogOrder", {})
    ok_pip = state.get("oktoberPipeline", {})

    # Auto-detect bulan jika tidak ditentukan secara eksplisit
    if not bulan:
        if ok_lo and ok_lo.get("orders"):
            bulan = "2026-10"
        elif cfg.get("cutoff", "").startswith("2026-10"):
            bulan = "2026-10"
        elif datetime.datetime.now().month == 10:
            bulan = "2026-10"
        else:
            bulan = "2026-09"

    is_oktober = (bulan == "2026-10")

    if is_oktober:
        cutoff = ok_lo.get("cutoff", "2026-10-01")
        total_days = 31
        month_label = "OKTOBER 2026"
        month_short = "Okt"
        orders = ok_lo.get("orders", [])
        shifts = ok_lo.get("shifts", [])
        leads_list = ok_lo.get("leads", [])
        expenses = [e for e in state.get("expenses", []) if e.get("tanggal", "").startswith("2026-10")]
        bookings_source = ok_pip.get("bookings", [])
    else:
        cutoff = cfg.get("cutoff", "2026-09-30")
        total_days = 30
        month_label = "SEPTEMBER 2026"
        month_short = "Sept"
        orders = [o for o in state.get("orders", []) if o.get("tanggal", "").startswith("2026-09")]
        shifts = [s for s in state.get("shifts", []) if s.get("tanggal", "").startswith("2026-09")]
        leads_list = [l for l in state.get("leads", []) if l.get("tanggal", "").startswith("2026-09")]
        expenses = [e for e in state.get("expenses", []) if e.get("tanggal", "").startswith(bulan)]
        bookings_source = state.get("schedule", {}).get("bookings", [])

    try:
        cutoff_dt = datetime.datetime.strptime(cutoff, "%Y-%m-%d")
    except Exception:
        cutoff_dt = datetime.datetime.now()
    cutoff_day = cutoff_dt.day

    tomorrow_dt = cutoff_dt + datetime.timedelta(days=1)
    tomorrow_str = tomorrow_dt.strftime("%Y-%m-%d")
    tomorrow_display = f"{tomorrow_dt.day:02d} {BULAN_NAMA[tomorrow_dt.month-1][:3].upper()} {tomorrow_dt.year}"

    cash_by_date = defaultdict(float)
    tf_by_date = defaultdict(float)
    tot_by_date = defaultdict(float)
    for o in orders:
        tgl = o.get("tanggal")
        if tgl:
            cash_by_date[tgl] += o.get("cash", 0)
            tf_by_date[tgl] += o.get("transfer", 0)
            tot_by_date[tgl] += o.get("grandTotal", o.get("total", 0))

    leads_map = {l.get("tanggal"): l for l in leads_list}

    def fmt_k(v):
        if v <= 0:
            return "-"
        return f"{int(round(v / 1000))}k"

    table_lines = []
    table_lines.append("============================================")
    table_lines.append(f"     SUMMARY FOXE STUDIO — {month_label:<14}")
    table_lines.append("============================================")
    table_lines.append("Tgl     Cash  Transfer   Total  Leads   Rate")
    table_lines.append("--------------------------------------------")

    for d in range(1, total_days + 1):
        tgl = f"{bulan}-{d:02d}"
        if d <= cutoff_day:
            c = cash_by_date.get(tgl, 0)
            t = tf_by_date.get(tgl, 0)
            tot = tot_by_date.get(tgl, 0)
            ld = leads_map.get(tgl)
            if ld and ld.get("leads") and ld["leads"] > 0:
                l_str = str(int(ld["leads"]))
                r_str = f"{int(round(ld.get('dp', 0) / ld['leads'] * 100))}%"
            elif ld and ld.get("dp") and ld["dp"] > 0:
                l_str = "-"
                r_str = f"{int(ld['dp'])} DP"
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

    cogs_tot = sum(e.get("nilai", 0) for e in expenses if e.get("jenis") == "COGS")
    opex_tot = sum(e.get("nilai", 0) for e in expenses if e.get("jenis") == "OPEX")
    nett_profit = grand_total - cogs_tot - opex_tot
    outcome_tot = cogs_tot + opex_tot
    outcome_ratio = (outcome_tot / grand_total * 100) if grand_total > 0 else 0.0

    # Rule: Berlakukan setelah tanggal 15 (> 15) atau jika bulan sudah tutup
    is_closed_month = (cutoff_day >= total_days)
    is_after_day_15 = (cutoff_day > 15) or is_closed_month
    is_outcome_alert = is_after_day_15 and (outcome_ratio >= 45.0) and (grand_total > 0)

    table_lines.append("--------------------------------------------")
    table_lines.append(f"{'TOTAL COGS (Produksi)':<24} {rp(cogs_tot):>19}")
    table_lines.append(f"{'TOTAL OPEX (Studio)':<24} {rp(opex_tot):>19}")
    table_lines.append(f"{'ESTIMASI NETT PROFIT':<24} {rp(nett_profit):>19}")
    if is_outcome_alert:
        table_lines.append("--------------------------------------------")
        table_lines.append(f"{'OUTCOME RATIO (≥45%)':<24} {f'{outcome_ratio:.1f}% ⚠️':>19}")
        table_lines.append(f"{'STATUS BUDGET CAP':<24} {'ALERT KRITIS':>19}")
    elif is_after_day_15 and grand_total > 0 and (cogs_tot + opex_tot > 0):
        table_lines.append("--------------------------------------------")
        table_lines.append(f"{'OUTCOME RATIO (<45%)':<24} {f'{outcome_ratio:.1f}% ✅':>19}")
        table_lines.append(f"{'STATUS BUDGET CAP':<24} {'PASSED (AMAN)':>19}")

    # Section Estimate Omzet Sampai Akhir Bulan (Unrealized Cash In & Omzet)
    if is_oktober:
        unrealized_cash_in = float(ok_pip.get("potentialOmzet", 0))
        total_dp_future = float(ok_pip.get("totalDp", 0))
        sisa_pelunasan = float(ok_pip.get("estimateCashIn", 0))
        unrealized_omzet = grand_total + sisa_pelunasan

        table_lines.append("--------------------------------------------")
        table_lines.append(f"{'Unrealized Cash In':<24} {rp(unrealized_cash_in):>19}")
        table_lines.append(f"{'DP (-)':<24} {rp(total_dp_future):>19}")
        table_lines.append(f"{'Total':<24} {rp(sisa_pelunasan):>19}")
        table_lines.append("")
        table_lines.append(f"{'Unrealized Omzet':<24} {rp(unrealized_omzet):>19}")
    else:
        future_bookings = [
            b for b in bookings_source
            if b.get("tgl") and b.get("tgl") > cutoff and b.get("tgl").startswith(cutoff[:7])
        ]
        if future_bookings:
            unrealized_cash_in = sum(b.get("harga", 0) for b in future_bookings)
            total_dp_future = 0.0
            for b in future_bookings:
                hp = str(b.get("noHp", "")).lower()
                m = re.search(r'dp\s*(\d+)', hp)
                if m:
                    total_dp_future += float(m.group(1)) * 1000
                elif "lunas" in hp:
                    total_dp_future += float(b.get("harga", 0))

            sisa_pelunasan = max(0.0, unrealized_cash_in - total_dp_future)
            unrealized_omzet = grand_total + sisa_pelunasan

            table_lines.append("--------------------------------------------")
            table_lines.append(f"{'Unrealized Cash In':<24} {rp(unrealized_cash_in):>19}")
            table_lines.append(f"{'DP (-)':<24} {rp(total_dp_future):>19}")
            table_lines.append(f"{'Total':<24} {rp(sisa_pelunasan):>19}")
            table_lines.append("")
            table_lines.append(f"{'Unrealized Omzet':<24} {rp(unrealized_omzet):>19}")

    table_lines.append("============================================")
    table_block = "\n".join(table_lines)

    # Leads s.d. cutoff
    total_leads = 0.0
    total_dp = 0.0
    for l in leads_list:
        try:
            ld_day = int(str(l.get("tanggal", f"{bulan}-01")).split("-")[2])
            if ld_day <= cutoff_day:
                total_leads += float(l.get("leads", 0) or 0)
                total_dp += float(l.get("dp", 0) or 0)
        except Exception:
            pass
    conv_rate = (total_dp / total_leads * 100) if total_leads > 0 else (100.0 if total_dp > 0 else 0.0)

    # Roster Shift aktual s.d. cutoff
    shift_counts = Counter()
    for sh in shifts:
        try:
            sh_day = int(str(sh.get("tanggal", f"{bulan}-01")).split("-")[2])
            if sh_day <= cutoff_day:
                shift_counts[str(sh.get("nama", "")).strip().upper()] += int(sh.get("slot", 1) or 1)
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
        b for b in bookings_source
        if b.get("tgl") == tomorrow_str
    ]

    booking_lines = []
    if tomorrow_bookings:
        limit_b = 12
        for idx, b in enumerate(tomorrow_bookings[:limit_b], 1):
            nama = b.get("nama", "Klien")
            paket = b.get("paket") or b.get("paketRaw") or "Sesi Foto"
            nohp = str(b.get("noHp", "")).lower()
            if "lunas" in nohp:
                status = "Lunas"
            elif "dp" in nohp or float(b.get("dp", 0) or 0) > 0:
                dp_val = float(b.get("dp", 0) or 0)
                status = f"DP {int(dp_val/1000)}k" if dp_val > 0 else "DP"
            else:
                status = "Confirmed"
            
            adm_code = str(b.get("admin", "")).strip().upper()
            adm_name = {"IN": "INDAH", "AM": "AMEL", "AD": "ADDEL"}.get(adm_code, adm_code) if adm_code else "-"
            waktu = b.get("waktu", "")
            studio = b.get("studio", "") or b.get("studioNama", "")
            extra_info = f" | {waktu} @ {studio}" if waktu and studio else ""
            booking_lines.append(f"{idx}. <b>{nama}</b> | {paket} ({status} | Adm: {adm_name}{extra_info})")
        if len(tomorrow_bookings) > limit_b:
            booking_lines.append(f"<i>... dan {len(tomorrow_bookings) - limit_b} sesi foto lainnya (cek dashboard web).</i>")
    else:
        booking_lines.append("<i>Belum ada jadwal booking terdaftar untuk besok.</i>")

    booking_block = "\n".join(booking_lines)
    total_klien_besok = len(tomorrow_bookings)

    # Super Peak Wisuda UMP Alert (jika Oktober)
    super_peak_block = ""
    if is_oktober:
        w_d1 = [b for b in bookings_source if b.get("tgl") == "2026-10-03"]
        w_d2 = [b for b in bookings_source if b.get("tgl") == "2026-10-04"]
        super_peak_block = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎓 <b>SUPER PEAK WISUDA UMP (3-4 OKT 2026):</b>\n"
            f"• <b>Jumat, 03 Okt</b> : <b>{len(w_d1)} Sesi Foto</b> (5 Backdrop Wisuda)\n"
            f"• <b>Sabtu, 04 Okt</b> : <b>{len(w_d2)} Sesi Foto</b> (5 Backdrop Wisuda)\n"
            f"• <b>Total Gelombang</b> : <b>{len(w_d1) + len(w_d2)} Sesi Terdaftar</b> (Potensi Kas: Rp 48,65 jt)\n"
            f"• <b>Kesiapan Roster</b> : Siaga 5 Fotografer & Asisten per hari.\n"
        )

    outcome_alert_block = ""
    if is_outcome_alert:
        outcome_alert_block = (
            f"🚨 <b>ALARM OPERASIONAL: BEBAN COGS + OPEX ≥ 45%!</b>\n"
            f"⚠️ <b>Rasio Beban: {outcome_ratio:.1f}%</b> (Ambang Batas: 45.0%)\n"
            f"• <b>Total Omzet</b>  : {rp(grand_total)}\n"
            f"• <b>Total Beban</b>  : {rp(outcome_tot)} (COGS {rp(cogs_tot)} + OPEX {rp(opex_tot)})\n"
            f"• <b>Estimasi Nett</b> : {rp(nett_profit)}\n"
            f"<i>Perhatian: Pengeluaran operasional studio telah menyerap ≥ 45% omzet. Segera perketat anggaran dan audit pos belanja COGS & OPEX!</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

    now = datetime.datetime.now()
    now_str = f"{now.day:02d} {BULAN_NAMA[now.month-1]} {now.year}, {now.strftime('%H:%M')} WIB"

    full_msg = (
        f"{outcome_alert_block}"
        f"<pre>{table_block}</pre>\n\n"
        f"🎯 <b>LEADS (s.d. {cutoff_day} {month_short}):</b>\n"
        f"• Leads   : <b>{int(total_leads)}</b>\n"
        f"• DP      : <b>{int(total_dp)}</b>\n"
        f"• Transaksi: <b>{len(orders)}</b>\n\n"
        f"👥 <b>ROSTER SHIFT (aktual s.d. {cutoff_day} {month_short}):</b>\n"
        f"{shift_block}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 <b>JADWAL FOTO BESOK ({tomorrow_display})</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{booking_block}\n\n"
        f"Total Jadwal Besok: <b>{total_klien_besok} Klien</b>\n\n"
        f"{super_peak_block}"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <i>Sumber: Foxe Studio — Schedule & Log Order {month_label.title()}.xlsm</i>\n"
        f"🕒 <i>Last Updated: {now_str}</i>\n"
        f"👉 <a href=\"https://whynunuu.github.io/FoxeStudio/\"><b>Buka Dashboard Live Foxe Studio</b></a>"
    )
    return full_msg

if __name__ == "__main__":
    print("Testing Telegram Notifier with new multi-month format...")
    if os.path.exists("foxe_full_state.json"):
        with open("foxe_full_state.json", "r", encoding="utf-8") as f:
            st = json.load(f)
        msg = build_summary_message(st)
        send_telegram_message(msg)
