"""
Foxe Studio — Agentic AI Lead Engine & Fonnte Webhook Receiver
=============================================================
Arsitektur Otomasi Cerdas untuk Studio Foto:
1. Menerima Webhook Masuk dari Fonnte (Pesan Customer & Balasan Admin).
2. Multi-Layer Matching vs Spreadsheet (File 1 Log Order, File 2 Schedule).
3. 3-Tier Lead Classification: Hot, Warm, Cold, Closed.
4. AI Response Recommendation: Bahasa manusiawi studio, anti-slop, no blind-action.
5. Admin Performance & Conversion Tracker (Speed to Lead & Closing Rate).
"""

import os
import json
import time
import datetime
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional

STATE_FILE = "foxe_full_state.json"
VAULT_FILE = "leads_vault.json"
SECRETS_FILE = "foxe_secrets.json"

_local_secrets = {}
if os.path.exists(SECRETS_FILE):
    try:
        with open(SECRETS_FILE, "r", encoding="utf-8") as _sf:
            _local_secrets = json.load(_sf)
    except Exception:
        pass

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or _local_secrets.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
FONNTE_TOKEN = os.environ.get("FONNTE_TOKEN") or _local_secrets.get("FONNTE_TOKEN", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or _local_secrets.get("TELEGRAM_BOT_TOKEN", "8809193335:AAER1t9MAnVSyIRJSWqHpFwaoFe4hYmcZ1s")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or _local_secrets.get("TELEGRAM_CHAT_ID", "1608969830")
ADMIN_PHONE = os.environ.get("ADMIN_PHONE") or _local_secrets.get("ADMIN_PHONE", "6285159210021")


FOXE_PAYMENT_INFO = {
    "bank": "BCA",
    "account_number": "0462897055",
    "account_name": "Dicky Ferry A",
    "min_dp": "100K (Rp 100.000)",
    "form_template": (
        "Untuk booking jadwal, mohon cantumkan format dibawah ya ka :\n\n"
        "- *Nama*        : \n"
        "- *Tanggal*     : \n"
        "- *Pukul*       : \n"
        "- *Paket*       : \n"
        "- *Tema*        : \n"
        "- *Jumlah Orang*: \n\n"
        "Untuk minimal *DP 100K* yaa kaa, \n"
        "bisa Transfer ke Rek BCA\n"
        "An. *Dicky Ferry A*\n"
        "0462897055\n"
        "Jika sudah transaksi, mohon kirimkan bukti transaksinya yaa kaa, Terima Kasih."
    )
}

DEFAULT_LEADS = [
    {
        "id": "lead_101",
        "phone": "6281298421102",
        "display_name": "Dinda Maharani",
        "paket": "Graduation",
        "admin": "AMEL",
        "tier": "HOT",
        "status": "UNCONVERTED",
        "created_at": "2026-10-01 08:30:00",
        "last_message_at": "2026-10-01 09:15:00",
        "last_customer_msg": "Kak aku ambil yang wisuda tgl 3 Okt jam 10 ya. Nama: Dinda Maharani, 4 orang, minta rek BCA nya kak",
        "last_admin_msg": "Siap kak Dinda! Untuk BCA Foxe Studio di 0462897055 a/n Dicky Ferry A. DP min 100K ya kak, ditunggu konfirmasinya 🙏",
        "summary": "Form booking wisuda sudah diisi, minta rekening 2.5 jam lalu tapi belum kirim bukti transfer DP 100K.",
        "ai_recommendation": "Kak Dindaa, mau ngabarin untuk sesi wisuda tgl 3 Okt jam 10 pagi ada yang nanyain slotnya juga nih kak. Biar aman jadwalnya nggak bentrok sama yang lain, mau langsung aku amankan slot fotografernya sekarang kak? Kalau udah transfer ke BCA 0462897055 a/n Dicky Ferry A kabarin yaa biar langsung aku buatin tanda terimanya 🙏",
        "estimated_value": 350000,
        "follow_up_count": 0
    },
    {
        "id": "lead_102",
        "phone": "6285877124091",
        "display_name": "Farhan Maulana",
        "paket": "Graduation",
        "admin": "INDAH",
        "tier": "HOT",
        "status": "UNCONVERTED",
        "created_at": "2026-10-01 09:00:00",
        "last_message_at": "2026-10-01 10:05:00",
        "last_customer_msg": "Halo kak kalau tgl 4 Okt sesi jam 14:00 backdrop B wisuda masih kosong? Totalnya jadi 300rb ya kak?",
        "last_admin_msg": "Iya betul kak Farhan, tgl 4 Okt jam 14:00 backdrop B masih aman. Mau sekalian di-lock slotnya kak?",
        "last_customer_msg_2": "Bisa tolong di-lock dulu kak? Aku transfer siang ini.",
        "summary": "Minta lock slot tgl 4 Okt jam 14:00. Janji transfer siang ini tapi sudah lewat 2 jam belum ada kabar.",
        "ai_recommendation": "Halo kak Farhan! Slot backdrop B jam 14:00 untuk tgl 4 Okt masih aku tahanin yaa kak. Biar nggak ketimpa yang antre di jadwal tim fotografer, kabarin aja kalau sudah sempet transfer DP-nya kak Farhan, makasih yaa 🙏",
        "estimated_value": 300000,
        "follow_up_count": 0
    },
    {
        "id": "lead_103",
        "phone": "6285743218890",
        "display_name": "Rizky Pratama",
        "paket": "Large Group",
        "admin": "AMEL",
        "tier": "WARM",
        "status": "UNCONVERTED",
        "created_at": "2026-09-30 16:20:00",
        "last_message_at": "2026-09-30 17:10:00",
        "last_customer_msg": "Kak bedanya Graduation Reguler sama Large Group apa ya kalau kita berlima?",
        "last_admin_msg": "Kalau berlima bisa ambil Graduation Reguler tambah add-person kak, atau langsung Large Group durasi 30 menit jadi lebih puas ganti gaya dan fotonya lebih banyak kak.",
        "summary": "Konsultasi paket untuk 5 orang kemarin sore, admin sudah jelaskan perbedaannya tapi client belum memutuskan.",
        "ai_recommendation": "Halo kak Rizky! Kemarin sempat kepikiran mau foto santai atau banyak ganti pose sama temen-temennya ya kak? Buat berlima saran aku paling pas yang Large Group 30 menit kak, space studio lebih leluasa dan nggak buru-buru. Udah ada obrolan lagi sama temen-temennya kah kak buat nentuin harinya?",
        "estimated_value": 250000,
        "follow_up_count": 0
    },
    {
        "id": "lead_104",
        "phone": "6281322895501",
        "display_name": "Nabila Putri",
        "paket": "Family",
        "admin": "ADIF",
        "tier": "WARM",
        "status": "UNCONVERTED",
        "created_at": "2026-09-30 14:00:00",
        "last_message_at": "2026-09-30 15:30:00",
        "last_customer_msg": "Bisa bawa baju ganti berapa kali kak buat foto keluarga 6 orang di tgl 10 Okt?",
        "last_admin_msg": "Bisa bawa 2 outfit kak, ada ruang ganti privat di studio kita. Untuk tgl 10 Okt slot pagi jam 09.30 dan siang jam 13.00 masih ada yang kosong kak.",
        "summary": "Tanya sesi foto keluarga 6 orang tanggal 10 Oktober dan outfit ganti. Admin sudah beri pilihan jam tapi belum dibalas.",
        "ai_recommendation": "Hai kak Nabila, mau cek santai nih kak barangkali sudah diobrolin sama keluarga untuk sesi tgl 10 Okt? Buat keluarga 6 orang biasanya paling favorit sesi jam 09.30 pagi kak, pencahayaan studio masih seger dan anak-anak/orang tua belum capek. Mau disiapin slot paginya kak?",
        "estimated_value": 450000,
        "follow_up_count": 0
    },
    {
        "id": "lead_105",
        "phone": "6287833129904",
        "display_name": "Anisa Rahma",
        "paket": "Graduation",
        "admin": "INDAH",
        "tier": "COLD",
        "status": "UNCONVERTED",
        "created_at": "2026-09-28 11:00:00",
        "last_message_at": "2026-09-28 11:15:00",
        "last_customer_msg": "Pricelist wisuda dong kak",
        "last_admin_msg": "Halo kak Anisa! Ini pricelist paket wisuda Foxe Studio ya kak [PDF terkirim]. Ada promo free all soft files kalau booking minggu ini kak.",
        "summary": "Hanya meminta pricelist wisuda 3 hari lalu, admin kirim PDF, client hanya read tanpa respon lanjut.",
        "ai_recommendation": "Hai kak Anisa! Kemarin sempat liat-liat paket wisuda Foxe Studio yaa? Kebetulan minggu ini kita ada display backdrop wisuda terbaru dengan lighting lebih warm & elegant. Mau aku kirimin contoh preview hasil fotonya kak buat referensi gaya nanti?",
        "estimated_value": 200000,
        "follow_up_count": 0
    },
    {
        "id": "lead_106",
        "phone": "6289655410023",
        "display_name": "Dimas Bagus",
        "paket": "Self Photo",
        "admin": "AMEL",
        "tier": "COLD",
        "status": "UNCONVERTED",
        "created_at": "2026-09-27 19:30:00",
        "last_message_at": "2026-09-27 19:40:00",
        "last_customer_msg": "Pricelist self photo studio kak",
        "last_admin_msg": "Halo kak Dimas! Untuk Self-Photo mulai 65rb per sesi sudah dapet cetak & soft files ya kak [Pricelist terkirim].",
        "summary": "Tanya pricelist self-photo 4 hari lalu, belum ada kelanjutan.",
        "ai_recommendation": "Halo kak Dimas! Mau ngabarin aja nih kak, buat self-photo studio kita baru nambah properti kacamata & props seru buat foto bareng bestie atau pasangan. Slot sore hari biasa masih banyak yang santai lho kak, mau coba mampir weekend ini?",
        "estimated_value": 85000,
        "follow_up_count": 0
    },
    {
        "id": "lead_107",
        "phone": "6281234567890",
        "display_name": "Hanifah (Live 1 Okt)",
        "paket": "Graduation",
        "admin": "AMEL",
        "tier": "CLOSED",
        "status": "CONVERTED",
        "created_at": "2026-10-01 07:15:00",
        "last_message_at": "2026-10-01 08:00:00",
        "last_customer_msg": "Kak ini bukti transfer DP 100rb atas nama Hanifah yaa buat sesi tgl 2 Okt",
        "last_admin_msg": "Alhamdulillah terverifikasi ya kak Hanifah! DP Rp 100.000 sudah masuk kasir, slot foto Graduation tgl 2 Okt sudah resmi terdaftar 🙏",
        "summary": "Berhasil closing DP Rp 100.000 via Transfer. Sudah terdaftar di Log Order Oktober.",
        "ai_recommendation": "Status: DEAL. Tidak memerlukan follow-up penawaran. Siapkan reminder H-1 sebelum sesi foto.",
        "estimated_value": 100000,
        "follow_up_count": 0
    }
]

class AgenticLeadEngine:
    def __init__(self, state_path: str = STATE_FILE, vault_path: str = VAULT_FILE):
        self.state_path = state_path
        self.vault_path = vault_path
        self.state = self._load_state()
        self.leads = self._load_vault()
        self.reconcile_and_clean_leads()

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARN] Gagal membaca state: {e}")
        return {}

    def _load_vault(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.vault_path):
            try:
                with open(self.vault_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data
            except Exception as e:
                print(f"[WARN] Gagal membaca vault: {e}")
        # Default seed
        self._save_vault(DEFAULT_LEADS)
        return DEFAULT_LEADS

    def _save_vault(self, leads: List[Dict[str, Any]]):
        try:
            with open(self.vault_path, "w", encoding="utf-8") as f:
                json.dump(leads, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Gagal menyimpan vault: {e}")

    def match_with_spreadsheet(self, phone: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Multi-Layer Matching:
        1. Nomor HP cocok persis (min 8 digit)
        2. Nama client cocok persis atau multi-kata di bulan aktif / pipeline berjalan
        """
        clean_phone = "".join(filter(str.isdigit, str(phone or "")))
        if clean_phone.startswith("0"):
            clean_phone = "62" + clean_phone[1:]
        valid_phone = len(clean_phone) >= 9

        # Ambil transaksi kasir (Oktober 2026 & September)
        okt_orders = (self.state.get("oktoberLogOrder") or {}).get("orders", [])
        sept_orders = self.state.get("orders", [])
        active_orders = okt_orders + sept_orders

        # Ambil jadwal & pipeline
        okt_pipe = (self.state.get("oktoberPipeline") or {}).get("bookings", [])
        schedule = (self.state.get("schedule") or {}).get("bookings", [])
        all_bookings = okt_pipe + schedule

        norm_name = str(name or "").strip().lower()

        def is_match_name(target: str) -> bool:
            t = str(target or "").strip().lower()
            if not t or not norm_name or norm_name in ("-", "."):
                return False
            if t == norm_name:
                return True
            if len(norm_name) >= 4 and (norm_name in t or t in norm_name):
                return True
            w1 = set(norm_name.split())
            w2 = set(t.split())
            if len(w1) >= 2 and len(w2) >= 2 and len(w1.intersection(w2)) >= 2:
                return True
            return False

        # Layer 1: Check Orders Aktif Kasir (Sudah DP/Lunas di Kasir)
        for ord in active_orders:
            ord_client = str(ord.get("client", "")).strip()
            ord_phone = str(ord.get("phone", "")).strip()
            clean_ord_phone = "".join(filter(str.isdigit, ord_phone))
            if valid_phone and clean_ord_phone and clean_ord_phone == clean_phone:
                return {"type": "order", "match": "phone", "data": ord}
            if norm_name and ord_client and is_match_name(ord_client):
                return {"type": "order", "match": "name", "data": ord}

        # Layer 2: Check Schedule Pipeline (Sudah terjadwal di Studio)
        for bk in all_bookings:
            bk_client = str(bk.get("client") or bk.get("nama") or "").strip()
            bk_phone = str(bk.get("noHp") or bk.get("phone") or "").strip()
            clean_bk_phone = "".join(filter(str.isdigit, bk_phone))
            if valid_phone and clean_bk_phone and clean_bk_phone == clean_phone:
                return {"type": "pipeline", "match": "phone", "data": bk}
            if norm_name and bk_client and is_match_name(bk_client):
                return {"type": "pipeline", "match": "name", "data": bk}

        return None

    def reconcile_and_clean_leads(self) -> Dict[str, Any]:
        """
        Rekonsiliasi berkala leads terhadap data live Google Sheets (File 1 Kasir & File 2 Schedule):
        1. Hapus entri dummy / test / pesan non-text tanpa nama.
        2. Cocokkan dengan Log Order & Schedule: Ubah status menjadi CONVERTED / DEAL atau RESCHEDULE.
        3. Arsipkan leads yang tanggal event incarannya sudah terlewati (misal wisuda UMP 3-4 Okt).
        4. Simpan ke leads_vault.json secara otomatis.
        """
        cleaned = []
        now_dt = datetime.datetime.now()

        for l in self.leads:
            name = str(l.get("display_name", "")).strip()
            phone = str(l.get("phone", "")).strip()
            msg = str(l.get("last_customer_msg", "")).strip().lower()

            # Filter data dummy / testing / sampah
            if phone in ("6289998887771", "089998887771") or "tes webhook" in name.lower() or "test" in name.lower():
                continue
            if name in ("-", ".", "") and (not msg or msg == "non-text message"):
                continue

            match = self.match_with_spreadsheet(phone, name)
            if match:
                m_type = match.get("type")
                m_data = match.get("data", {})
                if m_type == "order":
                    l["status"] = "CONVERTED"
                    l["tier"] = "CLOSED"
                    l["summary"] = f"Deal kasir: {m_data.get('paket','')} ({m_data.get('pembayaran','Lunas')})"
                    l["paket"] = m_data.get("paket") or l.get("paket") or self.detect_lead_paket(l)
                    l["ai_recommendation"] = "Status: DEAL di Kasir Log Order. Siapkan SOP reminder."
                elif m_type == "pipeline":
                    is_done = m_data.get("isDone") or m_data.get("statusSesi") == "done" or m_data.get("statusColor") == "biru"
                    is_resched = m_data.get("isReschedule") or m_data.get("statusSesi") == "reschedule" or m_data.get("statusColor") == "orange"
                    l["paket"] = m_data.get("paket") or l.get("paket") or self.detect_lead_paket(l)
                    if is_done:
                        l["status"] = "CONVERTED"
                        l["tier"] = "CLOSED"
                        l["summary"] = f"Sesi foto selesai: {m_data.get('paket','')} ({m_data.get('tgl','')})"
                        l["ai_recommendation"] = "Status: SELESAI di Studio. Kirim ucapan terima kasih."
                    elif is_resched:
                        l["status"] = "UNCONVERTED"
                        l["tier"] = "WARM"
                        l["summary"] = f"Reschedule: DP Rp {int(m_data.get('dp',100000)):,} tersimpan (Hak aktif 30 hari)"
                        l["ai_recommendation"] = "Status: RESCHEDULE. Follow up untuk re-book sesi weekday / foto santai."
                    else:
                        l["status"] = "CONVERTED"
                        l["tier"] = "CLOSED"
                        l["summary"] = f"Terjadwal: {m_data.get('paket','')} ({m_data.get('tgl','')} {m_data.get('waktu','')})"
            else:
                # Cek apakah lead kadaluwarsa (event wisuda 3-4 Okt sudah lewat)
                if l.get("status") != "CONVERTED":
                    if ("3 okt" in msg or "4 okt" in msg or "wisuda" in msg) and (now_dt.month >= 10 and now_dt.day >= 5):
                        l["status"] = "EXPIRED"
                        l["tier"] = "COLD"
                        l["summary"] = "Event wisuda 3-4 Okt telah terlewati."

            if not l.get("paket"):
                l["paket"] = self.detect_lead_paket(l)
            cleaned.append(l)

        self.leads = cleaned
        self._save_vault(self.leads)
        return {"status": "success", "total_cleaned": len(self.leads)}

    def detect_lead_paket(self, lead: Dict[str, Any]) -> str:
        """
        Deteksi paket foto yang diincar calon klien dari teks chat, summary, atau log order.
        """
        p = str(lead.get("paket") or "").strip()
        p_lower = p.lower()
        if "self photo" in p_lower or "photofox" in p_lower:
            return "Self Photo"
        if "family" in p_lower or "keluarga" in p_lower:
            return "Family"
        if "couple" in p_lower or "pasangan" in p_lower:
            return "Couple"
        if "single" in p_lower or "pas foto" in p_lower or "pasfoto" in p_lower:
            return "Single"
        if "large group" in p_lower:
            return "Large Group"
        if "graduation premium" in p_lower:
            return "Graduation Premium"
        if "graduation" in p_lower or "wisuda" in p_lower:
            return "Graduation"

        summary = str(lead.get("summary") or "").lower()
        msg = str(lead.get("last_customer_msg") or "").lower()
        rec = str(lead.get("ai_recommendation") or "").lower()
        text = f"{summary} {msg} {rec}".lower()

        if any(k in text for k in ["self photo", "selfphoto", "photofox", "self studio"]):
            return "Self Photo"
        if any(k in text for k in ["keluarga", "family"]):
            return "Family"
        if any(k in text for k in ["couple", "pasangan", "pacar", "prewed"]):
            return "Couple"
        if any(k in text for k in ["single", "pas foto", "pasfoto", "ijazah", "ktp"]):
            return "Single"
        if any(k in text for k in ["large group", "kelompok", "rombongan", "berlima", "5 orang"]):
            return "Large Group"
        if "graduation premium" in text:
            return "Graduation Premium"
        if any(k in text for k in ["wisuda", "graduation", "toga", "selempang", "backdrop b", "ump"]):
            return "Graduation"

        if p and p not in ("Konsultasi Umum", "Umum / Konsultasi"):
            return p
        return "Konsultasi Umum"

    def classify_lead_tier(self, messages: List[str]) -> str:
        """
        Analisis teks percakapan terakhir untuk menentukan tier:
        - HOT: Ada form nama, tanya rekening, total bayar, lock slot.
        - WARM: Tanya perbedaan paket, jumlah orang, tanggal kosong, outfit.
        - COLD: Cuma minta pricelist, salam singkat, atau tidak respon lama.
        """
        full_text = " ".join(messages).lower()

        hot_keywords = ["rek", "rekening", "bca", "bri", "mandiri", "qris", "transfer", "dp", "lock", "slot", "nama:", "booking", "fix", "bayar"]
        warm_keywords = ["bedanya", "berapa orang", "outfit", "backdrop", "paket", "graduation", "large", "studio", "kosong", "tanggal", "jam"]
        
        hot_score = sum(1 for kw in hot_keywords if kw in full_text)
        warm_score = sum(1 for kw in warm_keywords if kw in full_text)

        if hot_score >= 2 or ("rek" in full_text and "dp" in full_text) or "nama:" in full_text:
            return "HOT"
        elif warm_score >= 1 or hot_score == 1:
            return "WARM"
        else:
            return "COLD"

    def generate_ai_draft(self, client_name: str, tier: str, summary: str, context: str) -> str:
        """
        Generator balasan manusiawi berbasis LLM Google Gemini API.
        Anti-Slop, Santai, Sopan khas Tim Studio Foto Lokal.
        Fallback mulus ke template studio natural lokal jika offline atau limit.
        """
        cname = client_name.split()[0] if client_name else "Kak"

        # 1. Coba Generate via Google Gemini API
        if GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
                prompt = (
                    f"Role: Anda adalah tim CS/Admin Foxe Studio (studio foto profesional lokal yang hangat dan ramah).\n"
                    f"Tugas: Buatkan 1 pesan balasan WhatsApp santai, sopan, manusiawi, dan anti-slop (tanpa bahasa korporat kaku/robotik).\n"
                    f"Konteks Klien:\n"
                    f"- Nama Klien: {client_name}\n"
                    f"- Kategori: {tier} LEAD ({'hampir bayar DP / minta rekening' if tier=='HOT' else ('tanya-tanya paket foto' if tier=='WARM' else 'tanya pricelist lalu hening')})\n"
                    f"- Situasi: {summary}\n"
                    f"- Pesan Terakhir: {context}\n"
                    f"Konteks Resmi Foxe Studio:\n"
                    f"- Rekening Resmi Studio: BCA 0462897055 a/n Dicky Ferry A\n"
                    f"- Minimal DP: 100K (Rp 100.000)\n"
                    f"- Format Booking: Nama, Tanggal, Pukul, Paket, Tema, Jumlah Orang\n"
                    f"Aturan Penulisan:\n"
                    f"1. Panggil nama santai: 'Kak {cname}'.\n"
                    f"2. Maksimal 2-3 kalimat ringkas langsung ke tujuan.\n"
                    f"3. Jika klien butuh rekening/DP, cantumkan BCA 0462897055 an Dicky Ferry A (DP min 100K).\n"
                    f"4. Nada bersahabat, santai studio, tanpa menekan klien.\n"
                    f"5. Output HANYA teks balasan yang siap kirim, tanpa tanda kutip atau penjelasan tambahan."
                )
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    text = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                    text = text.strip('"\'')
                    if text:
                        return text
            except Exception as e:
                pass

        # 2. Fallback Natural Studio Template
        if tier == "HOT":
            return (
                f"Kak {cname}aa, mau ngabarin santai nih barangkali slot fotonya mau langsung kita amankan sekarang? "
                f"Takutnya bentrok sama yang antre di jadwal fotografer hari itu kak. "
                f"Untuk DP min 100K bisa ke Rek BCA 0462897055 a/n Dicky Ferry A yaa. "
                f"Kabarin aja kalau sudah transfer biar langsung aku bikinin tanda terima resminya 🙏"
            )
        elif tier == "WARM":
            return (
                f"Halo kak {cname}! Kemarin sempat kepikiran mau ambil paket yang mana nih kak buat sesi fotonya? "
                f"Kalau masih ragu nentuin konsep atau outfit-nya, kabarin aja yaa kak, nanti aku bantuin pilihin backdrop "
                f"yang paling pas biar hasilnya maksimal & nggak buru-buru 😊"
            )
        else: # COLD
            return (
                f"Hai kak {cname}! Kemarin sempat liat-liat paket foto Foxe Studio yaa? "
                f"Kebetulan kita ada beberapa referensi hasil foto terbaru di studio yang mungkin cocok buat ide gaya kakak. "
                f"Mau aku kirimin beberapa contoh fotonya kak buat inspirasi nanti?"
            )

    def ingest_fonnte_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Menerima payload resmi Fonnte Webhook:
        {
            "device": "62895xxxx",
            "sender": "6281234567890",
            "message": "...",
            "name": "...",
            "timestamp": 1727756400
        }
        """
        sender = str(payload.get("sender", "")).strip()
        name = str(payload.get("name") or payload.get("pushName") or "Client").strip()
        msg = str(payload.get("message", "")).strip()
        ts = payload.get("timestamp") or int(time.time())
        t_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

        # 1. Abaikan pesan dari grup WhatsApp
        if "@g.us" in sender or "-" in sender:
            return {"status": "ignored", "reason": "Pesan dari grup WhatsApp diabaikan"}

        # 2. Abaikan pesan keluar dari nomor admin studio sendiri
        clean_sender = "".join(filter(str.isdigit, sender))
        clean_dev = "".join(filter(str.isdigit, str(payload.get("device", ""))))
        if clean_sender in ("6285159210021", "085159210021") or (clean_dev and clean_sender == clean_dev):
            return {"status": "ignored", "reason": "Pesan keluar dari admin studio"}

        # Cek apakah nomor sudah ada di database
        lead = next((l for l in self.leads if l["phone"] == sender), None)

        # Cek matching spreadsheet
        match_result = self.match_with_spreadsheet(sender, name)
        is_converted = match_result and match_result.get("type") == "order"

        if lead:
            lead["last_message_at"] = t_str
            lead["last_customer_msg"] = msg
            if is_converted:
                lead["status"] = "CONVERTED"
                lead["tier"] = "CLOSED"
                lead["ai_recommendation"] = "Status: DEAL di Spreadsheet. Siapkan konfirmasi & reminder H-1 sesi foto."
            else:
                lead["tier"] = self.classify_lead_tier([lead.get("last_admin_msg", ""), msg])
                lead["ai_recommendation"] = self.generate_ai_draft(lead["display_name"], lead["tier"], lead["summary"], msg)
        else:
            tier = "CLOSED" if is_converted else self.classify_lead_tier([msg])
            new_lead = {
                "id": f"lead_{int(time.time())}",
                "phone": sender,
                "display_name": name,
                "admin": "AMEL", # Default rotasi admin aktif
                "tier": tier,
                "status": "CONVERTED" if is_converted else "UNCONVERTED",
                "created_at": t_str,
                "last_message_at": t_str,
                "last_customer_msg": msg,
                "last_admin_msg": "",
                "summary": f"Pesan baru masuk: {msg[:60]}...",
                "ai_recommendation": "Status: DEAL di Spreadsheet." if is_converted else self.generate_ai_draft(name, tier, "", msg),
                "estimated_value": 250000,
                "follow_up_count": 0
            }
            self.leads.insert(0, new_lead)
            lead = new_lead

        self._save_vault(self.leads)
        return {
            "status": "success",
            "tier": lead.get("tier"),
            "lead_status": lead.get("status"),
            "ai_recommendation": lead.get("ai_recommendation"),
            "lead": lead,
            "matched": bool(match_result)
        }

    def get_admin_metrics(self) -> Dict[str, Any]:
        """
        Kalkulasi performa admin:
        - Total Leads Ditangani
        - Closing Rate % (Masuk Sheet / DP)
        - Hot Leads Belum Closing
        - Potensi Omzet Menggantung
        """
        metrics = {}
        for l in self.leads:
            adm = l.get("admin") or "AMEL"
            if adm not in metrics:
                metrics[adm] = {"total_leads": 0, "converted": 0, "hot": 0, "warm": 0, "cold": 0, "unconverted_val": 0}
            m = metrics[adm]
            m["total_leads"] += 1
            if l.get("status") == "CONVERTED":
                m["converted"] += 1
            else:
                t = l.get("tier", "WARM")
                if t == "HOT": m["hot"] += 1
                elif t == "WARM": m["warm"] += 1
                elif t == "COLD": m["cold"] += 1
                m["unconverted_val"] += l.get("estimated_value", 0)

        for adm, data in metrics.items():
            tot = data["total_leads"]
            data["closing_rate"] = round((data["converted"] / tot * 100), 1) if tot > 0 else 0.0

        return metrics

    def get_leads_summary(self) -> Dict[str, Any]:
        """
        Mengambil summary leads dan performa admin untuk disinkronkan ke dashboard.
        """
        metrics = self.get_admin_metrics()
        total = len(self.leads)
        converted = sum(1 for l in self.leads if l.get("status") == "CONVERTED")
        hot = sum(1 for l in self.leads if l.get("tier") == "HOT" and l.get("status") != "CONVERTED")
        warm = sum(1 for l in self.leads if l.get("tier") == "WARM" and l.get("status") != "CONVERTED")
        cold = sum(1 for l in self.leads if l.get("tier") == "COLD" and l.get("status") != "CONVERTED")
        unconverted_val = sum(l.get("estimated_value", 0) for l in self.leads if l.get("status") != "CONVERTED")

        return {
            "status": "success",
            "total_leads": total,
            "converted_count": converted,
            "closing_rate": round((converted / total * 100), 1) if total > 0 else 0.0,
            "hot_count": hot,
            "warm_count": warm,
            "cold_count": cold,
            "unconverted_potential_value": unconverted_val,
            "admin_metrics": metrics,
            "leads": self.leads
        }

    def format_followup_reminder(self, current_hour_str: str = "12:00 WIB") -> str:
        """
        Meracik pesan reminder CRM & Follow-Up terstruktur untuk Admin Studio:
        1. 🟠 PIPELINE RECOVERY CRM: Klien Reschedule dengan hak DP 30 hari (Data live dari Google Sheets)
        2. 🔥 HOT & WARM LEADS AKTIF: Calon klien baru yang butuh closing DP
        3. 📊 RINGKASAN METRIK CRM: Total DP tersimpan, closing rate, & link ke CRM Web
        """
        # Ambil data booking label Orange (Reschedule) langsung dari state live
        okt_pipe = (self.state.get("oktoberPipeline") or {}).get("bookings", [])
        orange_bookings = [
            b for b in okt_pipe
            if b.get("isReschedule") or b.get("statusColor") == "orange" or b.get("statusSesi") == "reschedule"
        ]
        tot_orange_dp = sum(b.get("dp", 0) for b in orange_bookings)
        tot_orange_sisa = sum(b.get("sisaPelunasan", 0) for b in orange_bookings)

        # Filter leads aktif (bukan CONVERTED dan bukan EXPIRED)
        unconverted = [l for l in self.leads if l.get("status") not in ("CONVERTED", "EXPIRED")]
        hot_leads = [l for l in unconverted if l.get("tier") == "HOT"]
        warm_leads = [l for l in unconverted if l.get("tier") == "WARM"]
        total_potensi_leads = sum(l.get("estimated_value", 0) for l in unconverted)

        lines = [
            "🚨 *REMINDER CRM & FOLLOW-UP FOXE STUDIO*",
            f"⏰ *Pukul {current_hour_str}* | Jam Operasional (09:00 - 21:00 WIB)\n"
        ]

        # 1. Section Reschedule Recovery (Klien Orange)
        if orange_bookings:
            lines.append(f"🟠 *[CRM RECOVERY — {len(orange_bookings)} KLIEN RESCHEDULE]*")
            lines.append("🛡️ *Kredit DP 100% Aktif 30 Hari (s.d. 03 Nov 2026)*")
            lines.append(f"💰 *DP Terkunci:* Rp {int(tot_orange_dp):,} | *Target Pelunasan:* Rp {int(tot_orange_sisa):,}\n")
            for i, b in enumerate(orange_bookings[:8], 1):
                nama = b.get("nama", "Klien")
                waktu = b.get("waktu", "-")
                tgl = b.get("tgl", "")
                tgl_str = f"{tgl[-2:]} Okt" if len(tgl) >= 10 else ""
                paket = b.get("paket") or "Graduation"
                dp_val = int(b.get("dp", 100000))
                sisa_val = int(b.get("sisaPelunasan", 250000))
                lines.append(f"{i}. *{nama}* ({tgl_str} {waktu}) — {paket}")
                lines.append(f"   • DP Aman: Rp {dp_val:,} | Sisa Target: Rp {sisa_val:,}")
                lines.append(f"   • Aksi: Segera hubungi untuk re-book slot weekday / foto kasual\n")

        # 2. Section Leads Chat Baru (Hot & Warm)
        if hot_leads:
            lines.append("🔥 *[HOT LEADS — PRIORITAS AMANKAN SLOT]*")
            for i, l in enumerate(hot_leads[:3], 1):
                name = l.get("display_name", "Klien")
                phone = l.get("phone", "")
                adm = l.get("admin", "AMEL")
                val = l.get("estimated_value", 0)
                summary = l.get("summary", "Menunggu konfirmasi")
                lines.append(f"{i}. *{name}* ({phone}) — Admin {adm}")
                lines.append(f"   • Situasi: {summary}")
                lines.append(f"   • Potensi: Rp {val:,}\n")

        if warm_leads:
            lines.append("⚡ *[WARM LEADS — KONSULTASI AKTIF]*")
            for i, l in enumerate(warm_leads[:3], 1):
                name = l.get("display_name", "Klien")
                phone = l.get("phone", "")
                adm = l.get("admin", "AMEL")
                summary = l.get("summary", "Konsultasi paket")
                lines.append(f"{i}. *{name}* ({phone}) — Admin {adm}")
                lines.append(f"   • Info: {summary}\n")

        if not hot_leads and not warm_leads:
            lines.append("✅ *[STATUS CHAT MASUK]*")
            lines.append("Seluruh leads chat wisuda telah terkonversi / selesai.")
            lines.append("Fokus follow-up dialihkan ke: *8 Klien Reschedule di atas!* 🎯\n")

        # 3. Ringkasan Status CRM
        converted_cnt = sum(1 for l in self.leads if l.get("status") == "CONVERTED")
        total_cnt = len(self.leads)
        crate = round((converted_cnt / total_cnt * 100), 1) if total_cnt > 0 else 0.0

        lines.append("📊 *Ringkasan Status CRM:*")
        lines.append(f"• Klien Reschedule Aktif: {len(orange_bookings)} Klien (DP Rp {int(tot_orange_dp):,})")
        lines.append(f"• Leads Terkonversi: {converted_cnt} Klien ({crate}%)")
        lines.append(f"• Potensi Cash Recovery: Rp {int(tot_orange_sisa):,}\n")
        lines.append("👉 *Buka CRM & Detail Client:*")
        lines.append("https://whynunuu.github.io/FoxeStudio/")

        return "\n".join(lines)

    def format_followup_reminder_wa(self, current_hour_str: str = "12:00 WIB") -> str:
        """
        Format ringkas padat khusus WhatsApp agar kompatibel dengan limit karakter Fonnte Free Package.
        """
        okt_pipe = (self.state.get("oktoberPipeline") or {}).get("bookings", [])
        orange_bookings = [
            b for b in okt_pipe
            if b.get("isReschedule") or b.get("statusColor") == "orange" or b.get("statusSesi") == "reschedule"
        ]
        tot_orange_dp = sum(b.get("dp", 0) for b in orange_bookings)
        tot_orange_sisa = sum(b.get("sisaPelunasan", 0) for b in orange_bookings)

        unconverted = [l for l in self.leads if l.get("status") not in ("CONVERTED", "EXPIRED")]
        hot_leads = [l for l in unconverted if l.get("tier") == "HOT"]

        lines = [
            f"🚨 *REMINDER CRM FOXE STUDIO ({current_hour_str})*",
            "⏰ Jam Operasional (09:00 - 21:00 WIB)\n"
        ]

        if orange_bookings:
            lines.append(f"🟠 *{len(orange_bookings)} KLIEN RESCHEDULE (HAK DP 30 HARI):*")
            lines.append(f"DP Aman: Rp {int(tot_orange_dp):,} | Target Pelunasan: Rp {int(tot_orange_sisa):,}")
            for i, b in enumerate(orange_bookings[:6], 1):
                dp_k = int(b.get('dp', 100000) / 1000)
                sisa_k = int(b.get('sisaPelunasan', 250000) / 1000)
                lines.append(f"{i}. {b.get('nama')} (DP {dp_k}k - Sisa {sisa_k}k)")
            lines.append("💡 *Aksi:* Segera hubungi untuk re-book slot weekday sebelum 03 Nov 2026.\n")

        if hot_leads:
            lines.append("🔥 *HOT LEADS BARU:*")
            for i, l in enumerate(hot_leads[:2], 1):
                lines.append(f"{i}. {l.get('display_name')} ({l.get('phone')})")
            lines.append("")

        lines.append("CRM Web: whynunuu.github.io/FoxeStudio/")
        return "\n".join(lines)

    def send_followup_reminder(self, current_hour_str: str = "12:00 WIB", target_phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Mengirimkan notifikasi reminder otomatis ke:
        1. Telegram Bot (@NunuFxBot) — Format detail
        2. WhatsApp Admin via Fonnte Gateway — Format ringkas kompatibel
        """
        msg_tg = self.format_followup_reminder(current_hour_str)
        msg_wa = self.format_followup_reminder_wa(current_hour_str)

        results = {
            "status": "success",
            "time": current_hour_str,
            "telegram": False,
            "whatsapp": False,
            "recipients": []
        }

        # 1. Kirim ke Telegram (Format Detail Lengkap)
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            try:
                tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                payload = urllib.parse.urlencode({
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": msg_tg,
                    "parse_mode": "Markdown"
                }).encode("utf-8")
                req = urllib.request.Request(tg_url, data=payload)
                with urllib.request.urlopen(req, timeout=10) as r:
                    if r.getcode() == 200:
                        results["telegram"] = True
                        results["recipients"].append(f"Telegram (Chat ID: {TELEGRAM_CHAT_ID})")
            except Exception as e:
                print(f"[WARN] Gagal kirim reminder ke Telegram: {e}")

        # 2. Kirim ke WhatsApp via Fonnte (Format Ringkas Kompatibel)
        phone_dest = target_phone or ADMIN_PHONE
        if FONNTE_TOKEN and phone_dest:
            try:
                wa_url = "https://api.fonnte.com/send"
                payload = json.dumps({
                    "target": phone_dest,
                    "message": msg_wa
                }).encode("utf-8")
                req = urllib.request.Request(
                    wa_url,
                    data=payload,
                    headers={"Authorization": FONNTE_TOKEN, "Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    resp_data = json.loads(r.read().decode("utf-8"))
                    if resp_data.get("status"):
                        results["whatsapp"] = True
                        results["recipients"].append(f"WhatsApp ({phone_dest})")
            except Exception as e:
                print(f"[WARN] Gagal kirim reminder ke WhatsApp: {e}")

        return results

if __name__ == "__main__":
    engine = AgenticLeadEngine()
    print("==================================================")
    print("   FOXE STUDIO — AGENTIC AI LEAD ENGINE LOADED   ")
    print("==================================================")
    print(f"Total Leads di Vault: {len(engine.leads)}")
    metrics = engine.get_admin_metrics()
    for adm, m in metrics.items():
        print(f"Admin {adm}: {m['total_leads']} Leads | Converted: {m['converted']} ({m['closing_rate']}%) | Hot: {m['hot']} | Potensi Tertahan: Rp {m['unconverted_val']:,}")
    print("\nEngine siap menerima webhook Fonnte & menghasilkan draft rekomendasi humanis!")
