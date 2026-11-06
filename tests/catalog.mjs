import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {filterProducts,normalize,safeUrl,money} from '../dist/core.js';
import {makeDeck} from '../dist/study.js';
const catalog=JSON.parse(await readFile(new URL('../dist/catalog.json',import.meta.url)));
test('catalog has unique products and truthful source, price and composition fields',()=>{
 assert.ok(catalog.products.length>=85);assert.equal(new Set(catalog.products.map(p=>p.id)).size,catalog.products.length);
 for(const p of catalog.products){assert.ok(p.name);assert.ok(safeUrl(p.url));assert.ok(p.price===null||typeof p.price==='number'&&p.price>0);assert.ok(['basic','partial','detailed'].includes(p.detailLevel));assert.ok(Array.isArray(p.actives));if(p.imageUrl)assert.ok(safeUrl(p.imageUrl));}
 assert.ok(catalog.products.some(p=>p.inci===null));assert.ok(catalog.products.some(p=>p.inci));assert.equal(catalog.reportedCatalogCount,89);assert.ok(catalog.coverageNote.includes('profissional'));
});
test('treatments, lines and all audited kits remain distinct and traceable',()=>{
 for(const name of ['Reconstrução','Selagem','Botox','Detox','Controle de pH'])assert.ok(catalog.categories.some(c=>c.name===name));
 for(const p of catalog.products){assert.ok(p.categories.length);assert.ok(catalog.lines.some(l=>l.name===p.line&&l.productIds.includes(p.id)));}
 assert.equal(catalog.kitAudit.total,26);assert.equal(catalog.products.filter(p=>p.type==='Kits'&&p.sourceKind!=='consultor').length,26);
 const spray=catalog.products.find(p=>p.line==='24K'&&p.name.includes('Spray'));assert.ok(spray.categories.includes('Finalização'));assert.ok(!spray.categories.includes('Selagem'));
 const reference=catalog.products.find(p=>p.id==='consultor-kit-24k');assert.equal(reference.sourceKind,'consultor');assert.equal(reference.price,null);assert.equal(reference.kitItems.length,3);assert.equal(reference.kitItems[0].productId,null);
 const ph=catalog.products.find(p=>p.id==='consultor-ph-control');assert.ok(ph);assert.deepEqual(ph.actives,['Nano Link','LunaMatrix']);assert.equal(ph.price,null);
 assert.ok(filterProducts(catalog.products,{category:'Selagem',line:'24K'}).every(p=>p.line==='24K'&&p.categories.includes('Selagem')));
});
test('study questions use known facts and kit links do not invent missing volumes',()=>{
 const deck=makeDeck(catalog.products,{line:'24K'});assert.ok(deck.length);assert.ok(deck.every(c=>c.line==='24K'&&c.answer));
 assert.ok(makeDeck(catalog.products).some(c=>c.productId==='consultor-ph-control'&&c.topic==='Ativos divulgados'&&c.answer.includes('LunaMatrix')));
 const known=new Set(catalog.products.map(p=>p.id));
 for(const p of catalog.products.filter(p=>p.type==='Kits')){assert.ok(p.kitReview);for(const item of p.kitItems||[]){assert.ok(item.name);if(item.productId)assert.ok(known.has(item.productId));}}
 assert.ok(catalog.products.some(p=>p.kitReview?.status==='partial'&&p.kitItems.some(i=>i.volume===null)));
});
test('search accepts accents, ingredient names, fragrance notes and combined filters',()=>{
 assert.equal(normalize('Nutrição'), 'nutricao');
 const sample=[{id:'a',name:'Máscara A',line:'Linha',type:'Máscaras',actives:['Ceramidas'],needs:['Hidratação'],price:10},{id:'b',name:'Perfume B',line:'Outra',type:'Perfumes',actives:[],olfactoryNotes:{fundo:['Baunilha']},needs:['Perfumaria'],price:20}];
 assert.equal(filterProducts(sample,{query:'mascara ceramidas',need:'Hidratação',line:'Linha',type:'Máscaras'})[0].id,'a');
 assert.equal(filterProducts(sample,{query:'baunilha'})[0].id,'b');assert.equal(filterProducts(sample,{query:'sem correspondencia'}).length,0);
 assert.deepEqual(filterProducts(sample,{favorites:['b']}).map(p=>p.id),['b']);
 assert.ok(filterProducts(catalog.products,{query:'banana mel'}).length>0);
});
test('unknown prices sort last and URLs cannot inject scripts',()=>{
 const products=[{id:'x',name:'A',price:null},{id:'y',name:'B',price:20},{id:'z',name:'C',price:10}];
 assert.deepEqual(filterProducts(products,{sort:'price-up'}).map(p=>p.id),['z','y','x']);
 assert.deepEqual(filterProducts(products,{sort:'price-down'}).map(p=>p.id),['y','z','x']);
 assert.equal(money(null),'A confirmar');assert.equal(safeUrl('javascript:alert(1)'),'');assert.equal(safeUrl('https://evil.example/x'),'');
});

test('company history is sourced and does not fabricate international countries or competitive tests',()=>{
 assert.equal(catalog.company.facts.find(f=>f.label==='Criação da marca').value,'2015');
 assert.ok(catalog.company.facts.every(f=>safeUrl(f.sourceUrl)));
 assert.ok(catalog.company.facts.find(f=>f.label==='Atuação internacional').detail.includes('não especifica'));
 assert.ok(catalog.products.every(p=>p.competitiveEvidence===null));
});

test('every line and product has a complete, scoped conversation guide',()=>{
 for(const line of catalog.lines){assert.ok(line.approach);for(const key of ['question','opening','explanation','nextStep'])assert.ok(line.approach[key]?.length>15);}
 for(const p of catalog.products){assert.ok(p.presentation?.question);assert.ok(p.presentation?.opening);assert.ok(p.presentation?.scope);}
 assert.ok(catalog.company.brandApproach.valuePoints.every(p=>p.meaning&&p.say&&p.limit&&safeUrl(p.sourceUrl)));
 const ph=catalog.products.find(p=>p.id==='consultor-ph-control');assert.ok(ph.presentation.opening.includes('Nano Link'));assert.equal(ph.sourceKind,'official-catalog');assert.equal(ph.technical.declaredPH,null);
});

test('PDF photographs are bundled, verified and preserve SKU identities',async()=>{
 const photos=JSON.parse(await readFile(new URL('../research/pdf-photos.json',import.meta.url)));
 assert.equal(photos.images.length,23);
 for(const photo of photos.images){const p=catalog.products.find(p=>p.id===photo.productId);assert.ok(p);assert.equal(photo.verifiedPresentation,true);assert.equal(p.imageUrl,photo.imageUrl);assert.ok(safeUrl(p.imageUrl));assert.ok((await readFile(new URL('../dist'+p.imageUrl,import.meta.url))).length>100);}
 assert.ok(!catalog.products.find(p=>p.id==='consultor-kit-24k').imageUrl);
 const ph=catalog.products.find(p=>p.id==='consultor-ph-control');assert.ok(ph.name.includes('500 mL'));assert.ok(ph.use.includes('blindagem'));assert.ok(ph.occasions.length===3);
});
