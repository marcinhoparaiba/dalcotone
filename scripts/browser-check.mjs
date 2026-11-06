import {spawn} from 'node:child_process';
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
 await evaluate("document.querySelector('a[href=\"#catalogo/Selagem\"]').click()");await waitFor("document.getElementById('page-title').textContent==='Selagem'");
 await evaluate("document.querySelector('.line-card[href*=\"/24K\"]').click()");await waitFor("document.getElementById('page-title').textContent==='Linha 24K'");
 assert.equal(await evaluate("[...document.querySelectorAll('.card-title')].some(x=>x.textContent.includes('Spray'))"),false); await evaluate("document.querySelector('.line-presentation summary').click()");assert.ok(await evaluate("document.getElementById('line-script').innerText.includes('Lisselini')"));assert.ok(await evaluate("document.querySelector('[data-copy-script=line-script]')!==null"));

 await evaluate("location.hash='linhas/24K'");await waitFor("document.querySelectorAll('.product-card').length===4");
 await evaluate("document.querySelector('[data-open=consultor-kit-24k]').click();document.querySelector('[data-tab=kit]').click()");
 assert.equal(await evaluate("document.querySelectorAll('.kit-components li').length"),3);
 assert.ok(await evaluate("document.querySelector('.kit-status').textContent.includes('consultor')"));
 await evaluate("document.getElementById('product-dialog').close();location.hash='linhas/pH%20Control'");await waitFor("document.querySelectorAll('.product-card').length===1");
 assert.equal(await evaluate("document.querySelector('.card-title').textContent"),'pH Control 500 mL');await waitFor("document.querySelector('.product-photo img').complete&&document.querySelector('.product-photo img').naturalWidth>0");
 assert.equal(await evaluate("document.getElementById('hero').hidden"),true);
 await evaluate("location.hash='estudar/24K'");await waitFor("document.querySelector('.study-card')!==null");
 await evaluate("document.getElementById('reveal-study').click()");assert.ok(await evaluate("document.querySelector('.study-answer').textContent.length>0"));
 await evaluate("document.querySelector('[data-study-mark=known]').click();location.hash='catalogo'");await waitFor("document.querySelectorAll('.category-card').length>=10");
 for(const [width,height]of [[1440,1000],[390,844],[320,760]]){
  await cdp('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<680});
  assert.equal(await evaluate('document.documentElement.scrollWidth<=innerWidth'),true,'horizontal overflow '+width);
 }
 await evaluate("location.hash='empresa'");await waitFor("document.querySelectorAll('.company-fact').length===6");assert.ok(await evaluate("document.querySelector('.company-grid').textContent.includes('2015')"));assert.ok(await evaluate("document.getElementById('brand-script').textContent.includes('fabricação própria')"));assert.ok(await evaluate("document.querySelector('.company-grid').textContent.includes('não especifica os países')"));
 await evaluate("location.hash='pesquisa'");await waitFor("document.getElementById('page-title').textContent.includes('Pesquisar')");
 await evaluate("const input=document.getElementById('search');input.value='banana mel';input.dispatchEvent(new Event('input',{bubbles:true}))");
 assert.ok(await evaluate("document.querySelectorAll('.product-card').length>=1"));
 await evaluate("document.querySelector('[data-favorite]').click()");
 assert.ok(Number(await evaluate("document.getElementById('favorite-count').textContent"))>=1);
 await evaluate("document.querySelector('.card-open').click()");await waitFor("document.getElementById('product-dialog').open");
 await evaluate("document.querySelector('[data-tab=technical]').click()");assert.ok(await evaluate("document.querySelector('.technical-grid').textContent.includes('pH declarado')"));assert.ok(await evaluate("document.querySelector('.detail-section').textContent.includes('não há ensaio comparativo')"));
 await evaluate("document.querySelector('[data-tab=notes]').click();const n=document.getElementById('product-note');n.value='<script>window.BAD=true</script> Nota local de teste';n.dispatchEvent(new Event('input',{bubbles:true}))");
 assert.equal(await evaluate("document.getElementById('note-state').textContent"),'Salvo neste aparelho.'); await evaluate("document.querySelector('[data-tab=presentation]').click()");assert.ok(await evaluate("document.getElementById('product-script').textContent.includes('Banana')"));

 await evaluate("document.querySelector('[data-tab=composition]').click()");assert.ok(await evaluate("document.querySelector('.detail-section').textContent.includes('não foi encontrada')"));
 await evaluate("document.getElementById('product-dialog').close();document.getElementById('reset-filters').click()");
 await evaluate("const inputs=[...document.querySelectorAll('[data-compare]')].slice(0,2);inputs.forEach(i=>i.click());document.getElementById('open-compare').click()");
 assert.equal(await evaluate("document.querySelectorAll('.compare-table thead th').length"),3);
 await evaluate("document.getElementById('compare-dialog').close();document.getElementById('clear-compare').click();location.hash='offline'");
 await waitFor("document.getElementById('download-status')?.textContent.includes('Catálogo salvo')");
 await cdp('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 await cdp('Page.reload');await waitFor("document.getElementById('page-title')?.textContent.includes('offline')");
 assert.ok(await evaluate("document.getElementById('connection').textContent.includes('Offline')"));
 await evaluate("location.hash='favoritos'");await waitFor("document.querySelectorAll('.product-card').length>=1");
 await evaluate("document.querySelector('.card-open').click();document.querySelector('[data-tab=notes]').click()");
 assert.ok(await evaluate("document.getElementById('product-note').value.includes('Nota local de teste')"));assert.equal(await evaluate('window.BAD===undefined'),true);
 await evaluate("document.getElementById('product-dialog').close();location.hash='linhas/pH%20Control'");await waitFor("document.querySelectorAll('.product-card').length===1");await waitFor("document.querySelector('.product-photo img').naturalWidth>0");assert.ok(await evaluate("document.querySelector('.product-photo img').src.includes('/assets/products/consultor-ph-control.webp')"));
 await evaluate("document.getElementById('product-dialog').close();location.hash='pesquisa'");
 await waitFor("document.getElementById('search')!==null");await evaluate("const q=document.getElementById('search');q.value='ceramidas';q.dispatchEvent(new Event('input',{bubbles:true}))");assert.ok(await evaluate("document.querySelectorAll('.product-card').length>0"));
 assert.deepEqual(exceptions,[]);
 console.log('PASS categories/lines/kit contents, pH Control as regular entry, study cards, technical/source details, responsive 1440/390/320, search, favorites, comparison, notes and offline persistence. Official external photo downloads were not verified in this restricted network.');
}finally{socket?.close();browser.kill('SIGTERM');await new Promise(r=>setTimeout(r,300));await rm(directory,{recursive:true,force:true});}
