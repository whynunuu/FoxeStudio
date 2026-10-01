/**
 * Foxe Flow - Interactive Visual Canvas Engine
 * Draggable nodes, bezier curve SVG wires, interactive port connections, zoom & pan.
 */

class FlowCanvas {
  constructor(containerId, viewportId, svgId, options = {}) {
    this.container = document.getElementById(containerId);
    this.viewport = document.getElementById(viewportId);
    this.svg = document.getElementById(svgId);
    this.options = options;

    this.nodes = [];
    this.connections = [];
    this.selectedNodeId = null;

    // Viewport pan & zoom state
    this.pan = { x: 40, y: 40 };
    this.zoom = 1.0;
    this.isPanning = false;
    this.panStart = { x: 0, y: 0 };

    // Node dragging state
    this.draggingNode = null;
    this.dragOffset = { x: 0, y: 0 };

    // Port wire connection dragging state
    this.connectingFrom = null; // { nodeId, handle, startPos }
    this.tempWirePath = null;

    this.initEvents();
    this.applyTransform();
  }

  setData(nodes, connections) {
    this.nodes = JSON.parse(JSON.stringify(nodes || []));
    this.connections = JSON.parse(JSON.stringify(connections || []));
    this.render();
  }

  getData() {
    return {
      nodes: this.nodes,
      connections: this.connections
    };
  }

  initEvents() {
    // Canvas background panning
    this.container.addEventListener('mousedown', (e) => {
      if (e.target === this.container || e.target === this.svg || e.target.classList.contains('wires-svg')) {
        this.isPanning = true;
        this.panStart = { x: e.clientX - this.pan.x, y: e.clientY - this.pan.y };
        this.container.style.cursor = 'grabbing';
      }
    });

    window.addEventListener('mousemove', (e) => {
      // 1. Viewport panning
      if (this.isPanning) {
        this.pan.x = e.clientX - this.panStart.x;
        this.pan.y = e.clientY - this.panStart.y;
        this.applyTransform();
        return;
      }

      // 2. Node dragging
      if (this.draggingNode) {
        const mouseX = (e.clientX - this.pan.x) / this.zoom;
        const mouseY = (e.clientY - this.pan.y) / this.zoom;
        this.draggingNode.position.x = Math.round(mouseX - this.dragOffset.x);
        this.draggingNode.position.y = Math.round(mouseY - this.dragOffset.y);

        const el = document.getElementById(`node-${this.draggingNode.id}`);
        if (el) {
          el.style.left = `${this.draggingNode.position.x}px`;
          el.style.top = `${this.draggingNode.position.y}px`;
        }
        this.renderWires();
        return;
      }

      // 3. Port wire connection dragging (rubberband line)
      if (this.connectingFrom) {
        const mouseX = (e.clientX - this.pan.x) / this.zoom;
        const mouseY = (e.clientY - this.pan.y) / this.zoom;
        this.updateTempWire(this.connectingFrom.startPos.x, this.connectingFrom.startPos.y, mouseX, mouseY);
      }
    });

    window.addEventListener('mouseup', (e) => {
      if (this.isPanning) {
        this.isPanning = false;
        this.container.style.cursor = 'crosshair';
      }
      if (this.draggingNode) {
        this.draggingNode = null;
      }
      if (this.connectingFrom) {
        this.cancelConnecting();
      }
    });

    // Zoom via mouse wheel
    this.container.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
      const newZoom = Math.min(Math.max(this.zoom * zoomFactor, 0.4), 2.2);

      // Zoom towards mouse
      const rect = this.container.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      this.pan.x = mouseX - (mouseX - this.pan.x) * (newZoom / this.zoom);
      this.pan.y = mouseY - (mouseY - this.pan.y) * (newZoom / this.zoom);
      this.zoom = newZoom;

      this.applyTransform();
      if (this.options.onZoomChange) this.options.onZoomChange(this.zoom);
    }, { passive: false });
  }

  applyTransform() {
    this.viewport.style.transform = `translate(${this.pan.x}px, ${this.pan.y}px) scale(${this.zoom})`;
  }

  setZoom(val) {
    this.zoom = Math.min(Math.max(val, 0.4), 2.0);
    this.applyTransform();
  }

  fitView() {
    if (!this.nodes.length) {
      this.pan = { x: 50, y: 50 };
      this.zoom = 1.0;
      this.applyTransform();
      return;
    }
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    this.nodes.forEach(n => {
      minX = Math.min(minX, n.position.x);
      minY = Math.min(minY, n.position.y);
      maxX = Math.max(maxX, n.position.x + 240);
      maxY = Math.max(maxY, n.position.y + 140);
    });

    const pad = 60;
    this.pan.x = pad - minX;
    this.pan.y = pad - minY;
    this.zoom = 1.0;
    this.applyTransform();
  }

  render() {
    this.renderNodes();
    this.renderWires();
  }

  renderNodes() {
    // Clear existing rendered nodes
    const existingDomNodes = this.viewport.querySelectorAll('.flow-node');
    existingDomNodes.forEach(el => el.remove());

    this.nodes.forEach(node => {
      const el = this.createNodeElement(node);
      this.viewport.appendChild(el);
    });
  }

  createNodeElement(node) {
    const el = document.createElement('div');
    el.className = `flow-node ${this.selectedNodeId === node.id ? 'selected' : ''}`;
    el.id = `node-${node.id}`;
    el.style.left = `${node.position.x}px`;
    el.style.top = `${node.position.y}px`;

    // Type metadata
    const meta = this.getNodeMeta(node.type);

    // Build ports
    let portsHtml = '';
    // Input port (except triggers)
    if (!node.type.includes('trigger')) {
      portsHtml += `<div class="port port-input" data-node="${node.id}" data-handle="input" title="Input"></div>`;
    }

    // Output port(s)
    if (node.type === 'filter_if') {
      portsHtml += `
        <div class="port port-true" data-node="${node.id}" data-handle="true" title="Jika Benar (True)"></div>
        <span class="port-label label-true">True</span>
        <div class="port port-false" data-node="${node.id}" data-handle="false" title="Jika Salah (False)"></div>
        <span class="port-label label-false">False</span>
      `;
    } else {
      portsHtml += `<div class="port port-output" data-node="${node.id}" data-handle="output" title="Output"></div>`;
    }

    // Param preview snippet
    let previewText = '';
    const p = node.parameters || {};
    if (node.type === 'webhook_trigger') previewText = `/api/webhook/${p.webhook_token || 'hook'}`;
    else if (node.type === 'filter_if') previewText = `IF ${p.field || 'dp'} ${p.operator || '>'} ${p.value || '0'}`;
    else if (node.type === 'fonnte_whatsapp') previewText = `Kirim WA ke: ${p.target_phone || 'Client'}`;
    else if (node.type === 'telegram_bot') previewText = `Alert Chat: ${p.chat_id || 'Admin'}`;
    else if (node.type === 'set_transform') previewText = `Format Template WhatsApp`;
    else if (node.type === 'foxe_booking_trigger') previewText = `Sinkron Studio Live`;

    el.innerHTML = `
      ${portsHtml}
      <div class="node-header" style="background: ${meta.headerBg || '#182232'}">
        <div class="node-icon" style="background: ${meta.color}">${meta.icon}</div>
        <div class="node-title-group">
          <div class="node-title">${node.name}</div>
          <div class="node-category">${meta.category}</div>
        </div>
      </div>
      <div class="node-body">
        <div style="font-size:11px; color:#cbd5e1">${meta.desc}</div>
        ${previewText ? `<div class="node-param-preview">${previewText}</div>` : ''}
      </div>
    `;

    // Click to select node
    el.addEventListener('mousedown', (e) => {
      // Don't drag if clicking port
      if (e.target.classList.contains('port')) return;

      this.selectNode(node.id);

      // Start drag
      this.draggingNode = node;
      const mouseX = (e.clientX - this.pan.x) / this.zoom;
      const mouseY = (e.clientY - this.pan.y) / this.zoom;
      this.dragOffset = {
        x: mouseX - node.position.x,
        y: mouseY - node.position.y
      };
      e.stopPropagation();
    });

    // Port drag wire event
    const outputPorts = el.querySelectorAll('.port-output, .port-true, .port-false');
    outputPorts.forEach(port => {
      port.addEventListener('mousedown', (e) => {
        e.stopPropagation();
        const handle = port.getAttribute('data-handle');
        const startPos = this.getPortPosition(node.id, handle);
        this.connectingFrom = { nodeId: node.id, handle, startPos };
        this.createTempWire(startPos.x, startPos.y);
      });
    });

    // Port drop wire event
    const inputPorts = el.querySelectorAll('.port-input');
    inputPorts.forEach(port => {
      port.addEventListener('mouseup', (e) => {
        if (this.connectingFrom && this.connectingFrom.nodeId !== node.id) {
          e.stopPropagation();
          const targetHandle = port.getAttribute('data-handle');
          this.addConnection(this.connectingFrom.nodeId, this.connectingFrom.handle, node.id, targetHandle);
          this.cancelConnecting();
        }
      });
    });

    return el;
  }

  selectNode(nodeId) {
    this.selectedNodeId = nodeId;
    const all = this.viewport.querySelectorAll('.flow-node');
    all.forEach(el => el.classList.remove('selected'));
    const target = document.getElementById(`node-${nodeId}`);
    if (target) target.classList.add('selected');

    if (this.options.onSelectNode) {
      const nodeObj = this.nodes.find(n => n.id === nodeId);
      this.options.onSelectNode(nodeObj);
    }
  }

  addNode(type, position) {
    const meta = this.getNodeMeta(type);
    const newId = `node_${Date.now()}`;
    const newNode = {
      id: newId,
      name: meta.title,
      type: type,
      position: position || { x: 300, y: 250 },
      parameters: JSON.parse(JSON.stringify(meta.defaultParams || {}))
    };
    this.nodes.push(newNode);
    this.render();
    this.selectNode(newId);
    return newNode;
  }

  removeNode(nodeId) {
    this.nodes = this.nodes.filter(n => n.id !== nodeId);
    this.connections = this.connections.filter(c => c.source !== nodeId && c.target !== nodeId);
    if (this.selectedNodeId === nodeId) this.selectedNodeId = null;
    this.render();
  }

  addConnection(source, sourceHandle, target, targetHandle) {
    // Avoid duplicates
    const exists = this.connections.some(c => 
      c.source === source && c.sourceHandle === sourceHandle && c.target === target
    );
    if (!exists) {
      this.connections.push({
        id: `conn_${Date.now()}`,
        source,
        sourceHandle: sourceHandle || 'output',
        target,
        targetHandle: targetHandle || 'input'
      });
      this.renderWires();
      if (this.options.onChange) this.options.onChange();
    }
  }

  removeConnection(connId) {
    this.connections = this.connections.filter(c => c.id !== connId);
    this.renderWires();
    if (this.options.onChange) this.options.onChange();
  }

  getPortPosition(nodeId, handle) {
    const node = this.nodes.find(n => n.id === nodeId);
    if (!node) return { x: 0, y: 0 };
    const width = 240;
    const height = 110;

    let x = node.position.x;
    let y = node.position.y;

    if (handle === 'input') {
      return { x: x, y: y + height / 2 };
    } else if (handle === 'true') {
      return { x: x + width, y: y + 38 };
    } else if (handle === 'false') {
      return { x: x + width, y: y + 78 };
    } else {
      // standard output
      return { x: x + width, y: y + height / 2 };
    }
  }

  createBezierPath(x1, y1, x2, y2) {
    const dx = Math.abs(x2 - x1) * 0.5;
    const cx1 = x1 + Math.max(dx, 40);
    const cy1 = y1;
    const cx2 = x2 - Math.max(dx, 40);
    const cy2 = y2;
    return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`;
  }

  renderWires() {
    this.svg.innerHTML = '';

    this.connections.forEach(conn => {
      const start = this.getPortPosition(conn.source, conn.sourceHandle);
      const end = this.getPortPosition(conn.target, conn.targetHandle);
      const d = this.createBezierPath(start.x, start.y, end.x, end.y);

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', d);
      
      let extraClass = '';
      if (conn.sourceHandle === 'true') extraClass = 'wire-true';
      else if (conn.sourceHandle === 'false') extraClass = 'wire-false';

      path.setAttribute('class', `wire-path ${extraClass}`);
      path.setAttribute('data-id', conn.id);
      path.setAttribute('title', 'Klik untuk menghapus kabel koneksi');

      path.addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm('Hapus kabel koneksi ini?')) {
          this.removeConnection(conn.id);
        }
      });

      this.svg.appendChild(path);
    });
  }

  createTempWire(x, y) {
    if (!this.tempWirePath) {
      this.tempWirePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      this.tempWirePath.setAttribute('class', 'wire-path wire-active');
      this.svg.appendChild(this.tempWirePath);
    }
    this.updateTempWire(x, y, x, y);
  }

  updateTempWire(x1, y1, x2, y2) {
    if (this.tempWirePath) {
      const d = this.createBezierPath(x1, y1, x2, y2);
      this.tempWirePath.setAttribute('d', d);
    }
  }

  cancelConnecting() {
    this.connectingFrom = null;
    if (this.tempWirePath) {
      this.tempWirePath.remove();
      this.tempWirePath = null;
    }
  }

  animateExecution(executedNodeIds, success) {
    // Reset classes
    this.nodes.forEach(n => {
      const el = document.getElementById(`node-${n.id}`);
      if (el) el.classList.remove('executing', 'exec-success', 'exec-error');
    });

    executedNodeIds.forEach((nid, idx) => {
      setTimeout(() => {
        const el = document.getElementById(`node-${nid}`);
        if (el) {
          el.classList.add('executing');
          setTimeout(() => {
            el.classList.remove('executing');
            el.classList.add(success ? 'exec-success' : 'exec-error');
          }, 400);
        }
      }, idx * 250);
    });
  }

  getNodeMeta(type) {
    switch (type) {
      case 'webhook_trigger':
        return {
          title: 'Webhook Booking Masuk',
          category: 'Trigger',
          icon: '⚡',
          color: '#0284c7',
          headerBg: 'rgba(2, 132, 199, 0.25)',
          desc: 'Terima payload order/booking via HTTP Webhook.',
          defaultParams: { webhook_token: 'foxe-booking-hook' }
        };
      case 'foxe_booking_trigger':
        return {
          title: 'Foxe Studio Booking Live',
          category: 'Trigger',
          icon: '🦊',
          color: '#ea580c',
          headerBg: 'rgba(234, 88, 12, 0.25)',
          desc: 'Sinkronisasi riil dari database jadwal Foxe Studio.',
          defaultParams: { trigger_type: 'booking_baru' }
        };
      case 'manual_trigger':
        return {
          title: 'Trigger Manual / Test',
          category: 'Trigger',
          icon: '▶',
          color: '#3b82f6',
          headerBg: 'rgba(59, 130, 246, 0.25)',
          desc: 'Jalankan flow secara manual dari antarmuka.',
          defaultParams: {}
        };
      case 'filter_if':
        return {
          title: 'Filter (IF / Else)',
          category: 'Logic',
          icon: '⚖️',
          color: '#8b5cf6',
          headerBg: 'rgba(139, 92, 246, 0.25)',
          desc: 'Evaluasi kondisi & pecah jalur True / False.',
          defaultParams: { field: 'dp_masuk', operator: '>', value: '0' }
        };
      case 'set_transform':
        return {
          title: 'Format Template Pesan',
          category: 'Transform',
          icon: '📝',
          color: '#f59e0b',
          headerBg: 'rgba(245, 158, 11, 0.25)',
          desc: 'Susun template pesan & format rupiah variabel.',
          defaultParams: {
            message_template: 'Halo Kak *{{client_name}}*! ✨\nBooking paket {{paket}} di Foxe Studio pada {{tanggal_foto}} ({{jam_foto}}) telah kami terima.\nDP Masuk: Rp {{rupiah(dp_masuk)}}.\nSampai jumpa di studio! 📸'
          }
        };
      case 'fonnte_whatsapp':
        return {
          title: 'Kirim WhatsApp Fonnte',
          category: 'Action',
          icon: '💬',
          color: '#25d366',
          headerBg: 'rgba(37, 211, 102, 0.25)',
          desc: 'Kirim pesan WA otomatis via Fonnte Gateway.',
          defaultParams: {
            token: 'FONNTE_TOKEN_ANDA',
            target_phone: '{{phone}}',
            message: '{{rendered_message}}',
            is_simulation: true
          }
        };
      case 'telegram_bot':
        return {
          title: 'Notif Telegram Admin',
          category: 'Action',
          icon: '📢',
          color: '#0088cc',
          headerBg: 'rgba(0, 136, 204, 0.25)',
          desc: 'Kirim notifikasi ringkasan ke Telegram Studio.',
          defaultParams: {
            token: '8809193335:AAER1t9MAnVSyIRJSWqHpFwaoFe4hYmcZ1s',
            chat_id: '1608969830',
            message: '🔔 <b>Update Otomasi Studio</b>\n{{rendered_message}}'
          }
        };
      case 'delay':
        return {
          title: 'Delay / Jeda Waktu',
          category: 'Logic',
          icon: '⏳',
          color: '#64748b',
          headerBg: 'rgba(100, 116, 139, 0.25)',
          desc: 'Menunda eksekusi beberapa detik/menit.',
          defaultParams: { seconds: 2 }
        };
      default:
        return {
          title: 'Custom Node',
          category: 'Node',
          icon: '📦',
          color: '#64748b',
          headerBg: '#1e293b',
          desc: 'Custom node workflow.',
          defaultParams: {}
        };
    }
  }
}
