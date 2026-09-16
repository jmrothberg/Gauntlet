'use strict';
(() => {
  const J = window.JMR = { version: 'controls-v2', started: false, active: false, mode: 'original', starts: 0, resets: 0 };
  const sources = new Map(), sent = new Set(), timers = new Map();
  let serial = 0;
  J.gm = () => window.EJS_emulator && window.EJS_emulator.gameManager;
  J.events = [];
  J.drawInputs = () => {
    document.querySelectorAll('[data-dir]').forEach(e => e.classList.toggle('held', sent.has(+e.dataset.dir)));
    document.querySelectorAll('.key[data-key]').forEach(e => e.classList.toggle('held', sent.has(+e.dataset.key)));
    const b = document.getElementById('buttonB');
    if (b) { b.classList.toggle('latched', J.bLatched); b.setAttribute('aria-pressed', String(!!J.bLatched)); b.textContent = J.bLatched ? 'B ✓' : 'B'; }
    document.getElementById('inventoryStatus').textContent = J.bLatched ? 'ITEMS ON · directions select · tap B to exit' : 'Drag to move · tap or A to fire · B for items';
  };
  function sync() {
    const next = J.active ? new Set([...sources.values()].flat()) : new Set();
    for (const [a,b] of [[4,5],[6,7]]) if (next.has(a) && next.has(b)) { next.delete(a); next.delete(b); }
    const gm = J.gm();
    if (gm) for (const k of new Set([...sent,...next])) if (sent.has(k) !== next.has(k)) {
      const value = next.has(k) ? 1 : 0;
      gm.simulateInput(0, k, value);
      J.events.push({key:k, value, time:performance.now()});
      if (J.events.length > 2000) J.events.shift();
    }
    sent.clear(); if (gm) next.forEach(k => sent.add(k));
    J.drawInputs();
  }
  J.input = {
    set(source, keys) { if (keys.length && !J.active) return; keys.length ? sources.set(source, keys) : sources.delete(source); sync(); },
    release(source) { sources.delete(source); sync(); },
    pulse(key, duration = 100, source = 'pulse:' + (++serial)) {
      if (!J.active) return;
      clearTimeout(timers.get(source)); this.set(source,[key]);
      timers.set(source,setTimeout(() => { timers.delete(source); this.release(source); },duration));
    },
    clear() { timers.forEach(clearTimeout); timers.clear(); sources.clear(); J.bLatched = false; sync(); },
    snapshot() { return {active:J.active, held:[...sent], sources:[...sources], bLatched:!!J.bLatched}; }
  };
  J.setActive = value => { if (!value) { J.input.clear(); if (J.clearPointers) J.clearPointers(); } J.active = value; sync(); };
  J.toggleB = () => { if (!J.active) return; J.bLatched = !J.bLatched; J.input.set('inventory-latch', J.bLatched ? [0] : []); };
  // Directions never synthesize firing. Easier modes extend only a deliberate tap.
  J.fire = () => J.input.pulse(8, J.bLatched ? 100 : {original:100,easy:250,woke:500}[J.mode]);
  J.direction = (x,y,deadZone) => {
    if (Math.hypot(x,y) <= deadZone) return [];
    const a = [], ax = Math.abs(x), ay = Math.abs(y);
    if (ax >= ay * 0.41421356) a.push(x < 0 ? 6 : 7);
    if (ay >= ax * 0.41421356) a.push(y < 0 ? 4 : 5);
    return a;
  };
  const keyboard = {ArrowUp:4,ArrowDown:5,ArrowLeft:6,ArrowRight:7,KeyZ:8,Space:8,KeyQ:10,KeyW:11};
  for (const type of ['keydown','keyup']) window.addEventListener(type, e => {
    const key = keyboard[e.code], down = type === 'keydown';
    if (!J.active || (key === undefined && !['KeyX','Enter','Escape'].includes(e.code))) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (e.code === 'KeyX') { if (down && !e.repeat) J.toggleB(); }
    else if (e.code === 'Enter' || e.code === 'Escape') { if (down && !e.repeat && J.openMenu) J.openMenu(); }
    else J.input.set('keyboard:'+e.code, down ? [key] : []);
  }, true);
  let padSources = new Set();
  function pollPad() {
    const now = new Set();
    if (J.active && navigator.getGamepads) {
      for (const p of navigator.getGamepads()) if (p && p.mapping === 'standard') {
        const keys = [], b = i => p.buttons[i] && p.buttons[i].pressed;
        for (const [button,key] of [[0,8],[1,0],[4,10],[5,11],[12,4],[13,5],[14,6],[15,7]]) if (b(button)) keys.push(key);
        if (Math.abs(p.axes[0] || 0) > .5) keys.push(p.axes[0] < 0 ? 6 : 7);
        if (Math.abs(p.axes[1] || 0) > .5) keys.push(p.axes[1] < 0 ? 4 : 5);
        const source = 'gamepad:'+p.index; now.add(source); J.input.set(source,keys);
      }
    }
    for (const source of padSources) if (!now.has(source)) J.input.release(source);
    padSources = now; requestAnimationFrame(pollPad);
  }
  requestAnimationFrame(pollPad);
})();
