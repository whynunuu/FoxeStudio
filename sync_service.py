"""
=============================================================================
Foxe Studio — Layanan Sinkronisasi Otomatis Harian & Berkala
=============================================================================
Menjalankan 'deep_sync_foxe.py' secara otomatis:
- Mode Harian (default): Setiap hari pukul 09:00 pagi WIB
- Mode Interval: Setiap N detik/menit
- Mode Sekali Jalan: Menjalankan sinkronisasi langsung dan selesai
=============================================================================
"""

import sys
import time
import argparse
import datetime
from deep_sync_foxe import run_integration

def get_seconds_until_target(target_hour=9, target_minute=0):
    now = datetime.datetime.now()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target <= now:
        target += datetime.timedelta(days=1)
    return (target - now).total_seconds(), target

def start_daily_service(target_time_str="09:00"):
    target_hour, target_minute = map(int, target_time_str.split(":"))
    print("==========================================================", flush=True)
    print("   FOXE STUDIO — DAILY SYNC SERVICE (SETIAP HARI)        ", flush=True)
    print("==========================================================", flush=True)
    print(f"Jadwal harian: Pukul {target_time_str} pagi", flush=True)
    print(f"Waktu sistem : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("==========================================================\n", flush=True)

    iteration = 0
    while True:
        wait_seconds, next_run = get_seconds_until_target(target_hour, target_minute)
        hours = int(wait_seconds // 3600)
        minutes = int((wait_seconds % 3600) // 60)
        seconds = int(wait_seconds % 60)
        print(f"Menunggu jadwal berikutnya: {next_run.strftime('%Y-%m-%d %H:%M:%S')} ({hours} jam {minutes} menit {seconds} detik lagi)...", flush=True)
        
        # Tidur hingga waktu yang ditentukan
        time.sleep(wait_seconds)

        iteration += 1
        print(f"\n--- [EKSEKUSI HARIAN #{iteration}] Mulai Sinkronisasi: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        try:
            run_integration()
            print(f"[OK] Sinkronisasi harian #{iteration} berhasil.")
        except Exception as e:
            print(f"[ERROR] Sinkronisasi harian #{iteration} gagal: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()

        # Jeda 65 detik agar tidak terpicu ganda di menit yang sama
        time.sleep(65)

def start_interval_service(interval_seconds=900, run_once=False):
    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- [ITERASI #{iteration}] Mulai Sinkronisasi: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        try:
            run_integration()
            print(f"[OK] Iterasi #{iteration} berhasil.")
        except Exception as e:
            print(f"[ERROR] Iterasi #{iteration} gagal: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()

        if run_once:
            print("\nMode sekali jalan selesai.")
            break

        print(f"\nMenunggu {interval_seconds // 60} menit hingga sinkronisasi berikutnya...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Foxe Studio Sync Service")
    parser.add_argument("--daily", type=str, default="09:00", help="Waktu sinkronisasi harian format HH:MM (default: 09:00)")
    parser.add_argument("--interval", type=int, default=None, help="Interval dalam detik jika ingin mode interval")
    parser.add_argument("--once", action="store_true", help="Jalankan sekali sekarang dan keluar")
    args = parser.parse_args()

    if args.once:
        run_integration()
    elif args.interval:
        start_interval_service(interval_seconds=args.interval)
    else:
        start_daily_service(target_time_str=args.daily)
