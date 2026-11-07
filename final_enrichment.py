"""Current page extracts complement the dated PDF; missing captures are not absent facts."""
import json,re
from salon_presentations import polish
def read(root,name):return json.loads((root/name).read_text())
def enrich_current(products,research):
    by={p['id']:p for p in products}
    hair=read(research,'final-hair-page-audit.json')
    for entry in hair['corrections']:
        p=by.get(entry['productId'])
        if not p:continue
        truncated=entry.get('truncated',{})
        p.setdefault('fieldSources',{})
        for source_field,target in [('descriptionExcerpt','description'),('indicationExcerpt','indication'),('use','use')]:
            flag={'descriptionExcerpt':'description','indicationExcerpt':'indication','use':'use'}[source_field]
            value=entry.get(source_field)
            if value and not truncated.get(flag):
                if target=='use' and p['id'] in ['0362c5b04fc5ffb5','daff3cb1e87f8b2f','2c7828de22074cce'] and p.get('use') and p['use']!=value:
                    p.setdefault('instructionVersions',[]).append({'label':'Orientação registrada anteriormente · conferir edição','text':p['use'],'url':p['url']})
                p[target]=polish(value)
                if target=='indication':p['occasions']=[p[target]]
                p['fieldSources'][target]={'label':'Página individual oficial · consulta07/11/2026','url':entry['url']}
        if entry.get('compositionStatement') and not truncated.get('composition'):
            p['rawSiteComposition']=polish(entry['compositionStatement']);p['compositionKind']=entry['compositionKind']
        p['url']=entry['url'];p['sourceKind']='official-page'
        if not p.get('occasions') and p.get('indication'):p['occasions']=[p['indication']]
    perfumes=read(research,'final-perfumery-page-audit.json')
    for entry in perfumes['products']:
        p=by.get(entry['productId'])
        if not p or entry['status']=='inaccessible':continue
        for field,value in entry.get('fields',{}).items():
            if field=='composition':continue
            if field=='contents' and isinstance(value,list):value='; '.join(value)
            p[field]=polish(value)
        p['notes']=entry.get('notes',[])
        if entry.get('sourceUrl'):p['url']=entry['sourceUrl']
        p['rawSiteComposition']=polish(entry.get('rawSiteComposition') or '')
        p['compositionKind']=entry.get('compositionKind')
        if entry.get('compositionKind') in ['ingredient_list_as_published','ingredient_list_in_portuguese_as_published']:
            p['inci']=entry.get('fields',{}).get('inci') or entry.get('fields',{}).get('composition') or entry.get('rawSiteComposition')
            p['compositionIsINCI']=False;p['compositionOrigin']='Lista de ingredientes declarada no site. Nomenclatura preservada; padronização INCI não conferida.'
        p.setdefault('fieldSources',{})
        for field in entry.get('fields',{}):p['fieldSources'][field]={'label':'Página oficial · consulta07/11/2026','url':entry.get('sourceUrl') or p['url']}
        if entry.get('fields',{}).get('actives'):
            old={a['name'].casefold():a for a in p.get('activeDetails',[])}
            p['activeDetails']=[old.get(a.casefold(),{'name':a,'role':None,'sourceUrl':p['url']}) for a in p['actives']]
    kits=read(research,'final-kit-page-audit.json')
    for entry in kits['records']:
        p=by.get(entry['productId'])
        if not p or not entry.get('pageAccessed'):continue
        if entry.get('compositionSummary'):p['kitCompositionSummary']=polish(entry['compositionSummary'])
        if p['id']=='244136c3b5dfed21':continue
        components=entry.get('components') or []
        if components:
            p['kitItems']=[{'name':polish(x['name']),'quantity':x.get('quantity',1),'volume':polish(x.get('volume')),'productId':None} for x in components]
            p['kitReview']={'status':'confirmed' if all(i['volume'] for i in p['kitItems']) else 'partial','sourceUrls':[entry['url']],'notes':['Componentes recuperados na página individual em07/11/2026. Volumes não expressos permanecem a confirmar.']}
    # The current Crono page names four functions, without stating their volumes.
    crono=by['244136c3b5dfed21'];record=next(x for x in kits['records'] if x['productId']==crono['id'])
    uses=record.get('currentSections',{}).get('use',{}).get('exactText')
    if uses:crono['use']=polish(uses)
    items=[]
    for suffix,label in [('nutricao','Nutrição'),('tonico','Fortalecimento'),('hidratacao','Hidratação'),('reconstrucao','Reconstrução')]:
        child=by['crono-plus-'+suffix+'-18']
        child['name']='Crono Plus+ '+label+' · ampola';child['contents']=None;child['type']='Ampolas';child['technical']['presentation']=None
        child['imageContext']='Foto do conjunto de origem; volume individual não confirmado no texto atual.'
        child['imageOrigin']='Imagem do conjunto na página da loja'
        child['notes']=['Função descrita no texto atual. O volume não está confirmado nessa captura. O catálogo2025 mostra15mL; outra captura anterior da loja descreveu18mL.']
        child['use']='Aplicar no couro cabeludo limpo, massagear e não enxaguar. A orientação da página informa até2aplicações ao dia.' if label=='Fortalecimento' else 'Utilizar3–5mL em água fria até formar mousse, aplicar em fios limpos e molhados ou adicionar à máscara. Aguardar cerca de5min e enxaguar.'
        child['fieldSources']={'use':{'label':'Página oficial atual · função'+label,'url':crono['url']}}
        items.append({'name':'Crono Plus+ '+label,'quantity':1,'volume':None,'productId':child['id']})
    crono['kitItems']=items;crono['kitReview']={'status':'partial','sourceUrls':[crono['url']],'notes':['Quatro funções identificadas. Volume atual não confirmado no texto recuperado. PDF2025=15mL; captura anterior da loja=18mL. Não combinar apresentações.']}
    crono['contents']='Quatro ampolas: Nutrição, Fortalecimento, Hidratação e Reconstrução. Volume atual a confirmar.'
    # Do not retain an image of the old three-item Force Life bundle for today's two items.
    force=by['9297bd616196f4df']
    force['kitItems']=[{'name':'Shampoo Esfoliante Force Life','quantity':1,'volume':'300 mL','productId':'85e6ca2844f6803d'},{'name':'Máscara Revitalizante Force Life','quantity':1,'volume':'300 g','productId':'23691f31ecfc8833'}]
    force['kitReview']={'status':'confirmed','sourceUrls':[force['url']],'notes':['A página atual apresenta shampoo300mL e máscara300g. O condicionador da referência antiga não integra esta composição recuperada.']}
    force['imageUrl']=None;force['imageOrigin']='Consulte as fotografias dos dois componentes documentados.'
    force['contents']='Shampoo Esfoliante Force Life 300mL + Máscara Revitalizante Force Life 300g.'
    force['compositionCaptures']=[{'label':'Outra descrição recuperada da mesma página','text':'Shampoo: partículas de sílica; complexo de aminoácidos, PCA e lactato de sódio; extratos de bambu, alfafa, lúpulo, alecrim, trevo-amarelo e jaborandi. Máscara: manteiga de abacate, agentes condicionantes e o complexo de aminoácidos/extratos. Os destaques diferem da captura que nomeia Capilmax, bambu e jaborandi. Conferir a fórmula da embalagem.'}]
    # Recompute summaries affected by the current page data.
    for p in products:
        if p.get('technical'):p['technical']['productType']=p['type']
        if p.get('technical'):p['technical']['fullFormulaAvailable']=bool(p.get('inci')) and p.get('compositionIsINCI') is not False
        if p['line']=='Perfumaria' and p['type']!='Kits' and 'body splash' in p['name'].lower():p['type']='Body splashes masculinos' if 'masculino' in p['name'].lower() else 'Body splashes femininos'
    return products
