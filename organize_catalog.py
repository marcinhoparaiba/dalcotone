"""Organize reviewed products for study; keep unsupported fields explicit."""
import hashlib,json,re,unicodedata
from pathlib import Path
def norm(text):return ''.join(c for c in unicodedata.normalize('NFD',str(text)).lower() if unicodedata.category(c)!='Mn')
def matchkey(text):return re.sub(r'[^a-z0-9]','',norm(text))
def family(name):
    n=norm(name)
    for token,label in [('24k','24K'),('max force','Max Force'),('power repair','Power Repair'),('power curls','Power Curls'),('hydra ceramides','Hydra Ceramides'),('force life','Force Life'),('monovin','Monovin'),('blond up','Blond Up'),("l'amour","L’Amour"),('l’amour','L’Amour'),('s.o.s detox','S.O.S Detox'),('sos detox','S.O.S Detox'),('ph control','pH Control'),('bio plastia','Bio Plastia'),('oxo','Oxo Fusion'),('silk fiber','Silk Fiber'),('envelopamento','Envelopamento dos Fios'),('envolpamento','Envelopamento dos Fios'),('clean care','Clean Care'),('washing','Washing'),('bleached','Bleached'),('color creams','Color Creams'),('necessity','Necessity Use'),('must use','Force Life'),('golden','Golden Premium'),('luminous','Power Luminous Oil'),('argan oil','Argan Oil'),('crono','Cronograma'),('nutri protein','Cronograma'),('restore','Cronograma'),('verniz','Cronograma'),('ultra magic','Ampolas'),('vitaminica','Ampolas'),('queratina','Queratina')]:
        if token in n:return label
    if 'teia' in n:return 'Efeito Teia'
    if 'splash' in n or 'parfum' in n:return 'Perfumaria'
    return 'Tratamentos complementares'
def load(path):return json.loads(path.read_text())
def enrich(snapshot,research):
    products=snapshot['products'];pro=load(research/'professional-lines.json');guide=load(research/'active-guide.json');reviews=load(research/'kits-review.json')['kits'];pro_map={}
    for entry in pro['produtos']:
        name=entry['nome'];size=entry.get('tamanho')
        if size and matchkey(size) not in matchkey(name):name+=' '+size
        candidates=[p for p in products if matchkey(p['name'])==matchkey(name)]
        if entry['id']=='24k-spray-spray':candidates=[p for p in products if '24k' in norm(p['name']) and 'spray' in norm(p['name'])]
        if not candidates:
            identifier='pro-'+entry['id'];source=entry['proveniencia']['url']
            p={'id':identifier,'name':name,'url':source,'priceSource':source,'price':None,'regularPrice':None,'priceNote':'Preço público oficial não localizado para esta apresentação profissional.','imageUrl':entry.get('imageUrl'),'actives':entry.get('ativos',[]),'benefits':[entry['funcao']] if entry.get('funcao') else [],'indication':entry.get('indicacao'),'use':entry.get('modoUso'),'inci':entry.get('composicaoINCI'),'contents':None,'notes':entry.get('observacoes',[])+['Identificado no catálogo oficial 2025; disponibilidade atual não confirmada.'],'detailLevel':'partial','type':'Shampoos' if 'shampoo' in norm(name) else 'Condicionadores' if 'condicionador' in norm(name) else 'Máscaras' if any(t in norm(name) for t in ['mask','mascara','botox']) else 'Produtos profissionais','needs':[],'sourceKind':'official-catalog','sourcePage':entry['proveniencia'].get('paginaImpressa')}
            products.append(p);candidates=[p]
        p=candidates[0];pro_map[entry['id']]=p['id'];p['categories']=list(dict.fromkeys(entry.get('categorias',[])));p['line']=family(p['name'])
    if not any('ph control' in norm(p['name']) for p in products):
        products.append({'id':'consultor-ph-control','name':'pH Control','url':'https://dalcotone.com.br/','priceSource':'https://dalcotone.com.br/','price':None,'imageUrl':None,'actives':[],'benefits':[],'indication':None,'use':None,'inci':None,'contents':None,'notes':[guide['phControl']['status']],'detailLevel':'partial','type':'Controle de pH','line':'pH Control','categories':['Controle de pH'],'needs':[],'sourceKind':'consultor','aliases':['queridinho','regulador de pH'],'priceNote':'Preço público oficial ainda não confirmado.'})
    defaults={'24K':'Finalização','Max Force':'Reconstrução','Power Repair':'Hidratação','Power Curls':'Cachos','Hydra Ceramides':'Hidratação','Force Life':'Controle de oleosidade','Monovin':'Fortalecimento','Blond Up':'Matização','L’Amour':'Nutrição','S.O.S Detox':'Detox','pH Control':'Controle de pH','Necessity Use':'Reconstrução','Golden Premium':'Finalização','Power Luminous Oil':'Nutrição','Argan Oil':'Finalização','Cronograma':'Cronograma capilar','Ampolas':'Ampolas','Efeito Teia':'Reconstrução','Perfumaria':'Perfumaria','Tratamentos complementares':'Cuidados complementares'}
    aliases={'Botox capilar':'Botox','Limpeza / Purificação':'Detox','Limpeza e purificação':'Detox','Oleosidade':'Controle de oleosidade','Coloração e descoloração':'Coloração / Descoloração','Retexturização':'Selagem','Alinhamento':'Selagem'}
    for p in products:
        p['line']=family(p['name']);p.setdefault('sourceKind','official-page')
        categories=[aliases.get(c,c) for c in p.get('categories',[])]
        if not categories:categories=[defaults.get(p['line'],'Cuidados complementares')]
        if p['line']=='Efeito Teia' and 'banana' in norm(p['name']):categories=['Hidratação','Nutrição']
        if 'nutri protein' in norm(p['name']):categories=['Nutrição']
        if 'restore' in norm(p['name']) and p['type']!='Kits':categories=['Reconstrução']
        if 'verniz' in norm(p['name']) and p['type']!='Kits':categories=['Hidratação']
        p['categories']=list(dict.fromkeys(categories));p['primaryCategory']=p['categories'][0];p['needs']=list(dict.fromkeys(p.get('needs',[])+p['categories']))
        p['occasions']=[p['indication']] if p.get('indication') else []
        if p.get('use') and any(t in norm(p['use']) for t in ['secador','prancha','calor']):p['occasions'].append('Na etapa de finalização com calor, conforme o modo de uso desta ficha.')
        p['activeDetails']=[]
        for active in p.get('actives',[]):
            found=next((a for a in guide['actives'] if matchkey(active) in [matchkey(a['name']),*[matchkey(v) for v in a.get('aliases',[])]]),None)
            p['activeDetails'].append({'name':active,'role':found['role'] if found else None,'scope':found.get('scope') if found else None,'sourceUrl':found.get('sourceUrl') if found else None})
    by_id={p['id']:p for p in products}
    for review in reviews:
        p=by_id[review['productId']];p['kitReview']=review;p['kitItems']=review['items'];p['notes']=list(dict.fromkeys(p.get('notes',[])+review['notes']))
        category=aliases.get(review.get('mainCategory'),review.get('mainCategory'))
        if category in ['Limpeza/Purificação','Limpeza e purificação']:category='Detox'
        if category:p['categories']=[category];p['primaryCategory']=category
        for item in p['kitItems']:
            if item.get('volume'):
                target=matchkey(item['name']+' '+item['volume'])
                exact=[candidate for candidate in products if candidate['type']!='Kits' and matchkey(candidate['name'])==target]
                if len(exact)==1:item['productId']=exact[0]['id']
    for p in products:
        if 'crono plus' in norm(p['name']) and p.get('contents'):
            p['type']='Kits';p['kitItems']=[{'name':'Ampolas Crono Plus+','quantity':4,'volume':'18 mL','productId':None}]
            p['kitReview']={'status':'partial','sourceUrls':[p['url']],'notes':['A ficha menciona quatro ampolas de 18 mL. A identificação individual de todas as etapas ainda precisa de confirmação.']}
            reviews.append({'status':'partial'})
    # User-supplied assembly is a study reference, never a fabricated official SKU/price.
    kit={'id':'consultor-kit-24k','name':'Kit 24K — shampoo, selagem e máscara','line':'24K','primaryCategory':'Selagem','categories':['Selagem','Botox'],'url':'https://dalcotone.com.br/','priceSource':'https://dalcotone.com.br/','price':None,'priceNote':'Kit informado pelo consultor; preço público oficial não confirmado.','imageUrl':None,'actives':[],'activeDetails':[],'benefits':[],'indication':None,'occasions':[],'use':None,'inci':None,'contents':None,'notes':['Composição informada pelo consultor: shampoo, selagem e máscara. O catálogo oficial identifica a selagem e a máscara 24K, mas não confirma o nome/apresentação do shampoo deste kit. Não é o Spray 24K.'],'detailLevel':'partial','type':'Kits','needs':['Selagem','Botox'],'sourceKind':'consultor','kitItems':[{'name':'Shampoo do Kit 24K','quantity':1,'volume':None,'productId':None},{'name':'Selagem 24K Premium','quantity':1,'volume':None,'productId':pro_map.get('24k-premium-selagem')},{'name':'Máscara 24K Premium / Intensive Treatment Mask','quantity':1,'volume':None,'productId':pro_map.get('24k-mask-mask')}],'kitReview':{'status':'consultor','sourceUrls':[],'notes':['Montagem informada pelo consultor; detalhes comerciais ainda não confirmados.']}}
    products.append(kit)
    pdf_technical={item['productId']:item for item in load(research/'pdf-technical.json')['products']} if (research/'pdf-technical.json').exists() else {}
    pdf_photos={item['productId']:item for item in load(research/'pdf-photos.json')['images']} if (research/'pdf-photos.json').exists() else {}
    for p in products:
        review=pdf_technical.get(p['id'])
        if review:
            p['name']=review.get('name') or p['name']
            for field in ['actives','activeDetails','benefits','indication','use']:
                if review.get(field) is not None:p[field]=review[field]
            p['sourceKind']='official-catalog';p['url']=pro['fontes'][0] if isinstance(pro['fontes'][0],str) else pro['fontes'][0]['url']
            p['sourcePage']=review.get('sourcePage');p['notes']=[n for n in p.get('notes',[]) if not any(t in n.lower() for t in ['nome confirmado pelo consultor','ficha técnica, preço público e imagem'])]+review.get('notes',[])
            if review.get('occasions'):
                p['occasions']=[(o['name']+': '+o['use']) if isinstance(o,dict) else o for o in review['occasions']]
            for active in p.get('activeDetails',[]):active.setdefault('sourceUrl',p['url']);active.setdefault('scope','manufacturer-claim')
        if p['id'] in pdf_photos:
            photo=pdf_photos[p['id']];p['imageUrl']=photo['imageUrl'];p['imageSource']=p['url'];p['imageOrigin']='Foto extraída do catálogo oficial 2025';p['imagePage']=photo['page']
        sizes=re.findall(r'\b\d+(?:[.,]\d+)?\s*(?:kg|ml|mL|g|L|l)\b',p['name'])
        p['technical']={'line':p['line'],'productType':p['type'],'presentation':', '.join(sizes) or None,'declaredPH':review.get('declaredPH') if review else None,'concentrations':review.get('concentrations') if review else None,'fullFormulaAvailable':bool(p.get('inci')),'sourceKind':p.get('sourceKind'),'sourcePage':p.get('sourcePage')}
        p['differentials']=[]
        if p.get('actives'):
            p['differentials'].append({'title':'Ativos destacados na formulação','text':'; '.join(p['actives']),'evidence':'Ativos divulgados na fonte desta ficha; concentração e efeito isolado não confirmados.','sourceUrl':p['url']})
        if p.get('benefits'):
            p['differentials'].append({'title':'Proposta e função do produto','text':'; '.join(p['benefits']),'evidence':'Benefícios declarados pela marca, não um ensaio comparativo independente.','sourceUrl':p['url']})
        if p.get('kitItems'):
            p['differentials'].append({'title':'Composição desta versão do kit','text':'; '.join(i['name']+((' · '+i['volume']) if i.get('volume') else '') for i in p['kitItems']),'evidence':'Itens conferidos conforme o status do kit; montagens do consultor estão identificadas.','sourceUrl':p['url']})
        if p['line']=='24K' and 'spray' in norm(p['name']):
            p['differentials'].insert(0,{'title':'Tecnologia termoativada de efeito memória','text':'A marca descreve Lisselini e Silsoft AX-E para alinhamento e acabamento antifrizz com ativação por calor. É um finalizador; não é a Selagem 24K.','evidence':'Descrição técnica da página oficial do Spray 24K.','sourceUrl':p['url']})
        p['commercialSummary']='Proposta descrita pela marca: '+ '; '.join(p['benefits'][:3])+'.' if p.get('benefits') else None
        p['competitiveEvidence']=None
    order=['Reconstrução','Selagem','Botox','Detox','Hidratação','Nutrição','Controle de pH','Cachos','Matização','Fortalecimento','Controle de oleosidade','Finalização','Cronograma capilar','Ampolas','Preparação','Limpeza profunda','Limpeza','Condicionamento','Coloração / Descoloração','Perfumaria','Cuidados complementares']
    all_categories=list(dict.fromkeys(order+[c for p in products for c in p['categories']]))
    snapshot['categories']=[{'name':c,'count':sum(c in p['categories'] for p in products)} for c in all_categories if any(c in p['categories'] for p in products)]
    approaches=load(research/'approaches.json')
    snapshot['lines']=[{'name':name,'categories':list(dict.fromkeys(c for p in products if p['line']==name for c in p['categories'])),'productIds':[p['id'] for p in products if p['line']==name],'kitIds':[p['id'] for p in products if p['line']==name and p['type']=='Kits'],'approach':approaches['lines'][name]} for name in sorted(set(p['line'] for p in products),key=norm)]
    snapshot['kitAudit']={'total':len(reviews),'confirmed':sum(r['status']=='confirmed' for r in reviews),'partial':sum(r['status']=='partial' for r in reviews),'unavailable':sum(r['status']=='unavailable' for r in reviews),'consultorAssemblies':1}
    snapshot['company']=load(research/'company.json');snapshot['company']['brandApproach']=approaches['brand'];snapshot['company']['pitch']=approaches['brand']['short']
    for p in products:
        approach=approaches['lines'][p['line']]
        if p.get('benefits'):
            opening=f"Este é o {p['name']}. A proposta descrita pela marca inclui "+'; '.join(p['benefits'][:3])+'.'
        else:opening=f"Este é o {p['name']}. A ficha técnica ainda tem informações a confirmar; prefiro verificá-las antes de atribuir um resultado específico ao produto."
        if p.get('actives'):opening+=' Entre os ativos divulgados estão '+', '.join(p['actives'])+'.'
        p['presentation']={'question':approach['question'],'opening':opening,'nextStep':'Posso mostrar a ficha e conferir se essa proposta faz sentido para a necessidade que você me contou?','scope':'Sugestão de fala baseada nos campos catalogados; não é um depoimento ou garantia de resultado.'}
    snapshot['activeLibrary']=guide['actives'];snapshot['version']='2026-11-06.3';snapshot['coverageNote']='Catálogo de estudo reunindo páginas oficiais e o catálogo profissional 2025. Disponibilidade, preços e campos sem fonte atual estão sinalizados; não é uma lista de estoque.'
    snapshot['products']=sorted(products,key=lambda p:norm(p['name']))
    return snapshot
