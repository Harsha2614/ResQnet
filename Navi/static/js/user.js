(function () {
  const gridEl = document.getElementById('grid');
  if (!gridEl) return;

  const W = +gridEl.dataset.w;
  const H = +gridEl.dataset.h;

  gridEl.style.gridTemplateColumns = `repeat(${W}, var(--cell))`;
  gridEl.style.gridTemplateRows = `repeat(${H}, var(--cell))`;

  const hazards = new Set((window.__DATA__?.hazards || []).map(h => `${h.x},${h.y}`));
  const safehouses = (window.__DATA__?.safehouses || []).map(x => ({ ...x }));
  const pois = window.__DATA__?.pois || [];

  const cells = [];
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const c = document.createElement('div');
      c.className = 'cell';
      c.dataset.x = x; c.dataset.y = y;
      gridEl.appendChild(c);
      cells.push(c);
    }
  }
  const byXY = (x, y) => cells[y * W + x];

  hazards.forEach(s => {
    const [x, y] = s.split(',').map(Number);
    const c = byXY(x, y); if (c) c.classList.add('hazard');
  });

  for (const s of safehouses) {
    const c = byXY(s.x, s.y);
    if (!c) continue;
    c.classList.add('safehouse');
    c.title = `${s.name} (avail ${s.available}/${s.capacity})`;
    const t = document.createElement('span');
    t.className = 'tag'; t.textContent = 'S';
    c.appendChild(t);
  }

  const tagMap = { house: 'H', shop: 'SH', temple: 'T', school: 'SC', park: 'P' };
  let counts = { house: 0, shop: 0, temple: 0, school: 0, park: 0 };

  for (const p of pois) {
    const c = byXY(p.x, p.y);
    if (!c) continue;
    const t = (p.type || '').toLowerCase();
    c.classList.add(t);
    c.title = `${p.name} (${t})`;
    const label = tagMap[t];
    if (label) {
      const span = document.createElement('span');
      span.className = 'tag';
      span.textContent = label;
      c.appendChild(span);
    }
    if (counts.hasOwnProperty(t)) counts[t]++;
  }

  const setText = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = String(val); };
  setText('cnt-houses', counts.house || 0);
  setText('cnt-shops', counts.shop || 0);
  setText('cnt-temples', counts.temple || 0);
  setText('cnt-schools', counts.school || 0);
  setText('cnt-parks', counts.park || 0);

  const statusEl = document.getElementById('status');
  const safeList = document.getElementById('safeList');
  const directionsEl = document.getElementById('directions');
  const btnReset = document.getElementById('btn-reset');
  const btnArrive = document.getElementById('btn-arrive');
  const btnCheckout = document.getElementById('btn-checkout');
  const groupSizeEl = document.getElementById('groupSize');

  function renderSafeList() {
    if (!safeList) return;
    safeList.innerHTML = '';
    for (const s of safehouses) {
      const li = document.createElement('li');
      li.textContent = `${s.name} @ (${s.x}, ${s.y}) — Available: ${s.available}/${s.capacity}`;
      safeList.appendChild(li);
    }
  }
  renderSafeList();

  let start = null, currentPath = null, currentSafe = null;
  let lastCheckedInSafehouseId = null;

  function clearPath() {
    cells.forEach(c => c.classList.remove('path', 'start', 'goal'));
    currentPath = null; currentSafe = null;
    if (btnArrive) btnArrive.disabled = true;
    if (directionsEl) directionsEl.textContent = '';
  }

  gridEl.addEventListener('click', async (e) => {
    const cell = e.target.closest('.cell');
    if (!cell) return;
    const x = +cell.dataset.x, y = +cell.dataset.y;

    clearPath();
    start = [x, y];
    cell.classList.add('start');
    const groupSize = Math.max(1, +groupSizeEl?.value || 1);
    if (statusEl) statusEl.textContent = 'Finding nearest safehouse with capacity...';

    // ✅ Fixed route prefix
    const resp = await fetch('/navi/api/route_to_safehouse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start, group_size: groupSize })
    });

    const r = await resp.json();

    if (!r.ok) {
      if (statusEl) statusEl.textContent = r.message || 'No route found.';
      return;
    }

    currentPath = r.path || [];
    for (const [px, py] of currentPath) {
      const c = byXY(px, py); if (c) c.classList.add('path');
    }

    currentSafe = r.safehouse;
    const goalCell = byXY(currentSafe.x, currentSafe.y);
    if (goalCell) goalCell.classList.add('goal');

    if (directionsEl) directionsEl.textContent = r.instructions || '';
    if (btnArrive) btnArrive.disabled = false;
    if (statusEl) statusEl.textContent = `Routed to ${currentSafe.name}.`;
  });

  if (btnReset) {
    btnReset.addEventListener('click', () => {
      clearPath();
      start = null;
      if (statusEl) statusEl.textContent = 'Cleared.';
    });
  }

  if (btnArrive) {
    btnArrive.addEventListener('click', async () => {
      if (!currentPath || !currentSafe || !start) {
        if (statusEl) statusEl.textContent = 'Plan a route first.';
        return;
      }
      const groupSize = Math.max(1, +groupSizeEl?.value || 1);

      // ✅ Fixed route prefix
      const r = await fetch('/navi/api/arrive', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start, path: currentPath,
          safehouse_id: currentSafe.id,
          group_size: groupSize
        })
      }).then(r => r.json());

      if (!r.ok) {
        if (statusEl) statusEl.textContent = r.message || 'Failed to check-in.';
        return;
      }

      if (statusEl) statusEl.textContent = `Checked in. Safehouse availability now ${r.available}.`;
      const s = safehouses.find(x => x.id === currentSafe.id);
      if (s) s.available = r.available;
      renderSafeList();
      if (btnArrive) btnArrive.disabled = true;

      lastCheckedInSafehouseId = currentSafe ? currentSafe.id : null;
    });
  }

  if (btnCheckout) {
    btnCheckout.addEventListener('click', async () => {
      const sid = currentSafe?.id || lastCheckedInSafehouseId;
      if (!sid) {
        if (statusEl) statusEl.textContent = 'No active check-in found to checkout.';
        return;
      }

      // ✅ Fixed route prefix
      const groupSize = Math.max(1, +groupSizeEl?.value || 1);
      const r = await fetch('/navi/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ safehouse_id: sid, group_size: groupSize })
      }).then(r => r.json());


      if (!r.ok) {
        if (statusEl) statusEl.textContent = r.message || 'Failed to checkout.';
        return;
      }

      if (statusEl) statusEl.textContent = `Checked out. Safehouse availability now ${r.available}.`;
      const s = safehouses.find(x => x.id === (r.safehouse_id || sid));
      if (s) s.available = r.available;
      renderSafeList();

      if (btnArrive) btnArrive.disabled = false;
      lastCheckedInSafehouseId = null;
    });
  }
})();
