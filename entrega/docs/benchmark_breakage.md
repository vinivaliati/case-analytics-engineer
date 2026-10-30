# Breakage: definição de mercado e benchmark

## O que é breakage

Breakage é a parcela dos pontos **emitidos** que **nunca será resgatada**, porque expira ou é abandonada. Para um programa de pontos, é margem pura: o ponto foi vendido ao parceiro (aqui, ao banco) e nunca gera custo de resgate.

- A Multiplus (programa de fidelidade da LATAM, listada na B3 até 2019) definia como "pontos emitidos e não resgatados que, por isso, não geram custos" e tratava breakage como uma das quatro fontes de lucro do modelo (spread, float, breakage e serviços). [Relatório Anual 2012, p. 8]
- Em reportagem sobre o 1T18, a taxa é descrita como "quanto dos pontos acumulados venceram sem terem sido resgatados pelos clientes". [Forbes Brasil, 2018]
- Na contabilidade, o IFRS 15 (no Brasil, CPC 47) trata breakage como direitos não exercidos pelo cliente. Se a empresa espera ter direito ao breakage, reconhece a receita na proporção do padrão de resgate. Se não espera, reconhece quando a chance de resgate fica remota. A estimativa segue as regras de contraprestação variável e depende de histórico. [IFRS 15, B44 a B47]

**Consequência para o case:** breakage é uma razão **sobre pontos emitidos**, observada por **safra (coorte) de emissão** depois que a validade termina. Antes disso, só existe como estimativa.

## Case real: Multiplus Fidelidade

| Período | Taxa de breakage | Fonte |
|---|---|---|
| 2010 | 22,6% (média do ano) | Relatório Anual 2012, p. 2 |
| 2011 | 24,1% (média do ano) | Relatório Anual 2012, p. 2 |
| 2012 | 21,0% (média do ano) | Relatório Anual 2012, p. 2 |
| 1T18 | 17,6% (contra 16,8% no período comparável) | Forbes Brasil, mai/2018 |

Outros pontos do Relatório Anual 2012:
- A receita de breakage foi R$ 214 mi de R$ 1,63 bi de receita bruta em 2012 (13%), e R$ 319 mi em 2011.
- A empresa via a queda gradual da taxa como esperada e positiva: "indica maior engajamento dos participantes na rede" (p. 5).
- Breakage é gerido como risco comercial, dentro de uma faixa: "se muito alta, prejudica a atratividade da rede, se muito baixa, reduz a rentabilidade do negócio. A Multiplus tem uma área para monitoramento e manutenção da taxa de breakage no intervalo considerado ideal" (p. 15).

Referência secundária, não conferida na fonte primária: a United Airlines estimava em 2012 que cerca de 24% das milhas expirariam sem uso. [CustomerThink]

## O que isso significa para o Pontua+

1. **A meta de "não passar de 20%" está na faixa de mercado.** A Multiplus operou entre 17% e 24%. Também mostra que breakage não é só custo: abaixo da faixa, o programa perde margem.
2. **"40%" não é compatível com a definição de mercado nos dados do case:**
   - Programa novo: os créditos valem 24 meses e o primeiro vencimento é 25/09/2027. **Nenhuma safra venceu, então o breakage realizado é 0% e ainda não pode ser medido.** Só dá para projetar.
   - Saldo migrado: 64,1 mi de 324,0 mi pontos expiraram até set/2026, ou **19,8% realizado**. A safra continua expirando (~7 mi/mês).
   - Hipótese para o 40%, a validar com a diretoria: dividir a expiração do mês pelo resgate do mês dá 33% a 44% entre fev e mai/2026. Essa razão não é breakage, porque compara expiração com resgate e não com emissão. Os números entram na etapa 3.
3. **O Pix muda o breakage futuro.** Pela lógica da Multiplus, uma opção de resgate fácil (dinheiro na conta) aumenta o engajamento e reduz o breakage, ou seja, reduz uma fonte de margem. Isso entra na avaliação financeira de estimular ou coibir o Pix.

## Definição adotada no projeto

- **Breakage realizado por safra** = pontos expirados ÷ pontos emitidos, por origem (programa novo × migrado), para safras com validade vencida.
- **Taxa de expiração do período** = pontos expirados no período ÷ saldo em aberto no início do período (indicador de acompanhamento, não é breakage).
- **Breakage projetado** (programa novo): fica como estimativa declarada, com a premissa explícita, porque ainda não há safra vencida.

## Fontes

- Multiplus S.A., Relatório Anual 2012: https://www.mediagroup.com.br/host/multiplus/2012/port/downloads/Multiplus_RA2012.pdf (texto conferido nas p. 2, 5, 8, 15 e 25)
- Forbes Brasil, "Multiplus: lucro cai, mas base de clientes aumenta" (mai/2018): https://forbes.com.br/negocios/2018/05/multiplus-lucro-cai-mas-base-de-clientes-aumenta/
- IFRS Community, "Revenue from Customers' Unexercised Rights, or 'Breakage' (IFRS 15)": https://ifrscommunity.com/knowledge-base/revenue-from-customers-unexercised-rights-breakage/ (a página bloqueou a leitura automática; conteúdo resumido pelo resultado de busca)
- Universidade Federal de Uberlândia, estudo sobre a contabilização de receitas de programas de fidelidade no Brasil (2018 a 2020): https://repositorio.ufu.br/handle/123456789/34438
- CustomerThink, "Loyalty Myths: Is Breakage Good" (fonte secundária): https://customerthink.com/loyalty-myths-is-breakage-good/
