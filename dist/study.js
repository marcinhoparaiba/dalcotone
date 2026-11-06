export function kitItemLabel(item){return `${item.quantity?item.quantity+' × ':''}${item.name}${item.volume?' · '+item.volume:' · volume não confirmado'}`;}
export function makeDeck(products,{category='',line=''}={}){
 const deck=[];
 for(const p of products){
  if(category&&!(p.categories||[]).includes(category)||line&&p.line!==line)continue;
  const base={productId:p.id,productName:p.name,line:p.line,sourceUrl:p.url};
  if(p.benefits?.length)deck.push({...base,id:p.id+':benefits',question:`O que ${p.name} faz no cabelo?`,answer:p.benefits.join('\n'),topic:'Efeito no cabelo'});
  if(p.actives?.length)deck.push({...base,id:p.id+':actives',question:`Quais ativos são divulgados para ${p.name}?`,answer:p.actives.join('\n'),topic:'Ativos divulgados'});
  if(p.occasions?.length)deck.push({...base,id:p.id+':occasion',question:`Em qual ocasião consultar ${p.name}?`,answer:p.occasions.join('\n'),topic:'Quando usar'});
  if(p.kitItems?.length)deck.push({...base,id:p.id+':kit',question:`Quais componentes foram identificados em ${p.name}?`,answer:p.kitItems.map(kitItemLabel).join('\n')+(p.kitReview?.status!=='confirmed'?'\n\nConfira as pendências de confirmação na ficha do kit.':''),topic:'Componentes do kit'});
 }
 return deck;
}
