# Dal Cotone — guia de estudo do consultor

Aplicativo pessoal para estudar a marca, os produtos e as linhas e preparar conversas com salões. Interface instalável pelo navegador, com consulta offline, pesquisa, favoritos e notas locais.

## Conteúdo

- Navegação por categoria de tratamento, linha, kits e produtos avulsos.
- 119 entradas de estudo, reunindo a loja pública e o catálogo profissional2025. O exemplo de Kit24K não foi tratado como produto real.
- Ativos divulgados e suas funções cosméticas de referência, ocasiões de uso, ficha técnica, diferenciais, protocolos e INCI quando disponível.
- 26 conjuntos conferidos no material; volumes ou componentes não confirmados ficam explícitos.
- Roteiros de conversa para as28 linhas e para cada item, além da apresentação institucional e seus argumentos. Fabricação própria não é apresentada como prova automática de qualidade de todos os lotes ou de superioridade frente a concorrentes.
- pHControl500mL revisado na página25 do PDF: NanoLink e LunaMatrix; pré-química, pós-química e blindagem têm orientações distintas. A página não publica uma faixa numérica depH. O item aparece normalmente, sem destaque especial.
- 119 entradas: uma usa galeria dos componentes reais do kit; as demais têm imagem referenciada:94 fotografias doPDF verificadas e empacotadas localmente;24 referências oficiais ainda dependem do download no aparelho. Não se afirma que esses 24 registros e seus 20 arquivos remotos tenham sido validados neste ambiente.

## Fotos e fontes

As fotografias em `dist/assets/products/` são extrações ou recortes das fotografias incorporadas aoPDF, com conferência de rótulos e apresentações. Não são imagens geradas. `research/pdf-photos.json` e os manifestos de extração guardam a procedência; `research/uploaded-catalog.json` identifica oPDF por SHA-256. O arquivo original de8,8MB não é necessário para executar oapp e não foi incluído neste repositório. A fonte pública está registrada nos metadados.

As fotos locais são incluídas no cache da interface. As referências externas podem ser armazenadas pelo botão Offline no aparelho; a rede deste executor bloqueia o domínio da loja e não foi usada para atestar esses downloads. Respostas cross-origin opacas podem ser armazenadas; a interface sinaliza imagens que falham ao renderizar.

Dados técnicos são atribuídos às fontes da marca, não a ensaios independentes. O catálogo2025 pode representar versões anteriores. Preços públicos são referências consultadas em06/11/2026, com divergências e ausências identificadas; não são cotações em tempo real. Ativos destacados e notas olfativas são separados da lista completa INCI.

## Usar no Android

Abra o link publicado no Chrome com internet. Na aba Offline, prepare o catálogo e as fotos e confira o contador. Instale pelo menu doChrome. Depois use o mesmo navegador/perfil ou ícone instalado. Primeira autenticação e primeiro download exigem conexão.

Favoritos, progresso de revisão e notas ficam no aparelho, em localStorage. Exportação/importaçãoJSON permite cópia manual. Limpar os dados do navegador pode remover essas informações.

## Desenvolvimento

Sem dependências de execução. Sirva `dist/` por HTTP/HTTPS.

```sh
python prepare-catalog.py
npm run check
npm test
python -m http.server 31900 --bind 127.0.0.1 --directory dist
```

Em outro terminal, `node scripts/browser-check.mjs` valida a interface comChromium. Verificados: categorias/linhas/kits, fichas e roteiros, busca, favoritos, comparação, anotações, reabertura offline e fotos locais em1440/390/320px. Fotos externas são bloqueadas apenas nesse teste de infraestrutura, sem substitutas.

## Publicação e Expo

A configuração de hospedagem está em `.openai/hosting.json`. A audiência doSite permanece privada. Este repositório contém código e material de referência público, sem notas pessoais, tokens ou senhas.

Destino Expo informado: `@marcinhopb/dal-lcotone`. A integração nativa foi adiada para terminar primeiro o material de estudo, conforme solicitado. NenhumAPK foi gerado e não se afirma vinculação autenticada comExpo.

## Revisão integral do PDF e demonstrações

As51páginas foram confrontadas com as fichas. A auditoria acrescentou ShampooL’Amour300mL e WomanCaps60cápsulas, corrigiu17fichas e separou divergências doPDF2025 e das páginas da loja. Nuances e corretores ColorCreams estão estruturados. Campos não divulgados continuam identificados. Evidências e pendências por produto: `research/release-audit.json`.

A aba Demonstrações permite importar arquivos de vídeo por produto, filtrar, reproduzir e excluir offline. Os arquivos ficam em IndexedDB neste aparelho; não são enviados ao GitHub. O teste de importação/reload/reprodução/busca temporal/exclusão usa uma fixture sintética fora do app, nunca como demonstração comercial. Nenhum vídeo real de aplicação foi obtido para empacotar nesta revisão. A página oficial encontrada está identificada como online; não é apresentada como vídeo offline. Resultados reais e materiais oficiais ainda dependem de arquivos acessíveis.

Animações discretas respeitam `prefers-reduced-motion`. Favoritos e notas anteriores são preservados. Para dados profissionais ou reformulações divergentes, consultar o rótulo específico; o app não preenche parâmetros ausentes com outra embalagem.

## Revisão de 07/11/2026

Busca por situação descrita e resultado, cinco situações capilares, filtros múltiplos de cabelo e tipo de produto. Todos os componentes de kits permitem abrir a ficha individual ou escolher a apresentação quando o volume não está confirmado. Auditoria de navegador: 119 fichas, 859 abas, 99 caminhos de componente com retorno ao kit e 94 fotos locais decodificadas. Os 14 testes automatizados passaram.

Pendências: 20 arquivos oficiais de fotos ainda inacessíveis pela política de rede; nenhum vídeo real de demonstração está empacotado. A biblioteca importa vídeos do usuário para reprodução offline. A imagem das situações capilares é uma ilustração de navegação gerada, não prova de resultado. A vinculação e o build Expo ainda não foram realizados.
