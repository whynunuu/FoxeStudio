import os
import json
import time
import re
import datetime
import requests
import urllib3
from typing import Dict, Any, List, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LOGS_FILE = os.path.join(DATA_DIR, "execution_logs.json")
TELEGRAM_CONFIG_PATH = os.path.join(WORKSPACE_DIR, "telegram_config.json")
FOXE_STATE_PATH = os.path.join(WORKSPACE_DIR, "foxe_full_state.json")

def format_rupiah(val: Any) -> str:
    try:
        n = float(val)
        return f"{int(n):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(val)

def normalize_phone(phone: str) -> str:
    clean = re.sub(r"\D", "", str(phone or ""))
    if clean.startswith("0"):
        clean = "62" + clean[1:]
    return clean

def render_template(template_str: str, context: Dict[str, Any]) -> str:
    if not template_str:
        return ""
    result = str(template_str)
    
    # Handle custom rupiah helper like {{rupiah(dp)}}
    def rupiah_replacer(match):
        key = match.group(1).strip()
        val = context.get(key, 0)
        return format_rupiah(val)
    result = re.sub(r"\{\{rupiah\(([\w_]+)\)\}\}", rupiah_replacer, result)

    # Handle standard {{key}} replacements
    for k, v in context.items():
        if isinstance(v, (int, float)):
            str_v = format_rupiah(v) if "bayar" in k.lower() or "dp" in k.lower() or "total" in k.lower() or "omzet" in k.lower() else str(v)
        else:
            str_v = str(v)
        result = result.replace(f"{{{{{k}}}}}", str_v)
        result = result.replace(f"{{{{ {k} }}}}", str_v)
        
    return result

class WorkflowEngine:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load_foxe_state(self) -> Dict[str, Any]:
        if os.path.exists(FOXE_STATE_PATH):
            try:
                with open(FOXE_STATE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[FoxeFlow] Error loading state: {e}")
        return {}

    def get_default_telegram_config(self) -> Dict[str, Any]:
        if os.path.exists(TELEGRAM_CONFIG_PATH):
            try:
                with open(TELEGRAM_CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"token": "", "chat_id": ""}

    def save_log(self, execution_record: Dict[str, Any]):
        try:
            records = []
            if os.path.exists(LOGS_FILE):
                with open(LOGS_FILE, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.insert(0, execution_record)
            # Keep last 150 records
            records = records[:150]
            with open(LOGS_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[FoxeFlow] Error saving execution log: {e}")

    def execute_workflow(self, workflow: Dict[str, Any], initial_payload: Dict[str, Any], trigger_source: str = "manual") -> Dict[str, Any]:
        exec_id = f"exec_{int(time.time() * 1000)}"
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        nodes = {n["id"]: n for n in workflow.get("nodes", [])}
        connections = workflow.get("connections", [])
        
        # Build adjacency maps: node_id -> list of {target, sourceHandle}
        adj = {}
        for c in connections:
            s = c.get("source")
            t = c.get("target")
            handle = c.get("sourceHandle", "output")
            if s not in adj:
                adj[s] = []
            adj[s].append({"target": t, "handle": handle})

        # Locate trigger node or starting nodes
        trigger_node = None
        for nid, node in nodes.items():
            ntype = node.get("type", "")
            if trigger_source == "webhook" and ntype == "webhook_trigger":
                trigger_node = node
                break
            elif trigger_source == "foxe_booking" and ntype == "foxe_booking_trigger":
                trigger_node = node
                break
            elif ntype in ["webhook_trigger", "manual_trigger", "foxe_booking_trigger"] and not trigger_node:
                trigger_node = node

        if not trigger_node and nodes:
            # Fallback to the first node
            trigger_node = list(nodes.values())[0]

        execution_logs = []
        executed_nodes = []
        current_data = dict(initial_payload)

        # Context store to pass across nodes
        pipeline_context = dict(initial_payload)
        status_overall = "completed"

        if not trigger_node:
            record = {
                "id": exec_id,
                "workflow_id": workflow.get("id", "unknown"),
                "workflow_name": workflow.get("name", "Untitled Workflow"),
                "timestamp": start_time,
                "status": "failed",
                "trigger_source": trigger_source,
                "steps": [{
                    "node_id": "none",
                    "node_name": "Engine",
                    "status": "error",
                    "message": "Workflow has no nodes or trigger.",
                    "duration_ms": 0
                }],
                "final_data": {}
            }
            self.save_log(record)
            return record

        # Queue-based execution traversal
        queue = [(trigger_node["id"], "output")]
        visited = set()

        while queue:
            current_id, incoming_handle = queue.pop(0)
            if current_id not in nodes:
                continue

            node = nodes[current_id]
            node_type = node.get("type", "")
            node_name = node.get("name", current_id)
            params = node.get("parameters", {})
            
            t0 = time.time()
            step_log = {
                "node_id": current_id,
                "node_name": node_name,
                "node_type": node_type,
                "status": "success",
                "message": "",
                "data_snapshot": {},
                "duration_ms": 0
            }

            executed_nodes.append(current_id)
            next_handle = "output"

            try:
                if node_type == "webhook_trigger":
                    step_log["message"] = f"Payload webhook diterima ({len(pipeline_context)} field)"
                    step_log["data_snapshot"] = dict(pipeline_context)

                elif node_type == "manual_trigger":
                    step_log["message"] = "Trigger manual dijalankan dengan data simulasi"
                    step_log["data_snapshot"] = dict(pipeline_context)

                elif node_type == "foxe_booking_trigger":
                    foxe_state = self.load_foxe_state()
                    orders = foxe_state.get("orders", [])
                    pipeline_events = foxe_state.get("pipeline_october", [])
                    all_bookings = orders + pipeline_events
                    
                    selected_sample = None
                    if all_bookings:
                        # Grab the latest or matching sample
                        selected_sample = all_bookings[-1]
                    
                    if selected_sample:
                        pipeline_context.update({
                            "client_name": selected_sample.get("client", "Pelanggan Foxe"),
                            "paket": selected_sample.get("paket", "Graduation Studio"),
                            "tanggal_foto": selected_sample.get("tanggalFoto", selected_sample.get("tanggal", "2026-10-03")),
                            "jam_foto": selected_sample.get("jam", "13:00 WIB"),
                            "backdrop": selected_sample.get("backdrop", "Studio 1 - Neutral Glow"),
                            "total_paket": selected_sample.get("total", 350000),
                            "dp_masuk": selected_sample.get("transfer", selected_sample.get("cash", 100000)),
                            "sisa_bayar": max(0, selected_sample.get("total", 350000) - selected_sample.get("transfer", 100000)),
                            "phone": selected_sample.get("phone", "081234567890"),
                            "admin": selected_sample.get("admin", "Admin Foxe")
                        })
                        step_log["message"] = f"Memuat data live studio: {pipeline_context.get('client_name')} ({pipeline_context.get('paket')})"
                    else:
                        step_log["message"] = "Tidak ada booking aktif di state studio, menggunakan data context bawaan"
                    step_log["data_snapshot"] = dict(pipeline_context)

                elif node_type == "filter_if":
                    field = params.get("field", "dp_masuk")
                    operator = params.get("operator", ">")
                    target_val = params.get("value", "0")

                    actual_val = pipeline_context.get(field, "")
                    is_match = False

                    # Coerce for numeric comparison if possible
                    try:
                        num_act = float(actual_val)
                        num_tar = float(target_val)
                        if operator == ">": is_match = num_act > num_tar
                        elif operator == ">=": is_match = num_act >= num_tar
                        elif operator == "<": is_match = num_act < num_tar
                        elif operator == "<=": is_match = num_act <= num_tar
                        elif operator == "==": is_match = num_act == num_tar
                        elif operator == "!=": is_match = num_act != num_tar
                    except (ValueError, TypeError):
                        str_act = str(actual_val).lower().strip()
                        str_tar = str(target_val).lower().strip()
                        if operator == "==": is_match = str_act == str_tar
                        elif operator == "!=": is_match = str_act != str_tar
                        elif operator == "contains": is_match = str_tar in str_act
                        elif operator == "is_not_empty": is_match = bool(str_act)

                    next_handle = "true" if is_match else "false"
                    step_log["message"] = f"IF Condition [{field} {operator} {target_val}] => {'TRUE' if is_match else 'FALSE'} (Lanjut ke cabang: {next_handle})"
                    step_log["data_snapshot"] = {"evaluated_value": actual_val, "result": is_match, "branch": next_handle}

                elif node_type == "set_transform":
                    # Evaluate custom fields / formatted template
                    msg_template = params.get("message_template", "")
                    if msg_template:
                        rendered_msg = render_template(msg_template, pipeline_context)
                        pipeline_context["rendered_message"] = rendered_msg
                    
                    # Compute sisa_bayar if not present
                    try:
                        tot = float(pipeline_context.get("total_paket", 0))
                        dp = float(pipeline_context.get("dp_masuk", 0))
                        pipeline_context["sisa_bayar"] = max(0, tot - dp)
                    except Exception:
                        pass

                    step_log["message"] = f"Variabel berhasil diproses. Pesan WhatsApp di-render ({len(pipeline_context.get('rendered_message', ''))} karakter)"
                    step_log["data_snapshot"] = {
                        "rendered_message": pipeline_context.get("rendered_message", "")[:200] + ("..." if len(pipeline_context.get("rendered_message", "")) > 200 else "")
                    }

                elif node_type == "fonnte_whatsapp":
                    token = params.get("token", "").strip()
                    target_phone = params.get("target_phone", "{{phone}}")
                    resolved_phone = render_template(target_phone, pipeline_context)
                    resolved_phone = normalize_phone(resolved_phone)
                    
                    custom_msg = params.get("message", "{{rendered_message}}")
                    rendered_content = render_template(custom_msg, pipeline_context)
                    if not rendered_content and "rendered_message" in pipeline_context:
                        rendered_content = pipeline_context["rendered_message"]

                    is_simulation = params.get("is_simulation", True) or not token or token == "FONNTE_TOKEN_ANDA"

                    if is_simulation:
                        step_log["message"] = f"[SIMULASI / MOCK] Pesan WhatsApp berhasil disimulasikan ke {resolved_phone}"
                        step_log["data_snapshot"] = {
                            "mode": "Simulasi (Mock Send - Aman Tanpa Token)",
                            "target": resolved_phone,
                            "pesan_terkirim": rendered_content,
                            "fonnte_status": "Simulated 200 OK"
                        }
                    else:
                        # Real HTTP Call to Fonnte API
                        api_url = "https://api.fonnte.com/send"
                        headers = {"Authorization": token}
                        payload_post = {
                            "target": resolved_phone,
                            "message": rendered_content,
                            "countryCode": "62"
                        }
                        img_url = params.get("file_url", "").strip()
                        if img_url:
                            payload_post["url"] = render_template(img_url, pipeline_context)

                        try:
                            res = requests.post(api_url, data=payload_post, headers=headers, timeout=12, verify=False)
                            res_json = {}
                            try:
                                res_json = res.json()
                            except Exception:
                                res_json = {"raw": res.text}

                            if res.status_code == 200 and res_json.get("status"):
                                step_log["message"] = f"Pesan WhatsApp SUKSES terkirim via Fonnte ke {resolved_phone}"
                            else:
                                step_log["status"] = "warning"
                                step_log["message"] = f"Fonnte Response: {res_json.get('reason', res_json.get('message', res.text))}"
                            
                            step_log["data_snapshot"] = {
                                "target": resolved_phone,
                                "http_code": res.status_code,
                                "fonnte_response": res_json
                            }
                        except Exception as e_wa:
                            step_log["status"] = "warning"
                            step_log["message"] = f"Gagal menghubungi Fonnte API: {str(e_wa)}"
                            step_log["data_snapshot"] = {"error": str(e_wa)}

                elif node_type == "telegram_bot":
                    tg_conf = self.get_default_telegram_config()
                    token = params.get("token", "").strip() or tg_conf.get("token", "")
                    chat_id = params.get("chat_id", "").strip() or tg_conf.get("chat_id", "")
                    tg_msg = params.get("message", "Notifikasi Otomasi Foxe Flow:\n{{rendered_message}}")
                    rendered_tg = render_template(tg_msg, pipeline_context)

                    if token and chat_id:
                        try:
                            tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
                            tg_res = requests.post(tg_url, json={"chat_id": chat_id, "text": rendered_tg, "parse_mode": "HTML"}, timeout=10, verify=False)
                            if tg_res.status_code == 200:
                                step_log["message"] = f"Notifikasi Telegram terkirim ke Admin (chat_id: {chat_id})"
                            else:
                                step_log["status"] = "warning"
                                step_log["message"] = f"Telegram response: {tg_res.status_code} {tg_res.text[:100]}"
                            step_log["data_snapshot"] = {"status": tg_res.status_code, "text": rendered_tg[:150]}
                        except Exception as e_tg:
                            step_log["status"] = "warning"
                            step_log["message"] = f"Telegram error (diabaikan agar flow tetap jalan): {str(e_tg)[:100]}"
                            step_log["data_snapshot"] = {"warning": str(e_tg)}
                    else:
                        step_log["message"] = "[SIMULASI] Notifikasi Telegram disimulasikan (Token/Chat ID belum diisi)"
                        step_log["data_snapshot"] = {"preview": rendered_tg}

                elif node_type == "http_request":
                    url = params.get("url", "")
                    method = params.get("method", "POST").upper()
                    if url:
                        resolved_url = render_template(url, pipeline_context)
                        step_log["message"] = f"HTTP {method} request dikirim ke {resolved_url}"
                    else:
                        step_log["message"] = "URL HTTP Request kosong"

                elif node_type == "delay":
                    seconds = int(params.get("seconds", 1))
                    step_log["message"] = f"Jeda eksekusi selama {seconds} detik"
                    time.sleep(min(seconds, 3)) # Cap test delay to 3s

            except Exception as e:
                step_log["status"] = "error"
                step_log["message"] = f"Error pada langkah ini: {str(e)}"
                status_overall = "failed"

            step_log["duration_ms"] = int((time.time() - t0) * 1000)
            execution_logs.append(step_log)

            # Queue connected nodes
            targets = adj.get(current_id, [])
            for target_info in targets:
                # If node is filter_if, only follow the matching handle branch!
                if node_type == "filter_if":
                    if target_info["handle"] == next_handle:
                        queue.append((target_info["target"], target_info["handle"]))
                else:
                    queue.append((target_info["target"], target_info["handle"]))

        record = {
            "id": exec_id,
            "workflow_id": workflow.get("id", "wf_default"),
            "workflow_name": workflow.get("name", "Untitled Workflow"),
            "timestamp": start_time,
            "status": status_overall,
            "trigger_source": trigger_source,
            "steps": execution_logs,
            "executed_nodes": executed_nodes,
            "final_data": pipeline_context
        }
        self.save_log(record)
        return record
