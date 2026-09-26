# Foxe Studio Keuangan — Security & Secrets Vault

Dokumen ini adalah brankas referensi resmi (*vault*) untuk arsitektur keamanan, manajemen kredensial, dan tata kelola data sistem keuangan Foxe Studio.

---

## 1. Kebijakan Keamanan Kredensial (Zero-Leakage Policy)
> [!IMPORTANT]
> Repositori **`whynunuu/FoxeStudio`** bersifat publik untuk melayani GitHub Pages.
> **DILARANG KERAS** melakukan hardcode token, API key, atau kredensial rahasia apa pun ke dalam file skrip Python publik, HTML, JavaScript, atau commit git.

---

## 2. Manajemen Kredensial & Secrets

### A. GitHub Personal Access Token (PAT)
* **Kegunaan**: Memanggil GitHub REST API endpoint `POST /repos/whynunuu/FoxeStudio/actions/workflows/daily_sync.yml/dispatches` untuk memicu sinkronisasi on-demand dari tombol **`🔄 Update`** di website.
* **Scope Minimal**: `repo` (atau `workflow`).
* **Penyimpanan**:
  * **Hanya di Browser Klien**: Disimpan di `localStorage.getItem("foxe_gh_token")` pada perangkat pemilik yang terautentikasi.
  * Jika belum ada, sistem menampilkan prompt modal yang aman dan ramah di browser untuk memasukkan token satu kali.
  * **Tidak Pernah Masuk Repository**: Token tidak pernah dikirim ke backend selain langsung ke API resmi GitHub via koneksi HTTPS terenkripsi.

### B. Notifikasi Telegram (`@NunuFxBot`)
* **Kegunaan**: Mengirimkan laporan harian closing otomatis, struk POS monospace, rincian omzet, shift kru, dan jadwal foto H+1.
* **Bot Username**: `@NunuFxBot`
* **Penyimpanan Cloud**: GitHub Repository Secrets:
  * `TELEGRAM_BOT_TOKEN`
  * `TELEGRAM_CHAT_ID`
* **Penyimpanan Lokal**: `telegram_config.json` pada mesin lokal ASUS.

### C. Google Drive Operational File IDs
File operasional yang diunduh dan diparsing otomatis oleh `deep_sync_foxe.py`:
| File | Format | ID Google Drive | Fungsi Utama |
|---|---|---|---|
| **File 1 (Log Order)** | `.xlsm` | `1tQGIdkwGn4jXwroiMkctmOuEPb_444CJ` | Log transaksi pembayaran, kas harian, funnel lead, shift slot kru |
| **File 2 (Schedule)** | `.xlsx` | `14UfXpQhjpRpKtMIwGtdihL0Bu_n5SJpu6vNcLjZ7A8I` | Jadwal booking studio 1, 2, 3 & deteksi sesi foto H+1 |
| **File Neraca** | `.xlsx` | `1dvnCNyfZI5z-12081XJjGCVLtMaQpUStYT61qU3orKM` | Pengeluaran riil COGS & OPEX (sheet September kolom P s.d. U) |

*(Catatan: File 3 / Rekap Global sengaja di-skip sesuai arsitektur resmi).*

---

## 3. Autentikasi Portal Website
* **Master PIN**: `202688`
* **Mekanisme Kunci**: Keypad interaktif virtual 6-digit dengan fitur *"Ingat perangkat ini (30 hari)"* berbasis `localStorage` key `foxe_auth_pass`.
* **URL Live**: 👉 **https://whynunuu.github.io/FoxeStudio/**

---

## 4. Vault Status Rekonsiliasi & Kebenaran Data (Data Truth Status)
* **Bulan Terverifikasi (Live Verified)**:
  * **September 2026**: Status `Berjalan (Terverifikasi)`. Mengambil langsung data harian dari Log Order transaksi, perhitungan shift kru, dan neraca biaya resmi.
* **Bulan Unverified (Pending Verification)**:
  * **Januari – Agustus 2026 & Oktober – Desember 2026**: Status `Belum Dicocokkan`.
  * **Aturan Mutlak**: Seluruh angka omzet 2026 untuk bulan-bulan ini **wajib dikosongkan (`—`)** di dashboard maupun tabel komparasi sampai proses audit pencocokan data riil diselesaikan oleh owner.
* **Benchmark Musiman (Seasonality Index)**:
  * Menggunakan acuan siklus tahunan studio tahun 2025 dengan rata-rata 1.00× (Super Peak September 2.10×).
