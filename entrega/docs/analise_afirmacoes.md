# Análise: o que aconteceu e as três afirmações

Todos os números saem dos marts em `entrega/dbt/models/marts/analytics/` (dbt build, 202 testes). Base: resgates efetivos (APROVADO, líquido de devoluções). "Antes do Pix" = 01/02 a 26/05/2026; "depois" = 27/05 a 30/09/2026.

## 1. O que aconteceu com os resgates depois do Pix

| | Antes (fev-mai) | Depois (jun-set) | Fonte |
|---|---|---|---|
| Pontos resgatados por mês | 15,8 a 21,5 mi | 30,3 a 33,4 mi | `mart_goal_attainment_monthly` |
| Aéreas (pontos/mês) | 15,0 mi | 17,9 mi | `mart_redemption_economics` |
| Varejo só produto (pontos/mês) | 2,3 mi | 2,5 mi | idem |
| Agência de viagens (pontos/mês) | 0,7 mi | 1,1 mi | idem |
| Transferência a parceiros (pontos/mês) | 0,9 mi | 0,3 mi | idem |
| Pix (pontos/mês) | — | 9,1 mi | idem |
| % aéreas (meta ≥ 50%) | 75 a 81% | 56 a 59% | `mart_goal_attainment_monthly` |
| % varejo (meta ≥ 20%) | 19 a 21% | 12 a 13% | idem |

**Confirmado nos dados:**
- **O Pix somou volume, quase não substituiu.** Os resgates em aéreas e varejo **cresceram** em pontos absolutos. O total por mês passou de cerca de 19 mi para cerca de 31 mi.
- **A única modalidade que encolheu foi a transferência a parceiros**, de 0,9 para 0,3 mi/mês. Faz sentido: o cliente que queria "converter" pontos agora recebe dinheiro.
- **As metas caíram porque são percentuais**, e o Pix entra no denominador. Se o Pix ficasse fora do denominador, aéreas estariam em 81 a 83% e varejo em 17 a 19% (`aereas_pct_ex_pix`, `varejo_pct_ex_pix`).
- **Aéreas segue acima de 50% em todos os meses. Varejo está abaixo de 20% desde jun/2026**, e também já tinha ficado abaixo em abr/2026 (19,2%) e em jan/2026.
- **Na visão estrita** (varejo só com produto), o varejo nunca passou de 14,2% (máximo em nov/2025). A meta depende de como o contrato classifica transferências e agência de viagens.

**Janeiro/2026 (ponto importante para a apresentação):** em 12/01 houve 1.517 resgates aéreos e 75,9 mi pontos num único dia. Isso leva aéreas a 96,8% e varejo a 3,2% no mês. Sem esse dia, aéreas fica em 77,5%. O padrão (24h uniformes, clientes com saldo migrado, sem campanha de CRM) sugere uma promoção não registrada no CRM ou uma carga em lote. **A causa deve ser validada com a área de negócio.**

## 2. As três afirmações

### "A comunicação de lançamento explica o sucesso do Pix" (CRM): **não se sustenta nos dados**

Fonte: `mart_crm_pix_launch_adoption`. Adoção = cliente com ao menos um Pix efetivo até set/2026.

| Exposição na janela do lançamento (27/05 a 04/06) | Adoção, sem resgate anterior | Adoção, com resgate anterior |
|---|---|---|
| Recebeu o e-mail de lançamento e clicou | 10,8% (176 clientes) | 26,3% (76) |
| Recebeu, não clicou | 14,9% (6.108) | 24,2% (2.924) |
| Não recebeu o e-mail, recebeu outra campanha | 13,5% (1.160) | 26,5% (536) |
| **Nenhuma comunicação** | **15,9% (681)** | **22,7% (339)** |

- Quem **não recebeu nenhuma comunicação** adotou o Pix na mesma taxa de quem recebeu.
- Quem clicou no e-mail, entre os que nunca tinham resgatado, adotou **menos**.
- O primeiro Pix (27/05 às 09:15) é anterior ao primeiro envio da campanha (28/05 às 10:00).
- Dos 1.656 clientes que receberam o e-mail e usaram o Pix, só 6,0% usaram nos 7 dias seguintes. 71,3% usaram mais de 30 dias depois (`mart_crm_pix_launch_timing`).
- O link do e-mail de lançamento levava ao "catálogo", não ao Pix.
- **Ressalva:** `control_group` está 100% vazio, então isso é **descritivo, não causal**. Os grupos não foram sorteados. Mesmo assim, não há diferença de adoção nem relação de dose. O que explica a adoção parece ser o produto em si (dinheiro na conta), não a comunicação.
- **Para avançar:** um teste A/B com grupo de controle na próxima campanha, e o log de impressões in-app/app (o export não diz onde o cliente viu o Pix).

### "Na verdade o Pix sai a ~R$ 0,016 por ponto" (operador): **falsa; o custo é R$ 0,0190**

Fonte: `mart_pix_reconciliation_monthly` (testes travam os dois achados).

- Nos resgates efetivos, o Pix custa **exatamente R$ 0,0190 por ponto em todos os meses**, como anunciado.
- O relatório do operador divide os **R$ pagos** pelos **pontos de todos os pedidos Pix, de todos os status**. As transações e os pontos do relatório batem exatamente com todos os itens, inclusive os cancelados, inválidos, estornados e aguardando. Esses pedidos (13% a 19% dos pontos do mês) nunca foram pagos.
- Daí sai o 0,0154 a 0,0166 do relatório. É um erro de numerador e denominador em bases diferentes, não um custo menor.
- Ponto em aberto: o R$ do operador fica 0,2% a 0,7% abaixo do R$ dos resgates efetivos, e nenhuma regra testada explica (mês de atualização do status, aprovados sem devolução, conta única). **Pergunta ao operador.**
- Efeito colateral: o `pix_pct` do operador também usa pontos de todos os status. Em jun/2026 isso explica parte da diferença em aéreas (operador 55%, nós 56,4%).

### "Nosso breakage está em 40%; a meta é não passar de 20%" (diretor): **não é breakage; o número correto é 0% no programa novo e 19,8% no saldo migrado**

Fonte: `mart_points_flow_monthly`; definição e benchmark em `benchmark_breakage.md`.

- Pela definição de mercado (expirados ÷ emitidos, por safra), alinhada ao IFRS 15 e usada pela Multiplus (21% a 24% em 2010-2012):
  - **Programa novo: 0% realizado.** Os créditos valem 24 meses e o primeiro vence em 25/09/2027. Ainda não pode ser medido, só projetado.
  - **Saldo migrado: 19,8% realizado em set/2026** (64,1 de 324,0 mi). Sobe cerca de 2,2 p.p. por mês e **deve passar de 20% já em out/2026** (projeção: supõe que o ritmo de ~7 mi/mês continua).
- **Origem provável do "40%":** expiração do mês ÷ resgate do mês = 43,8% em fev, 37,7% em mar e 36,2% em abr/2026. Essa razão não é breakage, porque compara expiração com resgate e não com emissão.
  - Com o Pix aumentando os resgates, essa mesma razão caiu para 20,7%. Ou seja, quem acompanha esse número vai achar que o Pix "melhorou o breakage". Isso é falso.
- Contradição a levar ao negócio: o saldo migrado tem `valid_until` em 31/03/2028, mas expira desde jan/2026.

## 3. Saúde financeira (com hipótese declarada)

Fonte: `mart_redemption_economics`. Hipótese: custo ≈ (valor do produto − dinheiro pago pelo cliente) ÷ pontos.

| Modalidade | Custo por ponto | Observação |
|---|---|---|
| Transferência a parceiro | R$ 0,0125 | |
| Varejo / agência | R$ 0,0140 | valor de prateleira; o custo real é menor nos parceiros do grupo |
| Aéreas | R$ 0,0150 | o enunciado diz que já custa mais do que o banco paga |
| **Pix** | **R$ 0,0190** | **dinheiro, sem margem de parceiro** |

- O preço que o banco paga por ponto não está nos dados. Pelo enunciado, é **menor que R$ 0,015** (o custo de aéreas). Logo, **cada ponto em Pix dá prejuízo maior que um ponto em aéreas**: pelo menos R$ 0,004 a mais por ponto.
- Com ~9,1 mi pontos/mês em Pix, o desembolso em dinheiro é de **~R$ 173 mil/mês**.
  - Se o banco pagasse R$ 0,015 por ponto, o prejuízo seria de **≥ R$ 36 mil/mês só na diferença**.
  - Quanto menor o preço do banco, maior o prejuízo.
- O Pix também tende a **reduzir o breakage futuro**, porque são pontos que poderiam expirar e viram dinheiro. Breakage é margem pura.
- **Para avançar:** o preço por ponto do contrato com o banco, o custo real dos parceiros de varejo e o momento em que o banco paga o ponto (na emissão ou no resgate).
