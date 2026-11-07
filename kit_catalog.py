"""Documented kit children and navigation; unknown kit volumes stay unknown."""
import copy,re,unicodedata

def key(value):
    return ''.join(c for c in unicodedata.normalize('NFD',value).lower() if c.isalnum() and unicodedata.category(c)!='Mn')

def add_children(products,pdf_url):
    by={p['id']:p for p in products}
    def child(parent_id,identifier,name,volume,page,fields=None):
        parent=by[parent_id]
        p=copy.deepcopy(parent)
        p.update(id=identifier,name=name,type='Ampolas' if 'Ampola' in name else 'Máscaras',price=None,regularPrice=None,priceSource=pdf_url,url=pdf_url,sourceKind='official-catalog',sourcePage=page,detailLevel='partial',contents=volume,kitItems=[],kitReview=None,imageUrl=None,occasions=[],notes=['Apresentação individual documentada no catálogo2025; preço unitário não localizado.'],priceNote='O valor do kit não equivale ao preço público avulso desta apresentação.')
        p.pop('technical',None)
        if fields:p.update(fields)
        products.append(p);by[identifier]=p
        return p
    for parent,identifier,name,page in [
        ('bb946e7d15bc1e95','pdf-ultra-magic-15','Ampola Ultra Magic 15 mL',42),
        ('cefb5c7098b88e45','pdf-vitaminica-15','Ampola Vitamínica Premium 15 mL',43)]:
        p=child(parent,identifier,name,'15 mL',page)
        if identifier=='pdf-vitaminica-15':
            p['actives']=['Complexo de vitaminas não discriminadas','Capilmax'];p['activeDetails']=[{'name':a,'role':None} for a in p['actives']]
        by[parent]['kitItems'][0]['productId']=identifier
    for identifier,name,need in [('pdf-verniz-250','Verniz Intense','Hidratação'),('pdf-nutri-protein-250','Nutri Protein','Nutrição'),('pdf-restore-250','Restore','Reconstrução')]:
        indications={'Verniz Intense':'Cabelos opacos, ásperos e com frizz.','Nutri Protein':'Cabelos fracos, quebradiços e sem vitalidade.','Restore':'Cabelos secos, volumosos e danificados por química.'}
        p=child('4d656c72af8742ad',identifier,'Máscara '+name+' 250 g','250 g',37,{'actives':[],'activeDetails':[],'benefits':[need],'categories':[need],'primaryCategory':need,'needs':[need],'indication':indications[name],'use':'Após a lavagem, aplicar sobre os fios úmidos, espalhar e massagear. Deixar10–15min e enxaguar completamente. Alternar as etapas conforme a necessidade dos fios.','notes':['Esta ficha corresponde à máscara250g do cronograma. A fórmula completa da apresentação250g não é publicada na página37; não foi copiada da embalagem500g.']})
    by['4d656c72af8742ad']['kitItems']=[{'name':name,'quantity':1,'volume':'250 g','productId':identifier} for identifier,name in [('pdf-verniz-250','Verniz Intense'),('pdf-nutri-protein-250','Nutri Protein'),('pdf-restore-250','Restore')]]
    # Four18mL stages are explicitly described in separate sections of the shop page.
    parent=by['244136c3b5dfed21'];source=parent['url'];items=[]
    stages=[('hidratacao','Hidratação','Hidratação e maciez; cuidado descrito para retenção de umidade.','Fios ressecados.'),('nutricao','Nutrição','Nutrição e melhora do aspecto áspero ou opaco.','Fios ásperos ou opacos.'),('reconstrucao','Reconstrução','Reparação cosmética de áreas porosas e danificadas.','Fios danificados ou porosos.'),('tonico','Tônico Capilar','Fortalecimento cosmético na rotina do couro cabeludo.','Cabelos finos e enfraquecidos, conforme a página oficial.')]
    for suffix,label,benefit,indication in stages:
        identifier='crono-plus-'+suffix+'-18';name='Crono Plus+ '+label+' 18 mL'
        p=child(parent['id'],identifier,name,'18 mL',None,{'line':'Cronograma','type':'Tônicos' if suffix=='tonico' else 'Ampolas','categories':['Fortalecimento' if suffix=='tonico' else label],'primaryCategory':'Fortalecimento' if suffix=='tonico' else label,'needs':['Fortalecimento' if suffix=='tonico' else label],'actives':[],'activeDetails':[],'benefits':[benefit],'indication':indication,'use':'Aplicar no couro cabeludo limpo, massagear e não enxaguar. A página informa até2aplicações ao dia.' if suffix=='tonico' else 'Misturar em água fria até formar mousse, ou aplicar em fios limpos e molhados. Aguardar cerca de5min e enxaguar completamente.','url':source,'priceSource':source,'sourceKind':'official-page','imageUrl':parent['imageUrl'],'imageContext':'Imagem do conjunto Crono Plus+18mL; não é foto avulsa da etapa.','imageOrigin':'Fotografia do conjunto na página oficial','notes':['Etapa e volume18mL descritos na página da loja. O catálogo2025 exibe ampolas15mL; as imagens dessa edição não foram usadas como foto18mL.'],'priceNote':'Etapa do conjunto Crono Plus+; preço de venda avulsa não publicado na fonte.'})
        items.append({'name':'Crono Plus+ '+label,'quantity':1,'volume':'18 mL','productId':identifier})
    parent['kitItems']=items;parent['kitReview']={'status':'confirmed','sourceUrls':[source],'notes':['Quatro etapas e volume18mL identificados na página da loja. O PDF2025 apresenta outra versão15mL.']}
    # Historical composition is scoped explicitly instead of asserted as current stock.
    for parent_id,page,components in [
        ('008a07353d60761c',11,[('Shampoo Blond Up','300 mL','847ff96acdc5f26b'),('Máscara Blond Up','300 g','ad696ecbb8523b00')]),
        ('eef86335c476b86a',10,[('Shampoo Blond Up Premium','1 L','6f9f4653036c50d2'),('Máscara Blond Up Premium','1 kg','a9a848c44de789fb')]),
        ('a2d935f4e04f38b2',31,[('Shampoo L’Amour','300 mL','pdf-lamour-shampoo-300'),('Máscara L’Amour','300 g','f663762decc4c6b9')])]:
        p=by[parent_id];p['kitItems']=[{'name':name,'quantity':1,'volume':volume,'productId':identifier} for name,volume,identifier in components];p['kitReview']={'status':'partial','sourceUrls':[pdf_url],'notes':['Composição de referência mostrada no catálogo2025, página'+str(page)+'. Conferir se corresponde à oferta atual antes de apresentar preço ou pedido.'],'compositionVersion':'Catálogo2025 · composição de referência'}
    return link_components(products)

def link_components(products):
    by={p['id']:p for p in products}
    # Resolve links by documented size; without size provide a labelled selection.
    for p in products:
        for item in p.get('kitItems',[]):
            if item.get('productId'):continue
            n=key(item['name']);candidates=[]
            for q in products:
                if q['type']=='Kits':continue
                qn=key(re.sub(r'\b\d+(?:[.,]\d+)?\s*(?:mL|ml|g|kg|L|l)\b','',q['name']))
                if n in qn or qn in n:candidates.append(q)
            if not candidates:
                role=next((word for word in ['shampoo','mascara','condicionador','tonico','creme','ativador','perfume'] if word in n),None)
                if role:candidates=[q for q in products if q['type']!='Kits' and key(q['line']) in n and role in key(q['name'])]
            if 'bodysplash' in n:
                fragrance=next((word for word in ['freshskin','sweetcrush','provoke','luxy'] if word in n),None)
                if fragrance:candidates=[q for q in products if q['type']!='Kits' and fragrance in key(q['name'])]
            if p['id']=='cefb5c7098b88e45':candidates=[by['pdf-vitaminica-15']]
            if p['id']=='bb946e7d15bc1e95':candidates=[by['pdf-ultra-magic-15']]
            if 'mustuse' in n:candidates=[by['0362c5b04fc5ffb5']]
            if 'argan' in n:candidates=[q for q in products if q['line']=='Argan Oil']
            if 'womancaps' in n:candidates=[by['pdf-woman-caps']]
            if item.get('volume'):
                exact=[q for q in candidates if key(item['volume']) in key(q['name'])]
                if len(exact)==1:item['productId']=exact[0]['id'];continue
            item['candidateProductIds']=[q['id'] for q in candidates]
    return products
