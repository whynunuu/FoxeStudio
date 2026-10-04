"""
=============================================================================
Foxe Studio — Quota Reset Telegram Notifier
=============================================================================
Script pembantu untuk mengirimkan notifikasi otomatis ke Telegram (@NunuFxBot)
begitu kuota pemakaian AI (Antigravity 5h Window / Gemini) sudah FULL kembali.

Penggunaan:
  1. Kuota 5 Jam Full:
     python quota_notifier.py 5h
     python quota_notifier.py 5jam

  2. Timer Countdown Menit / Jam:
     python quota_notifier.py 45
     python quota_notifier.py 30 "Kuota Antigravity Flash"

  3. Jam Tertentu (Format HH:MM):
     python quota_notifier.py 20:22

  4. Auto Watch Gemini API (Polling tiap 2 menit hingga 429 sembuh):
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

def notify_quota_full(label="Gemini 3.8 Flash (Antigravity)", extra_info=""):
    now_str = datetime.datetime.now().strftime("%H:%M:%S WIB")
    msg = (
        f"🔋 <b>KUOTA 5 JAM SUDAH FULL (100%)!</b>\n\n"
        f"Halo Bos, kuota pemakaian AI 5 jam untuk <b>{label}</b> sudah <b>TERISI PENUH KEMBALI</b>!\n"
        f"⏰ <b>Waktu:</b> {now_str}\n"
    )
    if extra_info:
        msg += f"ℹ️ <b>Keterangan:</b> {extra_info}\n"
    msg += (
        f"\n⚡ Kapasitas komputasi sudah 100% prima dan segar!\n"
        f"🚀 Kamu sudah bisa lanjut gaspol coding / instruksi kerja panjang lagi tanpa khawatir limit!"
    )
    print(f"[{now_str}] Mengirim notifikasi kuota full ke Telegram...")
    send_telegram_message(msg)

def notify_reset(label="Antigravity / Gemini AI", extra_info=""):
    notify_quota_full(label, extra_info)

def run_countdown(minutes, label="Gemini 3.8 Flash (Antigravity)", is_5h=False):
    target_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    target_str = target_time.strftime("%H:%M:%S WIB")
    mode_text = "5 Jam Penuh" if is_5h else f"{minutes} Menit"
    print(f"[START] Timer notifikasi kuota {mode_text} aktif.")
    print(f"[INFO] Estimasi Kuota FULL pada: {target_str}")
    print("[INFO] Notifikasi akan otomatis terkirim ke Telegram (@NunuFxBot).")
    print("[INFO] Jendela ini bisa Anda minimalkan.\n")

    # Countdown loop
    total_seconds = int(minutes * 60)
    for remaining in range(total_seconds, 0, -10):
        hrs, rem = divmod(remaining, 3600)
        mins, secs = divmod(rem, 60)
        if hrs > 0:
            time_display = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        else:
            time_display = f"{mins:02d}:{secs:02d}"
        sys.stdout.write(f"\r⏳ Sisa waktu menuju KUOTA FULL: {time_display} ... ")
        sys.stdout.flush()
        time.sleep(min(10, remaining))

    sys.stdout.write("\r✅ Kuota 5 Jam kini SUDAH FULL!                      \n")
    if is_5h:
        notify_quota_full(label, f"Siklus 5 jam telah selesai. Kuota terisi 100% penuh.")
    else:
        notify_quota_full(label, f"Durasi tunggu {minutes} menit telah selesai.")

def run_until_time(target_hh_mm, label="Gemini 3.8 Flash (Antigravity)"):
    now = datetime.datetime.now()
    parts = target_hh_mm.strip().split(":")
    target_hour = int(parts[0])
    target_minute = int(parts[1])
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target_time <= now:
        target_time += datetime.timedelta(days=1)

    diff_seconds = (target_time - now).total_seconds()
    run_countdown(diff_seconds / 60.0, label, is_5h=True)

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
                        print("\n[OK] Kuota Gemini API berhasil pulih dan FULL!")
                        notify_quota_full("Google Gemini API", "Status API kembali 200 OK setelah periode pembatasan selesai.")
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
        print("  python quota_notifier.py 5h              (Otomatis hitung 5 jam dari sekarang)")
        print("  python quota_notifier.py <menit> [label]")
        print("  python quota_notifier.py <HH:MM> [label] (Target jam reset spesifik, misal 20:22)")
        print("  python quota_notifier.py --watch-api")
        sys.exit(0)

    arg1 = args[0].lower().strip()
    label = args[1] if len(args) > 1 else "Gemini 3.8 Flash (Antigravity)"

    if arg1 in ["5h", "5jam", "--5h"]:
        run_countdown(5 * 60, label, is_5h=True)
    elif arg1 == "--watch-api":
        watch_gemini_api()
    elif ":" in arg1:
        run_until_time(arg1, label)
    else:
        try:
            mins = float(arg1)
            run_countdown(mins, label)
        except ValueError:
            print(f"[ERROR] Format waktu tidak dikenali: {arg1}")
