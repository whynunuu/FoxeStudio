"""Foxe Studio Keuangan - Pearl Prism Frost SPA Assembler.

Validates foxe_full_state.json and pearl_prism_template.html assets, then stamps
fresh build/sync metadata into index.html (and v2/index.html if present) atomically.
Legacy Classic UI assembly is preserved in assemble_legacy.py -> legacy.html.
"""

import json
import os
import re
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "foxe_full_state.json")
TEMPLATE_FILE = os.path.join(BASE_DIR, "pearl_prism_template.html")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")
V2_DIR = os.path.join(BASE_DIR, "v2")
ASSET_REF_RE = re.compile(r'(?:src|href)=["\'](\./assets/[^"\']+)["\']')


def _atomic_write(target_path: str, content: str) -> None:
    tmp_path = f"{target_path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp_path, target_path)


def _validate_assets(refs: list[str], root_dir: str, label: str) -> None:
    missing = []
    for rel in refs:
        norm_rel = rel[2:] if rel.startswith("./") else rel
        disk_path = os.path.join(root_dir, norm_rel)
        if not os.path.isfile(disk_path) or os.path.getsize(disk_path) <= 0:
            missing.append(rel)
    if missing:
        raise RuntimeError(f"[{label}] Missing or empty referenced frontend assets: {', '.join(missing)}")


def assemble() -> str:
    if not os.path.isfile(STATE_FILE):
        raise RuntimeError(f"State file not found: {STATE_FILE}")
    if not os.path.isfile(TEMPLATE_FILE):
        raise RuntimeError(f"Template file not found: {TEMPLATE_FILE}")

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        full_state = json.load(f)

    if not isinstance(full_state, dict) or "config" not in full_state or "orders" not in full_state:
        raise RuntimeError("Invalid foxe_full_state.json structure: missing 'config' or 'orders'.")

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template_html = f.read()

    asset_refs = sorted(set(ASSET_REF_RE.findall(template_html)))
    if not asset_refs:
        raise RuntimeError("No ./assets/... references found in pearl_prism_template.html.")
    _validate_assets(asset_refs, BASE_DIR, "root")

    sync_list = full_state.get("sync")
    first_sync = sync_list[0] if isinstance(sync_list, list) and sync_list and isinstance(sync_list[0], dict) else {}
    sync_id = str(first_sync.get("id") or "sync_init")
    build_id = str(int(time.time()))

    rendered_html = (
        template_html
        .replace("__FOXE_BUILD_ID__", build_id)
        .replace("__FOXE_SYNC_ID__", sync_id)
    )

    _atomic_write(OUTPUT_HTML, rendered_html)

    v2_updated = False
    if os.path.isdir(os.path.join(V2_DIR, "assets")):
        _validate_assets(asset_refs, V2_DIR, "v2")
        _atomic_write(os.path.join(V2_DIR, "index.html"), rendered_html)
        v2_updated = True

    suffix = " + v2/index.html" if v2_updated else ""
    print(
        f"Generated index.html{suffix} (Pearl Prism Frost SPA, build={build_id}, "
        f"sync={sync_id}, assets={len(asset_refs)} verified)."
    )
    return rendered_html


assemble()
