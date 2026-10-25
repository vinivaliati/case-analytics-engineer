---
version: "1.0"
name: Brain003-slides-companion
extends: design-v3.md
description: "Companion de apresentação do design-v3.md da Brain003: como a mesma identidade dark-first, flat e laboratorial vira deck. Todo token visual abaixo é referência ao design-v3.md ({colors.x}, {typography.x}, {rounded.x}, {spacing.x}, {components.x}); este arquivo só adiciona o que um slide precisa e uma página web não: canvas, escala tipográfica de palco, cores semânticas de dado, banco de imagens, ~55 componentes de slide e ~60 templates com storytelling. Gerado com a skill slidemaster em 2026-09-16."

slide-canvas:
  aspect-ratio: "16:9"
  width: 1920px
  height: 1080px
  safe-margin-x: "115px"   # 6% de 1920 — {spacing.page-margin}
  safe-margin-y: "65px"    # 6% de 1080
  grid: "12 colunas, gutter 32px"
  vertical-tagline: "Sinapses conectadas, negócios expandidos — {typography.label-caption}, 90°, colada na borda direita, dentro da margem"
  footer: "número do slide + nome da seção em {typography.label-caption}, {colors.on-surface-low}, alinhado à base da margem"
  background-default: "{colors.neutral-900}"

deck-voice:
  comercial: "Títulos e corpo em Roboto Mono (venda, pitch, proposta) — padrão da Brain"
  produto: "Títulos em Roboto Mono, corpo em Inter (posicionamento, produto, onboarding)"
  rule: "Declarar a voz no topo do deck (atributo data-voice no <body>). {typography-slide.body} resolve para a família da voz."

typography-slide:
  # Escala de palco (1920×1080). Mesmas famílias, pesos e tracking dos tokens do design-v3;
  # só o tamanho cresce, porque 36px de headline web some numa sala.
  cover:
    extends: "{typography.display-hero}"
    fontSize: "132px"
    lineHeight: 1.08
  divider:
    extends: "{typography.display-hero}"
    fontSize: "104px"
    lineHeight: 1.05
  title:
    extends: "{typography.slide-title-mono}"
    fontSize: "64px"
    lineHeight: 1.18
  subtitle:
    extends: "{typography.headline-md}"
    fontSize: "36px"
  chapter-kicker:
    extends: "{typography.slide-title-mono}"
    fontSize: "40px"
  overline:
    extends: "{typography.overline}"
    fontSize: "20px"
  body:
    extends: "{typography.slide-body-mono} (voz comercial) | {typography.body-lg} (voz produto)"
    fontSize: "26px"
    lineHeight: 1.55
  body-sm:
    extends: "{typography.slide-body-mono} | {typography.body-md}"
    fontSize: "21px"
  data-xl:
    extends: "{typography.display-hero}"
    fontSize: "220px"
    letterSpacing: "-0.04em"
  data-lg:
    extends: "{typography.headline-lg}"
    fontSize: "72px"
  label:
    extends: "{typography.label-data}"
    fontSize: "20px"
  caption:
    extends: "{typography.label-caption}"
    fontSize: "16px"

colors-extended:
  semantic-positive: "{colors.success}"            # #3DFF6E — só sobre fundo escuro
  semantic-negative: "{colors.error}"              # #FF6E86
  semantic-neutral: "{colors.on-surface-low}"      # #6B7699
  semantic-positive-on-light: "{colors.primary}"   # neon some no claro (1,3:1); no claro, positivo = azul
  semantic-negative-on-light: "#C8284A"            # PROPOSTA — ver Known Gaps
  semantic-warning: "#FFB547"                      # PROPOSTA — ver Known Gaps
  series:
    - "{colors.primary}"
    - "{colors.accent-data}"
    - "{colors.accent-synapse}"
    - "{colors.on-surface-mid}"
  note: "positivo e negativo vêm dos tokens success/error que o design-v3 já define. O verde é o mesmo accent-synapse, que o design-v3 reserva a data-viz — um gráfico é exatamente esse uso. As duas cores marcadas PROPOSTA não existem na marca e só entram se aprovadas."

image-bank:
  strategy: "brand-library-first, generation-second, stock-fallback, registry-tracked"
  note: "A Brain já tem uma biblioteca própria com a assinatura visual (brandbook/visual-assets). Ela vem antes da geração por IA."
  online-base: "https://artifacts.brain3.com.br/share/z_pgQrSNRANa/raw/brandbook/visual-assets/"
  linking: "Referencie a biblioteca pela online-base (src) e guarde uma cópia leve ao lado do deck em data-local: se a URL falhar, o deck troca sozinho. O link depende de o brandbook seguir com compartilhamento público. Imagem fora da biblioteca (logos de parceiros, derivados) fica só local, até ser adicionada ao brandbook/visual-assets do repo de artefatos."
  slots:
    cover-photo:
      role: "Capa ou divisor. Wordmark sobre foto tratada azul/ciano."
      source: "brand-library"
      files: "Logos/logo_Brain_2001…2007 (já trazem a wordmark — não sobrepor outra)"
      fallback: "generate"
    hero-photo:
      role: "Foto full-bleed sem wordmark, com espaço negativo para título."
      source: "generate"
      prompt-base: "fotografia tratada em monocromia azul elétrico #1E2BFF a ciano #00CFFF sobre navy #060A1C, estética de exame médico e laboratório (raio-X, ressonância, imagem térmica, scan corporal, placa de petri), grão fino, alto contraste, sem texto, composição com 40% de área escura vazia para título, sem rosto identificável"
      fallback: "stock tratado com o mesmo duotone"
    data-art:
      role: "Visual de dado/rede para slides de produto e inteligência."
      source: "brand-library"
      files: "brain-graph/*.png e *.mp4 (loops 4:5; brain-graph-ref4 = um agrupamento aceso, bom para Clean Room), Pictograms_icons/heatmap*.png"
      fallback: "generate — mesmo prompt-base, assunto: rede de nós, grafo, mapa de calor"
    icon-set:
      role: "Ícones de conceito."
      source: "brand-library"
      files: "Pictograms_icons/*_pictogram.png (família de sinapse, primary sobre transparente)"
      note: "Em fundo escuro ou azul, tornar branco com filter: brightness(0) invert(1). Um ícone por ideia. Para ícones de interface (seta, check, x), SVG de traço 2px."
      fallback: "svg de traço 2px desenhado no vocabulário de nós conectados"
    product-media:
      role: "Tela ou vídeo de produto em moldura 4:5 ({components.media-frame})."
      source: "user-upload"
      fallback: "brain-graph loop"
    team-photo:
      role: "Pessoa real nomeada."
      source: "user-upload"
      fallback: "initials-avatar"
      note: "NUNCA gerar por IA."
    partner-logo:
      role: "Minu, Core e marcas do ecossistema."
      source: "user-upload / arquivos oficiais do parceiro"
      note: "Nunca redesenhar logo de terceiro; sem caixa branca atrás."
  registry-format: |
    | deck | slide-id | slot | resolved-source | type |
    tabela apensada ao fim deste arquivo, nunca sobrescrita

slide-components:

  # ---------- CHARTS ----------
  chart-bar:
    use: "Comparar um valor entre até ~8 categorias discretas."
    construction: "Baseline único em zero, nunca eixo cortado. Largura da barra 60-70% do slot. Ordem com significado (tempo, ranking). Barras em {colors.primary}; a barra que a narrativa aponta em {colors.accent-data}; valor impresso no topo em {typography-slide.label}. Sem arredondamento no topo da barra."
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-surface-hi}"
    typography: "{typography-slide.label}"
    rounded: "{rounded.sm}"
    animation: "grow-from-baseline 600ms power2.out, stagger 80ms"
  chart-bar-horizontal:
    use: "Rótulos longos ou ranking de 5+ itens."
    construction: "Cresce da esquerda a partir do zero. Ordem decrescente por valor. Rótulo à esquerda em {typography-slide.body-sm}."
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.sm}"
    animation: "grow-from-left 600ms, stagger 80ms"
  chart-line:
    use: "Uma métrica contínua no tempo (ex.: pontos resgatados por mês)."
    construction: "Eixo X uniforme. Linha 3px {colors.accent-data}, sem preenchimento. Ponto atual marcado com {components.status-dot} ampliado. Trecho projetado tracejado a 50% de opacidade. Gridlines em {colors.neutral-700}."
    strokeColor: "{colors.accent-data}"
    animation: "draw-path 800ms easeOutCubic (anime.js)"
  chart-multi-line:
    use: "2-4 séries no mesmo eixo."
    construction: "Cores fixas por série em todo o deck, na ordem de {colors-extended.series}. Rótulo direto na ponta da linha, sem legenda solta."
    strokeColor: "{colors-extended.series}"
    animation: "draw-path 800ms, stagger 150ms entre séries"
  chart-area:
    use: "Quando o volume acumulado importa."
    construction: "Regras do chart-line. Preenchimento {colors.accent-data} a 12%. No máximo 2 áreas."
    strokeColor: "{colors.accent-data}"
    fillOpacity: 0.12
    animation: "draw-path 800ms, preenchimento entra 400ms depois"
  chart-donut:
    use: "Partes de um todo, 3-6 fatias."
    construction: "Maior fatia às 12h, sentido horário, ordem decrescente (salvo sequência natural). Máximo 6 fatias, resto em 'Outros'. Centro com um único número em {typography-slide.data-lg}. Anel com espessura de 18% do diâmetro, pontas retas (sem stroke-linecap round)."
    strokeColor: "{colors-extended.series}"
    backgroundColor: "{colors.neutral-700}"
    animation: "sweep 700ms, número central conta em paralelo"
  chart-scatter:
    use: "Relação entre duas variáveis, 8+ pontos (ex.: clusters de comportamento)."
    construction: "Eixos a partir de zero ou mínimo natural. Pontos 10px, {rounded.circle}, uma cor. Só o outlier da narrativa ganha rótulo."
    backgroundColor: "{colors.accent-data}"
    rounded: "{rounded.circle}"
    animation: "fade + scale 300ms, stagger 15ms"
  chart-bubble:
    use: "Três variáveis (x, y, tamanho)."
    construction: "Tamanho codificado na ÁREA. Legenda de tamanho obrigatória. Opacidade 75%."
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.circle}"
    animation: "scale-in 400ms back.out(1.4) — o único overshoot do deck"
  sparkline:
    use: "Tendência ambiente dentro de metric-card ou tabela."
    construction: "Sem eixo nem rótulo. 2px, altura até 40px, {colors.on-surface-mid}."
    strokeColor: "{colors.on-surface-mid}"
    animation: "draw-path 400ms"
  waterfall-buildup:
    use: "Ponte entre dois totais por contribuições (ex.: de onde vem o 2x de Minu+Core). Até 6-7 passos."
    construction: |
      Ancoragem indutiva — a barra n+1 é função da barra n:
      - bottom(1)=0, top(1)=valor(1), V(1)=top(1).
      - Aumento: bottom(n+1)=V(n), top=bottom+valor, V=top. Queda: top(n+1)=V(n), bottom=top-|valor|, V=bottom.
      - Barra final: bottom=0, top=V(n-1). Validar base+Σaumentos-Σquedas = total impresso antes de desenhar.
      Toda barra ancorada por `bottom`; só `height` anima. Conector tracejado {colors.neutral-700}.
    animation: "height 0→valor, stagger 150ms; barra final 40% mais lenta"
  waterfall-bar-increase:
    use: "Contribuição positiva."
    backgroundColor: "{colors-extended.semantic-positive}"
    textColor: "{colors.neutral-900}"
    animation: "height 0→valor 500ms"
  waterfall-bar-decrease:
    use: "Contribuição negativa."
    backgroundColor: "{colors-extended.semantic-negative}"
    textColor: "{colors.neutral-900}"
    animation: "height 0→valor 500ms"
  waterfall-bar-total:
    use: "Barra base e barra de resultado."
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    animation: "height 0→valor 700ms"
  waterfall-connector:
    use: "Liga o anchor de uma barra à próxima."
    strokeColor: "{colors.neutral-700}"
    strokeStyle: dashed
    animation: "fade 150ms após cada barra"

  # ---------- MÉTRICAS ----------
  metric-card:
    use: "Um número com contexto."
    construction: "Um número por card, rótulo acima em {typography-slide.overline}. Espaço para trend-indicator colado ao número. Fio de 1px, sem sombra."
    backgroundColor: "{colors.neutral-800}"
    textColor: "{colors.on-surface-hi}"
    typography: "{typography-slide.data-lg}"
    rounded: "{rounded.md}"
    padding: "{spacing.xl}"
    animation: "revealUp 650ms, stagger 100ms"
  big-number:
    use: "O dado que é o slide inteiro. Máximo 2 por deck."
    construction: "Sozinho, sem gráfico competindo. Unidade (%, R$, x, M) a 40% do tamanho do número. Uma linha de contexto abaixo em {typography-slide.body}. Pode receber {components.text-highlight} em uma palavra do contexto."
    textColor: "{colors.on-surface-hi}"
    typography: "{typography-slide.data-xl}"
    animation: "countUp 900ms (anime.js), contexto entra 300ms depois"
  kpi-tile:
    use: "Fileira de 3-4 KPIs abrindo resultados."
    construction: "Tiles de mesma altura, número na mesma linha de base. Separados por fio de 1px (gap 1px sobre {colors.neutral-700}), como a proof-band do site."
    backgroundColor: "{colors.secondary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: "{spacing.xl}"
    animation: "revealUp 650ms, stagger 100ms, countUp em paralelo"
  trend-indicator-up:
    use: "Anexado a um número."
    construction: "Seta + percentual, colado ao número."
    textColor: "{colors-extended.semantic-positive}"
    animation: "fade 250ms"
  trend-indicator-down:
    use: "Variante negativa."
    construction: "Mesmo tamanho e posição do up."
    textColor: "{colors-extended.semantic-negative}"
    animation: "fade 250ms"

  # ---------- FRAMEWORKS ----------
  quadrant-container:
    use: "Motor de qualquer 2×2."
    construction: "Eixos rotulados nas duas pontas ('baixo → alto'). 4 quadrantes de área igual, separados por fio {colors.neutral-700}. Quadrante-alvo pode receber fundo {colors.neutral-800}."
    strokeColor: "{colors.neutral-700}"
    animation: "eixos desenham 400ms antes das células"
  quadrant-cell:
    use: "Item plotado."
    construction: "Etiqueta retangular {components.badge-solid}; itens não se sobrepõem."
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.sm}"
    animation: "fade 300ms, stagger 100ms por quadrante"
  bcg-bubble:
    use: "Unidade de negócio numa BCG."
    construction: "Diâmetro por área. Nome dentro se couber, fora com linha-guia."
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.circle}"
    animation: "popBubble back.out(1.4) — conta como o overshoot do deck"
  swot-box:
    use: "Os 4 blocos do SWOT."
    construction: "Ordem fixa F/W em cima, O/T embaixo. Áreas iguais. 2-4 bullets. Superfícies: F {colors.primary}, W {colors.neutral-800}, O {colors.secondary}, T {colors.neutral-700}."
    rounded: "{rounded.md}"
    animation: "fade-slide do canto de cada box, stagger 150ms"
  matrix-header-cell:
    use: "Cabeçalho de matriz N×2/N×3."
    construction: "Uma linha de altura. Coluna recomendada com fundo {colors.primary}."
    backgroundColor: "{colors.neutral-800}"
    textColor: "{colors.on-surface-hi}"
    typography: "{typography-slide.label}"
    animation: "fade 200ms antes das linhas"
  matrix-data-cell:
    use: "Célula de dado."
    construction: "Texto à esquerda, número à direita. Fio {colors.neutral-700} entre linhas."
    strokeColor: "{colors.neutral-700}"
    animation: "fade 200ms, stagger 40ms"
  canvas-cell:
    use: "Bloco de Business Model / Value Proposition Canvas."
    construction: "Proposta de Valor central com borda 2px {colors.accent-data}, não cor diferente."
    strokeColor: "{colors.neutral-700}"
    rounded: "{rounded.sm}"
    animation: "fade 250ms, stagger 60ms; Proposta de Valor primeiro"

  # ---------- PROCESSO ----------
  process-step:
    use: "Caixa de fluxo linear de 3-5 etapas. É o flow-card do site."
    construction: "Mesma largura em todas. Topo: chip de ícone {components.chip-icon} + rótulo '01 / conecte' em {typography-slide.label} {colors.accent-data}. Caixas coladas por fio de 1px, não espaçadas."
    backgroundColor: "{colors.neutral-900}"
    strokeColor: "{colors.neutral-700}"
    rounded: "{rounded.md}"
    padding: "{spacing.xl}"
    animation: "revealSequence x 20px, stagger 150ms"
  process-connector-arrow:
    use: "Liga dois process-step."
    construction: "Conector circular 44px ({rounded.circle}) na borda entre caixas, com seta {colors.accent-data} e pulso {colors.accent-synapse}. Quebra de linha: seta em ângulo reto."
    strokeColor: "{colors.accent-data}"
    rounded: "{rounded.circle}"
    animation: "aparece após o step anterior; pulso de opacidade 2,4s em loop"
  synapse-link:
    use: "Assinatura da Brain: fio entre dois nós (parceiros, sistemas, camadas) com um ponto verde percorrendo."
    construction: "Fio 1px {colors.neutral-700}; ponto {components.status-dot} de 10px no palco. No máximo 2 fios animados por slide."
    rounded: "{rounded.circle}"
    animation: "ponto percorre o fio em 2,4s, fade nas pontas, loop; direções opostas em fios espelhados"
  timeline-node:
    use: "Marco de roadmap (ex.: 60 → 90 dias → camada LLM)."
    construction: "Espaçamento proporcional ao tempo real, ou declarar 'fora de escala'. Nó 16px {rounded.circle}; o marco atual em {colors.accent-synapse}."
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.circle}"
    animation: "scale-in 300ms, stagger 150ms ao longo do eixo"
  timeline-connector:
    use: "Eixo contínuo do roadmap."
    construction: "Linha única 2px; trecho futuro tracejado."
    strokeColor: "{colors.neutral-700}"
    animation: "draw-path em sincronia com os nós"
  funnel-segment:
    use: "Queda de volume em etapas."
    construction: "Largura proporcional ao valor real. Retângulos centrados (sem trapézio arredondado); opacidade decresce por etapa a partir de {colors.primary}."
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.sm}"
    animation: "shrink-in-width 400ms, stagger 150ms"
  cycle-node:
    use: "Processo recorrente (ex.: Coleta → Análise → Ação → Coleta)."
    construction: "3-6 nós, horário. Nó quadrado com rótulo; o arco é um fio. É o loop de melhoria contínua da Brain."
    strokeColor: "{colors.accent-data}"
    rounded: "{rounded.sm}"
    animation: "nós na ordem do arco; o conector final fecha o loop por último"

  # ---------- COMPARAÇÃO ----------
  comparison-column:
    use: "2-5 opções lado a lado."
    construction: "Mesma largura, títulos na mesma altura. Colunas separadas por fio de 1px."
    backgroundColor: "{colors.neutral-800}"
    rounded: "{rounded.md}"
    padding: "{spacing.xl}"
    animation: "revealUp, stagger 120ms esquerda→direita"
  comparison-column-featured:
    use: "A opção que a Brain recomenda. Uma por slide."
    construction: "Mesmo conteúdo e dimensão; só a superfície muda: {components.card-highlight-solid}."
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    animation: "revealFeatured, pousa 100ms depois das vizinhas"
  comparison-row:
    use: "Linha de tabela de features."
    construction: "Altura consistente, fio {colors.neutral-700}."
    strokeColor: "{colors.neutral-700}"
    animation: "fade 250ms, stagger 40ms"
  versus-divider:
    use: "Só entre exatamente 2 colunas."
    construction: "Centralizado; 'vs' em {typography-slide.label} dentro de um quadrado {colors.primary}."
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.sm}"
    animation: "scale-in 300ms, por último"
  check-glyph:
    use: "Célula positiva."
    construction: "Mesmo tamanho do x-glyph. SVG de traço 2px."
    textColor: "{colors.accent-data}"
    animation: "fade 200ms"
  x-glyph:
    use: "Célula negativa."
    construction: "Paridade com check-glyph."
    textColor: "{colors.on-surface-low}"
    animation: "fade 200ms"
  pricing-tier:
    use: "Plano/pacote numa grade de 2-4."
    construction: "Mesma largura e ordem (nome → preço → lista)."
    backgroundColor: "{colors.neutral-800}"
    rounded: "{rounded.md}"
    animation: "revealUp, stagger 120ms"
  pricing-tier-featured:
    use: "O plano recomendado — única distinção estática permitida num grupo simétrico."
    construction: "Só a superfície muda ({colors.primary}); sem scale de layout, sem sombra."
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    animation: "revealFeatured, 100ms depois"

  # ---------- CARDS DE CONTEÚDO ----------
  content-card:
    use: "Bloco de texto com moldura."
    construction: "Até 3 linhas de corpo. Mais que isso vira modal-content-card. Neutro por padrão; hover = borda {colors.primary} + translateY(-4px), sem sombra."
    backgroundColor: "{colors.neutral-800}"
    textColor: "{colors.on-surface-mid}"
    rounded: "{rounded.md}"
    padding: "{spacing.xl}"
    animation: "revealUp 650ms, stagger 100ms"
  icon-card:
    use: "Benefício com ícone de sinapse."
    construction: "Pictograma da marca sempre no mesmo tamanho (56px) e cor em toda a lista; um ícone por ideia."
    iconColor: "{colors.on-surface-hi}"
    backgroundColor: "{colors.neutral-800}"
    rounded: "{rounded.md}"
    animation: "ícone scale-in 250ms, texto revealUp 250ms"
  highlight-card:
    use: "Diferencial ou mensagem principal que precisa pesar mais que o fundo (Diferenciais do site)."
    construction: "{components.card-highlight-solid}. Overline branca em negrito. Pode ser a grade inteira quando está sobre um float-panel claro."
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: "{spacing.xl}"
    animation: "revealUp 650ms, stagger 100ms"
  glass-card:
    use: "Texto sobre foto ou vídeo."
    construction: "{components.glass-card}: fundo {colors.neutral-900} a 78% + blur 6px, fio colorido. Nunca texto solto sobre imagem."
    rounded: "{rounded.md}"
    animation: "entra do lado oposto ao da mídia, x ±60px, 700ms"
  quote-card:
    use: "Depoimento com atribuição."
    construction: "Uma citação por slide, aspas em {colors.accent-data}, atribuição (nome + cargo + empresa) sempre visível."
    backgroundColor: "{colors.neutral-900}"
    textColor: "{colors.on-surface-hi}"
    typography: "{typography-slide.subtitle}"
    padding: "{spacing.3xl}"
    animation: "fade 600ms, sem stagger"
  profile-card:
    use: "Pessoa."
    construction: "Foto real (user-upload) em quadrado; avatar circular só na versão compacta. Nome + cargo."
    rounded: "{rounded.md}"
    avatarRounded: "{rounded.circle}"
    animation: "revealUp, stagger 100ms"
  logo-tile:
    use: "Ecossistema e prova social."
    construction: "Área visual similar entre logos. Logo sobre o próprio fundo do slide, sem caixa branca. Fio de 1px em volta, opcional."
    strokeColor: "{colors.neutral-700}"
    rounded: "{rounded.sm}"
    animation: "fade 250ms, stagger 60ms"
  text-highlight:
    use: "Grifo de 1-2 frases-chave por bloco."
    construction: "{components.text-highlight} ({colors.primary} atrás do texto branco). Sobre foto/vídeo: {components.text-highlight-invert}. No máximo 15% do texto."
    rounded: "{rounded.sm}"
    animation: "o retângulo cresce da esquerda (scaleX 0→1, 500ms) depois do texto aparecer"

  # ---------- TABELAS ----------
  table-header-cell:
    use: "Cabeçalho de tabela densa."
    construction: "Sublinhado 2px {colors.primary}, sem fundo sólido. Caixa-alta em {typography-slide.overline}."
    strokeColor: "{colors.primary}"
    typography: "{typography-slide.overline}"
    animation: "fade 200ms"
  table-row:
    use: "Linha de dado."
    construction: "Números à direita, em Roboto Mono (tabular por natureza)."
    strokeColor: "{colors.neutral-700}"
    animation: "fade 250ms, stagger 50ms"
  table-row-highlight:
    use: "Linha de resultado. 1-2 por tabela."
    backgroundColor: "{colors.neutral-800}"
    strokeColor: "{colors.accent-data}"
    animation: "como table-row + borda esquerda 3px {colors.accent-data} desenhando"

  # ---------- LAYOUT / ESTRUTURA ----------
  split-panel:
    use: "Foto + texto, antes × depois, branco × navy."
    construction: "55/45 a favor do texto quando o texto é denso. Variante de marca: metade {colors.surface-card} com texto {colors.ink} + metade {colors.neutral-900} com a arte."
    animation: "painéis entram dos lados opostos, 500ms"
  full-bleed-media:
    use: "Capa, divisor, reveal."
    construction: "object-fit: cover. Scrim em gradiente de {colors.neutral-900} (não cor chapada) quando há texto. Capas oficiais (cover-photo) já trazem a wordmark: não sobrepor título grande sobre elas."
    rounded: "{rounded.sm}"
    animation: "fade 600ms; ken-burns 1.0→1.04 em 10s opcional"
  float-panel-slide:
    use: "Slide claro que 'flutua' sobre o navy — conteúdo denso, comparativos, respiro no meio de um deck escuro."
    construction: "{components.float-panel}: painel {colors.surface-float} inset 40px do canvas, sobre {colors.neutral-900}. Dentro: títulos {colors.primary}, texto {colors.ink}, ícones {colors.on-light-low}, cards {colors.surface-card} ou highlight-card. Nunca {colors.accent-data} como texto."
    backgroundColor: "{colors.surface-float}"
    rounded: "{rounded.sm}"
    animation: "painel sobe 40px enquanto o slide entra (revealUp, 800ms); highlight-cards sobem 70px (camada mais próxima)"
  section-divider:
    use: "Entre seções."
    construction: "Só o título do capítulo em duas linhas: 'Capítulo 2:' em {typography-slide.chapter-kicker} + título em {typography-slide.divider}. Fundo {colors.primary} sólido ou cover-photo."
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    animation: "revealCinematic 900ms — o único slide cinematográfico"
  progress-indicator:
    use: "Trilho de posição em todo slide."
    construction: "Segmentos retangulares de 2px de altura, contados do DOM. Segmento atual {colors.accent-data}."
    rounded: "{rounded.sm}"
    animation: "cor 200ms na troca"
  agenda-item:
    use: "Agenda."
    construction: "Máximo 6. Número '01' em {typography-slide.label} {colors.accent-data} + título em {typography-slide.subtitle}. Item atual pode ser grifado."
    typography: "{typography-slide.subtitle}"
    animation: "fade-slide-left 350ms, stagger 100ms"
  vertical-tagline:
    use: "Moldura da marca em quase todo slide."
    construction: "{slide-canvas.vertical-tagline}. Some em capa fotográfica e em slide claro com mídia."
    textColor: "{colors.on-surface-low}"
    typography: "{typography-slide.caption}"
    animation: "nenhuma"
  wordmark:
    use: "Logo no canto superior ou na capa."
    construction: "Sempre o PNG oficial (branco sobre escuro/azul, preto sobre claro). Área livre = 1× altura do 'B'. Altura no canto: 36px."
    animation: "nenhuma no canto; na capa, fade 600ms"

  # ---------- BENTO ----------
  bento-cell-photo:
    use: "Célula com imagem real no bento."
    construction: "object-fit: cover; legenda no canto inferior sobre scrim {colors.neutral-900}. Sem rotação (a marca é ortogonal)."
    backgroundColor: "{colors.neutral-800}"
    rounded: "{rounded.md}"
    animation: "revealUp 650ms"
  bento-cell-icon:
    use: "Célula só ícone + texto curto."
    construction: "Até 2 linhas. Alterna {colors.neutral-800} e {colors.primary} para ritmo."
    backgroundColor: "{colors.neutral-800}"
    rounded: "{rounded.md}"
    padding: "{spacing.xl}"
    animation: "revealUp, stagger 100ms após as fotos"
  bento-expand-button:
    use: "Abre modal-image-overlay."
    construction: "Quadrado 48px no canto inferior direito, '+' em Roboto Mono, fundo {colors.neutral-900} a 70%."
    rounded: "{rounded.sm}"
    size: "48px"
    animation: "hover: fundo {colors.primary}"

  # ---------- CARROSSEL ----------
  carousel-card:
    use: "Mais pontos do que cabem lado a lado, cada um com profundidade sob demanda."
    construction: "Largura fixa 440px, scroll-snap, peek do próximo card. Botão '+' abre modal-content-card. Todos neutros."
    backgroundColor: "{colors.neutral-800}"
    rounded: "{rounded.md}"
    padding: "{spacing.xl}"
    animation: "a fileira faz revealUp; scroll nativo"
  carousel-card-featured:
    use: "Só com razão semântica real."
    construction: "Mesma dimensão; borda 2px {colors.primary}."
    strokeColor: "{colors.primary}"
    rounded: "{rounded.md}"
  carousel-nav-chevron:
    use: "Setas do carrossel."
    construction: "Quadrado 56px, fio {colors.neutral-700}, seta de traço 2px. Desabilitada nas pontas; some se não houver overflow."
    rounded: "{rounded.sm}"
    size: "56px"
    animation: "hover: fundo {colors.primary}; clique: scrollBy smooth"

  # ---------- MODAL ----------
  modal-content-card:
    use: "Destino de '+' que expande texto."
    construction: "Ordem: overline → título → 2-4 frases → link opcional. Véu {colors.neutral-900} a 72% + blur 4px. Sem sombra."
    backgroundColor: "{colors.neutral-800}"
    strokeColor: "{colors.neutral-700}"
    rounded: "{rounded.md}"
    padding: "{spacing.2xl}"
    animation: "véu 350ms; card cresce do centro (scale .94→1, y 10→0), power2.out"
  modal-image-overlay:
    use: "Destino de '+' que expande imagem."
    construction: "Véu {colors.neutral-900} a 90%; legenda abaixo da imagem."
    rounded: "{rounded.sm}"
    animation: "igual ao modal-content-card"

  # ---------- MOMENTO ----------
  headline-typed:
    use: "Capa ou reveal: a frase-manifesto com uma palavra que troca (como o hero do site)."
    construction: "Palavra dentro de {components.text-highlight-invert} (fundo branco, texto {colors.secondary}), cursor piscando. Substitui o 'texto com gradiente' genérico — a Brain não usa texto em gradiente. Máximo 1-2 slides por deck."
    typography: "{typography-slide.cover}"
    animation: "máquina de escrever: 90ms/letra, 45ms apagando, 1,4s parada"
  cta-block:
    use: "Pedido final ou proposta comercial com contexto."
    construction: "Faixa {colors.primary}: texto do pedido à esquerda, {components.button-white} à direita. Retângulo, nunca cápsula."
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.sm}"
    padding: "{spacing.xl}"
---

# Brain003 — Slides

## Overview

Este é o companion de apresentação do `design-v3.md`. A hierarquia é atômica:

```
design-v3.md → ÁTOMOS      cores, tipografia, raio, espaçamento, componentes do site
SLIDES.md    → MOLÉCULAS   slide-components (chart-bar, big-number, process-step, float-panel-slide…)
             → ORGANISMOS  templates de slide nomeados, com storytelling
```

Um slide nunca redescreve cor, fonte ou raio: diz "este slide é 3× `kpi-tile` + 1× `chart-bar`". Toda referência `{colors.x}`, `{typography.x}`, `{rounded.x}`, `{spacing.x}` e `{components.x}` aponta para o `design-v3.md`; `{typography-slide.x}`, `{colors-extended.x}`, `{slide-components.x}` e `{slide-canvas.x}` apontam para este arquivo. O script `scripts/check_slides_refs.py` da skill `brain003-design` confere que todas resolvem.

Três coisas herdadas do design-v3 que mais mudam um deck em relação a um deck genérico:

- **Tudo reto.** Nenhum card, botão, barra, modal ou seta arredondados. Círculo só em ponto de dado, nó de timeline, conector e avatar (`{rounded.circle}`).
- **Zero sombra.** Profundidade vem de camada tonal (`neutral-900` → `800` → `700`), fio de 1px e movimento. O hover de card é borda `primary` + subir 4px, sem sombra.
- **Monospace é a voz.** Deck comercial é todo em Roboto Mono; deck de produto usa Inter no corpo (`{deck-voice}`).

A assinatura visual própria da Brain que entra no palco: o grifo azul (`text-highlight`), a tagline vertical na borda, a palavra que troca na capa (`headline-typed`), o fio de sinapse com o ponto verde (`synapse-link`), os pictogramas de nós conectados e o bloco claro flutuando sobre o navy (`float-panel-slide`).

**Deck-modelo:** `assets/deck-template/deck.html` na skill `brain003-design` (cópia publicada em `artifacts/presentations/deck-modelo/`) mostra 21 slides com os templates principais funcionando: navegação, animação, modal, carrossel, waterfall calculado. As imagens da marca são referenciadas pela URL pública do brandbook, com cópia local em `img/` como reserva; GSAP e anime.js ficam em `lib/`. Comece copiando a pasta: cada `<section>` tem `data-template` com o nome do template deste arquivo. Para um arquivo único (e-mail, artifact), `scripts/embed_deck.py`.

### Mapa do deck-modelo

Cada `<section>` do deck-modelo declara `data-template` com um destes slugs; `check_slides_refs.py` confere que os dois lados batem.

| # | data-template | Template (seção abaixo) |
|---|---|---|
| 01 | `capa-fotografica` | Capa fotográfica |
| 02 | `capa-manifesto` | Capa manifesto |
| 03 | `agenda` | Agenda |
| 04 | `capitulo` | Capítulo |
| 05 | `sumario-executivo` | Sumário executivo |
| 06 | `branco-navy` | Branco × navy |
| 07 | `3-passos` | 3 passos |
| 08 | `big-number` | Big number |
| 09 | `divisor-fotografico` | Divisor fotográfico |
| 10 | `midia-glass-cards` | Mídia + glass cards |
| 11 | `dashboard` | Dashboard 3 cards + 2 gráficos |
| 12 | `waterfall` | Waterfall de crescimento |
| 13 | `ecossistema` | Ecossistema |
| 14 | `bloco-claro-flutuante` | Bloco claro flutuante |
| 15 | `comparacao-categorias` | Não somos CDP nem BI |
| 16 | `matriz-2x2` | Matriz 2×2 |
| 17 | `roadmap` | Roadmap |
| 18 | `carrossel-popup` | Carrossel de módulos com popup |
| 19 | `midia-texto` | Vídeo em loop / Foto + texto |
| 20 | `fechamento` | Fechamento / Ask |
| 21 | `contato` | Contato |

## Image Bank

A Brain tem biblioteca própria com a assinatura (fotos tratadas azul/ciano de exame, laboratório, térmica; grafos; pictogramas), então a ordem é **biblioteca da marca → geração → stock**. Capas oficiais (`logo_Brain_2001` a `2007`) já trazem a wordmark: são capa pronta, não fundo para outro título. Pessoas reais nunca são geradas por IA. Logos de parceiros entram sem caixa branca. Cada deck registra os assets resolvidos na tabela ao fim deste arquivo.

## Slide Components

Os tokens completos estão no frontmatter; aqui fica o critério de escolha por família.

**Charts.** `chart-bar` para comparar, `chart-line` para tendência, `chart-donut` para composição (até 6 fatias), `chart-scatter`/`chart-bubble` para relação, `waterfall-buildup` para ponte entre totais. Barras em `primary`, a barra da história em `accent-data`, positivo/negativo em `success`/`error` (só sobre escuro). Sem canto arredondado em barra, sem `linecap` redondo em donut. A regra de ancoragem do waterfall não é opcional: valide a soma antes de desenhar.

**Métricas.** `big-number` (no máximo 2 por deck) quando um dado é o argumento; `kpi-tile` em fileira `secondary` colada por fio, como a faixa de prova do site; `metric-card` para número com contexto e tendência.

**Frameworks.** `quadrant-container` serve para 2×2, BCG e Ansoff; `swot-box` em quatro superfícies da marca; `matrix-*` para comparação densa, com a coluna recomendada em `primary`.

**Processo.** `process-step` é o flow-card do site: caixas coladas por fio, rótulo "01 / conecte" em ciano, conector circular com pulso verde. `synapse-link` é a assinatura para ligar sistemas e parceiros. `cycle-node` desenha o loop Coleta → Análise → Ação.

**Comparação.** Colunas neutras; a recomendada vira `comparison-column-featured` (bloco `primary` chapado), no máximo uma por slide.

**Cards de conteúdo.** `content-card` neutro; `highlight-card` azul sólido para a mensagem principal; `glass-card` para texto sobre mídia; `icon-card` com pictograma da marca.

**Tabelas.** Cabeçalho sublinhado em `primary`, números à direita, linha de resultado com borda ciano.

**Layout.** `section-divider` em `primary` sólido com o título em duas linhas ("Capítulo 2:" + título); `split-panel` na variante branco × navy; `float-panel-slide` para respiro claro; `vertical-tagline` e `wordmark` como moldura.

**Bento, carrossel e modal.** Mesma lógica da slidemaster, com cantos retos, botões quadrados e véu com blur em vez de sombra. Todo "+" aponta para um `modal-content-card` ou `modal-image-overlay` definido no roteiro do deck.

**Momento.** `headline-typed` substitui o texto em gradiente genérico; `cta-block` substitui a cápsula de preço.

## Slide Templates

Formato: **Nome** — composição · quando usar · bom para representar · animação · exemplo Brain.

### 1 — Estrutura & Narrativa

**Capa fotográfica** — `full-bleed-media` com uma `cover-photo` oficial (já tem a wordmark) + título do deck pequeno no rodapé em `{typography-slide.label}`. · Abertura de deck institucional ou de posicionamento. · Marca antes de argumento. · fade 600ms da foto, rodapé 300ms depois. · *"Brain003 · Proposta para Caixa Cartões · set/2026"* sobre a capa de ressonância.

**Capa manifesto** — `headline-typed` sobre `{colors.neutral-900}` + `wordmark` no canto + subtítulo. · Deck comercial que abre com a tese. · Promessa em uma frase. · título revela, palavra começa a digitar. · *"Transformamos seus dados em [receita · vendas · decisão]"*.

**Agenda** — `agenda-item` × 3-6 + `progress-indicator`. · Decks com 3+ seções. · Mapa mental. · stagger 100ms. · *Contexto · O que a Brain faz · Clean Data Room · Plano de 90 dias · Próximos passos.*

**Sumário executivo** — tese em `{typography-slide.title}` com `text-highlight` + 3 `content-card`. · Audiência sênior que pode sair antes do fim. · Conclusão antes da evidência. · tese, grifo, cards. · *"A Brain dobra o faturamento de Minu+Core cobrando pela inteligência entregue."*

**Contexto e objetivos** — `split-panel`: contexto à esquerda, lista numerada à direita. · Abertura de conteúdo. · O porquê. · painéis dos lados. · *Dados fragmentados entre mídia, vendas, ERP e fidelidade × 3 objetivos do projeto.*

**Situação · Complicação · Resolução** — 3 blocos em `split-panel` com `hero-photo` no lado livre; a Resolução é um `highlight-card`. · Apresentar problema antes da solução. · Tensão narrativa. · rápido → pausa 900ms → resolução com `revealFeatured`. · *S: o UAU Caixa foi o motor · C: caiu de ~13M para ~4M pontos/mês desde o Pix · R: inteligência de comportamento para reativar.*

**Capítulo** — `section-divider`. · Entre seções. · Respiro. · `revealCinematic`. · *"Capítulo 2: / O Clean Data Room"*.

**Divisor fotográfico** — `full-bleed-media` + scrim. Com `cover-photo` (que já traz a wordmark), o capítulo entra pequeno no rodapé em `{typography-slide.label}`; título grande só sobre `hero-photo` sem wordmark. · Seção com peso emocional. · Mudança de tom. · `revealCinematic`. · *"Capítulo 3 · O Clean Data Room" no rodapé da capa de plasma.*

**Roadmap** — `timeline-node` + `timeline-connector`. · Plano no tempo. · Fases com prazos. · nós em sequência. · *60 dias: dashboard · 90 dias: integração via API · depois: camada de LLM.*

**Fechamento / Ask** — `cta-block` + 3 `content-card` de próximos passos. · Último slide. · Decisão clara. · cards, depois a faixa. · *"Aprovar o piloto de 60 dias"* + responsáveis e datas.

**Contato** — `wordmark` grande + `vertical-tagline` + contato em `{typography-slide.label}`. · Fim de deck enviado por e-mail. · Onde encontrar a Brain. · fade único.

### 2 — Build-up

**Waterfall de crescimento** — `waterfall-bar-increase` × N + `waterfall-bar-total`. · Construir um número a partir de drivers. · Origem do total. · barras 150ms, total mais lento. · *Faturamento atual → + novos clientes → + revenue share → + Brain Score → meta 2x.*

**Waterfall de perda** — `waterfall-bar-decrease` × N. · Onde o valor se perdeu. · Diagnóstico. · barras caindo em sequência. · *Pontos/mês de ~13M para ~4M, por causa.*

**Bullets progressivos** — linhas `{typography-slide.body}` entrando uma a uma; a anterior cai para 40%. · Argumento passo a passo, ao vivo. · Ritmo de fala. · clique por linha.

**Grifo progressivo** — parágrafo em `{typography-slide.body}` + `text-highlight` entrando por clique em 1-2 frases. · Deck comercial com texto. · O que importa no parágrafo. · retângulo cresce da esquerda.

### 3 — Comparação & Matrizes

**Comparação 2-5 colunas** — `comparison-column` × N (+ `versus-divider` se N=2) + uma `comparison-column-featured`. · Alternativas. · Escolha recomendada. · stagger 120ms, featured por último. · *CDP × BI × Brain.*

**Não somos CDP nem BI** — 3 colunas com `check-glyph`/`x-glyph` por capacidade, coluna Brain em `primary`. · Posicionamento contra categorias. · Diferença de categoria. · linhas stagger 40ms.

**Matriz N×3** — `matrix-header-cell` + `matrix-data-cell`. · Benchmark em critérios. · Decisão de compra. · stagger 40ms.

**Tabela de features** — `table-header-cell` + `table-row` + glyphs. · Specs entre pacotes. · Binário. · fade.

**Antes × Depois** — `split-panel` com o "antes" em `{colors.neutral-800}` e o "depois" em `float-panel-slide`. · Transformação. · O reveal é o argumento. · lado direito entra 500ms depois.

**De-Para** — pares ligados por `process-connector-arrow`. · Migração item a item. · Relatório → ação.

**Pacotes** — `pricing-tier` × 2-4 + um `pricing-tier-featured`. · Proposta comercial. · Escolha guiada. · featured por último.

### 4 — Frameworks

**Matriz 2×2** — `quadrant-container` + `quadrant-cell`. · Priorização (impacto × esforço). · Onde começar. · eixos, depois itens.

**BCG** — `quadrant-container` + `bcg-bubble`. · Portfólio de módulos ou marcas. · Maturidade. · bolhas com overshoot (o único do deck).

**SWOT** — 4× `swot-box`. · Diagnóstico. · Visão equilibrada. · cada caixa do seu canto.

**5 Forças** — força central + 4 periféricas com `process-connector-arrow`. · Atratividade de mercado (varejo como "oceano azul"). · Pressão competitiva.

**PESTEL** — 2×3 de `icon-card`. · Macroambiente (LGPD, fim dos cookies). · Due diligence.

**Ansoff** — `quadrant-container` rotulado. · Estratégia de crescimento. · Risco crescente.

**7S** — 7 `cycle-node` com valores no centro. · Diagnóstico organizacional (empresa AI-first).

**Cadeia de valor** — `process-step` primários + apoio. · Onde a Brain gera valor na operação do cliente.

**RACI** — `matrix-*`. · Responsabilidades entre Brain, Minu, Core e cliente.

### 5 — Modelo de Negócio

**TAM · SAM · SOM** — quadrados concêntricos (não círculos: a marca é ortogonal) com `big-number` em cada nível. · Dimensionar oportunidade. · Funil de realismo. · TAM primeiro, SOM por último.

**Business Model Canvas** — 9× `canvas-cell`. · Modelo da Brain (de venda de token para cobrança pela inteligência entregue). · Proposta de valor primeiro.

**Value Proposition Canvas** — 2 lados + setas. · Encaixe dor × solução por persona (agências × grande varejo). · setas por último.

**Clean Data Room** — `synapse-link` entre "Sua base", "Clean Room" e "Base do parceiro" + 2 `glass-card` (Conexão, Cruzamento). · Explicar privacidade. · Nenhuma parte vê o dado bruto da outra. · nós, fios, pontos verdes, cards de lados opostos.

**Ecossistema** — `logo-tile` (Minu, Core) ligados à Brain por `synapse-link`. · Quem alimenta a inteligência. · Força da rede. · logos juntos, pontos correndo.

### 6 — Financeiro & Métricas

**Big number** — `big-number`. · Momento "uau" (máximo 2 por deck). · Um dado que decide. · countUp. · *"~16 anos" de relação com o Banco do Brasil.*

**KPIs em faixa** — 3-4 `kpi-tile` em `secondary` colados por fio. · Abrir uma seção de resultados. · Placar. · tiles, depois contagem.

**Dashboard 3 cards + 2 gráficos** — `kpi-tile` + `chart-bar`/`chart-line`. · Resultado com explicação. · KPIs primeiro.

**Grade de métricas** — `metric-card` × 4-6. · Quando os números contam sozinhos.

**Gráfico + texto** — `split-panel`: chart à esquerda, insight à direita com grifo. · Explicar um gráfico. · Gráfico desenha, texto entra.

**Gráfico full-bleed** — um chart no slide inteiro. · Quando a forma da curva é o argumento. · *Queda de pontos/mês após o Pix.*

**Projeção** — `chart-bar` por período, projetado tracejado. · Metas. · Fato × previsão.

**DRE simplificada** — `table-row` + `table-row-highlight`. · Viabilidade. · Resultado. · cascata contábil.

**Tabela de dados** — `table-*`. · Apêndice. · Referência. · fade único.

### 7 — Visual + Texto

**Foto + texto** — `split-panel` com `hero-photo` ou `data-art`. · Cavalo de batalha do deck.

**Mídia + glass cards** — `full-bleed-media` ou `media-frame` + 2 `glass-card` de lados opostos. · Explicar um conceito visual. · (É a seção Clean Data Room do site em formato de slide.)

**Branco × navy** — `split-panel` variante de marca: texto `ink` no branco, arte no navy. · Slide de argumento do deck comercial.

**Bloco claro flutuante** — `float-panel-slide` + 3 `highlight-card`. · Respiro e mensagem principal no meio do deck escuro. · Diferenciais. · painel sobe, cards sobem mais. · *"Não somos CDP e nem BI. Somos muito mais."*

**Grade de fotos** — 3-4 `full-bleed-media`. · Variedade sem prosa.

**Ícones de sinapse** — `icon-card` × 3-6 com pictogramas. · Benefícios (use bento se houver imagem real).

**Citação** — `quote-card`. · Prova qualitativa. · fade lento.

**Vídeo em loop** — `media-frame` 4:5 com brain-graph + título e 3 linhas. · Produto que "respira". · vídeo sem som, autoplay.

### 8 — Processo

**3 passos** — 3 `process-step` + `process-connector-arrow`. · Como funciona. · Conecte · Pergunte · Execute. · sequência 150ms.

**5 passos** — 5 `process-step`. · Granularidade. · stagger mais rápido.

**Passo a passo numerado** — número em `{typography-slide.data-lg}` + `content-card`. · Onde a ordem importa (onboarding).

**Funil** — `funnel-segment`. · Pipeline ou conversão.

**Ciclo** — `cycle-node`. · Loop de melhoria contínua: Coleta → Análise → Ação.

**Arquitetura em camadas** — faixas horizontais `content-card` empilhadas (Fontes → Clean Room → Inteligência → Decisão → Ativação → Medição) com `synapse-link` de retorno. · Arquitetura. · camadas de baixo para cima.

### 9 — Pessoas & Prova

**Perfil** — `profile-card` grande. · Pessoa-chave.

**Time** — grade de `profile-card`. · Quem entrega.

**Prova social** — grade de `logo-tile`. · Marcas do ecossistema. · todos quase juntos.

### 10 — Interativos

**Carrossel de módulos com popup** — `carousel-card` × 4-6 com "+" → `modal-content-card`. · Painel 360°, Painel de Produtos, Brain Score, Campaign Analytics, Converse com seus dados, cada um com profundidade sob demanda.

**Bento de soluções** — `bento-cell-photo` + `bento-cell-icon` + `bento-expand-button` → `modal-image-overlay`. · Mostrar as soluções com telas reais.

**Grade de vantagens com popup** — cards pequenos com pictograma + "+" → `modal-content-card`. · Diferenciais com explicação curta sob demanda.

## Animation Principles

Herda as regras da slidemaster (sutil e elegante) e o capítulo Motion do `design-v3.md`:

- **Amplitude pequena:** entrada com `y` de 12-16px e `scale` de 0,94-0,97. A exceção é o `float-panel-slide` (40px) e seus `highlight-card` (70px), que imitam o paralaxe do site: a camada mais próxima anda mais.
- **Easing:** `power2.out` / `power3.out`. Overshoot só na `bcg-bubble`, e só uma família por deck. Nunca em texto.
- **Duração:** 600-700ms em reveals de texto e card; 900ms no divisor.
- **Timing por família:** build-up com pausas de 700-900ms; grades densas com stagger de 40-80ms; stagger total nunca acima de ~1,5s.
- **O mais importante pousa por último:** total do waterfall, coluna recomendada, resolução do SCR, palavra digitada da capa.
- **Navegação por clique** (setas, espaço, clique), com builds internos por slide. Transição entre slides por crossfade de 500ms, nunca slide lateral.
- **Assinaturas em loop são as únicas animações contínuas** (ponto verde no `synapse-link`, pulso do conector, cursor da capa), e nunca mais de duas por slide.
- **`prefers-reduced-motion`:** tudo pousa direto no estado final; loops param.
- **Motor:** GSAP 3.12.5 + anime.js 3.2.2 como arquivos locais em `lib/` ao lado do deck (a skill traz os dois em `assets/deck-template/lib/`); nunca CDN. `embed_deck.py` embute os dois quando o deck precisa ser arquivo único. Uma `gsap.timeline()` por slide com os presets `revealUp`, `revealScale`, `revealCinematic`, `revealFeatured`, `revealSequence`, `growBars`, `countUp`, `drawPath`, `popBubble`, `openModal`/`closeModal`, `typeWord` (já implementados no deck-modelo).
- **Hover** é transição CSS (borda `primary` + `translateY(-4px)`, 300ms), nunca sombra.
- **Modo estático:** `?static` na URL do deck desliga toda animação e mostra o estado final. Serve para conferir layout, tirar screenshot e exportar PDF. Não posicione elementos animados com `transform` inline — o modo estático limpa o `transform`; centralize com `margin:auto`.
- **Grifo e entrelinha:** título com `text-highlight` precisa de entrelinha ≥ 1,15, e a palavra da capa (`headline-typed`) usa bloco alinhado pela linha de base com entrelinha 1,08; menos que isso, o bloco colorido cobre a linha de cima.

## Do's and Don'ts (camada de apresentação)

- Do: uma ideia por slide; se precisar de mais de 3 linhas num card, use modal.
- Do: declarar a voz do deck (comercial = tudo mono) antes de escrever o corpo.
- Do: usar capa oficial como capa pronta, sem título grande por cima.
- Do: numerar slides no rodapé e manter o `progress-indicator` contado a partir do DOM.
- Do: ligar sistemas e parceiros com `synapse-link` em vez de setas genéricas.
- Don't: texto em gradiente, cápsula arredondada, card com sombra ou hover com sombra.
- Don't: pintar um card de azul em um grupo simétrico só para "chamar atenção" — `primary` sólido é recomendação ou mensagem principal.
- Don't: `accent-synapse` como texto, nem positivo em verde sobre slide claro (use `{colors-extended.semantic-positive-on-light}`).
- Don't: círculos concêntricos, bolhas e nós arredondados fora de dado/timeline/conector — TAM-SAM-SOM e ciclos usam quadrados.
- Don't: mais de 2 `big-number`, 2 `headline-typed` ou 2 loops animados por slide.
- Don't: "Brain 003" ou "Brain3"; no texto do slide é "a Brain".

## Iteration Guide

1. Componente novo: adicione em `slide-components` com `use`, `construction` e tokens que existam no `design-v3.md`; rode `check_slides_refs.py`.
2. Template novo: descreva composição · quando · bom para · animação · exemplo; se ele se repetir em decks reais, implemente-o no `deck-template/deck.html`.
3. Token que não existe no `design-v3.md`: corrija o `design-v3.md` primeiro, nunca só este arquivo.
4. Depois de mudar este arquivo ou o `design-v3.md`, rode `sync_references.py` na skill.

## Known Gaps

- **`semantic-warning` (#FFB547) e `semantic-negative-on-light` (#C8284A) são propostas** — a marca não tem âmbar nem vermelho escuro. Até aprovar, evite estados de alerta e, no claro, use texto `ink` com ícone `x-glyph`.
- **Positivo sobre claro usa `primary`**, porque o verde neon some no fundo claro. Funciona, mas perde a semântica de cor: sempre acompanhe com seta ou sinal.
- **Pictogramas só existem em PNG 70-87px.** Acima de ~80px no palco eles perdem nitidez; falta a versão vetorial da família.
- **Ícones de interface** (seta, check, x, +) não existem na biblioteca; o deck-modelo usa SVG de traço 2px desenhados no próprio arquivo.
- **Foto real do time** não está na biblioteca: `profile-card` depende de upload.
- **Logos da Minu e da Core não estão online** (só embutidos no site) e ficam locais no deck. Adicioná-los a `brandbook/visual-assets/` no repo de artefatos os coloca na online-base.
- **O brandbook publicado mostra as próprias imagens quebradas**: o `artifacts-home` resolve os caminhos relativos a partir da raiz do repo, não da pasta do artefato. As URLs completas (`…/raw/brandbook/visual-assets/…`) funcionam.
- **Logo da Core só existe em JPEG 200px** com fundo preto. O deck usa uma versão com fundo removido, de borda levemente serrilhada; falta o vetor oficial. (O site ainda mostra o JPEG com o quadrado preto.)
- **A lista de produtos do brandbook é antiga**; confira nomes de soluções no `CLAUDE.md` do projeto antes de usar em slide.

## Asset Registry

| deck | slide-id | slot | resolved-source | type |
|---|---|---|---|---|
| deck-template | 01-capa-fotografica | cover-photo | {online-base}Logos/logo_Brain_2001.png · local img/cover.jpg | url + local-path |
| deck-template | 06-branco-navy | data-art | {online-base}Pictograms_icons/heatmap1.png · local img/heatmap.jpg | url + local-path |
| deck-template | 09-divisor-fotografico | cover-photo | {online-base}Logos/logo_Brain_2004.png · local img/divider.jpg | url + local-path |
| deck-template | 10-midia-glass-cards | data-art | {online-base}brain-graph/brain-graph-ref4.png · local img/graph-cluster.jpg | url + local-path |
| deck-template | 13-ecossistema | partner-logo | site/minu-logo.png; site/core-logo.jpeg → img/core.png (fundo removido) — sem versão online | local-path |
| deck-template | 19-midia-texto | data-art | {online-base}brain-graph/brain-graph-ref2.png · local img/graph.jpg | url + local-path |
| deck-template | vários | icon-set / wordmark | {online-base}Pictograms_icons/*_pictogram.png e Logos/logo_brain_000*.png · locais em img/ | url + local-path |
