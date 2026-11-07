import {spawn,spawnSync} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import assert from 'node:assert/strict';
const directory=await mkdtemp('/tmp/dc-browser-');
const browser=spawn('chromium',['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--remote-debugging-port=0','--user-data-dir='+directory,'about:blank'],{stdio:['ignore','ignore','pipe']});
let socket;
try{
 const address=await new Promise((resolve,reject)=>{let log='';const timer=setTimeout(()=>reject(Error('Browser startup timeout')),15000);browser.stderr.on('data',b=>{log+=b;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m){clearTimeout(timer);resolve(m[1]);}});});
 socket=new WebSocket(address);await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});let seq=0;const pending=new Map(),exceptions=[];
 socket.onmessage=({data})=>{const msg=JSON.parse(data);if(msg.id){const p=pending.get(msg.id);pending.delete(msg.id);msg.error?p.reject(Error(JSON.stringify(msg.error))):p.resolve(msg.result);}else if(msg.method==='Runtime.exceptionThrown')exceptions.push(msg.params.exceptionDetails.text);};
 const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));});
 const {targetId}=await send('Target.createTarget',{url:'about:blank'});const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});const cdp=(method,params)=>send(method,params,sessionId);
 const evaluate=async expression=>{const r=await cdp('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const waitFor=async expression=>{for(let i=0;i<100;i++){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,100));}throw Error('UI timeout '+expression);};
 await cdp('Page.enable');await cdp('Runtime.enable');await cdp('Network.enable');
 // Only block external photos in this infrastructure test. No substitute photos are shown.
 await cdp('Network.setBlockedURLs',{urls:['https://dalcotone.com.br/*','https://cdn.shopify.com/*']});
 await cdp('Page.navigate',{url:'http://127.0.0.1:31900/'});await waitFor("document.querySelectorAll('.category-card').length>=10");
 await waitFor("navigator.serviceWorker.controller!==null");

 for(const width of [390,320,680]){
 await cdp('Emulation.setDeviceMetricsOverride',{width,height:844,deviceScaleFactor:1,mobile:true});
 assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth'),'No horizontal overflow at '+width);
 assert.equal(await evaluate("document.querySelectorAll('.bottom-nav a,.bottom-nav button').length"),5);
 await evaluate("document.getElementById('open-menu').click()");await waitFor("document.getElementById('navigation-dialog').open");
 await waitFor("document.getElementById('navigation-dialog').getBoundingClientRect().bottom<=innerHeight+1");
 assert.equal(await evaluate("document.querySelectorAll('.menu-grid a').length"),10);
 await evaluate("document.querySelector('.menu-grid a[href=\"#videos\"]').click()");await waitFor("document.getElementById('page-title').textContent==='Demonstrações e resultados'");
 assert.equal(await evaluate("document.getElementById('navigation-dialog').open"),false);
 await evaluate("document.getElementById('open-menu').click()");await cdp('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await cdp('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await waitFor("!document.getElementById('navigation-dialog').open");
 await evaluate("location.hash='catalogo'");await waitFor("document.querySelector('.situation-card')!==null");
 await evaluate("document.querySelector('.situation-card[href*=ressecamento]').click()");await waitFor("document.getElementById('page-title').textContent==='Ressecamento'");
 assert.ok(await evaluate("document.querySelectorAll('.product-card').length>4"));
 assert.equal(await evaluate("document.getElementById('catalog-controls').hidden"),true);
 assert.equal(await evaluate("document.getElementById('study-filter-panel').hidden"),true);
 await evaluate("location.hash='catalogo'");await waitFor("document.querySelector('.situation-card')!==null");
 }
 await cdp('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await new Promise(r=>setTimeout(r,500));
 const shot=await cdp('Page.captureScreenshot',{format:'png'});
 const {writeFile}=await import('node:fs/promises');await writeFile('/workspace/work/dal-release/new-interface-mobile.png',Buffer.from(shot.data,'base64'));
 await evaluate("document.getElementById('open-menu').click()");await new Promise(r=>setTimeout(r,350));const menuShot=await cdp('Page.captureScreenshot',{format:'png'});await writeFile('/workspace/work/dal-release/new-menu-mobile.png',Buffer.from(menuShot.data,'base64'));
 await evaluate("document.getElementById('close-menu').click()");
 await cdp('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
 await evaluate("location.hash='kits'");await waitFor("document.getElementById('page-title').textContent==='Kits e seus componentes'");
 await cdp('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});await cdp('Page.reload');await waitFor("document.querySelectorAll('.product-card').length>=26");
 assert.ok(await evaluate("[...document.styleSheets].some(s=>s.href?.includes('experience.css'))"));
 await evaluate("document.getElementById('open-menu').click()");assert.equal(await evaluate("document.getElementById('navigation-dialog').open"),true);
 await evaluate("document.querySelector('.menu-grid a[href=\"#linhas\"]').click()");await waitFor("document.querySelectorAll('.line-card').length>=28");
 await cdp('Network.emulateNetworkConditions',{offline:false,latency:0,downloadThroughput:-1,uploadThroughput:-1});await cdp('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 assert.equal(await evaluate("getComputedStyle(document.querySelector('.sidebar')).display==='none'"),false);assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth'));
 assert.deepEqual(exceptions,[]);console.log('PASS mobile navigation at 320/390/680, full menu, Escape, route closing, direct results, reduced motion, offline reload and menu, desktop layout.');
}finally{socket?.close();browser.kill('SIGTERM');await new Promise(r=>setTimeout(r,300));await rm(directory,{recursive:true,force:true});}
