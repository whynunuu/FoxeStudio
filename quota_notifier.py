"""
=============================================================================
Foxe Studio — Quota Reset Telegram Notifier
=============================================================================
Script pembantu untuk mengirimkan notifikasi otomatis ke Telegram (@NunuFxBot)
begitu kuota pemakaian AI (Antigravity / Gemini) sudah di-reset.

Penggunaan:
  1. Timer Countdown Menit:
     python quota_notifier.py 45
     python quota_notifier.py 30 "Kuota Antigravity Flash"

  2. Jam Tertentu (Format HH:MM):
     python quota_notifier.py 16:15

  3. Auto Watch Gemini API (Polling tiap 2 menit hingga 429 sembuh):
     python quota_notifier.py --watch-api
=============================================================================
"""

import sys
import time
import os
import datetime
import urllib.request
import json
from telegram_notifier import send_telegram_message

def notify_reset(label="Antigravity / Gemini AI", extra_info=""):
    now_str = datetime.datetime.now().strftime("%H:%M:%S WIB")
    msg = (
        f"🔔 <b>NOTIFIKASI RESET KUOTA AI</b>\n\n"
        f"Halo Bos, kuota pemakaian AI untuk <b>{label}</b> sudah selesai di-reset!\n"
        f"⏰ <b>Waktu Reset:</b> {now_str}\n"
    )
    if extra_info:
        msg += f"ℹ️ <b>Keterangan:</b> {extra_info}\n"
    msg += (
        f"\n🚀 Sesi chat dan antrean instruksi sudah aktif kembali. "
        f"Silakan buka Antigravity dan ketik instruksi atau lanjut kerja!"
    )
    print(f"[{now_str}] Mengirim notifikasi reset ke Telegram...")
    send_telegram_message(msg)

def run_countdown(minutes, label="Antigravity / Gemini AI"):
    target_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    target_str = target_time.strftime("%H:%M:%S WIB")
    print(f"[START] Timer notifikasi reset kuota aktif untuk {minutes} menit.")
    print(f"[INFO] Estimasi reset pada: {target_str}")
    print("[INFO] Notifikasi akan otomatis dikirim ke @NunuFxBot. Anda bisa minimalkan jendela ini.\n")

    # Countdown loop
    total_seconds = int(minutes * 60)
    for remaining in range(total_seconds, 0, -10):
        mins, secs = divmod(remaining, 60)
        sys.stdout.write(f"\r⏳ Sisa waktu menunggu reset: {mins:02d}:{secs:02d} ... ")
        sys.stdout.flush()
        time.sleep(min(10, remaining))

    sys.stdout.write("\r✅ Waktu reset tercapai!                      \n")
    notify_reset(label, f"Durasi tunggu {minutes} menit telah selesai.")

def run_until_time(target_hh_mm, label="Antigravity / Gemini AI"):
    now = datetime.datetime.now()
    parts = target_hh_mm.strip().split(":")
    target_hour = int(parts[0])
    target_minute = int(parts[1])
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target_time <= now:
        target_time += datetime.timedelta(days=1)

    diff_seconds = (target_time - now).total_seconds()
    run_countdown(diff_seconds / 60.0, label)

def watch_gemini_api(api_key=None):
    from agentic_lead_engine import GEMINI_API_KEY
    key = api_key or GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not key:
        print("[ERROR] GEMINI_API_KEY tidak ditemukan di environment maupun secrets.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    payload = json.dumps({"contents": [{"parts": [{"text": "ping"}]}]}).encode("utf-8")

    print("[WATCH] Memantau status Gemini API...")
    in_exhausted_state = False

    while True:
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as res:
                if res.status == 200:
                    if in_exhausted_state:
                        print("\n[OK] Kuota Gemini API berhasil pulih!")
                        notify_reset("Google Gemini API", "Status API kembali 200 OK setelah sebelumnya terkena limit 429.")
                        break
                    else:
                        print("[INFO] Status Gemini API saat ini aktif dan normal (200 OK).")
                        break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                in_exhausted_state = True
                print(f"\r[LIMIT] Kuota sedang exhausted (429). Mengecek kembali dalam 60 detik... ", end="")
                time.sleep(60)
            else:
                print(f"\n[WARN] Error HTTP: {e.code}")
                time.sleep(60)
        except Exception as e:
            print(f"\n[WARN] Error cek API: {e}")
            time.sleep(60)

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Penggunaan:")
        print("  python quota_notifier.py <menit> [label]")
        print("  python quota_notifier.py <HH:MM> [label]")
        print("  python quota_notifier.py --watch-api")
        print("\nContoh:")
        print("  python quota_notifier.py 45")
        print("  python quota_notifier.py 16:30 'Antigravity IDE'")
        sys.exit(0)

    arg1 = args[0]
    label = args[1] if len(args) > 1 else "Antigravity / Gemini AI"

    if arg1 == "--watch-api":
        watch_gemini_api()
    elif ":" in arg1:
        run_until_time(arg1, label)
    else:
        try:
            mins = float(arg1)
            run_countdown(mins, label)
        except ValueError:
            print(f"[ERROR] Format waktu tidak dikenali: {arg1}")
