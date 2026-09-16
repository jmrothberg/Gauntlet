'use strict';
(() => {
  const J=window.JMR, byId=id=>document.getElementById(id), menu=byId('menu'), help=byId('helpDlg');
  J.state='loading'; J.sound=true;
  J.message=text=>{byId('status').textContent=text;byId('loadMessage').textContent=text;};
  function fit(){const r=byId('screenWrap'),w=Math.max(1,Math.min(r.clientWidth-10,(r.clientHeight-10)*102/160));byId('screenSurface').style.width=w+'px';byId('screenSurface').style.height=w*160/102+'px';}
  new ResizeObserver(fit).observe(byId('screenWrap'));window.addEventListener('resize',fit);fit();
  const descriptions={original:'Original · normal tap-to-fire',easy:'Easy · short firing burst per tap',woke:'Woke · longer firing burst per tap'};
  J.choose=value=>{
    J.mode=['original','easy','woke'].includes(value)?value:'original';
    try{localStorage.setItem('jmr-gauntlet-skill',J.mode);}catch(_){}
    document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('selected',b.dataset.mode===J.mode);b.setAttribute('aria-pressed',String(b.dataset.mode===J.mode));});
    document.querySelectorAll('.modeDescription').forEach(e=>e.textContent=descriptions[J.mode]+'. Movement never fires.');
  };
  let saved='original';try{saved=localStorage.getItem('jmr-gauntlet-skill')||saved;}catch(_){}J.choose(saved);
  document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>J.choose(b.dataset.mode)));
  J.audioContexts=()=>{
    const M=window.EJS_emulator&&window.EJS_emulator.Module, contexts=new Set();
    const al=M&&M.AL&&M.AL.currentCtx;
    if(al){if(al.ctx)contexts.add(al.ctx);if(al.sources)Object.values(al.sources).forEach(s=>{if(s&&s.gain)contexts.add(s.gain.context);});}
    if(M&&M.SDL2&&M.SDL2.audioContext)contexts.add(M.SDL2.audioContext);
    return [...contexts].filter(c=>c&&typeof c.resume==='function');
  };
  J.unlockAudio=()=>{J.audioContexts().forEach(c=>{if(c.state==='suspended')c.resume().catch(()=>{});});};
  J.pause=reason=>{
    if(!J.started)return;J.setActive(false);window.EJS_emulator.pause();J.state='paused';
    if(reason!=='menu'&&!menu.open&&!help.open)byId('continueLayer').hidden=false;
    J.message('Paused · your game is preserved');
  };
  J.resume=()=>{
    if(!J.started||document.hidden)return;
    J.unlockAudio();byId('continueLayer').hidden=true;window.EJS_emulator.play();J.state='running';J.setActive(true);J.message('Drag to move · tap or A to fire · B toggles items');
  };
  J.openMenu=()=>{if(!J.started)return;J.pause('menu');byId('restartConfirm').hidden=true;menu.showModal();};
  byId('menuBtn').onclick=J.openMenu;
  byId('pauseBtn').onclick=J.openMenu;
  byId('resume').onclick=()=>{menu.close();J.resume();};
  menu.addEventListener('cancel',e=>{e.preventDefault();menu.close();J.resume();});
  byId('help').onclick=()=>{menu.close();help.showModal();};
  byId('closeHelp').onclick=()=>{help.close();menu.showModal();};
  help.addEventListener('cancel',e=>{e.preventDefault();help.close();menu.showModal();});
  byId('continueButton').onclick=J.resume;
  byId('restart').onclick=()=>{byId('restartConfirm').hidden=false;};
  byId('noRestart').onclick=()=>{byId('restartConfirm').hidden=true;};
  byId('yesRestart').onclick=()=>{if(!J.started)return;J.input.clear();J.resets++;J.gm().restart();menu.close();J.resume();};
  byId('sound').onclick=()=>{J.sound=!J.sound;window.EJS_emulator.setVolume(J.sound ? 0.8 : 0);byId('sound').textContent='Sound: '+(J.sound?'On':'Off');};
  byId('full').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else if(document.documentElement.requestFullscreen)await document.documentElement.requestFullscreen();else J.message('Use Safari’s Hide Toolbar for more screen space.');}catch(_){J.message('Full screen is unavailable in this browser.');}};
  byId('shareBtn').onclick=async()=>{J.pause('share');const url='https://jmrothberg.github.io/Gauntlet/JMR-original/';try{if(navigator.share)await navigator.share({title:"JMR's Original — Gauntlet",url});else{await navigator.clipboard.writeText(url);J.message('Play link copied');}}catch(_){};};
  document.addEventListener('visibilitychange',()=>{if(document.hidden)J.pause('background');});
  window.addEventListener('blur',()=>{if(J.active)J.pause('background');});
  window.addEventListener('pagehide',()=>J.pause('background'));
  document.addEventListener('pointerdown',()=>{if(J.started)J.unlockAudio();},{capture:true});
  document.addEventListener('keydown',()=>{if(J.started)J.unlockAudio();},{capture:true});
  J.fail=text=>{J.message(text);byId('play').textContent='Unable to start';byId('play').disabled=true;J.state='error';};
  J.ready=()=>{
    const emulator=window.EJS_emulator;
    emulator.checkStarted=()=>{};
    const special=emulator.handleSpecialOptions;
    emulator.handleSpecialOptions=function(option,value){
      if(option==='menu-bar-button'&&!this.elements.menuToggle)return;
      return special.call(this,option,value);
    };
    // Pinned Emscripten build does not catch asynchronous wake-lock rejection.
    // Do not request a wake lock; it is unnecessary for input or emulation.
    const proto=window.EJS_GameManager.prototype;
    if(!proto.jmrConfigured){
      const cfg=proto.getRetroArchCfg;
      proto.getRetroArchCfg=function(){return cfg.call(this)+'\nsuspend_screensaver_enable = false\n';};
      proto.jmrConfigured=true;
    }
    J.state='ready';byId('play').disabled=false;byId('play').textContent='PLAY';J.message('Ready · choose your mode, then PLAY');
  };
  byId('play').onclick=()=>{
    if(J.state!=='ready')return;
    const native=byId('game').querySelector('.ejs_start_button');
    if(!native){J.fail('Start control unavailable. Reload this page.');return;}
    J.state='starting';J.starts++;byId('play').disabled=true;byId('play').textContent='STARTING…';J.message('Starting Gauntlet…');
    native.click();
    J.startTimeout=setTimeout(()=>{if(!J.started)J.fail('The game did not start. Check your connection and reload.');},45000);
  };
  J.onStart=()=>{
    clearTimeout(J.startTimeout);if(J.started)return;J.started=true;J.state='running';
    document.body.classList.add('started');byId('start').hidden=true;byId('screenSurface').classList.add('running');
    byId('menuBtn').disabled=false;byId('shareBtn').disabled=false;fit();J.setActive(true);
    J.message('Tap A to advance the title screens. Choose with arrows, then A.');
    if(document.hidden)J.pause('background');
    setTimeout(()=>{if(J.audioContexts().some(c=>c.state==='suspended')&&J.active)J.pause('audio');},250);
  };
  J.drawInputs();
})();
