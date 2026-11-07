"""Sales study material anchored to each SKU, its stage, audience and source."""
import re,unicodedata
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
FOCUS={
'24K':'escolher entre alinhamento profissional, botox reconstrutor e acabamento termoativado',
'Ampolas':'encaixar um tratamento complementar em uma rotina que precisa de praticidade',
'Argan Oil':'melhorar o acabamento das pontas e o controle do frizz',
'Bio Plastia':'planejar um serviço profissional de retexturização',
'Bleached':'escolher a etapa de clareamento segundo a base, o objetivo e a condição da fibra',
'Blond Up':'controlar o amarelado e preservar a aparência dos cabelos claros',
'Clean Care':'preparar os fios com a limpeza anterior ao procedimento',
'Color Creams':'selecionar a nuance e a estratégia de coloração com o colorista',
'Cronograma':'separar hidratação, nutrição, reconstrução e fortalecimento por necessidade',
'Efeito Teia':'escolher a máscara pelo estado do comprimento e pelo acabamento desejado',
'Force Life':'tratar a rotina de uma raiz oleosa sem esquecer o comprimento',
'Golden Premium':'acrescentar brilho e controle de frizz à finalização',
'Hydra Ceramides':'cuidar do ressecamento e da superfície dos fios',
'L’Amour':'associar cuidado nutritivo, maciez e uma experiência de fragrância',
'Max Force':'cuidar da fibra fragilizada, especialmente na rotina após química',
'Monovin':'organizar uma rotina cosmética de fortalecimento',
'Necessity Use':'preparar e proteger o comprimento na finalização com calor',
'Oxo Fusion':'avaliar um procedimento profissional de alinhamento e controle do frizz',
'Perfumaria':'escolher uma fragrância corporal pelo perfil olfativo e pela ocasião',
'pH Control':'posicionar o cuidado de pH antes ou depois da química e na blindagem',
'Power Curls':'preservar a definição, o movimento e a maciez dos cachos',
'Power Luminous Oil':'valorizar o brilho e o toque das pontas na finalização',
'Power Repair':'cuidar do ressecamento, do frizz e da manutenção de cabelos coloridos',
'Queratina':'avaliar a necessidade de um cuidado reconstrutor na fibra',
'S.O.S Detox':'organizar limpeza, cuidado do couro cabeludo e proteção do comprimento',
'Silk Fiber':'selecionar uma retexturização profissional compatível com a avaliação da fibra',
'Washing':'estruturar a lavagem e o condicionamento na bancada do salão',
'Envelopamento dos Fios':'organizar uma rotina profissional de reconstrução e acabamento da fibra'}

def presentation(p,line,products):
    name=p['name'];n=norm(name);size=p.get('technical',{}).get('presentation') or p.get('contents') or 'descrita nesta ficha'
    professional=p['id'].startswith('pro-') or bool(re.search(r'\b(?:1\s*[Ll]|1\s*kg|2,5\s*L)\b',name)) or 'profissional' in n
    audience='na bancada do salão' if professional else 'na orientação de manutenção e revenda'
    focus=FOCUS[p['line']]
    roles=[a for a in p.get('activeDetails',[]) if a.get('role')]
    anchor=' '.join(a['name']+': '+a['role'] for a in roles[:2])
    ingredients=', '.join(p.get('actives',[])[:3])
    benefits='; '.join(p.get('benefits',[])[:2])
    reason=anchor or (('Os destaques divulgados são '+ingredients+'.') if ingredients else line['technicalReason'])
    if p['type']=='Kits':kind='kit'
    elif p['type']=='Suplementos':kind='supplement'
    elif p['line']=='Perfumaria':kind='fragrance'
    elif 'shampoo' in n:kind='shampoo'
    elif 'condicionador' in n:kind='conditioner'
    elif p['id']=='consultor-ph-control':kind='ph'
    elif p['line']=='Bleached':kind='lightener'
    elif p['line']=='Color Creams':kind='color'
    elif p['line']=='Queratina' or 'reconstrutor envelopamento' in n:kind='reconstructor'
    elif p['line'] in ['Bio Plastia','Oxo Fusion','Silk Fiber'] or ('selagem' in n):kind='chemical'
    elif 'mascara' in n or 'mask' in n:kind='mask'
    elif 'tonico' in n:kind='tonic'
    elif 'ampola' in n or p['type']=='Ampolas':kind='ampoule'
    elif 'perfume capilar' in n:kind='hair-fragrance'
    elif p['line'] in ['Argan Oil','Power Luminous Oil','Golden Premium']:kind='oil'
    elif p['line']=='Power Curls':kind='curl-finish'
    else:kind='finish'
    # These are stage-specific discovery questions, not a shared line introduction.
    questions={
    'lightener':f'Para avaliar {name}, qual é a base atual, o histórico químico, o objetivo de clareamento e a condição da fibra? Qual combinação o profissional pretende usar?',
    'color':f'Qual é a altura de tom atual, a cor desejada e o histórico da cliente para a escolha de {name}? Quem fará a análise de colorimetria?',
    'reconstructor':f'Que sinais de fragilidade ou porosidade levaram você a considerar {name}, e em qual etapa pretende usá-lo?',
    'shampoo':f'Na lavagem, o que mais atrapalha o atendimento: limpar a raiz ou manter o comprimento confortável? Como isso aparece nos clientes para os quais você avaliaria {name}?',
    'conditioner':f'Depois do tratamento, o comprimento continua difícil de desembaraçar ou perde o toque no enxágue? Em qual atendimento o {name} entraria?',
    'mask':f'Qual sinal você quer trabalhar com {name}: toque áspero, quebra, falta de brilho ou comportamento dos fios? Qual desses sinais aparece depois da lavagem?',
    'kit':f'Quais etapas dessa rotina o salão já atende bem e qual ainda falta? Vale comparar os componentes de {name} antes de propor o conjunto.',
    'chemical':f'Para avaliar {name}, qual é o histórico químico, a condição da fibra e o acabamento que a cliente deseja? Quem fará essa avaliação técnica no salão?',
    'ph':f'Em que ponto da química você precisa organizar o cuidado de pH: preparação, pós-procedimento ou blindagem? Essa resposta define o protocolo do {name}.',
    'oil':f'No acabamento, o incômodo maior é frizz nas pontas, falta de luminosidade ou toque ressecado? Em quais fios você quer avaliar {name}?',
    'curl-finish':f'Para quais clientes você avalia {name}: cachos que perdem definição, volume sem controle ou comprimento sem maciez? Como elas finalizam hoje?',
    'tonic':f'A cliente busca uma rotina cosmética de fortalecimento ou relata uma queixa de queda que precisa de avaliação de saúde? Essa distinção vem antes de apresentar {name}.',
    'ampoule':f'Em qual etapa da rotina você encaixaria {name}, e como vai diferenciar sua função das outras ampolas do atendimento?',
    'fragrance':f'Quem costuma escolher {name} no salão: prefere frescor, doçura ou maior presença de fragrância? A apresentação será para uso pessoal ou presente?',
    'hair-fragrance':f'A cliente quer perfumar o cabelo entre as lavagens ou completar a finalização com {name}? Como ela reage a fragrâncias nos fios?',
    'supplement':f'A pessoa já leu o rótulo e recebeu orientação adequada para avaliar {name}? A indicação não deve nascer somente de uma queixa capilar.',
    'finish':f'Onde o acabamento perde qualidade para os clientes que você atenderia com {name}: secagem, frizz, alinhamento ou brilho depois de finalizar?'}
    question=questions[kind]
    if kind=='shampoo':opening=f'Para {focus}, o {name} entra na etapa de limpeza. A proposta publicada inclui {benefits or "preparação da rotina"}. Eu apresentaria esta embalagem {audience}, observando a lavagem e o comportamento do comprimento antes de escolher as próximas etapas.'
    elif kind=='conditioner':opening=f'O {name} ocupa a etapa de condicionamento em uma rotina voltada a {focus}. A proposta é {benefits or "complementar o cuidado do comprimento"}. A avaliação deve observar desembaraço, toque e acabamento depois do enxágue, seguindo o tempo específico desta embalagem.'
    elif kind=='mask':opening=f'Eu posicionaria a {name} para {p.get("indication") or focus}. A proposta desta máscara é {benefits or focus}. A apresentação {size} precisa ser avaliada pelo efeito no comprimento e pelo protocolo próprio; tamanho de embalagem e etapa do cronograma fazem parte da escolha.'
    elif kind=='kit':
        names=[i['name']+((' '+i['volume']) if i.get('volume') else '') for i in p.get('kitItems',[])]
        opening=f'O {name} organiza uma rotina para {focus}. Os componentes identificados são '+', '.join(names)+'. Eu verificaria qual etapa falta no salão e como o conjunto se conecta à manutenção da cliente antes de propor a compra.'
    elif kind=='chemical':opening=f'O {name} é uma proposta de uso profissional para {focus}. A apresentação técnica começa pelo histórico químico, pelo estado da fibra e pelo protocolo da embalagem. A descrição do produto e a condição real do cabelo precisam orientar a escolha do procedimento.'
    elif kind=='lightener':opening=f'O {name} pertence à etapa profissional de clareamento. A apresentação e a concentração declaradas precisam ser conferidas antes de compor o protocolo. Eu relacionaria a escolha à base, ao objetivo e ao teste da fibra, usando a instrução específica do produto para proporção e pausa.'
    elif kind=='color':opening=f'A Color Creams60g deve ser apresentada pela escolha técnica de nuance: base atual, objetivo e estratégia do colorista. O catálogo organiza morenas, ruivas, loiros, super clareadores e corretores. Eu abriria os códigos disponíveis e a orientação da embalagem para planejar a aplicação.'
    elif kind=='reconstructor':opening=f'O {name} entra na avaliação de reparação cosmética da fibra. Os ativos divulgados são {ingredients or "os que constam na ficha"}. A apresentação deve relacionar a necessidade observada ao protocolo e ao acabamento esperado, respeitando a etapa e o enxágue indicados para o produto.'
    elif kind=='ph':opening=f'O {name} trabalha o cuidado de pH em situações diferentes: pré/pós-química e blindagem. Nano Link e LunaMatrix estão entre as tecnologias descritas. Eu escolheria primeiro a situação do atendimento e mostraria o protocolo correspondente, porque a pausa e o enxágue mudam conforme esse uso.'
    elif kind=='oil':opening=f'O {name} é uma opção de acabamento para {focus}. A proposta descrita inclui {benefits or "brilho e maciez"}'+(f', com destaque para {ingredients}.' if ingredients else '.')+' A avaliação deve observar o toque, a distribuição e a aparência das pontas na rotina de finalização.'
    elif kind=='fragrance':
        notes=p.get('olfactoryNotes') or {};profile='; '.join(k+': '+', '.join(v if isinstance(v,list) else [v]) for k,v in notes.items())
        opening=f'O {name} entra na escolha de fragrância corporal. '+(f'O perfil olfativo informado é {profile}. ' if profile else 'A escolha deve partir da avaliação olfativa da cliente. ')+f'Eu apresentaria a embalagem e o perfil de uso antes de comparar aromas. Notas olfativas descrevem o cheiro; não são uma lista de ingredientes nem uma promessa de fixação.'
    elif kind=='hair-fragrance':opening=f'O {name} é uma fragrância formulada para os fios, com proposta de {benefits or "perfumar o cabelo"}. Eu o apresentaria na conversa sobre finalização e experiência sensorial da cliente, mostrando a distância de aplicação e a orientação de uso desta ficha.'
    elif kind=='curl-finish':opening=f'O {name} atua na etapa de modelagem/finalização dos cachos. A proposta descrita é {benefits or focus}. Eu observaria o objetivo de definição e movimento, a técnica de aplicação e como o acabamento se mantém na rotina da cliente.'
    elif kind=='tonic':opening=f'O {name} tem aplicação voltada ao couro cabeludo na rotina descrita pela fonte. A conversa é sobre {benefits or "fortalecimento cosmético"}. A orientação de não enxaguar precisa ficar clara e queixas persistentes de queda não devem virar uma promessa de tratamento pelo consultor.'
    elif kind=='ampoule':opening=f'A {name} corresponde à etapa de {benefits or focus}. Eu explicaria onde entra na rotina e a aplicação desta apresentação. O preparo e o enxágue devem seguir sua ficha; protocolos de outras ampolas do mesmo conjunto podem ser diferentes.'
    elif kind=='supplement':opening='Woman Caps é apresentado como suplemento alimentar para adultos, com vitaminaB5 declarada no catálogo. A avaliação exige composição e recomendação do rótulo atual; o suplemento não substitui uma avaliação de saúde e não é um tratamento tópico para apresentar como resultado imediato no cabelo.'
    else:opening=f'O {name} entra no acabamento para {focus}. A proposta descrita inclui {benefits or "cuidado da finalização"}'+(f', com destaque para {ingredients}.' if ingredients else '.')+' Eu mostraria a etapa de aplicação e a necessidade de ativação ou proteção térmica conforme o protocolo desta ficha.'
    if ingredients and kind in ['shampoo','conditioner','mask']:
        opening+=' A fórmula destaca '+ingredients+'.'
    # Questions and responses are attached to an actual sales decision for this stage.
    objections={
    'lightener':('“Posso usar a mesma mistura em qualquer cabelo?”','A escolha de oxidante, proporção e pausa depende do protocolo, da base e da avaliação do profissional. Não preencho parâmetros ausentes no catálogo por semelhança com outro produto.'),
    'color':('“Esse código entrega a mesma cor em qualquer base?”','O resultado depende da base e do histórico. A cartela orienta a seleção, e o colorista precisa avaliar fundo de clareamento, mistura e instruções do rótulo.'),
    'reconstructor':('“Quanto mais usar, melhor?”','A rotina deve acompanhar a condição da fibra e a orientação desta apresentação. A presença de queratina ou outro ativo não justifica frequência ou dose além do uso indicado.'),
    'shampoo':('“Já tenho shampoo; o que muda na rotina?”','Vamos comparar a necessidade da lavagem, os ativos divulgados e o protocolo de '+name+'. Se sua limpeza já atende esse perfil, a etapa prioritária pode ser outra.'),
    'conditioner':('“Posso usar só a máscara?”','A comparação precisa considerar o protocolo da rotina. Para '+name+', mostro a função de condicionamento e o uso específico sem presumir que qualquer máscara substitui essa etapa.'),
    'mask':('“Todas as máscaras fazem a mesma coisa?”','Nesta ficha, a proposta e os ativos divulgados para '+name+' estão separados. Vamos relacioná-los ao sinal observado no comprimento e respeitar a pausa desta apresentação.'),
    'kit':('“Preciso levar o kit inteiro?”','Primeiro identificamos o que a sua rotina já resolve. Abra cada componente para comparar função e apresentação; a compra do conjunto só faz sentido se as etapas forem úteis no seu atendimento.'),
    'chemical':('“Funciona em qualquer cabelo com química?”','A escolha exige avaliação da fibra, histórico e testes indicados pelo fabricante. Não apresento '+name+' como compatível com todas as químicas ou todos os cabelos.'),
    'ph':('“Qual é o pH exato? Serve para alisar?”','A fonte consultada não publica faixa numérica. A proposta desta ficha é cuidado de pH e reconstrução/blindagem; isso não permite prometer alisamento.'),
    'oil':('“Vai pesar ou deixar aspecto oleoso?”','A distribuição e a quantidade precisam seguir o uso do produto e o tipo de fio. Eu avaliaria '+name+' nas pontas e observaria o acabamento, sem garantir o mesmo comportamento em todos os cabelos.'),
    'fragrance':('“Quanto tempo fixa?”','Não há um tempo de fixação comprovado nesta ficha. Prefiro apresentar o perfil olfativo e a concentração quando declarada, deixando a avaliação da fragrância para a cliente.'),
    'hair-fragrance':('“Posso usar perfume corporal no lugar?”','Este produto possui indicação e aplicação capilar. A comparação deve considerar a orientação para os fios; a presença de fragrância em dois produtos não torna os usos equivalentes.'),
    'tonic':('“Vai resolver a queda?”','A ficha registra a proposta cosmética da marca. Queda tem causas diferentes e não é diagnóstico do consultor; não prometo cura, novos fios ou substituição de orientação de saúde.'),
    'ampoule':('“É só aplicar como qualquer outra ampola?”','Cada etapa pode ter preparo e destino diferentes. Abra o modo de uso de '+name+'; uma etapa de couro cabeludo sem enxágue não deve receber o protocolo enxaguável das outras.'),
    'curl-finish':('“Vai mudar o meu tipo de cacho?”','A proposta é modelagem e acabamento cosmético. Eu mostro o uso de '+name+' para a definição e o movimento desejados, sem prometer mudança permanente da curvatura.'),
    'supplement':('“Posso indicar para qualquer cliente com queda?”','A indicação de suplemento requer conferir o rótulo e a orientação adequada. A queixa de queda não justifica uma recomendação automática pelo consultor.'),
    'finish':('“Substitui todos os finalizadores?”','Vamos comparar a função e o protocolo de '+name+' com o que você já usa: proteção, brilho, alinhamento e ativação por calor não são etapas automaticamente equivalentes.')}
    observation={'lightener':'compatibilidade do protocolo com a base e a fibra, avaliada pelo profissional','color':'seleção da nuance e leitura da cartela pelo colorista','reconstructor':'comportamento e maleabilidade da fibra após o protocolo','shampoo':'comportamento da raiz e do comprimento após o enxágue','conditioner':'desembaraço e toque após o condicionamento','mask':'toque, maleabilidade e acabamento do comprimento','chemical':'condição da fibra e acabamento do serviço avaliado pelo profissional','ph':'situação escolhida e protocolo correto de pausa/enxágue','oil':'distribuição, toque e aparência das pontas','curl-finish':'definição, movimento e comportamento na rotina','fragrance':'preferência olfativa da pessoa, sem promessa de fixação','hair-fragrance':'experiência de fragrância e aplicação nos fios','tonic':'compreensão da aplicação no couro cabeludo e da orientação sem enxágue','ampoule':'preparo, destino da aplicação e necessidade de enxágue','supplement':'composição e recomendações do rótulo com orientação adequada','kit':'função e apresentação de cada componente','finish':'etapa de aplicação e acabamento depois da finalização'}[kind]
    if p['line']=='24K' and 'spray' in n:opening='O Spray Efeito Memória24K300mL é um finalizador termoativado para o acabamento liso e o controle do frizz. Lisselini participa do alinhamento e SilsoftAX-E do brilho e toque. Eu o apresentaria para quem quer facilitar a finalização e manter o acabamento, mostrando a aplicação após lavar/condicionar, a pausa de10–15min e a ativação por calor da orientação publicada.'
    if p['id']=='4d9dff105dbdfa72':opening='O Ativador de CachosPowerCurls250mL é uma proposta para o intervalo entre lavagens. A aplicação pode ser no comprimento úmido ou seco: borrifar, amassar e deixar secar naturalmente ou com difusor, sem enxágue. Eu o apresentaria à cliente que quer reativar a definição e controlar o frizz no dia seguinte, explicando o papel do pantenol e do coco divulgados nesta ficha.'
    if p['id']=='82bcbdacdb562f8e':opening='A GeleiaPowerCurls1kg entra na etapa de fixação e definição dos cachos. Eu a apresentaria ao profissional que quer avaliar o desenho e o comportamento do penteado depois da finalização. O protocolo orienta aplicar nos fios úmidos ou secos, evitando o couro cabeludo, amassar e secar naturalmente ou com difusor. Pantenol e coco são os destaques divulgados.'
    if p['id'] in ['cdb0b5f5eef8f0a9','4a924f8c36b7f317']:opening=f'O {name} foi pensado para a modelagem dos cachos, com definição, hidratação e controle do frizz na proposta da marca. A orientação é aplicar pequena quantidade no comprimento úmido ou seco, evitar a raiz, amassar e manter sem enxágue. Eu avaliaria com o salão o acabamento desejado e a apresentação de{size} para '+('a bancada de atendimento.' if professional else 'a manutenção da cliente em casa.')
    if p['id']=='0362c5b04fc5ffb5':opening='MustUse250mL é um fluido reconstrutor que conecta cuidado do comprimento e finalização: nutrição, flexibilidade, penteabilidade e proteção térmica. A fórmula divulgada reúne pantenol, ômegas3/5/6, queratina, NanoLink, SemiDiLino e silicones especiais. Eu o apresentaria a partir do ponto que falta no acabamento do salão e mostraria o protocolo, que admite uso com ou sem enxágue conforme a fonte.'
    if p['id']=='c9cf1f6be6f34a0f':opening='NecessityUse500mL é uma proposta de proteção térmica e cuidado reconstrutor para a rotina com secador, prancha ou modelador. Eu o apresentaria ao salão que quer revisar a etapa de proteção antes do calor, relacionando os ativos divulgados ao brilho, à flexibilidade e ao controle do frizz. A forma de aplicação deve seguir a ficha desta embalagem.'
    if p['line']=='Efeito Teia':
        opening=f'A {name} deve ser apresentada pela necessidade do comprimento: {p.get("indication") or benefits}. Os destaques desta fórmula são {ingredients or "os que constam na ficha do produto"}. O efeito teia é uma característica da apresentação cosmética; a escolha deve considerar a proposta de '+(benefits or focus)+'.'
    return {'question':question,'opening':opening,'nextStep':f'Escolher um atendimento compatível com {name}, conferir a apresentação e combinar uma avaliação de {observation}.','scope':'Roteiro de estudo para adaptar à conversa; argumentos vinculados aos dados desta apresentação.','audience':'Uso profissional no salão' if professional else 'Orientação de uso e manutenção','decisionGoal':focus,'technicalReason':reason,'discoveryQuestions':[question,line['discoveryQuestion']],'demonstration':{'plan':line['demonstrationPlan'],'watchFor':observation,'protocol':p.get('use')},'objections':[{'question':objections[kind][0],'answer':objections[kind][1]},{'question':'Questão específica desta linha','answer':line['realObjectionReply']}],'avoidClaims':line['avoidClaims'],'kind':kind,'sourceUrls':list(dict.fromkeys([p['url']]+[a['sourceUrl'] for a in roles if a.get('sourceUrl')]))}

def polish(value):
    if isinstance(value,list):return [polish(v) for v in value]
    if isinstance(value,dict):return {k:(v if k in ['id','sourceUrls'] else polish(v)) for k,v in value.items()}
    if not isinstance(value,str) or value.startswith('http'):return value
    for before,after in [('PowerCurls','Power Curls'),('MustUse','Must Use'),('NecessityUse','Necessity Use'),('NanoLink','Nano Link'),('SemiDiLino','Semi di Lino'),('SilsoftAX-E','Silsoft AX-E'),('HomeCare','Home Care'),('vitaminaB5','vitamina B5'),('em2015','em 2015'),('fiosúmidos','fios úmidos'),('DalCotone','Dal Cotone'),('Catálogo2025','Catálogo 2025'),('PDF2025','Catálogo 2025')]:value=value.replace(before,after)
    value=re.sub(r'(?<=\d)(?=(?:mL|ml|kg|g|min|vezes|cápsulas)\b)',' ',value)
    value=re.sub(r'(?<=[A-Za-zÀ-ÿ])(?=\d+(?:[.,]\d+)?\s*(?:mL|ml|kg|g)\b)',' ',value)
    value=re.sub(r'(?<=\d)\s*ml\b',' mL',value)
    value=re.sub(r'([,:;])(?=[A-Za-zÀ-ÿ])',r'\1 ',value)
    value=re.sub(r'([a-zà-ÿ]{3,})\.(?=[A-ZÀ-Ý])',r'\1. ',value)
    value=re.sub(r'(?<=\d)(?=cm\b)',' ',value)
    return value
