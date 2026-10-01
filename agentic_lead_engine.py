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
from typing import Dict, List, Any, Optional

STATE_FILE = "foxe_full_state.json"
VAULT_FILE = "leads_vault.json"

DEFAULT_LEADS = [
    {
        "id": "lead_101",
        "phone": "6281298421102",
        "display_name": "Dinda Maharani",
        "admin": "AMEL",
        "tier": "HOT",
        "status": "UNCONVERTED",
        "created_at": "2026-10-01 08:30:00",
        "last_message_at": "2026-10-01 09:15:00",
        "last_customer_msg": "Kak aku ambil yang wisuda tgl 3 Okt jam 10 ya. Nama: Dinda Maharani, 4 orang, minta rek BCA nya kak",
        "last_admin_msg": "Siap kak Dinda! Untuk BCA Foxe Studio di 122-098-771 a/n Foxe Studio. DP min 100rb ya kak, ditunggu konfirmasinya 🙏",
        "summary": "Form booking wisuda sudah diisi, minta rekening 2.5 jam lalu tapi belum kirim bukti transfer DP.",
        "ai_recommendation": "Kak Dindaa, mau ngabarin untuk sesi wisuda tgl 3 Okt jam 10 pagi ada yang nanyain slotnya juga nih kak. Biar aman jadwalnya nggak bentrok sama yang lain, mau langsung aku amankan slot fotografernya sekarang kak? Kalau udah transfer kabarin yaa biar langsung aku buatin tanda terimanya 🙏",
        "estimated_value": 350000,
        "follow_up_count": 0
    },
    {
        "id": "lead_102",
        "phone": "6285877124091",
        "display_name": "Farhan Maulana",
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
        1. Nomor HP cocok dengan phone di Log Order
        2. Nama client cocok persis atau sebagian (fuzzy)
        """
        clean_phone = "".join(filter(str.isdigit, phone))
        if clean_phone.startswith("0"):
            clean_phone = "62" + clean_phone[1:]

        orders = self.state.get("orders", [])
        schedule = (self.state.get("schedule") or {}).get("bookings", [])
        okt_pipe = (self.state.get("oktoberPipeline") or {}).get("allBookings", [])

        # Layer 1: Check Orders (Sudah DP/Lunas)
        for ord in orders:
            ord_client = str(ord.get("client", "")).strip().lower()
            ord_phone = str(ord.get("phone", "")).strip()
            clean_ord_phone = "".join(filter(str.isdigit, ord_phone))
            if clean_ord_phone and clean_phone and clean_ord_phone == clean_phone:
                return {"type": "order", "match": "phone", "data": ord}
            if name and ord_client and (name.lower() in ord_client or ord_client in name.lower()):
                return {"type": "order", "match": "name", "data": ord}

        # Layer 2: Check Schedule Pipeline
        for bk in (schedule + okt_pipe):
            bk_client = str(bk.get("client", "")).strip().lower()
            if name and bk_client and (name.lower() in bk_client or bk_client in name.lower()):
                return {"type": "pipeline", "match": "name", "data": bk}

        return None

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
        Generator balasan manusiawi (Humanis, Anti-Slop, Santai khas Kru Studio Foto).
        """
        cname = client_name.split()[0] if client_name else "Kak"

        if tier == "HOT":
            return (
                f"Kak {cname}aa, mau ngabarin santai nih barangkali slot fotonya mau langsung kita amankan sekarang? "
                f"Takutnya bentrok sama yang antre di jadwal fotografer hari itu kak. "
                f"Kabarin aja yaa kalau sudah sempet transfer DP-nya biar langsung aku bikinin tanda terima resminya 🙏"
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
        return {"status": "success", "lead": lead, "matched": bool(match_result)}

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
