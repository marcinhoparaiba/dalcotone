"""Build the personal catalog from reviewed official-source research."""
from pathlib import Path
import hashlib,json,re,unicodedata
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode

ROOT=Path(__file__).resolve().parent
RESEARCH=ROOT/'research'
def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFD',str(value)).lower() if unicodedata.category(c)!='Mn')
def key(value):
    value=norm(value)
    for word in ['dal cotone','capilar','cachos','nutritiva','nutritivas']:
        value=value.replace(word,'')
    value=re.sub(r'\b(de|do|da|com)\b',' ',value)
    value=value.replace('vitaminicas','vitaminica')
    value=re.sub(r'(\d)\s+(ml|kg|g|l)\b',r'\1\2',value)
    return ''.join(sorted(re.findall(r'[a-z0-9]+',value)))
def product_type(name):
    n=norm(name)
    if n.startswith('kit'):return 'Kits'
    if 'body splash' in n:return 'Body splashes'
    if 'perfume capilar' in n:return 'Perfumes capilares'
    if 'parfum' in n or 'perfume' in n:return 'Perfumes'
    for word,label in [('shampoo','Shampoos'),('condicionador','Condicionadores'),('mascara','Máscaras'),('ampola','Ampolas'),('crono','Ampolas'),('tonico','Tônicos')]:
        if word in n:return label
    return 'Finalizadores'
def product_line(name):
    n=norm(name)
    for label in ['Power Curls','Power Repair','Max Force','Hydra Ceramides','Force Life','Monovin','Blond Up',"L'Amour"]:
        if norm(label).replace("'",'') in n.replace("'",''):return label
    if 'detox' in n:return 'S.O.S Detox'
    if 'body splash' in n or 'parfum' in n:return 'Perfumaria'
    if 'teia' in n:return 'Efeito Teia'
    return 'Cuidados especiais'
def array(value):return value if isinstance(value,list) else [value] if isinstance(value,str) and value else []

research=json.loads((RESEARCH/'catalog-list.json').read_text())
products=[]
for raw in research['products']:
    products.append({'id':'','name':raw['name'],'url':raw['url'],'priceSource':raw['url'],'price':raw.get('price'),'regularPrice':raw.get('regularPrice'),'imageUrl':raw.get('imageUrl'),'actives':[],'benefits':[],'indication':None,'use':None,'inci':None,'contents':None,'notes':array(raw.get('notes')),'priceNote':'Preço capturado em página oficial; pode variar com promoções. Confirme online antes de apresentar uma proposta.','detailLevel':'basic'})
unmatched=[]
for filename in ['details.json','perfumaria.json']:
    path=RESEARCH/filename
    if not path.exists():continue
    document=json.loads(path.read_text())
    for detail in document.get('produtos',document.get('products',[])):
        name=detail.get('nome',detail.get('name',''));url=detail.get('url','')
        aliases=[name,*array(detail.get('aliases'))]
        candidates=[p for p in products if key(p['name']) in [key(a) for a in aliases]]
        if not candidates and '/products/' in url:candidates=[p for p in products if p['url']==url]
        if len(candidates)>1:
            exact=[p for p in candidates if key(p['name'])==key(name)]
            candidates=exact if exact else candidates[:1]
        if not candidates:
            p={'name':name,'url':url,'priceSource':url,'price':detail.get('precoPublico'),'regularPrice':None,'imageUrl':detail.get('imageUrl'),'notes':[],'priceNote':'Preço capturado em página oficial; sujeito a alteração.'}
            products.append(p);candidates=[p];unmatched.append(name)
        for p in candidates:
            contents=detail.get('conteudoKit') or detail.get('conteudo')
            if isinstance(contents,list):contents='; '.join(contents)
            level='partial' if detail.get('detalhamentoStatus')=='parcial' else 'detailed'
            p.update(actives=array(detail.get('ativos')),olfactoryNotes=detail.get('notasOlfativas'),benefits=array(detail.get('beneficios')),indication=detail.get('indicacao'),use=detail.get('modoUso'),inci=detail.get('composicaoINCI'),contents=contents,detailLevel=level)
            if detail.get('imageUrl'):p['imageUrl']=detail['imageUrl']
            # The broad catalog was checked against the current promotional pages.
            if p.get('price') is None:p['price']=detail.get('precoPublico')
            if p['url'].find('/products/')<0 and '/products/' in url:p['url']=url
            p['notes']=list(dict.fromkeys(array(p.get('notes'))+array(detail.get('observacoes'))))
            if detail.get('composicaoStatus'):p['notes'].append(detail['composicaoStatus'])

dedup={}
for p in products:
    identity=key(p['name'])
    if identity not in dedup or p.get('detailLevel')=='detailed':dedup[identity]=p
products=list(dedup.values())
for p in products:
    p['id']=hashlib.sha256(key(p['name']).encode()).hexdigest()[:16]
    p['line']=product_line(p['name']);p['type']=product_type(p['name']);p.setdefault('detailLevel','basic')
    text=norm(' '.join([p['name'],p.get('indication') or '',*p.get('benefits',[])]))
    rules={'Hidratação':['hidrat','ressec'],'Nutrição':['nutri','lipid'],'Reconstrução':['reconstr','reparacao','reparar','danific','fragiliz'],'Cachos':['cacho','cachead','crespo','ondulado'],'Frizz':['frizz','alinhamento'],'Oleosidade':['oleos','oleoso'],'Loiros':['loiro','platinad','descolor','matiz'],'Fortalecimento':['fortalec','crescimento','quebra'],'Perfumaria':['body splash','parfum']}
    p['needs']=[label for label,terms in rules.items() if any(term in text for term in terms)]
    p['price']=float(p['price']) if isinstance(p.get('price'),(int,float)) else None
    for field in ['actives','benefits','notes']:p.setdefault(field,[])
    for field in ['indication','use','inci','contents','imageUrl']:p.setdefault(field,None)
    if p['imageUrl']:
        p['imageSource']=p['imageUrl']
        url=urlsplit(p['imageUrl']);params=dict(parse_qsl(url.query));params['width']='600'
        p['imageUrl']=urlunsplit((url.scheme,url.netloc,url.path,urlencode(params),url.fragment))
products.sort(key=lambda p:norm(p['name']))
snapshot={'title':'Guia do Consultor — Dal Cotone','version':'2026-11-06.1','queriedAt':'2026-11-06','dateLabel':'06/11/2026','currency':'BRL','reportedCatalogCount':89,'coverageNote':f"Foram identificados {len(products)} produtos nas fontes acessíveis. A loja anunciava 89 itens; a cobertura total e o catálogo profissional ainda precisam de conferência.",'sources':['https://dalcotone.com.br/collections/all','https://dalcotone.com.br/products/'],'products':products}
from organize_catalog import enrich
snapshot=enrich(snapshot,RESEARCH)
(ROOT/'dist/catalog.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2))
print(json.dumps({'products':len(products),'detailed':sum(p['detailLevel']=='detailed' for p in products),'photos':sum(bool(p['imageUrl']) for p in products),'additionalDetailProducts':unmatched},ensure_ascii=False))
