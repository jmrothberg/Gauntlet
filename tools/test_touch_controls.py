"""Real Handy/WASM regression: UI actions reach the actual core."""
import json, os, traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
OUT=Path(os.environ.get('RESULT_DIR','control-results'));OUT.mkdir(exist_ok=True)
URL=os.environ.get('GAME_URL','http://127.0.0.1:8765/JMR-original/')
DIRECTIONS=[(0,-45,[4]),(45,-45,[4,7]),(45,0,[7]),(45,45,[5,7]),(0,45,[5]),(-45,45,[5,6]),(-45,0,[6]),(-45,-45,[4,6])]
failed=False
with sync_playwright() as pw:
 for name in ['chromium','webkit']:
  result={'engine':name,'url':URL,'checks':[]};errors=[];page=None;browser=None
  try:
   browser=getattr(pw,name).launch(headless=True)
   ctx=browser.new_context(viewport={'width':820,'height':1180},has_touch=True,is_mobile=True,device_scale_factor=1)
   page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(URL,wait_until='domcontentloaded');page.wait_for_function('window.JMR && JMR.state === "ready"',timeout=45000)
   def check(condition,label):
    assert condition,label
    result['checks'].append(label)
   def tap(selector):page.locator(selector).tap()
   def snap():return page.evaluate('JMR.input.snapshot()')
   def keys():return sorted(snap()['held'])
   def reset_log():page.evaluate('window.coreEvents=[]')
   def no_shots(label):check(not any(x[1]==8 and x[2] for x in page.evaluate('coreEvents')),label)
   def center(selector):
    r=page.locator(selector).bounding_box();return r['x']+r['width']/2,r['y']+r['height']/2
   for mode in ['easy','woke','original']:
    tap('#startModes [data-mode='+mode+']');check(page.evaluate('JMR.mode')==mode,'splash selects '+mode)
   page.screenshot(path=str(OUT/(name+'-splash.png')))
   tap('#play');page.wait_for_function('JMR.started',timeout=45000);page.wait_for_timeout(1000)
   if page.locator('#continueButton').is_visible():tap('#continueButton')
   check(page.evaluate('JMR.active && JMR.starts===1 && window.JMR_romVerified'),'one live verified cartridge')
   check(page.locator('#gesture').count()==1,'gesture survives emulator initialization')
   x,y=center('#gesture');check(page.evaluate('([x,y])=>document.elementFromPoint(x,y).id',[x,y])=='gesture','touch surface is actually topmost')
   page.evaluate('''()=>{window.coreEvents=[];window.originalEmulator=EJS_emulator;const f=EJS_emulator.gameManager.functions,old=f.simulateInput;f.simulateInput=(p,k,v)=>{coreEvents.push([p,k,v]);return old(p,k,v);};}''')
   page.wait_for_timeout(4000)
   for i in range(4):
    page.locator('#buttonA').click(delay=160);page.wait_for_timeout(1500)
    page.screenshot(path=str(OUT/(name+'-game-step'+str(i)+'.png')))
   frame=page.locator('canvas').first.screenshot();im=Image.open(BytesIO(frame)).convert('RGB')
   check(len(im.getcolors(im.width*im.height) or [])>=8,'actual cartridge renders a multicolor frame')
   page.screenshot(path=str(OUT/(name+'-gameplay.png')))
   for mode in ['original','easy','woke']:
    tap('#menuBtn');tap('#menu [data-mode='+mode+']');tap('#resume');page.wait_for_timeout(100)
    check(page.evaluate('JMR.mode')==mode,'in-game mode '+mode)
    reset_log();page.wait_for_timeout(300);no_shots(mode+' idle never fires')
    for dx,dy,expected in DIRECTIONS:
     reset_log();x,y=center('#gesture');page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+dx,y+dy,steps=4);page.wait_for_timeout(45)
     check(keys()==sorted(expected),mode+' swipe holds '+str(expected))
     page.mouse.up();page.wait_for_timeout(30);check(keys()==[],mode+' swipe releases '+str(expected));no_shots(mode+' swipe never shoots '+str(expected))
     x,y=center('#dpad');page.mouse.move(x+dx,y+dy);page.mouse.down();page.wait_for_timeout(35)
     check(keys()==sorted(expected),mode+' dpad holds '+str(expected));page.mouse.up();page.wait_for_timeout(25)
     check(keys()==[],mode+' dpad releases '+str(expected));no_shots(mode+' dpad never shoots '+str(expected))
    for key,code in [('ArrowUp',4),('ArrowDown',5),('ArrowLeft',6),('ArrowRight',7)]:
     reset_log();page.keyboard.down(key);check(keys()==[code],mode+' keyboard '+key);page.keyboard.up(key);no_shots(mode+' keyboard never shoots '+key)
    reset_log();page.locator('#gesture').tap();page.wait_for_timeout(20);check(8 in keys(),mode+' deliberate tap fires');page.wait_for_timeout(600);check(keys()==[],mode+' tap releases')
    reset_log();tap('#buttonB');check(keys()==[0] and snap()['bLatched'],mode+' B latches')
    x,y=center('#dpad');page.mouse.move(x,y-45);page.mouse.down();check(keys()==[0,4],mode+' inventory gets B plus direction');page.mouse.up();check(keys()==[0],mode+' B stays after direction release');no_shots(mode+' inventory does not auto-fire');tap('#buttonB');check(keys()==[],mode+' B unlatches')
   for code in [10,11]:
    reset_log();page.locator('[data-key="'+str(code)+'"]').tap();page.wait_for_timeout(180)
    check([[x[1],x[2]] for x in page.evaluate('coreEvents')]==[[code,1],[code,0]],'option '+str(code)+' exact press/release')
   from test_multitouch_controls import exercise_multitouch
   exercise_multitouch(page,name,check,keys,reset_log,no_shots)
   tap('#menuBtn');f1=page.evaluate('JMR.gm().functions.getFrameNum()');page.wait_for_timeout(300);f2=page.evaluate('JMR.gm().functions.getFrameNum()');check(f1==f2,'menu freezes actual emulator frames')
   tap('#restart');tap('#noRestart');tap('#resume');check(page.evaluate('JMR.resets===0 && JMR.starts===1 && EJS_emulator===originalEmulator'),'restart cancel and resume preserve instance')
   tap('#buttonB');page.evaluate('window.dispatchEvent(new Event("blur"))');check(keys()==[] and not snap()['bLatched'],'background clears all inputs and B');tap('#continueButton');check(page.evaluate('JMR.active && EJS_emulator===originalEmulator'),'background resume same instance')
   for w,h in [(1180,820),(390,844),(844,390),(375,667)]:
    page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(200)
    good=page.locator('#screenSurface,#dpad,#buttonA,#buttonB').evaluate_all('(els)=>els.every(e=>{let r=e.getBoundingClientRect();return r.width>20&&r.height>20&&r.x>=0&&r.y>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1;})')
    check(good,'layout '+str(w)+'x'+str(h));x,y=center('#gesture');check(page.evaluate('([x,y])=>document.elementFromPoint(x,y).id',[x,y])=='gesture','gesture hit test '+str(w)+'x'+str(h))
   page.screenshot(path=str(OUT/(name+'-phone.png')))
   check(not errors,'no uncaught JavaScript errors');result['passed']=True
  except Exception:
   failed=True;result['error']=traceback.format_exc();result['passed']=False
   if page:
    try:page.screenshot(path=str(OUT/(name+'-failure.png')));result['body']=page.locator('body').inner_text()
    except Exception:pass
  finally:
   result['errors']=errors
   (OUT/(name+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
   if browser:browser.close()
if failed:raise SystemExit(1)
