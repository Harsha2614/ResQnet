(function () {
  const grid = document.getElementById('adminGrid');
  if (!grid) return;

  const W = +grid.dataset.w, H = +grid.dataset.h;

  grid.style.gridTemplateColumns = `repeat(${W}, var(--cell))`;
  grid.style.gridTemplateRows = `repeat(${H}, var(--cell))`;

  const data = window.__ADMIN__ || { hazards: [], safehouses: [], pois: [] };

  const cells = [];
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const c = document.createElement('div');
      c.className = 'cell';
      c.dataset.x = x; c.dataset.y = y;
      grid.appendChild(c);
      cells.push(c);
    }
  }
  const byXY = (x, y) => cells[y * W + x];

  const hazardsSet = new Set(data.hazards.filter(h => h.active !== false).map(h => `${h.x},${h.y}`));

  function paintHazards() {
    cells.forEach(c => c.classList.remove('hazard'));
    hazardsSet.forEach(key => {
      const [x, y] = key.split(',').map(Number);
      const c = byXY(x, y);
      if (c) c.classList.add('hazard');
    });
    const ul = document.getElementById('hzList');
    if (ul) {
      ul.innerHTML = '';
      hazardsSet.forEach(k => {
        const li = document.createElement('li');
        li.textContent = `(${k})`;
        ul.appendChild(li);
      });
    }
  }

  function paintSafehouses() {
    for (const s of data.safehouses) {
      const c = byXY(s.x, s.y);
      if (c) c.classList.add('safehouse');
    }
  }

  function paintPOIs() {
    for (const p of (data.pois || [])) {
      const c = byXY(p.x, p.y);
      if (c) c.classList.add(p.type);
    }
  }

  paintSafehouses();
  paintPOIs();
  paintHazards();

  // ✅ FIXED: Correct prefixed route
  grid.addEventListener('click', async (e) => {
    const cell = e.target.closest('.cell');
    if (!cell) return;
    const x = +cell.dataset.x, y = +cell.dataset.y;
    const r = await fetch('/navi/admin/api/toggle_hazard', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x, y })
    }).then(r => r.json());
    if (r.ok) {
      const key = `${x},${y}`;
      if (r.active) hazardsSet.add(key);
      else hazardsSet.delete(key);
      paintHazards();
    }
  });

  document.querySelectorAll('#shList li').forEach(li => {
    const id = +li.dataset.id;

    // ✅ FIXED: Correct prefixed route
    li.querySelector('.setCap').onclick = async () => {
      const val = +li.querySelector('.cap').value;
      const r = await fetch('/navi/admin/api/set_capacity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ safehouse_id: id, capacity: val })
      }).then(r => r.json());
      if (r.ok) {
        li.querySelector('.occ').textContent = r.occupied;
        li.querySelector('.avail').textContent = r.available;
      }
    };

    // ✅ FIXED: Correct prefixed route
    li.querySelector('.resetSh').onclick = async () => {
      const r = await fetch('/navi/admin/api/reset_safehouse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ safehouse_id: id })
      }).then(r => r.json());
      if (r.ok) {
        li.querySelector('.occ').textContent = 0;
        li.querySelector('.avail').textContent = r.available;
      }
    };
  });
})();
