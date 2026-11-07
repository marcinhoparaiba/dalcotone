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
 const data=await evaluate("fetch('catalog.json').then(r=>r.json()).then(c=>c.products.map(p=>({id:p.id,name:p.name,type:p.type,image:p.imageUrl})))");
 const names=Object.fromEntries(data.map(p=>[p.id,p.name]));
 const local=data.filter(p=>p.image?.startsWith('/assets/'));
 assert.equal(await evaluate(`Promise.all(${JSON.stringify(local.map(p=>p.image))}.map(src=>new Promise(resolve=>{const image=new Image();image.onload=()=>resolve(image.naturalWidth>0);image.onerror=()=>resolve(false);image.src=src;}))).then(result=>result.filter(Boolean).length)`),local.length);
 await evaluate("location.hash='pesquisa'");await waitFor(`document.querySelectorAll('.product-card').length===${data.length}`);
 let tabsVisited=0,kitPaths=0;
 for(const p of data){
  await evaluate(`document.querySelector('.card-open[data-open="${p.id}"]').click()`);
  assert.equal(await evaluate("document.getElementById('detail-name').textContent"),p.name);
  const tabs=await evaluate("[...document.querySelectorAll('.detail-tabs button')].map(b=>b.dataset.tab)");
  for(const tab of tabs){
   await evaluate(`document.querySelector('[data-tab="${tab}"]').click()`);
   const text=await evaluate("document.querySelector('.detail-section').innerText");
   assert.ok(text.trim().length>20,p.id+' '+tab+' empty');
   assert.ok(!/undefined|\[object Object\]/.test(text),p.id+' '+tab+' malformed data');tabsVisited++;
  }
  if(p.type==='Kits'){
   await evaluate("document.querySelector('[data-tab=kit]').click()");
   const children=await evaluate("[...document.querySelectorAll('.kit-components [data-from-kit]')].map(b=>b.dataset.open)");
   assert.ok(children.length,p.id+' has no component links');
   for(const id of [...new Set(children)]){
    await evaluate(`document.querySelector('.kit-components [data-open="${id}"]').click()`);
    assert.equal(await evaluate("document.getElementById('detail-name').textContent"),names[id]);
    await evaluate("document.querySelector('[data-back-kit]').click()");
    assert.equal(await evaluate("document.getElementById('detail-name').textContent"),p.name);kitPaths++;
   }
  }
  await evaluate("document.getElementById('product-dialog').close()");
 }
 assert.deepEqual(exceptions,[]);
 console.log(JSON.stringify({productsVisited:data.length,tabsVisited,kitComponentRoundTrips:kitPaths,bundledPhotosDecoded:local.length,unverifiedRemotePhotoReferences:data.length-local.length}));
}finally{socket?.close();browser.kill('SIGTERM');await new Promise(r=>setTimeout(r,300));await rm(directory,{recursive:true,force:true});}
