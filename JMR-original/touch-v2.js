'use strict';
(() => {
  const J = window.JMR, I = J.input, surface = document.getElementById('screenSurface');
  const pointers = new Map(), THRESHOLD = 13;
  let sequence = 0;
  function capture(el,e) { try { el.setPointerCapture(e.pointerId); } catch (_) {} }
  function stop(e) { if (e.cancelable) e.preventDefault(); e.stopPropagation(); }
  function screenDown(e) {
    if (!J.active || (e.pointerType === 'mouse' && e.button !== 0) || e.target.closest('button')) return;
    stop(e); capture(surface,e);
    pointers.set(e.pointerId,{kind:'screen',x:e.clientX,y:e.clientY,time:performance.now(),moving:false,source:'screen:'+(++sequence)});
  }
  function screenMove(e) {
    const p = pointers.get(e.pointerId); if (!p || p.kind !== 'screen') return;
    stop(e); const dx=e.clientX-p.x, dy=e.clientY-p.y;
    if (Math.hypot(dx,dy)>THRESHOLD) p.moving=true;
    if (p.moving) I.set(p.source,J.direction(dx,dy,THRESHOLD));
  }
  function end(e,cancelled=false) {
    const p = pointers.get(e.pointerId); if (!p) return;
    pointers.delete(e.pointerId); stop(e);
    if (p.kind === 'screen') {
      I.release(p.source);
      const distance = Math.hypot(e.clientX-p.x,e.clientY-p.y);
      if (!cancelled && !p.moving && distance<=THRESHOLD && performance.now()-p.time<400) J.fire();
    } else if (p.kind === 'key' && !cancelled) {
      const remaining=90-(performance.now()-p.time);
      remaining>0 ? I.pulse(p.key,remaining,p.source) : I.release(p.source);
    } else I.release(p.source);
  }
  surface.addEventListener('pointerdown',screenDown,true);
  surface.addEventListener('pointermove',screenMove,true);
  surface.addEventListener('pointerup',e=>end(e),true);
  for (const event of ['pointercancel','lostpointercapture']) surface.addEventListener(event,e=>end(e,true),true);
  surface.addEventListener('contextmenu',e=>e.preventDefault());
  surface.addEventListener('dragstart',e=>e.preventDefault());
  const pad=document.getElementById('dpad');
  function padMove(e) {
    const p=pointers.get(e.pointerId); if (!p || p.kind!=='pad') return;
    stop(e); const r=pad.getBoundingClientRect();
    I.set(p.source,J.direction(e.clientX-r.left-r.width/2,e.clientY-r.top-r.height/2,r.width*.16));
  }
  pad.addEventListener('pointerdown',e=>{
    if (!J.active || (e.pointerType==='mouse' && e.button!==0)) return;
    stop(e); capture(pad,e); pointers.set(e.pointerId,{kind:'pad',source:'pad:'+(++sequence)});padMove(e);
  });
  pad.addEventListener('pointermove',padMove);
  pad.addEventListener('pointerup',e=>end(e));
  for(const event of ['pointercancel','lostpointercapture'])pad.addEventListener(event,e=>end(e,true));
  for(const b of document.querySelectorAll('.key[data-key]')) {
    b.addEventListener('pointerdown',e=>{
      if(!J.active || (e.pointerType==='mouse' && e.button!==0))return;
      stop(e); capture(b,e);
      const p={kind:'key',key:+b.dataset.key,time:performance.now(),source:'button:'+(++sequence)};
      pointers.set(e.pointerId,p);I.set(p.source,[p.key]);
    });
    b.addEventListener('pointerup',e=>end(e));
    for(const event of ['pointercancel','lostpointercapture'])b.addEventListener(event,e=>end(e,true));
    b.addEventListener('click',e=>{if(e.detail===0&&J.active)I.pulse(+b.dataset.key,100);});
  }
  document.getElementById('buttonB').addEventListener('click',e=>{e.preventDefault();J.toggleB();});
  window.addEventListener('pointerup',e=>end(e));
  window.addEventListener('pointercancel',e=>end(e,true));
  J.clearPointers=()=>pointers.clear();
})();
