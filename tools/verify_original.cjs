'use strict';
const {chromium,webkit}=require('playwright');
const {PNG}=require('pngjs');
const fs=require('fs'),crypto=require('crypto');
const out='browser-results';fs.mkdirSync(out,{recursive:true});
const base=process.env.GAME_URL||'http://127.0.0.1:8080/JMR-original/';
(async()=>{
 let failed=false;
 for(const [name,type] of Object.entries({chromium,webkit})){
  const logs=[],urls=new Set(),result={browser:name,url:base};let browser,page;
  try{
   browser=await type.launch({headless:true});
   const context=await browser.newContext({viewport:{width:820,height:1180},hasTouch:true,isMobile:true,deviceScaleFactor:1});
   page=await context.newPage();
   page.on('console',m=>{if(['error','warning'].includes(m.type()))logs.push(m.type()+': '+m.text());});
   page.on('pageerror',e=>logs.push('PAGE ERROR: '+e.stack));
   page.on('requestfailed',r=>logs.push('REQUEST FAILED: '+r.url()+' '+JSON.stringify(r.failure())));
   page.on('response',r=>{urls.add(r.url());if(r.status()>=400)logs.push('HTTP '+r.status()+' '+r.url());});
   await page.addInitScript(()=>{
    window.__audio={buffers:0,nonzero:0};
    const proto=window.AudioBufferSourceNode&&AudioBufferSourceNode.prototype;
    if(proto){const start=proto.start;proto.start=function(...args){window.__audio.buffers++;if(this.buffer){const data=this.buffer.getChannelData(0);for(let i=0;i<data.length;i+=16)if(Math.abs(data[i])>.00001){window.__audio.nonzero++;break;}}return start.apply(this,args);};}
   });
   await page.goto(base,{waitUntil:'domcontentloaded',timeout:60000});
   await page.getByText('PLAY GAUNTLET',{exact:true}).click({timeout:60000});
   await page.waitForFunction(()=>document.body.classList.contains('started'),{},{timeout:45000});
   await page.waitForTimeout(6000);
   result.started=true;result.romVerified=await page.evaluate(()=>window.JMR_romVerified===true);
   result.audio=await page.evaluate(()=>window.__audio);
   result.settings=await page.evaluate(()=>({rotation:window.EJS_defaultOptions.handy_rot,core:window.EJS_core,dataPath:window.EJS_pathtodata,version:window.EJS_emulator.ejs_version}));
   await page.screenshot({path:`${out}/${name}-boot.png`});
   const frames=[];
   for(let i=0;i<4;i++){
    await page.locator('#button-a').click({delay:180});await page.waitForTimeout(1800);
    await page.screenshot({path:`${out}/${name}-step${i+1}.png`});
    frames.push(crypto.createHash('sha256').update(await page.locator('canvas').first().screenshot()).digest('hex'));
   }
   const r=await page.locator('#dpad').boundingBox();
   await page.mouse.move(r.x+r.width/2,r.y+15);await page.mouse.down();await page.waitForTimeout(1600);await page.mouse.up();
   await page.locator('#button-b').click({delay:180});await page.waitForTimeout(1500);
   await page.locator('#button-a').click({delay:900});await page.waitForTimeout(1500);
   result.audioDuringGameplay=await page.evaluate(()=>window.__audio);
   await page.screenshot({path:`${out}/${name}-gameplay.png`});
   const frame=await page.locator('canvas').first().screenshot();fs.writeFileSync(`${out}/${name}-frame.png`,frame);
   const png=PNG.sync.read(frame),colors=new Set();let lit=0,magenta=0;
   for(let i=0;i<png.data.length;i+=4){const [r,g,b]=png.data.subarray(i,i+3);colors.add((r<<16)|(g<<8)|b);if(r+g+b>40)lit++;if(r>100&&b>100&&g<50)magenta++;}
   result.render={width:png.width,height:png.height,colors:colors.size,lit:lit/(png.width*png.height),magenta:magenta/(png.width*png.height)};
   result.framesChanged=new Set(frames).size>1;
   result.controlsVisible=await page.locator('#button-a').isVisible()&&await page.locator('#dpad').isVisible();
   result.heldAfterRelease=await page.evaluate(()=>Array.from(held.values()));
   await page.locator('#help').click();result.helpOpens=await page.locator('dialog').isVisible();await page.locator('#close-help').click();
   for(const size of [{width:1180,height:820},{width:390,height:844},{width:844,height:390}]){
    await page.setViewportSize(size);await page.waitForTimeout(600);
    await page.screenshot({path:`${out}/${name}-${size.width}x${size.height}.png`});
    const bounds=await page.locator('#button-a,#dpad,#game').evaluateAll(els=>els.map(el=>{const r=el.getBoundingClientRect();return {id:el.id,x:r.x,y:r.y,w:r.width,h:r.height,visible:r.x>=0&&r.y>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1};}));
    result.layouts=result.layouts||[];result.layouts.push({size,bounds});
   }
   result.text=await page.locator('body').innerText();
   result.passed=result.started&&result.romVerified&&result.controlsVisible&&result.render.colors>=8&&result.render.lit>.02&&result.render.magenta<.35&&result.heldAfterRelease.length===0&&result.layouts.every(x=>x.bounds.every(b=>b.visible));
   if(!result.passed)failed=true;
  }catch(e){result.error=e.stack;failed=true;if(page)await page.screenshot({path:`${out}/${name}-error.png`}).catch(()=>{});}
  finally{if(browser)await browser.close();fs.writeFileSync(`${out}/${name}.json`,JSON.stringify({result,logs,urls:[...urls]},null,2));console.log(JSON.stringify({result,logs}));}
 }
 if(failed)process.exitCode=1;
})();
