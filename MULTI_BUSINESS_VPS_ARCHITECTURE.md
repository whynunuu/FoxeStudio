# Multi-Business VPS Infrastructure & Architecture Blueprint
Dokumen Arsitektur Server Terpadu Multi-Tenant untuk 7 Lini Bisnis

---

## 1. Executive Summary

Arsitektur ini dirancang untuk mengelola **7 lini bisnis independen** dalam **1 unit Virtual Private Server (VPS)** tanpa saling mengganggu (terisolasi), efisien secara biaya, memiliki alur pencadangan data terpusat, dan mendukung agen AI serta bot otomatisasi yang siaga 24/7.

### Daftar 7 Bisnis & Alokasi Identitas:
| No | Lini Bisnis | Sektor / Karakteristik | Estimasi Domain Utama | Port Internal | Database Name | Agent / Bot Service |
|:---|:---|:---|:---|:---:|:---|:---|
| 1 | **FoxeStudio** | Photography & Creative Studio | `foxestudio.com` | `3001` | `db_foxestudio` | `@NunuFxBot` (Keuangan & Booking) |
| 2 | **Folx** | Creative Agency / Media Collective | `folx.id` | `3002` | `db_folx` | `@FolxAgentBot` (Client Intake) |
| 3 | **Alas House** | Space / Hospitality / Cafe & Co-working | `alashouse.com` | `3003` | `db_alashouse` | `@AlasHouseBot` (Reservasi Ruang) |
| 4 | **LIB** | Brand Lifestyle / Retail / Commerce | `lib.id` | `3004` | `db_lib` | `@LibStoreBot` (Notifikasi Order) |
| 5 | **Milous** | Apparel / F&B / Craft Goods | `milous.id` | `3005` | `db_milous` | `@MilousBot` (Inventory & Tracking) |
| 6 | **FEM** | Media / Agency / Female-Focused Network | `fem.id` | `3006` | `db_fem` | `@FemNetworkBot` (Content & Leads) |
| 7 | **Locus** | Venue / Studio Rental / Event Production | `locus.id` | `3007` | `db_locus` | `@LocusVenueBot` (Slot & Jadwal) |

---

## 2. Diagram Alur Pipeline Sistem (System Flow Architecture)

```
[ PENGUNJUNG / CLIENT ]
   │
   ├──> foxestudio.com ─────┐
   ├──> folx.id ────────────┤
   ├──> alashouse.com ──────┤
   ├──> lib.id ─────────────┼──> [ DNS RESOLVER / CLOUDFLARE ]
   ├──> milous.id ──────────┤    (Semua Domain mengarah ke 1 IP VPS Publik)
   ├──> fem.id ─────────────┤
   └──> locus.id ───────────┘
                                    │ (Traffic Port 80 / 443)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   SINGLE CLOUD VPS (Ubuntu 24.04 LTS)                  │
│                                                                        │
│   [ REVERSE PROXY GATEWAY: NGINX / CADDY ]                            │
│   • Auto SSL / Let's Encrypt Multi-Domain                              │
│   • Domain-to-Port Router (Virtual Host Routing)                      │
│   • DDoS Rate Limiter & Security Header Firewalls                     │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                    DOCKER / PROCESS NETWORK                    │   │
│   │                                                                │   │
│   │  [01_foxestudio]   Port 3001 ──> App + Storage + Bot Daemon    │   │
│   │  [02_folx]         Port 3002 ──> App + Storage + Bot Daemon    │   │
│   │  [03_alashouse]    Port 3003 ──> App + Storage + Bot Daemon    │   │
│   │  [04_lib]          Port 3004 ──> App + Storage + Bot Daemon    │   │
│   │  [05_milous]       Port 3005 ──> App + Storage + Bot Daemon    │   │
│   │  [06_fem]          Port 3006 ──> App + Storage + Bot Daemon    │   │
│   │  [07_locus]        Port 3007 ──> App + Storage + Bot Daemon    │   │
│   │                                                                │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
│   [ CENTRAL DATABASE ENGINE ]      [ CENTRAL AI & LLM AGENT ROUTER ]   │
│   • PostgreSQL 16 / MySQL 8        • Shared Gemini/OpenAI API Gateway  │
│   • 7 Isolated Schemas/Databases   • Background Task Runner (Celery/PM2)│
│                                                                        │
│   [ NIGHTLY BACKUP ENGINE ]                                            │
│   • Cron Job 02:00 WIB ──> Snapshot DB + File ──> Google Drive / R2   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Project Tree (Struktur Direktori Server Produksi)

Berikut adalah struktur folder server standar enterprise yang ditaruh di direktori `/srv/multibiz-vps/`:

```plaintext
/srv/multibiz-vps/
├── .env.global                     # Kunci API Global (Telegram Root, Gemini/OpenAI API, Cloudflare Token)
├── docker-compose.yml              # Orkestrasi seluruh container bisnis & database
├── Makefile                        # Shortcut perintah CLI (make start, make backup, make status)
│
├── gateway/                        # Reverse Proxy & SSL Gateway
│   ├── nginx/
│   │   ├── nginx.conf              # Pengaturan global Nginx, HTTP/2, Gzip, SSL params
│   │   └── conf.d/                 # Virtual host per domain bisnis
│   │       ├── 01_foxestudio.conf  # Routing foxestudio.com -> localhost:3001
│   │       ├── 02_folx.conf        # Routing folx.id -> localhost:3002
│   │       ├── 03_alashouse.conf   # Routing alashouse.com -> localhost:3003
│   │       ├── 04_lib.conf         # Routing lib.id -> localhost:3004
│   │       ├── 05_milous.conf      # Routing milous.id -> localhost:3005
│   │       ├── 06_fem.conf         # Routing fem.id -> localhost:3006
│   │       └── 07_locus.conf       # Routing locus.id -> localhost:3007
│   └── certbot/                    # Direktori sertifikat SSL Let's Encrypt (Auto-renew)
│       └── certificates/
│
├── shared/                         # Infrastruktur & Utility Bersama
│   ├── database/
│   │   ├── init-scripts/           # Script auto-create 7 database terpisah
│   │   │   └── init_multidb.sql
│   │   └── postgres_data/          # Volume fisik data database PostgreSQL
│   ├── redis_data/                 # Cache & message broker untuk antrean bot
│   ├── ai_gateway/                 # Router terpusat untuk integrasi model AI / LLM
│   │   ├── agent_core.py           # Core agent logic, rate limit token, logging
│   │   └── requirements.txt
│   └── scripts/                    # Script maintenance & pemeliharaan server
│       ├── auto_backup_all.sh      # Backup 7 database & file upload ke Cloud Storage
│       └── health_check.sh         # Pengecekan otomatis kesehatan server & alert jika down
│
└── businesses/                     # MODULAR FOLDER: 7 Sektor Bisnis Terisolasi
    │
    ├── 01_foxestudio/              # Sektor 1: FoxeStudio
    │   ├── .env                    # Variabel lokal FoxeStudio (DB_NAME, BOT_TOKEN, PORT=3001)
    │   ├── app/                    # Web App / Dashboard Keuangan (FastAPI / Next.js / HTML)
    │   │   ├── static/
    │   │   └── index.html
    │   ├── agent/                  # AI Agent & Sync Engine (deep_sync_foxe.py, bot listener)
    │   │   ├── deep_sync_foxe.py
    │   │   ├── telegram_bot.py
    │   │   └── parser_engine/
    │   └── storage/                # Folder penyimpanan file, invoice, rekap order
    │       ├── uploads/
    │       └── exports/
    │
    ├── 02_folx/                    # Sektor 2: Folx Creative Agency
    │   ├── .env                    # Variabel lokal (PORT=3002)
    │   ├── app/                    # Web Portofolio & Client Portal
    │   ├── agent/                  # AI Intake Bot (Brief client otomatis)
    │   └── storage/                # Media pitch desk, aset desain, kontrak
    │       └── client_assets/
    │
    ├── 03_alashouse/               # Sektor 3: Alas House
    │   ├── .env                    # Variabel lokal (PORT=3003)
    │   ├── app/                    # Sistem Booking Ruang / Menu / Reservasi
    │   ├── agent/                  # Reservasi Bot & Notifikasi Tamu
    │   └── storage/                # Bukti reservasi & mutasi kas
    │       └── bookings/
    │
    ├── 04_lib/                     # Sektor 4: LIB
    │   ├── .env                    # Variabel lokal (PORT=3004)
    │   ├── app/                    # Web Store / Katalog Produk
    │   ├── agent/                  # Order Notification & CRM Bot
    │   └── storage/                # Foto produk, faktur penjualan
    │       └── catalog/
    │
    ├── 05_milous/                  # Sektor 5: Milous
    │   ├── .env                    # Variabel lokal (PORT=3005)
    │   ├── app/                    # Web Katalog / Kasir Toko
    │   ├── agent/                  # Inventory Alert & Stock Tracker
    │   └── storage/                # Foto koleksi, bukti transfer
    │       └── inventory/
    │
    ├── 06_fem/                     # Sektor 6: FEM
    │   ├── .env                    # Variabel lokal (PORT=3006)
    │   ├── app/                    # Editorial Platform / Komunitas
    │   ├── agent/                  # Content Scheduler & Lead Capture
    │   └── storage/                # Artikel, editorial asset, media kit
    │       └── media_assets/
    │
    └── 07_locus/                   # Sektor 7: Locus Venue & Studio Rental
        ├── .env                    # Variabel lokal (PORT=3007)
        ├── app/                    # Kalender Ketersediaan Venue & Rental
        ├── agent/                  # Slot Availability Bot & Schedule Alert
        └── storage/                # Dokumen sewa venue & deposit
            └── lease_agreements/
```

---

## 4. Contoh Konfigurasi Virtual Host Nginx (Reverse Proxy)

Contoh file konfigurasi Nginx untuk **FoxeStudio** (`/gateway/nginx/conf.d/01_foxestudio.conf`):

```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name foxestudio.com www.foxestudio.com;

    # SSL Certificates (Auto-generated by Certbot)
    ssl_certificate /etc/letsencrypt/live/foxestudio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/foxestudio.com/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";

    # Forwarding Traffic to FoxeStudio Port 3001
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Static Media Storage Handling
    location /storage/ {
        alias /srv/multibiz-vps/businesses/01_foxestudio/storage/uploads/;
        expires 30d;
        access_log off;
    }
}
```
*(Format file yang sama cukup diduplikasi untuk `folx.id`, `alashouse.com`, `lib.id`, `milous.id`, `fem.id`, dan `locus.id` dengan mengganti port internal `3002` s.d. `3007`)*.

---

## 5. Rekomendasi Spesifikasi Hardware VPS

Untuk menjalankan 7 sektor bisnis di atas dengan beban operasional UMKM menengah:

| Komponen | Spesifikasi Rekomendasi | Keterangan & Alokasi |
|:---|:---|:---|
| **CPU** | **4 vCPU Cores** | Cukup untuk memproses traffic web bersamaan + eksekusi background agent |
| **RAM** | **8 GB RAM** | ~500 MB per bisnis (x7 = 3.5 GB) + Database PostgreSQL (2 GB) + Sistem OS & Cache (2.5 GB) |
| **Storage** | **100 GB – 160 GB NVMe SSD** | Penyimpanan sistem OS, database transaksional, dan file media lokal |
| **Bandwidth** | **2 TB – 4 TB / bulan** | Sangat longgar untuk traffic web UMKM harian |
| **OS** | **Ubuntu 24.04 LTS (x86_64)** | Paling stabil, kompatibel dengan semua tool Python, Docker, dan Nginx |
| **Estimasi Biaya** | **\$10 – \$25 / bulan (Rp 160rb – Rp 400rb)** | Di provider seperti Hetzner Cloud (CX32/CX42), Contabo, DigitalOcean, atau IDCloudHost |

---

## 6. Protokol Keamanan & Isolasi Antar Bisnis

1. **Prinsip Least Privilege**: Database user masing-masing bisnis (`user_foxe`, `user_folx`, dll.) hanya memiliki izin membaca & menulis ke databasenya sendiri. Jika satu bisnis terjadi error, bisnis lain 100% aman dan tidak terdampak.
2. **Pemisahan File Storage**: File upload disimpan dalam direktori terisolasi per folder bisnis.
3. **Penyatuan Billing Domain**: Setiap domain bisnis dibeli atas nama akun Cloudflare/Registrar yang sama untuk memudahkan pengelolaan DNS satu pintu.
4. **Auto-Backup Otomatis Harian**: Setiap pukul 02:00 WIB, script `auto_backup_all.sh` melakukan dump database 7 bisnis, mengompres folder storage, lalu mengunggah file zip terenkripsi ke Google Drive / Cloudflare R2 secara otomatis.
