import os
import json
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from foxe_flow.engine import WorkflowEngine, DATA_DIR, LOGS_FILE, WORKSPACE_DIR

app = FastAPI(title="Foxe Flow - Admin Studio Automation", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = WorkflowEngine()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
WORKFLOWS_FILE = os.path.join(DATA_DIR, "workflows.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def load_workflows():
    if os.path.exists(WORKFLOWS_FILE):
        try:
            with open(WORKFLOWS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_workflows(data):
    with open(WORKFLOWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {
        "fonnte_token": "",
        "telegram_token": "8809193335:AAER1t9MAnVSyIRJSWqHpFwaoFe4hYmcZ1s",
        "telegram_chat_id": "1608969830",
        "studio_name": "Foxe Studio",
        "default_simulation": True
    }

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h3>Foxe Flow Builder is loading...</h3>")

@app.get("/api/workflows")
async def get_all_workflows():
    return load_workflows()

@app.get("/api/workflows/{wf_id}")
async def get_workflow(wf_id: str):
    wfs = load_workflows()
    for w in wfs:
        if w.get("id") == wf_id:
            return w
    raise HTTPException(status_code=404, detail="Workflow not found")

@app.post("/api/workflows")
async def save_workflow(workflow: dict = Body(...)):
    wfs = load_workflows()
    wf_id = workflow.get("id")
    if not wf_id:
        wf_id = f"wf_{int(os.path.getmtime(WORKFLOWS_FILE) if os.path.exists(WORKFLOWS_FILE) else 1000)}"
        workflow["id"] = wf_id

    # Check if existing workflow
    found = False
    for i, w in enumerate(wfs):
        if w.get("id") == wf_id:
            wfs[i] = workflow
            found = True
            break
    if not found:
        wfs.append(workflow)

    save_workflows(wfs)
    return {"status": "success", "workflow": workflow}

@app.delete("/api/workflows/{wf_id}")
async def delete_workflow(wf_id: str):
    wfs = load_workflows()
    initial_len = len(wfs)
    wfs = [w for w in wfs if w.get("id") != wf_id]
    if len(wfs) == initial_len:
        raise HTTPException(status_code=404, detail="Workflow not found")
    save_workflows(wfs)
    return {"status": "deleted", "id": wf_id}

@app.post("/api/workflows/{wf_id}/toggle")
async def toggle_workflow_active(wf_id: str):
    wfs = load_workflows()
    for w in wfs:
        if w.get("id") == wf_id:
            w["is_active"] = not w.get("is_active", False)
            save_workflows(wfs)
            return {"status": "success", "is_active": w["is_active"]}
    raise HTTPException(status_code=404, detail="Workflow not found")

@app.post("/api/workflows/{wf_id}/execute")
async def test_execute_workflow(wf_id: str, request: Request):
    payload = {}
    try:
        payload = await request.json()
    except Exception:
        pass

    wfs = load_workflows()
    target_wf = next((w for w in wfs if w.get("id") == wf_id), None)
    if not target_wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # If payload is empty, provide rich demo booking data
    if not payload:
        payload = {
            "client_name": "Denny Hardiansyah",
            "phone": "081234567890",
            "paket": "Graduation Super Peak",
            "tanggal_foto": "2026-10-03",
            "jam_foto": "10:30 WIB",
            "backdrop": "Backdrop A (Graduation Elite)",
            "total_paket": 350000,
            "dp_masuk": 100000,
            "sisa_bayar": 250000,
            "admin": "AMEL"
        }

    exec_result = engine.execute_workflow(target_wf, payload, trigger_source="manual")
    return exec_result

@app.post("/api/webhook/{webhook_token}")
async def handle_incoming_webhook(webhook_token: str, request: Request):
    payload = {}
    try:
        payload = await request.json()
    except Exception:
        try:
            form = await request.form()
            payload = dict(form)
        except Exception:
            payload = {}

    wfs = load_workflows()
    matching_wfs = [
        w for w in wfs
        if w.get("is_active", False) and (
            w.get("webhook_token") == webhook_token or
            any(n.get("parameters", {}).get("webhook_token") == webhook_token for n in w.get("nodes", []))
        )
    ]

    if not matching_wfs:
        return JSONResponse(
            status_code=404,
            content={"status": "not_found", "message": f"No active workflow found matching webhook token: {webhook_token}"}
        )

    results = []
    for wf in matching_wfs:
        res = engine.execute_workflow(wf, payload, trigger_source="webhook")
        results.append(res)

    return {"status": "executed", "total_workflows": len(results), "executions": results}

@app.get("/api/logs")
async def get_execution_logs():
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

@app.get("/api/foxe/bookings")
async def get_foxe_real_bookings():
    state = engine.load_foxe_state()
    orders = state.get("orders", [])
    pipeline = state.get("pipeline_october", [])
    
    # Return 25 latest bookings
    combined = []
    for o in orders[-15:]:
        combined.append({
            "source": "Orders MTD",
            "client_name": o.get("client", "Pelanggan"),
            "paket": o.get("paket", "Graduation"),
            "tanggal_foto": o.get("tanggalFoto", o.get("tanggal", "2026-09-30")),
            "jam_foto": "11:00 WIB",
            "backdrop": "Studio 1",
            "total_paket": o.get("total", 250000),
            "dp_masuk": o.get("transfer", o.get("cash", 100000)),
            "sisa_bayar": max(0, o.get("total", 250000) - (o.get("transfer", 0) + o.get("cash", 0))),
            "phone": "081298765432",
            "admin": o.get("admin", "Admin")
        })

    for p in pipeline[:15]:
        combined.append({
            "source": "Pipeline Oktober",
            "client_name": p.get("client", "Mahasiswa Wisuda"),
            "paket": p.get("paket", "Wisuda UMP"),
            "tanggal_foto": p.get("tanggal", "2026-10-03"),
            "jam_foto": p.get("jam", "09:00 WIB"),
            "backdrop": p.get("spot", "Backdrop 1"),
            "total_paket": p.get("harga", 450000),
            "dp_masuk": p.get("dp", 100000),
            "sisa_bayar": max(0, p.get("harga", 450000) - p.get("dp", 100000)),
            "phone": p.get("phone", "081345678901"),
            "admin": "Admin Studio"
        })

    return combined

@app.get("/api/settings")
async def get_settings():
    return load_settings()

@app.post("/api/settings")
async def update_settings(settings: dict = Body(...)):
    current = load_settings()
    current.update(settings)
    save_settings(current)
    return {"status": "saved", "settings": current}

def start_server():
    uvicorn.run("foxe_flow.server:app", host="0.0.0.0", port=8765, reload=True)

if __name__ == "__main__":
    start_server()
