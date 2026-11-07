import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {discoveryFilter,matchesGoal,matchesHairType,inferSituations} from '../dist/discovery.js';
const catalog=JSON.parse(await readFile(new URL('../dist/catalog.json',import.meta.url)));
test('a result returns every eligible product and kit rather than four featured bundles',()=>{
 const all=catalog.products;const matches=discoveryFilter(all,{selectedGoal:'hidratacao-brilho'});
 assert.ok(matches.length>4);assert.ok(matches.some(p=>p.type==='Kits'));assert.ok(matches.some(p=>p.type!=='Kits'));
 assert.deepEqual(matches.map(p=>p.id).sort(),all.filter(p=>matchesGoal(p,'hidratacao-brilho')).map(p=>p.id).sort());
});
test('a description combines oily roots and dry ends without classifying body fragrances as hair treatments',()=>{
 const text='minha raiz está oleosa e as pontas ressecadas';assert.deepEqual(inferSituations(text),['ressecamento','oleosidade']);
 const matches=discoveryFilter(catalog.products,{description:text});assert.ok(matches.some(p=>p.id==='85e6ca2844f6803d'));assert.ok(matches.some(p=>p.id==='c1104649da13708c'));assert.ok(!matches.some(p=>p.line==='Perfumaria'||p.type==='Suplementos'));
});
test('multiple hair and product checkboxes preserve OR within a group and AND between groups',()=>{
 const hair=['Cacheados, ondulados ou crespos','Oleosos ou mistos'];const types=['Shampoos','Máscaras'];
 const actual=discoveryFilter(catalog.products,{selectedHairTypes:hair,selectedTypes:types});assert.ok(actual.length>2);
 assert.ok(actual.every(p=>types.includes(p.type)&&hair.some(label=>matchesHairType(p,label))));
 const reordered=[...catalog.products].reverse();assert.deepEqual(discoveryFilter(reordered).map(p=>p.id),reordered.map(p=>p.id));
});
test('current composition distinguishes ingredient declarations from fragrance notes and old bundle editions',()=>{
 const p=catalog.products.find(p=>p.id==='60e03232e7b79d05');assert.ok(p.inci.includes('Citral'));assert.equal(p.compositionIsINCI,false);assert.ok(p.use.toLowerCase().includes('pele'));
 const force=catalog.products.find(p=>p.id==='9297bd616196f4df');assert.equal(force.kitItems.length,2);assert.ok(force.kitItems.every(i=>i.productId));
 const crono=catalog.products.find(p=>p.id==='244136c3b5dfed21');assert.equal(crono.kitItems.length,4);assert.ok(crono.kitItems.every(i=>i.volume===null));
});
