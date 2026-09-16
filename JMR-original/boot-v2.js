'use strict';
(async()=>{
  const J=window.JMR;
  const SHA='21a83624a636fde4d6f6a01363ebd7644dd5c3da19013525aae11ff0aeb2eb60';
  try{
    const url='./Gauntlet-The-Third-Encounter.lnx?sha='+SHA.slice(0,12);
    const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),20000);
    let response;try{response=await fetch(url,{cache:'no-cache',signal:abort.signal});}finally{clearTimeout(timer);}
    if(!response.ok)throw Error('Cartridge download failed ('+response.status+')');
    const bytes=await response.arrayBuffer();
    if(bytes.byteLength!==131136)throw Error('Cartridge download incomplete');
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
    if(hash!==SHA)throw Error('Cartridge checksum mismatch');
    Object.assign(window,{
      JMR_romVerified:true,EJS_player:'#game',EJS_core:'handy',EJS_gameUrl:url,
      EJS_gameName:'Gauntlet JMR Original',EJS_gameID:19900908,
      EJS_pathtodata:'./vendor/emulatorjs-4.2.3/',EJS_startOnLoaded:false,
      EJS_startButtonName:'PLAY GAUNTLET',EJS_alignStartButton:'center',EJS_volume:.8,
      EJS_controlScheme:'lynx',EJS_threads:false,EJS_backgroundColor:'#000',EJS_color:'#b72739',
      EJS_disableLocalStorage:true,EJS_VirtualGamepadSettings:[],EJS_noAutoFocus:true,
      EJS_defaultOptions:{handy_rot:'270'},
      EJS_defaultControls:{0:{},1:{},2:{},3:{}},EJS_ready:J.ready,EJS_onGameStart:J.onStart
    });
    window.EJS_Buttons=Object.fromEntries(['play','pause','playPause','restart','mute','settings','fullscreen','saveState','loadState','screenRecord','gamepad','cheat','volume','saveSavFiles','loadSavFiles','quickSave','quickLoad','screenshot','cacheManager','exitEmulation','contextMenu'].map(k=>[k,{visible:false}]));
    const loader=document.createElement('script');loader.src=window.EJS_pathtodata+'loader.js';
    loader.onerror=()=>J.fail('Player files could not load. Check your connection and reload.');
    document.body.appendChild(loader);
  }catch(error){console.error(error);J.fail(error.name==='AbortError'?'Download timed out. Check your connection and reload.':error.message);}
})();
