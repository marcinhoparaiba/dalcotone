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
    # The consultant's 24K example is not an official product or kit.
    audit=load(research/'full-technical-audit.json')
    pdf_url=pro['fontes'][0] if isinstance(pro['fontes'][0],str) else pro['fontes'][0]['url']
    for entry in audit['missingProducts']:
        fields=entry['fields'];supplement=entry['productId']=='pdf-woman-caps'
        products.append({'id':entry['productId'],'name':('Woman Caps — suplemento alimentar 60 cápsulas' if supplement else 'Shampoo L’Amour Strawberry 300 mL'),'url':pdf_url,'priceSource':pdf_url,'price':None,'regularPrice':None,'priceNote':'Preço público oficial não localizado para esta apresentação.','imageUrl':None,'actives':fields.get('actives',[]),'activeDetails':[{'name':a,'role':None} for a in fields.get('actives',[])],'benefits':[],'indication':fields.get('indication'),'use':fields.get('use'),'inci':None,'contents':None,'notes':entry['notes'],'detailLevel':'partial','type':'Suplementos' if supplement else 'Shampoos','line':'Monovin' if supplement else "L’Amour",'primaryCategory':'Cuidados complementares' if supplement else 'Nutrição','categories':['Cuidados complementares'] if supplement else ['Nutrição'],'needs':['Cuidados complementares'] if supplement else ['Nutrição'],'sourceKind':'official-catalog','sourcePage':entry['page']})
    pdf_technical={item['productId']:item for item in load(research/'pdf-technical.json')['products']} if (research/'pdf-technical.json').exists() else {}
    pdf_photos={item['productId']:item for item in load(research/'pdf-photos.json')['images']} if (research/'pdf-photos.json').exists() else {}
    audited_functions=load(research/'audited-active-functions.json')
    web_corrections={x['productId']:x for x in load(research/'current-web-corrections.json')['products']}
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
        web=web_corrections.get(p['id'])
        if web:
            p['fieldSources']={key:{'label':'Página oficial · consulta06/11/2026','url':web['sourceUrl']} for key in web['fields']}
            p.update(web['fields'])
            if 'actives' in web['fields']:p['activeDetails']=[{'name':a,'role':None,'sourceUrl':web['sourceUrl']} for a in p['actives']]
            if web.get('kitItems'):
                p['kitItems']=web['kitItems'];p['kitReview']={'status':'confirmed','sourceUrls':[web['sourceUrl']],'notes':['Componentes e volumes conferidos na descrição atual da página oficial.']}
        if p['id'] in pdf_photos:
            photo=pdf_photos[p['id']];p['imageUrl']=photo['imageUrl'];p['imageSource']=p['url'];p['imageOrigin']='Foto extraída do catálogo oficial 2025';p['imagePage']=photo['page']
        if p['id'] in audited_functions:
            roles={norm(x['name']):x for x in audited_functions[p['id']]}
            for active in p.get('activeDetails',[]):
                match=roles.get(norm(active['name']))
                if match:
                    active.update({'role':match['role'],'scope':'blend' if match.get('scope') in ['collective','blend'] else 'manufacturer-claim','sourceUrl':pdf_url,'sourcePage':match['sourcePage']})
        sizes=re.findall(r'\b\d+(?:[.,]\d+)?\s*(?:kg|ml|mL|g|L|l)\b',p['name'])
        extra=next((x for x in audit['missingProducts'] if x['productId']==p['id']),None)
        p['technical']={'line':p['line'],'productType':p['type'],'presentation':', '.join(sizes) or None,'declaredPH':review.get('declaredPH') if review else extra['fields'].get('declaredPH') if extra else None,'concentrations':review.get('concentrations') if review else None,'fullFormulaAvailable':bool(p.get('inci')),'sourceKind':p.get('sourceKind'),'sourcePage':p.get('sourcePage')}
        p['sourceDifferences']=[x for x in audit['contradictions'] if x['productId']==p['id']]
        descriptions={
            'eef86335c476b86a':'A página da loja publica pausas de3–5min para shampoo e10–20min para máscara. O catálogo2025 apresenta orientações diferentes para as versões profissional e Home Care.',
            '2c7828de22074cce':'O catálogo2025 Home Care publica pausa de5–10min; a ficha da loja consultada indica3min para o shampoo. Confirme a edição do rótulo.',
            'b72901db8710aa58':'As páginas profissional e Home Care do catálogo2025 apresentam instruções distintas de acabamento e enxágue. Confira a apresentação de300mL.',
            '48678d0216074934':'Os ativos divulgados pela loja e pelo catálogo2025 são diferentes. As duas referências aparecem separadas nesta ficha.',
            '4b0b72183af62db7':'A loja publica pausa de7min para Restore500g. O tempo de10–15min do kit250g não deve ser aplicado automaticamente à embalagem500g.',
            '3e6b73f994297918':'O rótulo do catálogo2025 mostra pH3,5–4,5; a descrição da loja consultada informa3,0–4,0.',
            'pro-color-creams-coloracao':'O catálogo publica nuances e corretores, mas não fornece proporção de mistura ou tempo de pausa. Consulte a instrução da embalagem.'}
        for difference in p['sourceDifferences']:difference['description']=descriptions[p['id']]
        p['historicalFields']=[{'source':'Catálogo oficial 2025','page':x['page'],'fields':x['fields']} for x in audit['products'] if x['productId']==p['id'] and p['id'] in ['48678d0216074934','28860487c0334cd1','244136c3b5dfed21']]
        p['variants']=[x for x in audit['missingVariants'] if x['productId']==p['id']]
        if p['id']=='244136c3b5dfed21':
            p['notes'].append('Divergência de apresentação: catálogo2025 mostra quatro ampolas de15mL; ficha da loja menciona18mL. Não tratar como a mesma apresentação confirmada.')
        if p['id']=='pro-color-creams-coloracao':
            p['indication']='Coloração permanente de uso profissional; seleção de nuance conforme avaliação do colorista.'
            p['notes'].append('O catálogo não publica proporção de mistura ou tempo de pausa. Conferir a instrução da embalagem desta versão antes do procedimento.')
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
    snapshot['kitAudit']={'total':len(reviews),'confirmed':sum(r['status']=='confirmed' for r in reviews),'partial':sum(r['status']=='partial' for r in reviews),'unavailable':sum(r['status']=='unavailable' for r in reviews),'consultorAssemblies':0}
    snapshot['company']=load(research/'company.json');snapshot['company']['brandApproach']=approaches['brand'];snapshot['company']['pitch']=approaches['brand']['short']
    for p in products:
        approach=approaches['lines'][p['line']]
        if p.get('benefits'):
            opening=f"Este é o {p['name']}. A proposta descrita pela marca inclui "+'; '.join(p['benefits'][:3])+'.'
        else:opening=f"Este é o {p['name']}. A ficha técnica ainda tem informações a confirmar; prefiro verificá-las antes de atribuir um resultado específico ao produto."
        if p.get('actives'):opening+=' Entre os ativos divulgados estão '+', '.join(p['actives'])+'.'
        p['presentation']={'question':approach['question'],'opening':opening,'nextStep':'Posso mostrar a ficha e conferir se essa proposta faz sentido para a necessidade que você me contou?','scope':'Sugestão de fala baseada nos campos catalogados; não é um depoimento ou garantia de resultado.'}
        if p['type']=='Suplementos':p['presentation']={'question':'Você procura informações sobre este suplemento e já conferiu a composição e as recomendações do rótulo?','opening':'Woman Caps é um suplemento alimentar para adultos, apresentado pela marca com vitamina B5. A tabela nutricional completa não está disponível no catálogo consultado.','nextStep':'Vamos conferir o rótulo atual e as orientações do profissional de saúde antes de qualquer recomendação de consumo.','scope':'Suplemento não é tratamento capilar tópico nem medicamento; não prometer crescimento ou tratamento de doenças.'}
    snapshot['activeLibrary']=guide['actives'];snapshot['version']='2026-11-06.3';snapshot['coverageNote']='Catálogo de estudo reunindo páginas oficiais e o catálogo profissional 2025. Disponibilidade, preços e campos sem fonte atual estão sinalizados; não é uma lista de estoque.'
    snapshot['products']=sorted(products,key=lambda p:norm(p['name']))
    return snapshot
