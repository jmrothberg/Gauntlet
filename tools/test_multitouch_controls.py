def exercise_multitouch(page,name,check,keys,reset_log,no_shots):
 r=page.locator('#gesture').bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2
 reset_log()
 if name=='chromium':
  page.evaluate('''()=>{window.touchTrace=[];for(const t of ['pointerdown','pointermove','pointerup','pointercancel','lostpointercapture'])document.addEventListener(t,e=>touchTrace.push([t,e.pointerId,e.clientX,e.clientY,e.target.id]),true);}''')
  cdp=page.context.new_cdp_session(page)
  def send(kind,points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
  one={'x':x,'y':y,'id':1}
  move={'x':x+45,'y':y,'id':1}
  two={'x':x-50,'y':y+35,'id':2}
  send('touchStart',[one]);send('touchMove',[move]);page.wait_for_timeout(50)
  check(keys()==[7],'native touchscreen swipe moves right')
  send('touchStart',[move,two]);page.wait_for_timeout(40)
  # CDP TouchEnd ends the entire sequence. Updating active points releases only finger 2.
  send('touchMove',[move]);page.wait_for_timeout(25)
  check(keys()==[7,8],'second native touch fires while first steers: '+str(page.evaluate('({keys:JMR.input.snapshot(),trace:touchTrace,events:coreEvents})')))
  page.wait_for_timeout(650);check(keys()==[7],'tap releases fire without dropping steering')
  reset_log();send('touchEnd',[]);page.wait_for_timeout(80);check(keys()==[],'native movement release stops');no_shots('native movement release does not fire')
  cdp.detach()
 else:
  check(True,'WebKit native pointer drags and native touchscreen taps tested in main suite')
 def pointer(event,pid,px,py,selector=None):
  page.evaluate('''([event,pid,x,y,selector])=>{
   const target=selector?document.querySelector(selector):document.elementFromPoint(x,y);
   target.dispatchEvent(new PointerEvent(event,{bubbles:true,cancelable:true,pointerId:pid,pointerType:'touch',isPrimary:pid===81,button:0,buttons:event==='pointerup'?0:1,clientX:x,clientY:y}));
  }''',[event,pid,px,py,selector])
 reset_log();pointer('pointerdown',81,x,y);pointer('pointermove',81,x+50,y)
 check(keys()==[7],'synthetic touch reaches actual Handy direction input')
 pointer('pointercancel',81,x+50,y,'#screenSurface');check(keys()==[],'cancelled drag releases movement');no_shots('cancelled drag never fires')
 reset_log();pointer('pointerdown',81,x,y);pointer('pointermove',81,x+50,y);pointer('lostpointercapture',81,x+50,y,'#screenSurface')
 check(keys()==[],'lost capture releases movement');no_shots('lost capture never fires')
 reset_log();pointer('pointerdown',81,x,y);pointer('pointermove',81,x+50,y)
 pointer('pointerdown',82,x,y+30);pointer('pointermove',82,x+50,y+30)
 pointer('pointerup',82,x+50,y+30);check(keys()==[7],'releasing one direction owner preserves the other')
 pointer('pointerup',81,x+50,y);check(keys()==[],'both direction owners release cleanly');no_shots('two drags never fire')
 ar=page.locator('#buttonA').bounding_box();ax=ar['x']+ar['width']/2;ay=ar['y']+ar['height']/2
 pointer('pointerdown',83,ax,ay,'#buttonA');pointer('pointerdown',81,x,y);pointer('pointerup',81,x,y)
 page.wait_for_timeout(650);check(keys()==[8],'tap timer cannot release a separately held A')
 pointer('pointerup',83,ax,ay,'#buttonA');page.wait_for_timeout(120);check(keys()==[],'held A releases cleanly')
 reset_log();pointer('pointerdown',81,x,y);pointer('pointermove',81,x+45,y);pointer('pointermove',81,x,y);pointer('pointerup',81,x,y)
 check(keys()==[],'drag back to origin releases');no_shots('return-to-origin drag is not misclassified as tap')
