# Dal Cotone — guia de estudo do consultor

Aplicativo pessoal para estudar a marca, os produtos e as linhas e preparar conversas com salões. Interface instalável pelo navegador, com consulta offline, pesquisa, favoritos e notas locais.

## Conteúdo

- Navegação por categoria de tratamento, linha, kits e produtos avulsos.
- 109 entradas de estudo, reunindo a loja pública, o catálogo profissional2025 e uma montagem de Kit24K informada pelo consultor. Não representa estoque atual.
- Ativos divulgados e suas funções cosméticas de referência, ocasiões de uso, ficha técnica, diferenciais, protocolos e INCI quando disponível.
- 26 conjuntos conferidos no material e uma montagem do consultor; volumes ou componentes não confirmados ficam explícitos.
- Roteiros de conversa para as28 linhas e para cada item, além da apresentação institucional e seus argumentos. Fabricação própria não é apresentada como prova automática de qualidade de todos os lotes ou de superioridade frente a concorrentes.
- pHControl500mL revisado na página25 do PDF: NanoLink e LunaMatrix; pré-química, pós-química e blindagem têm orientações distintas. A página não publica uma faixa numérica depH. O item aparece normalmente, sem destaque especial.
- 108 entradas com foto:85 referências da loja e23 fotografias extraídas doPDF enviado pelo consultor. A montagem não confirmada de Kit24K não recebe uma foto inventada.

## Fotos e fontes

As23 imagens em `dist/assets/products/` são extrações ou recortes das fotografias incorporadas aoPDF, com conferência de rótulos e apresentações. Não são imagens geradas. `research/pdf-photos.json` e os manifestos de extração guardam a procedência; `research/uploaded-catalog.json` identifica oPDF por SHA-256. O arquivo original de8,8MB não é necessário para executar oapp e não foi incluído neste repositório. A fonte pública está registrada nos metadados.

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
