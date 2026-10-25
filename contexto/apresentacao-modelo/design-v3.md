---
version: "3.0"
name: "Brain003"
description: "v3 — laboratório de inteligência de dados e comportamento: dark-first, laboratorial, elétrico, flat. Parte do design.md (v1), consolida o que o site institucional (site/index.html) estabeleceu na prática e absorve as duas regras certas do design-v2.md (círculo só para pontos, zero sombra). Descarta do v2 o botão em pílula, a sidebar sólida e o breadcrumb, que o site não usa."
colors:
  primary: "#1E2BFF"
  secondary: "#2438E6"
  accent-data: "#00CFFF"
  accent-synapse: "#3DFF6E"
  neutral-900: "#060A1C"
  neutral-800: "#0E142F"
  neutral-700: "#161D40"
  surface: "#F1F3F8"
  surface-card: "#FFFFFF"
  surface-float: "#E4E9F7"
  ink: "#0C1230"
  on-light-low: "#5A6384"
  on-surface-hi: "#EAF0FF"
  on-surface-mid: "#A9B4D0"
  on-surface-low: "#6B7699"
  error: "#FF6E86"
  success: "#3DFF6E"
typography:
  display-hero:
    fontFamily: "Roboto Mono"
    fontSize: "56px"
    fontWeight: 700
    lineHeight: 1.0
    letterSpacing: "-0.03em"
  headline-lg:
    fontFamily: "Roboto Mono"
    fontSize: "36px"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  headline-md:
    fontFamily: "Roboto Mono"
    fontSize: "26px"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  overline:
    fontFamily: "Roboto Mono"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.16em"
  body-lg:
    fontFamily: "Inter"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: "Inter"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  label-data:
    fontFamily: "Roboto Mono"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  label-caption:
    fontFamily: "Roboto Mono"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "italic"
  slide-title-mono:
    fontFamily: "Roboto Mono"
    fontSize: "34px"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  slide-body-mono:
    fontFamily: "Roboto Mono"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: "0px"
  md: "0px"
  lg: "0px"
  xl: "0px"
  full: "0px"
  circle: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
  2xl: "64px"
  3xl: "96px"
  section-y: "clamp(96px, 11vw, 136px)"
  section-head-gap: "72px"
  title-to-text: "24px"
  card-title-to-text: "20px"
  page-margin: "6%"
  content-max: "1400px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-surface-hi}"
    typography: "{typography.label-data}"
    rounded: "{rounded.full}"
    padding: "12px 20px"
  button-primary-hover:
    backgroundColor: "{colors.secondary}"
  badge-solid:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    typography: "{typography.label-caption}"
    rounded: "{rounded.full}"
    padding: "5px 12px"
  badge-outline:
    backgroundColor: "transparent"
    textColor: "{colors.on-surface-hi}"
    typography: "{typography.label-caption}"
    rounded: "{rounded.full}"
    padding: "5px 12px"
  card-dark:
    backgroundColor: "{colors.neutral-800}"
    textColor: "{colors.on-surface-mid}"
    rounded: "{rounded.md}"
    padding: "24px"
  card-light:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "24px"
  callout:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    typography: "{typography.label-data}"
    rounded: "{rounded.md}"
    padding: "24px 40px"
  chip-icon:
    backgroundColor: "{colors.primary}"
    rounded: "0px"
    size: "52px"
  text-highlight:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    padding: "0 4px"
    rounded: "0px"
  text-highlight-invert:
    backgroundColor: "#FFFFFF"
    textColor: "{colors.secondary}"
    padding: "0 0.18em 0.06em"
    rounded: "0px"
    shadow: "none"
  button-white:
    backgroundColor: "#FFFFFF"
    textColor: "{colors.ink}"
    typography: "{typography.label-data}"
    rounded: "0px"
    padding: "14px 24px"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.on-surface-hi}"
    border: "1px solid rgba(234,240,255,0.4)"
    typography: "{typography.label-data}"
    rounded: "0px"
    padding: "14px 24px"
  tab-active:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "0px"
  float-panel:
    backgroundColor: "{colors.surface-float}"
    textColor: "{colors.ink}"
    titleColor: "{colors.primary}"
    border: "rgba(12,18,48,0.14)"
    inset: "clamp(12px, 2.2vw, 32px)"
    padding: "{spacing.section-y} 0"
    rounded: "0px"
  card-highlight-solid:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "0px"
    padding: "32px"
  glass-card:
    backgroundColor: "rgba(6,10,28,0.78)"
    backdropFilter: "blur(6px)"
    border: "1px solid {colors.accent-data} a 55% ou {colors.primary} a 85%"
    rounded: "0px"
    padding: "24px 26px"
  media-frame:
    aspectRatio: "4/5"
    border: "1px solid rgba(255,255,255,0.12)"
    backgroundColor: "{colors.neutral-700}"
    rounded: "0px"
  status-dot:
    backgroundColor: "{colors.accent-synapse}"
    rounded: "{rounded.circle}"
    size: "6px"
---

# Brain003

## Overview
Brain003 (grafia canônica: "Brain" + superíndice "003", nunca "Brain3" ou "Brain 003") é o laboratório de inteligência de dados e comportamento que transforma fidelização, consumo e mídia em decisões baseadas em evidência. A identidade é dark-first, laboratorial e elétrica: uma única escala de azuis sobre navy profundo, com ciano e verde-neon reservados a acentos de dado. O tom visual é de instrumento de precisão — nunca dashboard genérico, nunca vitrine de dados brutos, nunca hype vazio. Tagline primária: "Sinapses nada óbvias". Apoio: "Sinapses conectadas, negócios expandidos".

**Companion de apresentação:** `SLIDES.md` (mesma pasta) estende este arquivo para decks: canvas 1920×1080, escala tipográfica de palco, cores semânticas de dado, banco de imagens, componentes e templates de slide. Ele só referencia tokens daqui (`{colors.x}`, `{typography.x}`…) — se um slide precisar de um token novo, ele entra **neste** arquivo primeiro.

## Colors
Sistema de azul único, não uma paleta múltipla. `primary` (#1E2BFF, Azul Elétrico) é a cor de assinatura — display, acentos, CTAs — e nunca aparece em corpo de texto longo sobre fundo escuro (falha de contraste/vibração). `secondary` (#2438E6, Azul Royal) veste fundos e capas. `accent-data` (#00CFFF, Ciano) marca dados, links e o motivo "converse com seus dados". `accent-synapse` (#3DFF6E, Verde Neon) é estritamente decorativo — só em data-viz e no motivo de sinapse, nunca em texto ou UI funcional. A escala `neutral-900/800/700` (navy) é o palco: 900 é o fundo padrão, 800 é o card, 700 é borda/elevação. `surface` e `surface-card` cobrem os poucos momentos claros (conteúdo denso: matrizes, comparativos). Texto sobre dark usa `on-surface-hi` (#EAF0FF) para corpo/títulos e `on-surface-mid` (#A9B4D0) para apoio — ambos com contraste ≥ 4.5:1; `on-surface-low` é só legenda. Sobre claro, o texto é sempre `ink` (#0C1230).

**Momentos claros (v3, validado no site):** o fundo claro da marca é `surface-float` (#E4E9F7, um azul-gelo), usado nos blocos flutuantes (ver `float-panel`). Dentro dele: títulos e overlines em `primary`, texto corrido em `ink`, ícones e legendas em `on-light-low` (#5A6384), bordas em `ink` a 14%, cartões internos em `surface-card` branco (a diferença de 1,2:1 para o fundo, somada à borda, basta para separar as camadas). Contraste medido no site: `primary` sobre `surface-float` 6,1:1, `ink` 15,1:1. **Nunca usar `accent-data` (ciano) como texto sobre claro** — dá ~1,6:1 e some; a overline que é ciano no dark vira `primary` no claro.

## Typography
Duas vozes, não três: **Space Grotesk foi descontinuada** (correção v1.3 — a fonte de display agora é a mesma fonte de dado, sem uma segunda grotesca concorrendo por identidade). **Roboto Mono** é a voz inteira de título/display/dado — `display-hero` (capas, frases-manifesto), `headline-lg`/`headline-md` (títulos de seção/slide), `overline` (kickers uppercase), `label-data`/`label-caption` (dados, contato, legendas). **Inter** (`body-lg`/`body-md`) segue como a única voz de leitura corrida — todo parágrafo longo de produto e marketing.

- **Produto/UI/marketing/papelaria**: título e acento sempre em Roboto Mono (inclusive títulos de bloco de workflow, botões, badges); corpo longo sempre em Inter.
- **Slides comerciais / apresentações de venda** (moodboard de referência: fundo navy/azul sólido, silhueta térmica plasma azul-ciano-verde, texto marcado com retângulo azul sólido): única exceção onde **Inter não aparece** — Roboto Mono cobre título (`slide-title-mono` 700) e corpo (`slide-body-mono` 400) também, porque aqui o monospace é a voz inteira do documento, não só o acento.

Em todos os contextos, `accent-data`/`primary` pode marcar uma frase ou trecho curto dentro de um parágrafo com um retângulo sólido atrás do texto (ver componente `text-highlight`) — um recurso de "grifo" observado no moodboard de slides comerciais, útil para destacar 1–2 frases-chave sem quebrar o corpo em blocos separados. Don't: não grifar mais de ~15% do texto de um parágrafo, ou o destaque perde força.

## Layout
Grid de 12 colunas com margem de segurança de 6% em todos os lados (canvas de referência 1920×1080 para slides/social). A escala de espaçamento (`xs` 4px a `3xl` 96px) sobe em passos que mapeiam papéis fixos: `xs`/`sm` para gaps internos de ícone/label, `md` entre elementos, `lg` como padding padrão de card, `xl`/`2xl` entre blocos e como margem externa. Nunca empilhar 2 itens de uma grade de 6 em uma coluna só — 6 itens = grade 3×2, nunca 2 colunas duplas. Máximo de 3 cards por linha.

**Web (v3, do site):** conteúdo em até `content-max` 1400px com `page-margin` 6% nas laterais. O respiro vertical de seção é fluido, `section-y` = `clamp(96px, 11vw, 136px)` — no celular não cai abaixo de 96px, no desktop chega a 136px. Entre o cabeçalho da seção (overline + título + lead) e o conteúdo: `section-head-gap` 72px. Título → texto: 24px nos cabeçalhos de seção, 20px dentro de cards e painéis; overline → título: 20px. Grades de cards se separam por fio de 1px (`gap:1px` sobre fundo `stroke`), não por espaço vazio, quando os cards formam um conjunto (etapas, pilares); cards independentes usam gap de 20px. Mídia de produto (imagem ou vídeo) é vertical 4:5 e alinha o topo com o título do bloco. Título de hero com quebra de linha fixa ("Transformamos seus / dados em [x]") usa `min(clamp(…), 8.4vw)` para a primeira linha nunca quebrar no celular.

## Elevation & Depth
**Zero sombra em tela (v3).** Nenhum `box-shadow`, `text-shadow` ou `filter: drop-shadow` em UI, slide, card, painel, texto ou modal — nem sobre claro. A profundidade vem de três fontes, e só delas:

1. **Camada tonal:** `neutral-900` → `neutral-800` → `neutral-700` (dark) ou `surface-float` → `surface-card` (claro).
2. **Fio de 1px:** `stroke` (branco a 12–14%) no dark, `ink` a 14% no claro.
3. **Movimento em camadas (web):** paralaxe, em que o que está mais perto anda mais rápido que o scroll (ver Motion).

Overlay (modal) se separa do conteúdo por um véu `neutral-900` a 72% com `backdrop-filter: blur(4px)`, não por sombra. Cartão sobre vídeo usa o `glass-card` (fundo translúcido + blur), também sem sombra. A única sombra que sobrevive é a de mockup físico (papelaria, merchandising), porque ali ela descreve o material e não é UI.

## Shapes
**Cantos sempre retos — zero raio em qualquer componente de UI** (a escala `rounded` antiga, de `sm` 6px a `xl` 24px, foi descontinuada; `sm`/`md`/`lg`/`xl`/`full` valem `0px`). Botões, badges, chips, cards, abas, inputs, modais, callouts e o balão de destaque de texto são sempre retângulos de canto reto — nenhuma pílula, nenhum raio "quase reto".

**A única exceção é o círculo perfeito (`rounded.circle`, v3):** só quando o elemento É um ponto — bullet, `status-dot`, porta/conector entre etapas de um fluxo, avatar. Nunca como raio de canto de um retângulo. (O `design-v2.md` usava `full: 9999px` também para botão em pílula; isso não vale — o site não tem nenhum botão arredondado.) Formas geométricas simples (círculos como marca pontual — ex.: bullet/status dot — e retângulos de canto reto) dominam; o único motivo orgânico é o logomark de sinapse (nós arredondados conectados), que segue seu próprio desenho por ser um símbolo, não um componente de UI, e não é afetado por esta regra.

## Components

### Botão primário (`button-primary`)
**Quando usar:** ação de destaque em CTAs de e-mail, site ou apresentação.
**Variantes:** `button-primary-hover` (fundo escurece para `secondary`).
**Don't:** nunca usar `accent-synapse` (verde) como fundo de botão — é reservado a data-viz.

### Badges / chips (`badge-solid`, `badge-outline`)
**Quando usar:** rótulos curtos de produto/atributo ("Data Clean Room", "LGPD-native") em cards e slides.
**Variantes:** `badge-solid` (fundo azul elétrico sólido), `badge-outline` (contorno, fundo transparente), e uma variante ciano translúcida para métricas ("Brain Score") — mesma estrutura de `badge-outline` com `backgroundColor` em ciano 14% de opacidade.
**Don't:** não misturar mais de 2 estilos de badge na mesma linha/tela.

### Card (`card-dark`, `card-light`)
**Quando usar:** blocos de conteúdo agrupado — etapas de processo, itens de portfólio, blocos de matriz comparativa.
**Variantes:** `card-dark` (padrão, sobre navy), `card-light` (só em telas de conteúdo denso sobre `surface`), e uma variante "accent" = `card-dark` com borda esquerda de 3px em `accent-data`.
**Don't:** nunca combinar `card-light` isolado dentro de uma seção majoritariamente dark — a troca de fundo claro/escuro acontece por seção inteira, não por card solto.

### Callout (`callout`)
**Quando usar:** um único destaque de frase por slide/seção, nunca mais de um por tela.
**Don't:** não usar para parágrafos longos — é para uma frase-síntese curta em `label-data`.

### Destaque de texto invertido (`text-highlight-invert`)
**Quando usar:** palavra/frase de destaque animada (ex.: efeito "máquina de escrever" trocando palavras) sobre fundo escuro ou foto/vídeo — quando `text-highlight` padrão (fundo azul elétrico, texto branco) não teria contraste suficiente contra o que está atrás.
**Estrutura:** fundo `#FFFFFF` sólido e flat, texto em `secondary` (Azul Royal), zero raio, **zero sombra** (`shadow: none` — nem `text-shadow` nem `box-shadow`/`filter`). O fundo branco cresce/encolhe acompanhando o texto conforme ele é digitado, sem salto de layout brusco.
**Don't:** nunca aplicar `text-shadow`, `box-shadow`, `filter` ou gradiente a este componente — é estritamente flat design. Nunca usar `primary` como cor de texto aqui (mistura com o `text-highlight` padrão); é sempre `secondary`.

### Chip de ícone (`chip-icon`)
**Quando usar:** par ícone+texto em listas de diferenciais/features.
**Don't:** nunca repetir o mesmo ícone em chips diferentes na mesma peça — um ícone comunica uma ideia.

### Botões do site (`button-white`, `button-outline`) — v3
**Quando usar:** CTAs sobre fundo azul, vídeo ou navy. `button-white` é a ação principal (fundo branco, texto `ink`) — o CTA fixo "Fale com a gente" do menu é esse botão; `button-outline` é a secundária, lado a lado com ele.
**Estrutura:** Roboto Mono 14px/500, canto reto, sem caixa-alta (caixa-alta fica para os links do menu, 13px com tracking 0.04em). Hover do branco vai para `on-surface-hi`; hover do contorno fecha a borda para `on-surface-hi`.
**Don't:** não criar variante em pílula; não usar `accent-synapse` como fundo.

### Aba ativa (`tab-active`) — v3
**Quando usar:** lista lateral ou barra de abas que troca um painel (Setores, Soluções).
**Estrutura:** a aba selecionada é um bloco `primary` sólido com texto e ícone brancos. Abas inativas: fundo do contexto, borda `stroke`, texto `on-surface-mid`/`ink`, ícone em `on-surface-low`/`on-light-low`. Ícone da aba ativa em chip: fundo do chip pode virar `accent-synapse` com ícone `primary` (exceção decorativa validada no site).
**Don't:** não marcar a aba ativa com ciano nem só com borda — a decisão final no site foi azul royal sólido.

### Bloco claro flutuante (`float-panel`) — v3
**Quando usar:** seções que devem "respirar" no meio de uma página dark (no site: Diferenciais e Setores). Referência: hermes-agent.nousresearch.com.
**Estrutura:** a `<section>` é só o chão escuro, **na mesma cor da seção anterior** (senão o bloco parece colado, não flutuando). Dentro dela, um painel `surface-float` com recuo lateral `clamp(12px, 2.2vw, 32px)`, cantos retos, padding vertical `section-y`, e os tokens redefinidos por escopo (títulos `primary`, texto `ink`, fios `ink` 14%, cartões brancos). Com paralaxe, o painel sobe mais rápido que o scroll e passa por cima do fim da seção anterior; a seção compensa a subida com `margin-bottom` negativo igual a ela.
**Don't:** não usar o fundo claro como seção de ponta a ponta — o efeito é o bloco com a borda escura aparecendo em volta; não usar ciano como texto dentro dele.

### Card de destaque sólido (`card-highlight-solid`) — v3
**Quando usar:** dentro de um `float-panel`, os cards que carregam a mensagem principal (Diferenciais). Bloco `primary` chapado, overline branca em negrito, texto branco (contraste 7,4:1).
**Estrutura:** mesmo canto reto e mesma grade dos demais; no site é a camada mais próxima do paralaxe e vaza `clamp(32px, 5vw, 64px)` pela borda de baixo do painel.
**Don't:** sem gradiente, sem sombra. Diferente do v2, pode ser o conjunto inteiro de uma grade quando a grade está sobre fundo claro — o contraste é com o painel, não entre os cards.

### Card sobre mídia (`glass-card`) — v3
**Quando usar:** texto sobreposto a vídeo/imagem (Clean Data Room).
**Estrutura:** fundo `neutral-900` a 78% + `backdrop-filter: blur(6px)`, fio de 1px colorido (ciano a 55% ou `primary` a 85%) para distinguir os cards entre si; título em Roboto Mono 14/600 `accent-data`, corpo Inter 14px `on-surface-mid`. Cards opostos espelham o alinhamento (um à esquerda, outro à direita) no desktop; no celular empilham e voltam a alinhar à esquerda.

### Moldura de mídia (`media-frame`) — v3
**Quando usar:** imagem ou vídeo de produto. Proporção 4:5 vertical, `object-fit: cover`, fio `stroke`, fundo `neutral-700` enquanto carrega. Vídeo: `autoplay muted loop playsinline` com `poster` (o primeiro quadro), comprimido para ~720px de largura. O topo da mídia alinha com o título do bloco.

### Logomark de sinapse
Símbolo de três nós orgânicos conectados. **Não existe vetor isolado do símbolo** — os únicos arquivos oficiais são o lockup completo (símbolo + wordmark) em `artifacts/brandbook/visual-assets/Logos/logo_brain_0000_logo_branco.png` (branco, uso sobre dark/azul) e `logo_brain_0001_logo_preto.png` (preto, uso sobre claro), e três renders 3D do símbolo isolado — metal prata (`201e6d42-b79a-4021-adcb-a308bfe54299.jpg`), metal preto (`361655eb-a820-43e4-aaab-8fa7f93fe372.jpg`) e metal azul (`7366655541075528611.jpg`) — para uso como elemento gráfico de destaque (capa, avatar, marca d'água), não para recriar o símbolo do zero. Medido no arquivo oficial: o símbolo tem ≈1,35× a altura de caixa de "Brain" (mesma linha de base), com ≈0,16× essa altura de respiro antes do texto. Nunca redesenhar os nós, recolorir fora da paleta ou usar uma quarta cor de render 3D além das três oficiais.

## Do's and Don'ts
- Do: usar pontuação real — travessão "—" e seta "→" numa fonte que contenha o glifo.
- Don't: deixar "i" ou "≤" soltos no lugar de travessão/seta (falha de fonte não detectada).
- Do: usar a grafia canônica "Brain003" (Brain + "003" em superíndice, medido em ≈0,43× a altura de "Brain", alinhado ao topo da caixa) quando o nome aparece **como marca**: logo, título de peça, assinatura, rodapé, menção formal única.
- Do (v3): **no texto corrido, a empresa é só "Brain"**, no feminino ("a Brain conecta…", "os agentes da Brain…"). Não repetir "Brain003" a cada frase.
- Don't: usar "Brain3", "Brain 003" (com espaço) ou "Brain³" em lugar nenhum — é "Brain003" como marca ou "Brain" no texto.
- Do: corpo longo sempre em Inter, com contraste ≥ 4.5:1 (`on-surface-hi`/`on-surface-mid` sobre navy) — exceto em slide comercial/apresentação de venda, onde Roboto Mono cobre corpo e título (ver Typography).
- Don't: usar Space Grotesk ou qualquer outra grotesca de display — foi descontinuada; título e display são Roboto Mono em toda a marca.
- Don't: usar `primary` (azul elétrico puro) em texto de corpo sobre navy — vibra e cansa a leitura; é só para display grande.
- Do: manter os ícones numa única família (traço 2px, cantos arredondados, base 24px), um ícone distinto por ideia.
- Don't: repetir o mesmo ícone em cards/blocos diferentes da mesma peça.
- Don't: usar qualquer `border-radius` em botão, badge, card, callout, tab ou balão de destaque — cantos são sempre retos (ver Shapes). Círculo só como marca pontual (bullet, status dot), nunca como raio de canto.
- Don't (v3): usar `box-shadow`, `text-shadow` ou `drop-shadow` em qualquer elemento de tela — inclusive para "ajudar a leitura" de texto sobre vídeo; nesse caso, reposicione o texto ou use `glass-card`.
- Don't (v3): usar `accent-data` (ciano) como texto sobre `surface-float`/branco — contraste ~1,6:1.
- Do (v3): medir contraste depois de trocar cor de fundo; mínimo 4,5:1 para corpo, e anotar o valor quando for decisão nova.
- Do (v3): todo movimento respeita `prefers-reduced-motion` (o elemento fica parado na posição final) e roda com metade da amplitude abaixo de 900px.
- Don't (v3): usar travessão "—" em copy de site ou peça comercial — é o principal sinal de texto de IA em português; reescrever a frase (vírgula, dois-pontos, ponto). A regra de "pontuação real" acima vale para setas e para documentação interna.

<!-- Everything below this line is a non-standard extension, not part of the canonical DESIGN.md spec. Consumers that don't recognize these headings will preserve them without erroring. -->

## Screens

### Capa / Slide de abertura
**Quando usar:** primeira tela de qualquer apresentação, ou stories/posts de abertura de campanha.
**Estrutura:** fundo gradiente hero (radial, `secondary`→`neutral-800`→`neutral-900`), wordmark grande centralizado ou ancorado, tagline em `label-data` logo abaixo.
**Don't:** nunca colocar bloco de texto longo nesta tela — é só wordmark + tagline curta.

### Capa fotográfica / hero (`artifacts/brandbook/visual-assets/Logos/logo_Brain_2001.png` a `_2007.png`)
**Quando usar:** capa de deck de posicionamento/conceito (ver `BRAIN3 Conceito e Posicionamento.pdf`), momentos de alto impacto onde a capa-gradiente padrão é pouco específica.
**Estrutura:** só a wordmark "Brain003" (sem o símbolo) centralizada sobre fotografia em tons de azul/ciano — raio-X, textura orgânica/petri, silhueta térmica, ressonância/scan, retrato térmico, grade de scanner de pessoas ou figuras humanas em grain/desfoque (esta última é a mesma imagem da capa do PDF de posicionamento). Grid numérico "001" e ruído/grain são camada de apoio recorrente, não obrigatória.
**Don't:** não usar o símbolo junto da wordmark nesse tratamento — aqui é sempre wordmark isolada sobre a fotografia; não misturar mais de um tratamento fotográfico na mesma peça.

### Aplicações de papelaria e social (observadas em `artifacts/brandbook/visual-assets/enxoval/`)
**Quando usar:** cartão de visita, envelope, papel timbrado, assinatura de e-mail, header de LinkedIn, avatar, template de Slack, posts de feed/stories.
**Estrutura:** fundo sólido `primary`/`secondary` com o lockup branco (`logo_brain_0000_logo_branco.png`), ou fundo branco com o lockup preto (`logo_brain_0001_logo_preto.png`); texto de apoio (nome, cargo, contato) em Roboto Mono, letter-spacing aberto, uppercase para labels curtos. Posts de feed alternam fundo preto/`neutral-900` e `primary` sólido, com um dos três renders 3D do símbolo (prata/preto/azul) como elemento gráfico de destaque (inclusive como avatar circular) e texturas de glow ciano/plasma como imagem de apoio.
**Don't:** não introduzir uma terceira cor de fundo fora de `primary`/`secondary`/navy/branco nessas aplicações; não recriar o lockup em texto/CSS — sempre usar os arquivos PNG oficiais.

### Slides comerciais / moodboard de venda
> A especificação completa de apresentações (componentes, ~60 templates, animação, deck-modelo) está em `SLIDES.md`. Esta seção resume o moodboard de origem.

**Quando usar:** apresentação comercial/pitch (não confundir com o deck de posicionamento interno já documentado acima) — capítulos, títulos de bloco, corpo de argumento.
**Estrutura observada no moodboard de referência:**
- Tipografia: **Roboto Mono para título e corpo** — aqui é a única tela onde nem o corpo usa Inter (ver Typography). Título de capítulo em duas linhas ("Capítulo 1:" pequeno + título grande, ambos mono negrito); corpo em duas colunas quando o texto é longo.
- Grifo: 1–2 frases-chave por parágrafo marcadas com retângulo `primary` sólido atrás do texto (componente `text-highlight`), nunca o parágrafo inteiro.
- Fundo: alterna `neutral-900` full-bleed, `primary` sólido (variante "capítulo tipografia/ícones" com texto branco) e split 50/50 (metade `surface-card` branca + metade `neutral-900` com a arte).
- Arte de destaque: silhueta/aura térmica orgânica em gradiente azul→ciano→verde-neon (variação mais elaborada da "textura plasma" já citada em Ícones & Motivos), ocupando a maior parte do slide como elemento emocional/hero — não é o logomark, é fotografia/render tratado.
- Ícones: família expandida do motivo de sinapse — variações do mesmo vocabulário (nós circulares conectados) em arranjos diferentes (cruz, estrela/flor, ondulação em linha, grade), sempre branco sobre `primary` ou `primary` sobre branco. É um grid de exploração do símbolo, não substitui o logomark oficial (intocável, ver seção Logomark de sinapse).
- Moldura recorrente: a tagline de apoio "Sinapses conectadas, negócios expandidos" corre na vertical (texto rotacionado 90°), pequena, em Roboto Mono, colada nas bordas esquerda e/ou direita do slide — presente em praticamente todo template do deck.
- Aplicação física: mesmo sistema aparece em merchandising (ex.: sacola/tote com wordmark + mancha `primary` orgânica + tagline), reforçando que o grifo e a tagline vertical não são só digitais.
**Don't:** não usar Inter nesses slides — nem no corpo; não usar o grifo `text-highlight` em mais de duas frases por bloco de texto; não tratar os ícones de exploração da seção acima como o logomark oficial.

## Motion (v3, do site)
O movimento na Brain003 é ligado ao scroll e comunica profundidade — nunca é decoração em loop chamando atenção. Tudo em JS com `requestAnimationFrame` e listener passivo (não `animation-timeline`/`view()`, que ainda falha em Firefox e Safari antigo), só com `transform`/`opacity`.

- **Paralaxe em 3 camadas** (blocos flutuantes): fundo escuro mais fundo, desce até +40px (anda mais devagar que o scroll); `float-panel` no meio, sobe até `min(22% da altura da tela, 170px)` enquanto seu topo atravessa a tela, e trava; cards `primary` mais perto, deslocamento contínuo proporcional à distância do centro da tela (fator 0,10 + 0,04 por card, então os cards de uma grade andam em velocidades levemente diferentes e se alinham no centro). A sobreposição do painel sobre a seção anterior só acontece nos ~35% de cima da tela, quando o conteúdo de cima já está saindo.
- **Entrada de cards ligada ao scroll** (Clean Data Room): cards opostos entram de lados opostos (`translateX` ±120% da própria largura + opacidade) e chegam à posição final exatamente quando a seção está centralizada na tela; depois disso ficam parados.
- **Palavra que troca no hero:** efeito máquina de escrever (90ms por letra, 45ms apagando, 1,4s parada) dentro do `text-highlight-invert`, com cursor piscando.
- **Pontos de sinapse:** `status-dot` verde percorrendo o fio entre nós (2,4s), e pulso de opacidade nos conectores de etapas.
- **Contagem numérica:** números sobem com easing cúbico em 1,4s quando entram na tela.
- Reduzir movimento: tudo acima desliga; elementos ficam na posição/valor final. Celular (<900px): metade da amplitude.

## Screens — Site institucional (v3)
**Referência viva:** `site/index.html` (deploy em Brain-003/site). Ritmo de seções: hero `secondary` com vídeo de fundo → faixa `secondary` de prova → fluxo em 3 passos (`neutral-800`) → **bloco flutuante claro** (Diferenciais, chão `neutral-800`) → abas de soluções (`neutral-800`) → Clean Data Room com vídeo e `glass-card` (`neutral-900`) → **bloco flutuante claro** (Setores, chão `neutral-900`) → Quem Somos (`neutral-900`) → Ecossistema (`neutral-800`) → faixa de CTA `primary` → rodapé `neutral-900`.
**Estrutura fixa:** menu transparente que vira `secondary` sólido após 40px de scroll; links do menu em caixa-alta; CTA "Fale com a gente" como `button-white` abrindo modal de formulário (não página nova); tagline vertical "Sinapses conectadas, negócios expandidos" na borda do hero; favicon = símbolo branco recortado do lockup oficial (16/32px) e ícone iOS 180px branco sobre `primary`.
**Don't:** não quebrar a alternância de chão escuro — as seções vizinhas de um bloco flutuante têm a mesma cor que o chão dele.

## Instructions for AI Agents
1. Ler este arquivo por completo antes de gerar qualquer UI, slide, peça de papelaria ou post. A skill `brain003-design` (`.claude/skills/brain003-design/`) empacota este arquivo, o brandbook e os padrões de código do site, com um verificador automático.
2. Usar somente os tokens definidos no front matter YAML — nenhum hex solto, nenhum espaçamento ou raio inventado. Opacidades de tokens (ex.: `ink` a 14%, `neutral-900` a 78%) são permitidas.
3. Para apresentações, usar `SLIDES.md` (componentes `slide-components` e templates) sobre estes tokens. Para web e o resto, casar o pedido com a entrada mais próxima em `components` (ou `Screens` acima). Se nada corresponder, usar Overview + Do's and Don'ts como base e sinalizar a lacuna em vez de adivinhar.
4. Seguir todo "Don't" relevante ao componente/tela usado, incluindo a grafia canônica "Brain003" e a regra de pontuação real (— e →).
5. Se este arquivo conflitar com uma instrução mais específica no prompt atual, o prompt vence — mas apontar o conflito.
