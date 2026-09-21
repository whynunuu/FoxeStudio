"""
=============================================================================
Foxe Agent — Ultra-Lightweight GitHub Helper (Zero-RAM Footprint)
=============================================================================
Dirancang khusus untuk sistem dengan kapasitas RAM terbatas (4 GB).
- Berjalan on-demand (RAM dipakai hanya saat dieksekusi, lalu langsung bebas).
- Tanpa background daemon / service.
- Menggunakan native token yang sudah terhubung di Git remote.
=============================================================================
"""

import sys
import subprocess
import re
import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Gunakan truststore jika ada agar sertifikat SSL Windows tervalidasi native
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_auth_token():
    res = subprocess.run(["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True)
    match = re.search(r"https://([^@]+)@github\.com", res.stdout.strip())
    if match:
        return match.group(1)
    return None

TOKEN = get_auth_token()
HEADERS = {
    "Authorization": f"token {TOKEN}" if TOKEN else "",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "FoxeAgent-Lite/1.0"
}

def list_repos():
    print("Mengecek repositori akun...")
    r = requests.get("https://api.github.com/user/repos?per_page=30&sort=updated", headers=HEADERS, timeout=10)
    if r.status_code == 200:
        repos = r.json()
        print(f"\n[OK] Ditemukan {len(repos)} Repositori:")
        for rp in repos:
            priv = "Private" if rp.get("private") else "Public"
            updated = rp.get("updated_at", "")[:10]
            print(f"• {rp.get('full_name'):<26} [{priv}] (Updated: {updated}) - {rp.get('description') or '-'}")
    else:
        print(f"[ERR] Gagal mengambil repo: {r.status_code} {r.text}")

def list_actions_runs(repo="whynunuu/FoxeStudio", limit=5):
    print(f"Mengecek GitHub Actions di {repo}...")
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page={limit}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        data = r.json()
        runs = data.get("workflow_runs", [])
        print(f"\n[OK] {len(runs)} Workflow Runs Terbaru di {repo}:")
        for rn in runs:
            status = rn.get("status")
            conclusion = rn.get("conclusion") or "running"
            badge = "✅" if conclusion == "success" else ("❌" if conclusion == "failure" else "⏳")
            name = rn.get("name")
            event = rn.get("event")
            created = rn.get("created_at")
            print(f"{badge} [{conclusion.upper():<7}] {name} ({event}) | Waktu: {created}")
    else:
        print(f"[ERR] Gagal mengambil status Actions: {r.status_code}")

def list_commits(repo="whynunuu/FoxeStudio", limit=5):
    print(f"Mengecek commit terbaru di {repo}...")
    url = f"https://api.github.com/repos/{repo}/commits?per_page={limit}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        commits = r.json()
        print(f"\n[OK] {len(commits)} Commit Terakhir di {repo}:")
        for c in commits:
            sha = c.get("sha")[:7]
            msg = c.get("commit", {}).get("message", "").split("\n")[0]
            author = c.get("commit", {}).get("author", {}).get("name")
            date = c.get("commit", {}).get("author", {}).get("date")[:10]
            print(f"• {sha} | {date} | {author:<14} | {msg}")
    else:
        print(f"[ERR] Gagal mengambil commit: {r.status_code}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "repos"
    arg1 = sys.argv[2] if len(sys.argv) > 2 else None

    if cmd == "repos":
        list_repos()
    elif cmd == "runs":
        target_repo = arg1 or "whynunuu/FoxeStudio"
        list_actions_runs(target_repo)
    elif cmd == "commits":
        target_repo = arg1 or "whynunuu/FoxeStudio"
        list_commits(target_repo)
    else:
        print(f"Perintah: python github_tools.py [repos | runs | commits] [nama_repo]")
