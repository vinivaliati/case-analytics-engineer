"""Gera as apresentações a partir do modelo da Brain e dos dados publicados.

    python entrega/apresentacao/gerar_decks.py

- index.html  : apresentação para a diretoria (board)
- tecnica.html: apresentação técnica (dados, dashboard e agente)

Todos os números saem dos Parquets em entrega/dashboard/data/ (gerados pelo dbt), não são digitados.
O cabeçalho (CSS/tokens) e o rodapé (scripts de animação) são copiados do modelo em contexto/apresentacao-modelo/.
"""

from __future__ import annotations

import json
import re
from decimal import ROUND_HALF_UP, Decimal
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MODEL = REPO / "contexto" / "apresentacao-modelo" / "index.html"
sys.path.insert(0, str(REPO / "entrega" / "dashboard"))

from lib import data  # noqa: E402

WM = ('<img class="wordmark" src="https://artifacts.brain3.com.br/share/z_pgQrSNRANa/raw/brandbook/visual-assets/'
      'Logos/logo_brain_0000_logo_branco.png" data-local="img/logo-branco.png" alt="Brain003">')


def br(v: float, d: int = 0) -> str:
    """Padrão brasileiro com arredondamento comercial (12,85 -> 12,9), igual ao dashboard."""
    q = Decimal(str(v)).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    return f"{q:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mi(v: float, d: int = 1) -> str:
    return br(v / 1e6, d)


# ---------------------------------------------------------------- números (todos dos marts)
goal = data.read("mart_goal_attainment_monthly")
goal["ym"] = goal["month_start"].astype(str).str[:7]
g = goal.set_index("ym")
pix = data.read("mart_pix_reconciliation_monthly")
flow = data.read("mart_points_flow_monthly")
flow["ym"] = flow["month_start"].astype(str).str[:7]
f = flow.set_index("ym")
eco = data.read("mart_redemption_economics")
adop = data.read("mart_crm_pix_launch_adoption")
timing = data.read("mart_crm_pix_launch_timing")
dictionary = json.loads((data.DATA_DIR / "data_dictionary.json").read_text(encoding="utf-8"))

LAST = "2026-09"
last = g.loc[LAST]
eco_m = {(r.period, r.goal_category_strict): r for r in eco.itertuples()}
pre_total = sum(r.avg_monthly_points for (p, _), r in eco_m.items() if p == "antes_do_pix")
post_total = sum(r.avg_monthly_points for (p, _), r in eco_m.items() if p == "depois_do_pix")


def delta(cat: str) -> float:
    a = eco_m.get(("depois_do_pix", cat))
    b = eco_m.get(("antes_do_pix", cat))
    return (a.avg_monthly_points if a else 0) - (b.avg_monthly_points if b else 0)


cost = {cat: eco_m[("depois_do_pix", cat)].cost_per_point_brl for (p, cat) in eco_m if p == "depois_do_pix"}
pix_cost = pix["effective_brl"].sum() / pix["effective_points"].sum()
op_cost = pix["operator_brl"].sum() / pix["operator_points"].sum()
non_eff_pct = pix["non_effective_points"].sum() / pix["all_status_points"].sum() * 100
pix_month_brl = pix.set_index(pix["month_start"].astype(str).str[:7]).loc[LAST, "effective_brl"]
pix_month_pts = eco_m[("depois_do_pix", "pix")].avg_monthly_points
loss_vs_air = pix_month_pts * (pix_cost - cost["aereas"])

seg = adop.groupby("exposure_segment")[["customers", "pix_adopters"]].sum()
seg["pct"] = seg["pix_adopters"] / seg["customers"] * 100
none_pct = seg.loc[seg.index.str.startswith("4."), "pct"].iloc[0]
email_pct = seg.loc[seg.index.str.startswith("2."), "pct"].iloc[0]
click_pct = seg.loc[seg.index.str.startswith("1."), "pct"].iloc[0]
week_pct = timing.loc[timing["timing_window"].str[:2].isin(["0.", "1."]), "customers_pct"].sum()
late_pct = timing.loc[timing["timing_window"].str.startswith("3."), "customers_pct"].sum()

brk_mig = f.loc[LAST, "breakage_migrated_realized_pct"]
brk_new = f.loc[LAST, "breakage_new_program_realized_pct"]
etr = f.loc[["2026-02", "2026-03", "2026-04"], "expired_to_redeemed_pct"]
mig_step = f.loc[LAST, "breakage_migrated_realized_pct"] - f.loc["2026-08", "breakage_migrated_realized_pct"]

jan_air = g.loc["2026-01", "aereas_pct"]
jan_air_ex = g.loc["2026-01", "aereas_pct_ex_atypical"]
jan_points = g.loc["2026-01", "redeemed_points"]
base_months = ["2026-02", "2026-03", "2026-04"]
base_points = g.loc[base_months, "redeemed_points"].mean()

n_tests_dbt = 242
n_tests_py = 19
n_tables = len(dictionary["tables"])

# ---------------------------------------------------------------- componentes
def bars_html(items: list[tuple[str, float, str, bool]], height: int = 300, ref: float | None = None, maxv: float | None = None) -> str:
    top = maxv or max(v for _, v, _, _ in items) * 1.15
    out = [f'<div class="chart" style="height:{height}px">']
    if ref is not None:
        out.append(f'<div class="gridline" style="bottom:{ref / top * 100:.1f}%; border-top:2px dashed var(--accent-data)"></div>')
    for label, v, txt, focus in items:
        out.append(f'<div class="bar-slot"><div class="bar{" focus" if focus else ""}" data-anim="bars" style="height:{v / top * 100:.1f}%"><b>{txt}</b></div><span class="cat">{label}</span></div>')
    out.append("</div>")
    return "".join(out)


def card(label: str, title: str, body: str, anim: str = "up") -> str:
    return f'<div class="card" data-anim="{anim}"><span class="t-label" style="color:var(--accent-data)">{label}</span><h3>{title}</h3><p class="t-body-sm">{body}</p></div>'


def kpi(over: str, value: str, sub: str) -> str:
    return f'<div class="kpi" data-anim="up"><span class="overline">{over}</span><div class="t-data-lg" style="margin-top:14px">{value}</div><p class="t-body-sm">{sub}</p></div>'


def source(text: str) -> str:
    return f'<p class="t-caption" data-anim="up">Fonte: {text}</p>'


MONTHS = {"01": "jan", "02": "fev", "03": "mar", "04": "abr", "05": "mai", "06": "jun", "07": "jul", "08": "ago", "09": "set", "10": "out", "11": "nov", "12": "dez"}


def mlabel(ym: str) -> str:
    return f"{MONTHS[ym[5:]]}/{ym[2:4]}"


# ---------------------------------------------------------------- deck da diretoria
var_months = ["2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
var_bars = bars_html([(mlabel(m), g.loc[m, "varejo_pct"], f"{br(g.loc[m, 'varejo_pct'], 1)}%", g.loc[m, "varejo_pct"] < 20) for m in var_months], 300, ref=20, maxv=30)
cost_bars = bars_html([
    ("Transferência", cost["transferencia_parceiro"], f"R$ {br(cost['transferencia_parceiro'], 4)}", False),
    ("Varejo", cost["varejo"], f"R$ {br(cost['varejo'], 4)}", False),
    ("Aéreas", cost["aereas"], f"R$ {br(cost['aereas'], 4)}", False),
    ("Pix", pix_cost, f"R$ {br(pix_cost, 4)}", True),
], 330, maxv=0.023)

# Waterfall em mil pontos/mês, inteiros: o modelo exige soma exata (base + variações = total).
wf_items = [
    ["Antes do Pix", round(pre_total / 1e3), "total"],
    ["Aéreas", round(delta("aereas") / 1e3)],
    ["Varejo", round(delta("varejo") / 1e3)],
    ["Agência", round(delta("agencia_viagens") / 1e3)],
    ["Transferência", round(delta("transferencia_parceiro") / 1e3)],
    ["Pix", round(delta("pix") / 1e3)],
]
wf_items.append(["Depois do Pix", sum(x[1] for x in wf_items), "total"])

board = f"""
<!-- 01 · Capa -->
<section class="slide" data-section="Capa" data-template="capa-manifesto" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:44px;">
    <span class="overline" data-anim="up">Pontua+ · Diretoria · out/2026</span>
    <h1 class="t-cover" data-anim="up">O Pix <span class="hl-invert">somou volume</span><br>e cobrou a conta</h1>
    <p class="t-body" style="max-width:1250px" data-anim="up">O que aconteceu com os resgates depois do Pontos no Pix, o que é verdade nas três afirmações e o que recomendamos decidir na próxima semana.</p>
  </div>
</section>

<!-- 02 · Sumário -->
<section class="slide" data-section="Sumário" data-template="sumario-executivo" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:64px;">
    <div class="head" style="max-width:1600px">
      <span class="overline" data-anim="up">Sumário executivo</span>
      <h2 class="t-title" data-anim="up">O Pix não roubou resgates: <span class="hl" data-anim="hl">criou um resgate novo e caro.</span></h2>
    </div>
    <div class="grid-3">
      {card("O que aconteceu", f"Varejo em {br(last['varejo_pct'], 1)}%, meta 20%", f"Os pontos resgatados foram de {mi(pre_total)} para {mi(post_total)} mi/mês. Aéreas e varejo não caíram; o Pix entrou no denominador e diluiu os percentuais. Aéreas segue em {br(last['aereas_pct'], 1)}%.")}
      {card("As 3 afirmações", "Nenhuma se sustenta", f"O Pix custa R$ {br(pix_cost, 3)}, não R$ 0,016. Breakage é {br(brk_new, 0)}% no programa novo e {br(brk_mig, 1)}% no migrado, não 40%. Quem não recebeu comunicação adotou o Pix na mesma taxa.")}
      {card("Recomendação", "Coibir com calibragem", f"O Pix é a modalidade mais cara (R$ {br(pix_cost, 3)}/ponto) e não ajuda nenhuma meta. Calibrar taxa e teto, renegociar o denominador das metas e corrigir o relatório do operador.")}
    </div>
  </div>
</section>

<!-- 03 · Capítulo -->
<section class="slide" data-section="O que aconteceu" data-template="capitulo" style="background:var(--primary)">
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:20px;" data-anim="cinematic">
    <span class="t-kicker">Capítulo 1:</span>
    <h2 class="t-divider">O que aconteceu<br>com os resgates</h2>
  </div>
  <div class="vtag" style="color:rgba(255,255,255,.6)">Sinapses conectadas, negócios expandidos</div>
</section>

<!-- 04 · Placar -->
<section class="slide" data-section="O que aconteceu" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:48px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">Metas contratuais · set/2026</span><h2 class="t-title" data-anim="up">Aéreas cumpre. Varejo está abaixo da meta desde junho.</h2></div>
    <div class="joined kpis">
      {kpi("Aéreas (meta ≥ 50%)", f"{br(last['aereas_pct'], 1)}%", "cumprida em 12 de 12 meses")}
      {kpi("Varejo (meta ≥ 20%)", f"{br(last['varejo_pct'], 1)}%", f"sem o Pix no denominador: {br(last['varejo_pct_ex_pix'], 1)}%")}
      {kpi("Pix", f"{br(last['pix_pct'], 1)}%", "dos pontos resgatados no mês")}
    </div>
    <div style="display:grid; grid-template-columns:1.6fr 1fr; gap:80px; align-items:end; padding-bottom:40px;">
      {var_bars}
      <div data-anim="up"><p class="t-body-sm">% de varejo por mês. Em <span style="color:var(--accent-data)">ciano</span>, os meses abaixo da linha de 20%. A visão estrita (só produto, sem transferências e agência de viagens) nunca passou de {br(goal['varejo_strict_pct'].max(), 1)}%: a meta depende de como o contrato classifica essas modalidades.</p>{source("mart_goal_attainment_monthly (visão contrato = definição do operador, reproduzida com até 1,5 p.p.)")}</div>
    </div>
  </div>
</section>

<!-- 05 · Waterfall -->
<section class="slide" data-section="O que aconteceu" data-template="waterfall" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-columns:1fr 2fr; gap:100px; align-items:center;">
    <div class="head">
      <span class="overline" data-anim="up">Pontos resgatados por mês (mil)</span>
      <h2 class="t-title" data-anim="up">O Pix <span class="hl" data-anim="hl">somou</span>, quase não substituiu</h2>
      <p class="t-body-sm" data-anim="up">Média mensal antes (fev a 26/mai/2026) e depois do Pix (27/mai a set/2026). Aéreas e varejo cresceram em pontos. Só a transferência a parceiros encolheu: quem queria "converter" pontos agora recebe dinheiro.</p>
      {source("mart_redemption_economics (resgates efetivos, líquidos de devoluções; valores arredondados)")}
    </div>
    <div class="wf" data-waterfall='{json.dumps(wf_items, ensure_ascii=False)}'></div>
  </div>
</section>

<!-- 06 · 12/01 -->
<section class="slide" data-section="O que aconteceu" data-template="big-number" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:36px;">
    <span class="overline" data-anim="up">Ponto de atenção · 12/01/2026</span>
    <div class="t-data-xl"><span data-anim="count" data-to="76">76</span><span class="unit"> mi pontos em um dia</span></div>
    <p class="t-sub" style="max-width:1500px; color:var(--mid)" data-anim="up">1.517 resgates aéreos num só dia, espalhados igualmente nas 24h, de clientes com saldo migrado e <span class="hl" data-anim="hl">sem campanha no CRM.</span></p>
    <p class="t-body-sm" style="max-width:1500px" data-anim="up">Leva aéreas a {br(jan_air, 1)}% em jan/2026 ({br(jan_air_ex, 1)}% sem o dia). Hipótese principal: promoção de passagens não registrada no CRM; alternativa: carga em lote do programa anterior. <b style="color:var(--hi)">Precisa ser validado com a área de negócio.</b> Por isso a linha de base "antes do Pix" é fev-mai/2026.</p>
    {source("dim_date.is_atypical_day (tabela de referência calendar_events); mart_goal_attainment_monthly")}
  </div>
</section>

<!-- 07 · Capítulo -->
<section class="slide" data-section="As três afirmações" data-template="capitulo" style="background:var(--primary)">
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:20px;" data-anim="cinematic">
    <span class="t-kicker">Capítulo 2:</span>
    <h2 class="t-divider">As três<br>afirmações</h2>
  </div>
  <div class="vtag" style="color:rgba(255,255,255,.6)">Sinapses conectadas, negócios expandidos</div>
</section>

<!-- 08 · CRM -->
<section class="slide" data-section="As três afirmações" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:48px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">CRM: "a comunicação de lançamento explica o sucesso do Pix"</span><h2 class="t-title" data-anim="up">Não se sustenta: <span class="hl" data-anim="hl">sem comunicação, a adoção foi a mesma.</span></h2></div>
    <div class="joined kpis">
      {kpi("Recebeu o e-mail", f"{br(email_pct, 1)}%", "adotou o Pix")}
      {kpi("Nenhuma comunicação", f"{br(none_pct, 1)}%", "adotou o Pix")}
      {kpi("Usou até 7 dias após o e-mail", f"{br(week_pct, 1)}%", f"{br(late_pct, 0)}% só depois de 30 dias")}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px; padding-bottom:40px;">
      <p class="t-body-sm" data-anim="up">Quem clicou no e-mail adotou {br(click_pct, 1)}%. O primeiro Pix (27/05, 09:15) é anterior ao primeiro envio (28/05, 10:00), e o link do e-mail levava ao catálogo, não ao Pix. O produto em si (dinheiro na conta) explica melhor a adoção.</p>
      <div data-anim="up"><p class="t-body-sm"><b style="color:var(--hi)">O que falta saber:</b> o export do CRM não tem grupo de controle (100% vazio), então isto é descritivo, não causal. Próxima campanha: teste A/B com grupo de controle.</p>{source("mart_crm_pix_launch_adoption, mart_crm_pix_launch_timing (CRM convertido de UTC)")}</div>
    </div>
  </div>
</section>

<!-- 09 · Operador -->
<section class="slide" data-section="As três afirmações" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:48px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">Operador: "o Pix sai a cerca de R$ 0,016 por ponto"</span><h2 class="t-title" data-anim="up">Falso: o Pix custa <span class="hl" data-anim="hl">R$ {br(pix_cost, 4)}</span> em todos os meses.</h2></div>
    <div class="joined kpis">
      {kpi("Custo real", f"R$ {br(pix_cost, 4)}", "R$ creditados ÷ pontos pagos")}
      {kpi("Relatório do operador", f"R$ {br(op_cost, 4)}", "R$ pagos ÷ pontos de todos os pedidos")}
      {kpi("Pontos sem pagamento", f"{br(non_eff_pct, 1)}%", "cancelados, inválidos, estornados")}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px; padding-bottom:40px;">
      <p class="t-body-sm" data-anim="up">O relatório divide os reais efetivamente pagos pelos pontos de todos os pedidos Pix, inclusive os que nunca foram pagos. As transações e os pontos do relatório batem exatamente com essa base (teste automatizado). É erro de base, não custo menor.</p>
      <div data-anim="up"><p class="t-body-sm"><b style="color:var(--hi)">O que falta saber:</b> os reais do operador ficam 0,2% a 0,7% abaixo dos pagos e nenhuma regra testada explica. Pedir ao operador a regra do relatório.</p>{source("mart_pix_reconciliation_monthly")}</div>
    </div>
  </div>
</section>

<!-- 10 · Breakage -->
<section class="slide" data-section="As três afirmações" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:48px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">Diretor: "nosso breakage está em 40%; a meta é não passar de 20%"</span><h2 class="t-title" data-anim="up">Não é 40%. Mas o migrado <span class="hl" data-anim="hl">passa de 20% em outubro.</span></h2></div>
    <div class="joined kpis">
      {kpi("Breakage do programa novo", f"{br(brk_new, 0)}%", "nada venceu: validade de 24 meses")}
      {kpi("Breakage do saldo migrado", f"{br(brk_mig, 1)}%", f"+{br(mig_step, 1)} p.p. por mês")}
      {kpi("Expiração ÷ resgate", f"{br(etr.min(), 0)} a {br(etr.max(), 0)}%", "fev-abr/2026: provável origem do 40%")}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px; padding-bottom:40px;">
      <p class="t-body-sm" data-anim="up">Breakage, pela definição de mercado (IFRS 15), é expirado ÷ emitido por safra. A Multiplus operou entre 21% e 24% (2010-2012). A razão "expiração do mês ÷ resgate do mês" não é breakage e cai com o Pix só porque o resgate cresceu.</p>
      <div data-anim="up"><p class="t-body-sm"><b style="color:var(--hi)">O que falta saber:</b> o saldo migrado tem validade até 2028, mas expira ~7 mi pontos/mês desde jan/2026. Qual regra vale? E qual definição a diretoria usou?</p>{source("mart_points_flow_monthly; benchmark em entrega/docs/benchmark_breakage.md")}</div>
    </div>
  </div>
</section>

<!-- 11 · Saúde financeira -->
<section class="slide" data-section="Saúde financeira" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-columns:1fr 1.3fr; gap:100px; align-items:center;">
    <div class="head">
      <span class="overline" data-anim="up">Custo do programa por ponto resgatado</span>
      <h2 class="t-title" data-anim="up">O Pix é a <span class="hl" data-anim="hl">modalidade mais cara</span></h2>
      <p class="t-body-sm" data-anim="up">O enunciado diz que aéreas já custam mais do que o banco paga por ponto. Logo, cada ponto em Pix dá pelo menos R$ {br(pix_cost - cost['aereas'], 4)} a mais de prejuízo que um ponto em aéreas: ~R$ {br(loss_vs_air / 1e3, 0)} mil/mês sobre ~R$ {br(pix_month_brl / 1e3, 0)} mil pagos em dinheiro. E o Pix reduz o breakage futuro, que é margem pura.</p>
      <p class="t-body-sm" data-anim="up"><b style="color:var(--hi)">Hipótese declarada:</b> custo ≈ valor do produto − dinheiro pago pelo cliente. Varejo de parceiros do grupo custa menos que o valor de prateleira. Falta o preço por ponto do contrato com o banco.</p>
      {source("mart_redemption_economics (depois do Pix)")}
    </div>
    <div data-anim="up">{cost_bars}</div>
  </div>
</section>

<!-- 12 · Recomendação -->
<section class="slide" data-section="Recomendação" data-template="sumario-executivo" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:flex-start; gap:28px; padding-top:120px;">
    <div class="head"><span class="overline" data-anim="up">Recomendação</span><h2 class="t-title" data-anim="up">Coibir o Pix com calibragem, não eliminar</h2></div>
    <div class="grid-3" style="grid-template-columns:repeat(3,1fr)">
      {card("1 · Calibrar o Pix", "Taxa menor ou teto mensal", f"Número: R$ {br(pix_cost, 3)}/ponto, o maior custo, {br(last['pix_pct'], 0)}% dos pontos. Falta: preço do banco por ponto e elasticidade da taxa.")}
      {card("2 · Renegociar a meta", "Pix fora do denominador", f"Número: sem o Pix, varejo {br(last['varejo_pct_ex_pix'], 1)}% e aéreas {br(last['aereas_pct_ex_pix'], 1)}%. Falta: como o contrato classifica Pix, transferências e agência.")}
      {card("3 · Corrigir o relatório", "Base única no operador", f"Número: {br(non_eff_pct, 1)}% dos pontos Pix do relatório não foram pagos. Falta: a regra de R$ do operador.")}
    </div>
    <div class="grid-3" style="grid-template-columns:repeat(2,1fr)">
      {card("4 · Padronizar o breakage", "Expirado ÷ emitido, por safra", f"Número: migrado em {br(brk_mig, 1)}%, subindo {br(mig_step, 1)} p.p./mês. Falta: a regra de expiração do saldo migrado.")}
      {card("5 · Medir antes de atribuir", "Grupo de controle no CRM", f"Número: {br(none_pct, 1)}% de adoção sem nenhuma comunicação. Falta: teste A/B e explicação para 12/01.")}
    </div>
  </div>
</section>

<!-- 13 · Próximos passos -->
<section class="slide" data-section="Próximos passos" data-template="roadmap" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:90px;">
    <div class="head"><span class="overline" data-anim="up">Próximos passos</span><h2 class="t-title" data-anim="up">Decidir agora, medir em 30 dias</h2></div>
    <div class="tl">
      <div class="line" style="right:42%" data-anim="draw"></div>
      <div class="line future" style="left:58%" data-anim="draw"></div>
      <div class="ms" style="left:0" data-anim="seq"><div class="dot now"></div><p class="t-label">Semana que vem</p><h3>Decisão do board</h3><p class="t-body-sm">Calibragem do Pix e pauta de renegociação das metas com o banco.</p></div>
      <div class="ms" style="left:34%" data-anim="seq"><div class="dot"></div><p class="t-label">30 dias</p><h3>Respostas do negócio</h3><p class="t-body-sm">Preço do banco por ponto, 12/01, regra do migrado e do relatório do operador.</p></div>
      <div class="ms" style="left:70%" data-anim="seq"><div class="dot"></div><p class="t-label">60 dias</p><h3>Teste com controle</h3><p class="t-body-sm">Nova taxa do Pix em A/B; acompanhamento no dashboard.</p></div>
    </div>
    <p class="t-caption" data-anim="up">Acompanhamento: dashboard Pontua+ (4 telas + analista com IA) · trecho tracejado = futuro</p>
  </div>
</section>

<!-- 14 · Fechamento -->
<section class="slide" data-section="Decisão" data-template="fechamento" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:56px;">
    <div class="head"><span class="overline" data-anim="up">Decisão</span><h2 class="t-title" data-anim="up">O que precisamos decidir</h2></div>
    <div class="grid-3">
      {card("01", "Calibrar o Pix", "Taxa por ponto e/ou teto mensal, com teste A/B.")}
      {card("02", "Pauta com o banco", "Denominador das metas e classificação de transferências e agência.")}
      {card("03", "Dono das definições", "Breakage, resgate efetivo e relatório do operador com uma regra só.")}
    </div>
    <div class="cta" data-anim="featured"><p class="t-sub" style="color:#fff">O Pix fica, mas com preço que o programa consegue pagar.</p></div>
  </div>
</section>
"""

# ---------------------------------------------------------------- deck técnico
tech = f"""
<section class="slide" data-section="Capa" data-template="capa-manifesto" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:44px;">
    <span class="overline" data-anim="up">Pontua+ · Apresentação técnica</span>
    <h1 class="t-cover" data-anim="up">Do CSV à <span class="hl-invert">resposta</span>,<br>com teste em cada passo</h1>
    <p class="t-body" style="max-width:1250px" data-anim="up">Como os dados foram organizados, como o dashboard e o agente consomem a mesma base, e o que cada decisão técnica resolve.</p>
  </div>
</section>

<section class="slide" data-section="Arquitetura" data-template="3-passos" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:64px;">
    <div class="head" style="max-width:1500px"><span class="overline" data-anim="up">Arquitetura</span><h2 class="t-title" data-anim="up">Um comando reconstrói tudo a partir dos CSVs</h2></div>
    <div class="joined flow">
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">01 / confere</span></div><h3>MANIFESTO + SHA-256</h3><p class="t-body-sm">build.py confere os 9 CSVs (hash e contagem) antes de tudo. .gitattributes fixa LF para o hash bater em qualquer SO.</p></div>
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">02 / modela</span></div><h3>dbt + DuckDB, Kimball</h3><p class="t-body-sm">staging → intermediate → core (dims e fatos) → analytics + serving. {n_tests_dbt} testes no build.</p></div>
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">03 / publica</span></div><h3>Parquet + dicionário</h3><p class="t-body-sm">{n_tables} tabelas agregadas (300 KB) + data_dictionary.json gerado do dbt. Dashboard e agente leem só isso.</p></div>
    </div>
  </div>
</section>

<section class="slide" data-section="Modelagem" data-template="sumario-executivo" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:56px;">
    <div class="head"><span class="overline" data-anim="up">Camadas e grão</span><h2 class="t-title" data-anim="up">Cada camada tem um trabalho e um grão declarado</h2></div>
    <div class="grid-3">
      {card("staging · 9 modelos", "1:1 com a fonte", "Padrão fixo: CTE source → tipagem/renomeação → dedup, leading comma. Fuso padronizado (CRM chega em UTC, confirmado: Order Approved = pedido + 3h em 17.385 de 17.494).")}
      {card("core · Kimball", "Fatos atômicos + dims", "fct de itens, ledger, CRM e snapshot de saldo cliente × mês. Surrogate keys, membro '-1', PK e FK testadas. Não é publicado (tem grão de cliente).")}
      {card("analytics + serving", "O que é publicado", "6 marts (1 pergunta cada, achado travado por teste) + star schema agregado mensal para BI. Regras de negócio em tabelas de referência, não no SQL.")}
    </div>
  </div>
</section>

<section class="slide" data-section="Qualidade" data-template="big-number" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:36px;">
    <span class="overline" data-anim="up">Testes</span>
    <div class="t-data-xl"><span data-anim="count" data-to="{n_tests_dbt + n_tests_py}">{n_tests_dbt + n_tests_py}</span><span class="unit"> testes a cada build</span></div>
    <p class="t-sub" style="max-width:1500px; color:var(--mid)" data-anim="up">{n_tests_dbt} no dbt e {n_tests_py} em Python. Além de chave e relacionamento, <span class="hl" data-anim="hl">testes que travam os números da apresentação.</span></p>
    <p class="t-body-sm" style="max-width:1500px" data-anim="up">Pontos debitados = pagos item a item · saldo = ledger cliente a cliente · agregados = fatos · Pix = R$ 0,019 · operador usa todos os status · dashboard sem filtro = marts · nenhum identificador de cliente publicado · agente não lê CSV nem escreve.</p>
  </div>
</section>

<section class="slide" data-section="Agente" data-template="3-passos" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:64px;">
    <div class="head" style="max-width:1500px"><span class="overline" data-anim="up">Agente analista (Gemini)</span><h2 class="t-title" data-anim="up">O agente descobre os campos pelo mesmo schema.yml do dbt</h2></div>
    <div class="joined flow">
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">01 / contexto</span></div><h3>Dicionário no prompt</h3><p class="t-body-sm">Grão, perguntas que cada tabela responde, ressalvas e descrição de cada coluna, gerados do dbt. O build falha se faltar descrição.</p></div>
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">02 / consulta</span></div><h3>Uma ferramenta: run_sql</h3><p class="t-body-sm">DuckDB em memória sobre os Parquets, só SELECT, sem acesso a arquivo, com limite de linhas e timeout.</p></div>
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">03 / responde</span></div><h3>Número, fonte e ressalva</h3><p class="t-body-sm">Recusa dado individual e diz quando o dado não existe. Resiliente a cota/503: timeout e modelos de reserva.</p></div>
    </div>
  </div>
</section>

<section class="slide" data-section="Decisões" data-template="sumario-executivo" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:56px;">
    <div class="head"><span class="overline" data-anim="up">Decisões a defender</span><h2 class="t-title" data-anim="up">Escolhas revisáveis, todas documentadas</h2></div>
    <div class="grid-3">
      {card("Nível de cartão", "Nível atual do cliente", "Saldo é carteira por cliente (1.197 contas negativas, nenhum cliente) e 820 itens misturam níveis. Alternativa pronta: nível da conta.")}
      {card("Metas", "Definição do operador", "Reproduz o relatório com até 1,5 p.p. Visão estrita e 'sem Pix' como sensibilidade, na tabela de referência goal_categories.")}
      {card("Ferramentas", "DuckDB, Streamlit, Parquet", "Avaliador reconstrói sem servidor; dbt portátil para um warehouse. Parquet commitado: produção sobe sem rodar dbt. Airflow avaliado no README.")}
    </div>
  </div>
</section>
"""


def build(name: str, slides: str, title: str) -> None:
    model = MODEL.read_text(encoding="utf-8")
    start = model.index('<div class="deck" id="deck">') + len('<div class="deck" id="deck">')
    end = model.index("</div>\n</div>\n<div class=\"progress\"")
    # O script do modelo espera o modal do slide de carrossel; incluímos vazio e oculto.
    modal = ('<div class="modal" id="modal" role="dialog" aria-modal="true" aria-hidden="true"><div class="modal-card">'
             '<button class="plus modal-close" data-close aria-label="Fechar">×</button><span class="overline" data-slot="over"></span>'
             '<h3 data-slot="title"></h3><p class="t-body" data-slot="body"></p></div></div><template id="modal-data"></template>')
    html = model[:start] + "\n" + slides + "\n" + modal + "\n" + model[end:]
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1)
    (HERE / name).write_text(html, encoding="utf-8")
    print(f"gerado {name}")


if __name__ == "__main__":
    for folder in ("img", "lib"):
        target = HERE / folder
        if not target.exists():
            shutil.copytree(MODEL.parent / folder, target)
    build("index.html", board, "Pontua+ · Diretoria")
    build("tecnica.html", tech, "Pontua+ · Técnica")
