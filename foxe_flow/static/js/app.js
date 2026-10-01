/**
 * Foxe Flow - Admin Automation Application Controller
 */

let canvas = null;
let currentWorkflow = null;
let allWorkflows = [];
let appSettings = {};
let liveBookings = [];

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize Visual Canvas
  canvas = new FlowCanvas('canvasContainer', 'canvasViewport', 'wiresSvg', {
    onSelectNode: (node) => openNodeInspector(node),
    onChange: () => { /* auto-change trigger */ },
    onZoomChange: (z) => {
      document.getElementById('lblZoom').innerText = `${Math.round(z * 100)}%`;
    }
  });

  // Load backend data
  await loadSettings();
  await loadWorkflows();
  await loadFoxeBookings();

  // Setup UI event listeners
  initUIEvents();
});

async function loadSettings() {
  try {
    const res = await fetch('/api/settings');
    appSettings = await res.json();
  } catch (e) {
    console.error('Failed to load settings', e);
  }
}

async function loadWorkflows() {
  try {
    const res = await fetch('/api/workflows');
    allWorkflows = await res.json();
    renderWorkflowSelector();
    if (allWorkflows.length > 0) {
      selectWorkflow(allWorkflows[0].id);
    }
  } catch (e) {
    console.error('Failed to load workflows', e);
  }
}

async function loadFoxeBookings() {
  try {
    const res = await fetch('/api/foxe/bookings');
    liveBookings = await res.json();
  } catch (e) {
    console.error('Failed to load bookings', e);
  }
}

function renderWorkflowSelector() {
  const sel = document.getElementById('selWorkflow');
  sel.innerHTML = '';
  allWorkflows.forEach(w => {
    const opt = document.createElement('option');
    opt.value = w.id;
    opt.textContent = w.name;
    sel.appendChild(opt);
  });
}

function selectWorkflow(wfId) {
  const wf = allWorkflows.find(w => w.id === wfId);
  if (!wf) return;
  currentWorkflow = JSON.parse(JSON.stringify(wf));
  
  document.getElementById('selWorkflow').value = wf.id;
  updateActiveToggle(wf.is_active);

  // Set canvas data
  canvas.setData(currentWorkflow.nodes, currentWorkflow.connections);
  canvas.fitView();
  closeNodeInspector();
}

function updateActiveToggle(isActive) {
  const toggle = document.getElementById('toggleActive');
  if (isActive) {
    toggle.classList.add('is-active');
    toggle.querySelector('.label').innerText = 'Otomasi Aktif';
  } else {
    toggle.classList.remove('is-active');
    toggle.querySelector('.label').innerText = 'Nonaktif';
  }
}

function initUIEvents() {
  // Workflow dropdown switch
  document.getElementById('selWorkflow').addEventListener('change', (e) => {
    selectWorkflow(e.target.value);
  });

  // Toggle active
  document.getElementById('toggleActive').addEventListener('click', async () => {
    if (!currentWorkflow) return;
    try {
      const res = await fetch(`/api/workflows/${currentWorkflow.id}/toggle`, { method: 'POST' });
      const data = await res.json();
      currentWorkflow.is_active = data.is_active;
      const targetInList = allWorkflows.find(w => w.id === currentWorkflow.id);
      if (targetInList) targetInList.is_active = data.is_active;
      updateActiveToggle(data.is_active);
    } catch (e) {
      alert('Gagal mengubah status: ' + e);
    }
  });

  // Save workflow
  document.getElementById('btnSaveWf').addEventListener('click', async () => {
    if (!currentWorkflow) return;
    const canvasData = canvas.getData();
    currentWorkflow.nodes = canvasData.nodes;
    currentWorkflow.connections = canvasData.connections;

    try {
      const res = await fetch('/api/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentWorkflow)
      });
      const data = await res.json();
      alert('✅ Alur kerja berhasil disimpan!');
      // Update in local list
      const idx = allWorkflows.findIndex(w => w.id === currentWorkflow.id);
      if (idx >= 0) allWorkflows[idx] = currentWorkflow;
      renderWorkflowSelector();
      document.getElementById('selWorkflow').value = currentWorkflow.id;
    } catch (e) {
      alert('Gagal menyimpan: ' + e);
    }
  });

  // Test Run workflow
  document.getElementById('btnTestWf').addEventListener('click', async () => {
    await runWorkflowTest();
  });

  // Zoom controls
  document.getElementById('btnZoomIn').addEventListener('click', () => {
    canvas.setZoom(canvas.zoom * 1.15);
    document.getElementById('lblZoom').innerText = `${Math.round(canvas.zoom * 100)}%`;
  });
  document.getElementById('btnZoomOut').addEventListener('click', () => {
    canvas.setZoom(canvas.zoom * 0.85);
    document.getElementById('lblZoom').innerText = `${Math.round(canvas.zoom * 100)}%`;
  });
  document.getElementById('btnZoomReset').addEventListener('click', () => {
    canvas.fitView();
    document.getElementById('lblZoom').innerText = `${Math.round(canvas.zoom * 100)}%`;
  });

  // Left palette items click or drag
  const paletteItems = document.querySelectorAll('.palette-item');
  paletteItems.forEach(item => {
    item.addEventListener('click', () => {
      const type = item.getAttribute('data-type');
      // Place near center of viewport
      const cx = (-canvas.pan.x + 400) / canvas.zoom;
      const cy = (-canvas.pan.y + 250) / canvas.zoom;
      canvas.addNode(type, { x: Math.round(cx), y: Math.round(cy) });
    });
  });

  // Drawer toggle
  document.getElementById('btnToggleLogs').addEventListener('click', () => {
    const drawer = document.getElementById('execDrawer');
    drawer.classList.toggle('collapsed');
  });

  // Webhook modal
  document.getElementById('btnOpenWebhook').addEventListener('click', () => {
    openWebhookModal();
  });

  // Studio booking modal
  document.getElementById('btnOpenBookings').addEventListener('click', () => {
    openBookingPickerModal();
  });

  // Settings modal
  document.getElementById('btnOpenSettings').addEventListener('click', () => {
    openSettingsModal();
  });

  // Close modals
  document.querySelectorAll('.btn-close-modal').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
    });
  });
}

async function runWorkflowTest(customPayload = null) {
  if (!currentWorkflow) return;

  // Make sure current canvas state is synced
  const canvasData = canvas.getData();
  currentWorkflow.nodes = canvasData.nodes;
  currentWorkflow.connections = canvasData.connections;

  // Save first
  await fetch('/api/workflows', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(currentWorkflow)
  });

  // Open drawer
  const drawer = document.getElementById('execDrawer');
  drawer.classList.remove('collapsed');

  const timeline = document.getElementById('execTimeline');
  const preview = document.getElementById('execPreview');
  timeline.innerHTML = '<div style="padding:10px; color:#94a3b8">Menjalankan simulasi alur kerja...</div>';
  preview.innerHTML = '// Menunggu eksekusi...';

  try {
    const res = await fetch(`/api/workflows/${currentWorkflow.id}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(customPayload || {})
    });
    const result = await res.json();

    // Trigger visual animation on canvas nodes
    canvas.animateExecution(result.executed_nodes || [], result.status === 'completed');

    // Render timeline
    timeline.innerHTML = '';
    result.steps.forEach((step, i) => {
      const stepDiv = document.createElement('div');
      stepDiv.className = `timeline-step ${step.status}`;
      stepDiv.innerHTML = `
        <div class="step-top">
          <span>${i + 1}. ${step.node_name}</span>
          <span style="font-family:var(--font-mono); font-size:10px; color:#94a3b8">${step.duration_ms}ms</span>
        </div>
        <div class="step-desc">${step.message}</div>
      `;
      timeline.appendChild(stepDiv);
    });

    // Render preview JSON
    preview.innerHTML = JSON.stringify(result, null, 2);
  } catch (e) {
    timeline.innerHTML = `<div class="timeline-step error">Gagal menjalankan eksekusi: ${e}</div>`;
  }
}

/* NODE INSPECTOR (RIGHT SIDEBAR) */
function openNodeInspector(node) {
  const inspector = document.getElementById('sidebarInspector');
  inspector.style.display = 'flex';

  document.getElementById('inspTitle').innerText = node.name;
  document.getElementById('inspNodeName').value = node.name;

  const content = document.getElementById('inspDynamicFields');
  content.innerHTML = '';

  const params = node.parameters || {};

  if (node.type === 'webhook_trigger') {
    content.innerHTML = `
      <div class="field-group">
        <label class="field-label">Webhook Token / Path</label>
        <input type="text" id="p_webhook_token" class="field-input" value="${params.webhook_token || 'foxe-booking-hook'}">
        <div style="font-size:10px; color:#64748b; margin-top:2px;">URL Endpoint: http://localhost:8765/api/webhook/<span id="lblWebhookTokenPreview">${params.webhook_token || 'foxe-booking-hook'}</span></div>
      </div>
    `;
    document.getElementById('p_webhook_token').addEventListener('input', (e) => {
      document.getElementById('lblWebhookTokenPreview').innerText = e.target.value;
    });
  } else if (node.type === 'foxe_booking_trigger') {
    content.innerHTML = `
      <div class="field-group">
        <label class="field-label">Pemicu Event Studio</label>
        <select id="p_trigger_type" class="field-select">
          <option value="booking_baru" ${params.trigger_type === 'booking_baru' ? 'selected' : ''}>Booking Baru Masuk</option>
          <option value="dp_masuk" ${params.trigger_type === 'dp_masuk' ? 'selected' : ''}>Pembayaran DP Terverifikasi</option>
          <option value="h1_reminder" ${params.trigger_type === 'h1_reminder' ? 'selected' : ''}>Reminder H-1 Sesi Foto</option>
          <option value="pelunasan" ${params.trigger_type === 'pelunasan' ? 'selected' : ''}>Pelunasan Kasir Selesai</option>
        </select>
      </div>
      <div style="font-size:11px; color:#94a3b8; background:rgba(0,0,0,0.2); padding:8px; border-radius:6px;">
        📌 Mengambil data langsung dari file log & jadwal live Foxe Studio (163 booking pipeline & orders MTD).
      </div>
    `;
  } else if (node.type === 'filter_if') {
    content.innerHTML = `
      <div class="field-group">
        <label class="field-label">Nama Variabel yang Diuji</label>
        <input type="text" id="p_field" class="field-input" value="${params.field || 'dp_masuk'}">
      </div>
      <div class="field-group">
        <label class="field-label">Operator Kondisi</label>
        <select id="p_operator" class="field-select">
          <option value=">" ${params.operator === '>' ? 'selected' : ''}>Lebih Besar (>)</option>
          <option value=">=" ${params.operator === '>=' ? 'selected' : ''}>Lebih Besar Sama Dengan (>=)</option>
          <option value="==" ${params.operator === '==' ? 'selected' : ''}>Sama Dengan (==)</option>
          <option value="!=" ${params.operator === '!=' ? 'selected' : ''}>Tidak Sama Dengan (!=)</option>
          <option value="contains" ${params.operator === 'contains' ? 'selected' : ''}>Mengandung Teks (contains)</option>
          <option value="is_not_empty" ${params.operator === 'is_not_empty' ? 'selected' : ''}>Tidak Kosong</option>
        </select>
      </div>
      <div class="field-group">
        <label class="field-label">Nilai Target</label>
        <input type="text" id="p_value" class="field-input" value="${params.value || '0'}">
      </div>
      <div style="font-size:11px; color:#10b981; margin-top:4px;">
        💡 Jika kondisi terpenuhi, sinyal dikirim ke port <b>True</b> (hijau). Jika tidak, ke <b>False</b> (merah).
      </div>
    `;
  } else if (node.type === 'set_transform') {
    content.innerHTML = `
      <div class="field-group">
        <label class="field-label">Template Pesan WhatsApp</label>
        <textarea id="p_message_template" class="field-textarea">${params.message_template || ''}</textarea>
        <div style="font-size:10px; color:#94a3b8; margin-top:2px;">Klik tag untuk menyisipkan variabel:</div>
        <div class="tag-suggestions" id="tagSuggestions">
          <span class="tag-badge" data-tag="{{client_name}}">+ {{client_name}}</span>
          <span class="tag-badge" data-tag="{{phone}}">+ {{phone}}</span>
          <span class="tag-badge" data-tag="{{paket}}">+ {{paket}}</span>
          <span class="tag-badge" data-tag="{{tanggal_foto}}">+ {{tanggal_foto}}</span>
          <span class="tag-badge" data-tag="{{jam_foto}}">+ {{jam_foto}}</span>
          <span class="tag-badge" data-tag="{{backdrop}}">+ {{backdrop}}</span>
          <span class="tag-badge" data-tag="{{rupiah(total_paket)}}">+ {{rupiah(total_paket)}}</span>
          <span class="tag-badge" data-tag="{{rupiah(dp_masuk)}}">+ {{rupiah(dp_masuk)}}</span>
          <span class="tag-badge" data-tag="{{rupiah(sisa_bayar)}}">+ {{rupiah(sisa_bayar)}}</span>
          <span class="tag-badge" data-tag="{{admin}}">+ {{admin}}</span>
        </div>
      </div>
    `;

    // Click tags to append to textarea
    const tags = content.querySelectorAll('.tag-badge');
    const txtArea = document.getElementById('p_message_template');
    tags.forEach(t => {
      t.addEventListener('click', () => {
        const tagText = t.getAttribute('data-tag');
        const start = txtArea.selectionStart;
        const end = txtArea.selectionEnd;
        txtArea.value = txtArea.value.substring(0, start) + tagText + txtArea.value.substring(end);
        txtArea.focus();
        txtArea.selectionStart = txtArea.selectionEnd = start + tagText.length;
      });
    });
  } else if (node.type === 'fonnte_whatsapp') {
    const isSim = params.is_simulation !== false;
    content.innerHTML = `
      <div class="field-group">
        <label class="field-label">Fonnte API Token</label>
        <input type="text" id="p_token" class="field-input" placeholder="Masukkan token Fonnte Anda" value="${params.token || appSettings.fonnte_token || ''}">
      </div>
      <div class="field-group">
        <label class="field-label">Target Nomor WhatsApp</label>
        <input type="text" id="p_target_phone" class="field-input" value="${params.target_phone || '{{phone}}'}">
      </div>
      <div class="field-group">
        <label class="field-label">Isi Pesan</label>
        <textarea id="p_message" class="field-textarea" style="min-height:90px;">${params.message || '{{rendered_message}}'}</textarea>
      </div>
      <div class="field-group">
        <label class="field-label">URL Lampiran Gambar / Invoice (Opsional)</label>
        <input type="text" id="p_file_url" class="field-input" placeholder="https://..." value="${params.file_url || ''}">
      </div>
      <div class="field-group" style="flex-direction:row; align-items:center; justify-content:space-between; background:rgba(0,0,0,0.2); padding:8px 10px; border-radius:6px;">
        <div>
          <div style="font-size:11px; font-weight:600; color:#fff">Mode Simulasi (Mock Send)</div>
          <div style="font-size:10px; color:#94a3b8">Uji alur tanpa memotong kuota pesan Fonnte</div>
        </div>
        <input type="checkbox" id="p_is_simulation" ${isSim ? 'checked' : ''} style="width:16px; height:16px;">
      </div>
    `;
  } else if (node.type === 'telegram_bot') {
    content.innerHTML = `
      <div class="field-group">
        <label class="field-label">Bot Token Telegram</label>
        <input type="text" id="p_token" class="field-input" value="${params.token || '8809193335:AAER1t9MAnVSyIRJSWqHpFwaoFe4hYmcZ1s'}">
      </div>
      <div class="field-group">
        <label class="field-label">Chat ID Admin / Channel</label>
        <input type="text" id="p_chat_id" class="field-input" value="${params.chat_id || '1608969830'}">
      </div>
      <div class="field-group">
        <label class="field-label">Format Pesan (HTML)</label>
        <textarea id="p_message" class="field-textarea" style="min-height:90px;">${params.message || '🔔 <b>Update Otomasi Studio</b>\n{{rendered_message}}'}</textarea>
      </div>
    `;
  }

  // Save changes to current node
  document.getElementById('btnSaveNodeParams').onclick = () => {
    node.name = document.getElementById('inspNodeName').value;
    
    // Gather dynamic params
    if (node.type === 'webhook_trigger') {
      node.parameters.webhook_token = document.getElementById('p_webhook_token').value;
    } else if (node.type === 'foxe_booking_trigger') {
      node.parameters.trigger_type = document.getElementById('p_trigger_type').value;
    } else if (node.type === 'filter_if') {
      node.parameters.field = document.getElementById('p_field').value;
      node.parameters.operator = document.getElementById('p_operator').value;
      node.parameters.value = document.getElementById('p_value').value;
    } else if (node.type === 'set_transform') {
      node.parameters.message_template = document.getElementById('p_message_template').value;
    } else if (node.type === 'fonnte_whatsapp') {
      node.parameters.token = document.getElementById('p_token').value;
      node.parameters.target_phone = document.getElementById('p_target_phone').value;
      node.parameters.message = document.getElementById('p_message').value;
      node.parameters.file_url = document.getElementById('p_file_url').value;
      node.parameters.is_simulation = document.getElementById('p_is_simulation').checked;
    } else if (node.type === 'telegram_bot') {
      node.parameters.token = document.getElementById('p_token').value;
      node.parameters.chat_id = document.getElementById('p_chat_id').value;
      node.parameters.message = document.getElementById('p_message').value;
    }

    canvas.render();
    canvas.selectNode(node.id);
    alert('Parameter node diperbarui!');
  };

  // Delete node
  document.getElementById('btnDeleteNode').onclick = () => {
    if (confirm(`Hapus node "${node.name}"?`)) {
      canvas.removeNode(node.id);
      closeNodeInspector();
    }
  };
}

function closeNodeInspector() {
  document.getElementById('sidebarInspector').style.display = 'none';
}

/* MODALS */
function openWebhookModal() {
  const modal = document.getElementById('modalWebhook');
  modal.classList.add('active');

  const token = (currentWorkflow && currentWorkflow.webhook_token) || 'foxe-booking-hook';
  const url = `${window.location.origin}/api/webhook/${token}`;
  document.getElementById('txtWebhookUrl').innerText = url;

  document.getElementById('codeCurl').innerText = `curl -X POST "${url}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_name": "Denny Hardiansyah",
    "phone": "081234567890",
    "paket": "Graduation Super Peak",
    "tanggal_foto": "2026-10-03",
    "jam_foto": "10:00 WIB",
    "backdrop": "Backdrop 1",
    "total_paket": 350000,
    "dp_masuk": 100000,
    "sisa_bayar": 250000,
    "admin": "AMEL"
  }'`;
}

function openBookingPickerModal() {
  const modal = document.getElementById('modalBookings');
  modal.classList.add('active');

  const list = document.getElementById('listLiveBookings');
  list.innerHTML = '';

  if (!liveBookings.length) {
    list.innerHTML = '<div style="padding:16px; color:#94a3b8">Belum ada booking tersinkron di state studio.</div>';
    return;
  }

  liveBookings.forEach((b, i) => {
    const item = document.createElement('div');
    item.className = 'palette-item';
    item.style.marginBottom = '8px';
    item.innerHTML = `
      <div class="icon" style="background:#ea580c">📸</div>
      <div class="info">
        <div class="name">${b.client_name} (${b.paket})</div>
        <div class="desc">${b.tanggal_foto} · DP: Rp ${parseInt(b.dp_masuk).toLocaleString('id-ID')} · ${b.source}</div>
      </div>
      <button class="btn btn-primary btn-sm">Gunakan Untuk Tes</button>
    `;

    item.querySelector('button').addEventListener('click', () => {
      modal.classList.remove('active');
      runWorkflowTest(b);
    });

    list.appendChild(item);
  });
}

function openSettingsModal() {
  const modal = document.getElementById('modalSettings');
  modal.classList.add('active');

  document.getElementById('cfgFonnteToken').value = appSettings.fonnte_token || '';
  document.getElementById('cfgTgToken').value = appSettings.telegram_token || '8809193335:AAER1t9MAnVSyIRJSWqHpFwaoFe4hYmcZ1s';
  document.getElementById('cfgTgChatId').value = appSettings.telegram_chat_id || '1608969830';

  document.getElementById('btnSaveSettings').onclick = async () => {
    appSettings.fonnte_token = document.getElementById('cfgFonnteToken').value;
    appSettings.telegram_token = document.getElementById('cfgTgToken').value;
    appSettings.telegram_chat_id = document.getElementById('cfgTgChatId').value;

    await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appSettings)
    });

    modal.classList.remove('active');
    alert('Pengaturan gateway berhasil disimpan!');
  };
}
