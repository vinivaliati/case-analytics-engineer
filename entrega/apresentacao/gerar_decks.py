"""Gera as apresentações a partir do modelo da Brain e dos dados publicados.

    python entrega/apresentacao/gerar_decks.py

- index.html  : apresentação para a diretoria (board)
- tecnica.html: apresentação técnica (dados, dashboard e agente)

Todos os números saem dos Parquets em entrega/dashboard/data/ (gerados pelo dbt), não são digitados.
O cabeçalho (CSS/tokens) e o rodapé (scripts de animação) são copiados do modelo em contexto/apresentacao-modelo/.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
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


# ---------------------------------------------------------------- números extras (perfil, manifesto, testes)
prof = data.read("mart_data_profile").set_index("metric")["value"].to_dict()
with (REPO / "contexto" / "MANIFESTO_v1.csv").open(encoding="utf-8", newline="") as fh:
    manifest_rows = {r["arquivo"].removesuffix(".csv"): int(r["linhas"]) for r in csv.DictReader(fh)}
months_var_below = int((goal["varejo_pct"] < 20).sum())
months_total = len(goal)
months_air_ok = int((goal["aereas_pct"] >= 50).sum())
strict_max = goal["varejo_strict_pct"].max()
ex_pix_var = last["varejo_pct_ex_pix"]
ex_pix_air = last["aereas_pct_ex_pix"]
APP_URL = "https://vinivaliati-case-analytics-engineer-entregadashboardapp-qytb2d.streamlit.app/"


def count_dbt_tests() -> int:
    manifest_path = REPO / "entrega" / "dbt" / "target" / "manifest.json"
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    return sum(1 for n in m["nodes"].values() if n["resource_type"] == "test") + len(m.get("unit_tests", {}))


def count_py_tests() -> int:
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "agente/tests", "entrega/dashboard/tests"],
        cwd=REPO, capture_output=True, text=True,
    ).stdout
    found = re.search(r"(\d+) tests? collected", out)
    return int(found.group(1)) if found else 0


n_tests_dbt = count_dbt_tests()
n_tests_py = count_py_tests()
n_tables = len(dictionary["tables"])


def table_html(cols: str, headers: list[str], rows: list[list[str]], size: int = 19) -> str:
    """Tabela no estilo do modelo (blocos 'joined'): cabeçalho escuro, primeira coluna em destaque."""
    cells = "".join(
        f'<div style="background:var(--n800); padding:14px 20px; font-size:{size - 2}px; font-weight:700; '
        f'letter-spacing:.04em; text-transform:uppercase; color:var(--accent-data)">{h}</div>' for h in headers
    )
    for row in rows:
        for i, c in enumerate(row):
            color = "var(--hi)" if i == 0 else "var(--mid)"
            weight = "600" if i == 0 else "400"
            cells += (f'<div style="background:var(--n900); padding:12px 20px; font-size:{size}px; line-height:1.38; '
                      f'color:{color}; font-weight:{weight}">{c}</div>')
    return f'<div class="joined" style="grid-template-columns:{cols}" data-anim="up">{cells}</div>'


def chapter(n: int, title: str, section: str) -> str:
    return f"""
<section class="slide" data-section="{section}" data-template="capitulo" style="background:var(--primary)">
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:20px;" data-anim="cinematic">
    <span class="t-kicker">Capítulo {n}:</span>
    <h2 class="t-divider">{title}</h2>
  </div>
  <div class="vtag" style="color:rgba(255,255,255,.6)">Sinapses conectadas, negócios expandidos</div>
</section>"""


def meaning(text: str) -> str:
    return f'<p class="t-body-sm" data-anim="up" style="border-left:3px solid var(--accent-data); padding-left:18px"><b style="color:var(--hi)">O que significa:</b> {text}</p>'


# ---------------------------------------------------------------- deck da diretoria
var_months = ["2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
var_bars = bars_html([(mlabel(m), g.loc[m, "varejo_pct"], f"{br(g.loc[m, 'varejo_pct'], 1)}%", g.loc[m, "varejo_pct"] < 20) for m in var_months], 250, ref=20, maxv=30)
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

data_rows = [
    ["orders", "Pedidos", br(manifest_rows["orders"]), "um pedido de resgate"],
    ["order_items", "Pedidos", br(manifest_rows["order_items"]), "um item: fornecedor, categoria, pontos e R$"],
    ["carts", "Pedidos", br(manifest_rows["carts"]), "carrinho: cliente e canal (APP/WEB)"],
    ["redeemed_points", "Pedidos", br(manifest_rows["redeemed_points"]), "pontos que saíram de cada conta por item"],
    ["points_ledger", "Pontos", br(manifest_rows["points_ledger"]), "extrato: créditos, resgates, estornos, expirações"],
    ["dim_operation", "Pontos", br(manifest_rows["dim_operation"]), "tipos de movimento do extrato"],
    ["cards", "Cartões", br(manifest_rows["cards"]), "contas de cartão e nível (Essencial a Black)"],
    ["crm_events", "CRM", br(manifest_rows["crm_events"]), "e-mails e pushes enviados, vistos, clicados"],
    ["relatorio_mensal_cliente", "Operador", br(manifest_rows["relatorio_mensal_cliente"]), "o relatório que o operador manda ao banco"],
]

discovery_rows = [
    ["Pedidos sem cliente", f"{br(prof['orders_user_id_null_pct'], 0)}% dos pedidos com <code>user_id</code> vazio", "o cliente vem do carrinho; ajuste de ingestão pedido"],
    ["CRM em outro fuso", f"{br(prof['crm_events_3h_after_order'])} de {br(prof['crm_order_approved_events'])} eventos 'pedido aprovado' chegam exatamente 3h depois do pedido", "o CRM grava em UTC; convertemos para Brasília"],
    ["CRM sem grupo de controle", f"{br(prof['crm_control_group_null_pct'], 0)}% dos eventos sem grupo de controle", "efeito de campanha só pode ser lido de forma descritiva"],
    ["Pagamento dividido", f"{br(prof['items_paid_by_multiple_accounts'])} itens pagos por mais de uma conta; {br(prof['items_paid_by_mixed_card_classes'])} com níveis diferentes", "não é duplicata; o nível de cartão precisa ser o do cliente"],
    ["Saldo é do cliente", f"{br(prof['accounts_negative_balance_last_month'])} contas negativas e {br(prof['customers_negative_balance_last_month'])} clientes negativos em set/26", "saldo e breakage medidos por cliente"],
    ["Um dia fora da curva", f"{br(prof['atypical_day_air_items'])} resgates aéreos e {mi(prof['atypical_day_air_points'])} mi pontos em 12/01/26", "dia marcado como atípico; base 'antes do Pix' = fev a mai/26"],
]

decision_rows = [
    ["Resgate efetivo = APROVADO, líquido de devoluções", f"cancelados não tiram pontos; em {br(prof['items_points_reconciled'])} itens os pontos debitados = pagos", "é a base que o contrato deveria usar; expôs o erro do operador"],
    ["Metas pela definição do operador", "reproduz o relatório dele com até 1,5 p.p.", "comparável ao que o banco já recebe; a visão estrita mostra o risco"],
    ["CRM convertido de UTC", f"{br(prof['crm_events_3h_after_order'])} de {br(prof['crm_order_approved_events'])} eventos confirmam +3h", "cada envio e clique cai no dia certo da análise de campanha"],
    ["Nível de cartão = atual do cliente", f"{br(prof['accounts_negative_balance_last_month'])} contas negativas, 0 clientes; {br(prof['items_paid_by_mixed_card_classes'])} itens mistos", "corte por nível sem dupla contagem"],
    ["Breakage = expirado ÷ emitido, por safra", "definição de mercado (IFRS 15); Multiplus 21% a 24%", "número comparável ao mercado e à meta de 20%"],
    ["12/01 marcado como atípico", f"{br(prof['atypical_day_air_items'])} resgates num dia, 24h uniformes, sem campanha", "a base 'antes do Pix' não fica inflada por aéreas"],
    ["Regras em tabelas de referência", "metas e eventos ficam fora do SQL", "o negócio muda a regra sem mexer no código"],
]

open_rows = [
    ["Nível = atual do cliente", "nível da conta que pagou", "só muda cortes por nível; a alternativa já está pronta"],
    ["Metas pela definição do operador", "visão estrita (varejo só produto)", f"varejo nunca passou de {br(strict_max, 1)}%: a meta nunca teria sido cumprida"],
    ["Pix dentro do denominador", "Pix fora do denominador", f"set/26: varejo {br(ex_pix_var, 1)}% e aéreas {br(ex_pix_air, 1)}%"],
    ["Resgate efetivo líquido", "aprovado bruto ou + estornados", "no máximo 0,11 p.p.; nenhum mês muda de status de meta"],
    ["Base antes do Pix = fev a mai/26", "incluir jan/26", f"jan tem 12/01: aéreas {br(jan_air, 1)}% ({br(jan_air_ex, 1)}% sem o dia)"],
    ["Custo ≈ valor do produto − dinheiro do cliente", "custo real dos parceiros", "varejo fica mais barato; o Pix segue sendo o mais caro"],
]

question_rows = [
    ["O Pix conta no denominador das metas? Transferências e agência contam como varejo?", "contrato / negócio", "se a meta de varejo está ou não sendo cumprida"],
    ["Quanto o banco paga por ponto, e quando (emissão ou resgate)?", "financeiro / contrato", "o prejuízo total do Pix e a taxa ideal"],
    ["O que aconteceu em 12/01/2026?", "negócio / marketing", "o histórico de aéreas e a linha de base"],
    ["Por que o saldo migrado expira desde jan/26 se vale até 2028?", "dono do sistema de pontos", "a projeção do breakage do migrado"],
    ["Qual a regra do R$ do Pix no relatório?", "operador", "a diferença de 0,2% a 0,7% no valor pago"],
    ["Qual definição gerou o breakage de 40%?", "diretoria", "o alinhamento da métrica oficial"],
    ["Corrigir user_id dos pedidos, fuso e IDs do CRM, grupo de controle", "donos dos sistemas", "a qualidade e o custo das próximas análises"],
]

board = f"""
<!-- 01 · Capa -->
<section class="slide" data-section="Capa" data-template="capa-manifesto" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:44px;">
    <span class="overline" data-anim="up">Pontua+ · Diretoria · out/2026</span>
    <h1 class="t-cover" data-anim="up">O Pix <span class="hl-invert">somou volume</span><br>e cobrou a conta</h1>
    <p class="t-body" style="max-width:1250px" data-anim="up">O que recebemos, o que construímos para responder com segurança, o que os dados mostram, o que ainda está em aberto e o que recomendamos decidir.</p>
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

<!-- 03 · Agenda -->
<section class="slide" data-section="Agenda" data-template="agenda" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-columns:1fr 1.3fr; align-items:center; gap:120px;">
    <div class="head"><span class="overline" data-anim="up">Agenda</span><h2 class="t-title" data-anim="up">Uma história em cinco partes</h2></div>
    <ol style="list-style:none; display:grid; gap:0;" class="joined">
      <li style="background:var(--n900); padding:30px 36px; display:flex; gap:32px; align-items:baseline" data-anim="seq"><span class="t-label" style="color:var(--accent-data)">01</span><span class="t-sub">O que recebemos</span></li>
      <li style="background:var(--n900); padding:30px 36px; display:flex; gap:32px; align-items:baseline" data-anim="seq"><span class="t-label" style="color:var(--accent-data)">02</span><span class="t-sub">O que construímos para responder</span></li>
      <li style="background:var(--n900); padding:30px 36px; display:flex; gap:32px; align-items:baseline" data-anim="seq"><span class="t-label" style="color:var(--accent-data)">03</span><span class="t-sub">O que os dados mostram</span></li>
      <li style="background:var(--n900); padding:30px 36px; display:flex; gap:32px; align-items:baseline" data-anim="seq"><span class="t-label" style="color:var(--accent-data)">04</span><span class="t-sub">O que ainda está em aberto</span></li>
      <li style="background:var(--n900); padding:30px 36px; display:flex; gap:32px; align-items:baseline" data-anim="seq"><span class="t-label" style="color:var(--accent-data)">05</span><span class="t-sub">O que recomendamos</span></li>
    </ol>
  </div>
</section>

{chapter(1, "O que<br>recebemos", "O que recebemos")}

<!-- 04 · Contexto -->
<section class="slide" data-section="O que recebemos" data-template="sumario-executivo" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:48px;">
    <div class="head" style="max-width:1600px"><span class="overline" data-anim="up">O contexto</span><h2 class="t-title" data-anim="up">Uma decisão para a semana que vem, com <span class="hl" data-anim="hl">metas de contrato em jogo</span></h2></div>
    <div class="grid-3">
      {card("O programa", "Pontua+, do Banco Aurora", "Quem usa o cartão acumula pontos e troca por passagens aéreas, produtos de varejo ou transferências a parceiros. Uma empresa do grupo opera e presta contas ao banco todo mês.")}
      {card("O Pix · 27/05/2026", "Pontos viram dinheiro", "O cliente troca pontos por dinheiro na conta a R$ 0,019 por ponto (cerca de 53 pontos = R$ 1). O resgate nessa modalidade disparou.")}
      {card("O contrato", "Aéreas ≥ 50% · varejo ≥ 20%", "Metas sobre o total de pontos resgatados. Aéreas custam ao programa mais do que o banco paga por ponto; varejo é onde o grupo tem parceiros próprios.")}
    </div>
    <p class="t-sub" style="color:var(--hi)" data-anim="up">A pergunta da diretoria: <span class="hl" data-anim="hl">estimular ou coibir o resgate via Pix?</span></p>
  </div>
</section>

<!-- 05 · Afirmações -->
<section class="slide" data-section="O que recebemos" data-template="sumario-executivo" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:48px;">
    <div class="head" style="max-width:1600px"><span class="overline" data-anim="up">Três afirmações para checar</span><h2 class="t-title" data-anim="up">Cada uma, se verdadeira, levaria a uma decisão diferente</h2></div>
    <div class="grid-3">
      {card("Time de CRM", "“A comunicação de lançamento explica o sucesso do Pix”", "Se for verdade: o sucesso é da campanha, e a alavanca para estimular ou frear o Pix é a comunicação.")}
      {card("Relatório do operador", "“O Pix sai a cerca de R$ 0,016 por ponto”", "Se for verdade: o Pix custa 16% menos que o anunciado e seria uma modalidade mais barata que aéreas.")}
      {card("Um diretor", "“Nosso breakage está em 40%; a meta é não passar de 20%”", "Se for verdade: pontos demais expiram sem uso, e o cliente percebe o programa como pouco útil.")}
    </div>
  </div>
</section>

<!-- 06 · Dados recebidos -->
<section class="slide" data-section="O que recebemos" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-columns:1.7fr 1fr; gap:64px; align-items:center;">
    <div data-anim="up">{table_html("1.1fr .7fr .6fr 2fr", ["Arquivo", "Origem", "Linhas", "Uma linha é"], data_rows, 20)}</div>
    <div class="head">
      <span class="overline" data-anim="up">Os dados</span>
      <h2 class="t-title" data-anim="up" style="font-size:52px">9 arquivos, 5 sistemas, <span class="hl" data-anim="hl">nenhum dicionário</span></h2>
      <p class="t-body-sm" data-anim="up">Entender os arquivos fazia parte do exercício. Antes de qualquer número, cada arquivo foi investigado: o que é uma linha, qual coluna a identifica, o que vem vazio e como as tabelas se ligam.</p>
      {meaning("cada número desta apresentação parte desses arquivos, e a contagem de linhas de cada um é conferida contra o MANIFESTO a cada execução.")}
      {source("contexto/MANIFESTO_v1.csv")}
    </div>
  </div>
</section>

<!-- 07 · Descobertas -->
<section class="slide" data-section="O que recebemos" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:36px;">
    <div class="head" style="max-width:1650px"><span class="overline" data-anim="up">O que a investigação revelou</span><h2 class="t-title" data-anim="up" style="font-size:54px">Antes de responder, os dados precisaram ser entendidos: <span class="hl" data-anim="hl">cada descoberta virou uma decisão</span></h2></div>
    {table_html("1fr 2fr 1.7fr", ["Descoberta", "Evidência nos dados", "O que decidimos"], discovery_rows, 22)}
    {source("mart_data_profile (descobertas recalculadas a cada build)")}
  </div>
</section>

{chapter(2, "O que construímos<br>para responder", "O que construímos")}

<!-- 08 · Arquitetura -->
<section class="slide" data-section="O que construímos" data-template="3-passos" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:56px;">
    <div class="head" style="max-width:1600px"><span class="overline" data-anim="up">Do arquivo à decisão</span><h2 class="t-title" data-anim="up">Um comando reconstrói tudo: <span class="hl" data-anim="hl">qualquer número aqui é rastreável</span></h2></div>
    <div class="joined flow">
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">01 / confere</span></div><h3>Os arquivos são os do case</h3><p class="t-body-sm">Impressão digital (SHA-256) e contagem dos 9 arquivos conferidas antes de tudo. Para o negócio: ninguém trabalha com uma versão diferente dos dados.</p><div class="conn"><svg width="20" height="20" viewBox="0 0 24 24"><circle class="pulse" cx="12" cy="12" r="4"/><path d="M4 12h13m0 0-4-4m4 4-4 4" fill="none" stroke="#00CFFF" stroke-width="2" stroke-linecap="square"/></svg></div></div>
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">02 / modela</span></div><h3>Regras explícitas e testadas</h3><p class="t-body-sm">dbt + DuckDB, modelo Kimball (fatos e dimensões), {br(n_tests_dbt)} testes. Para o negócio: cada regra (o que é resgate, o que é varejo) está escrita e pode ser revista.</p><div class="conn"><svg width="20" height="20" viewBox="0 0 24 24"><circle class="pulse" cx="12" cy="12" r="4"/><path d="M4 12h13m0 0-4-4m4 4-4 4" fill="none" stroke="#00CFFF" stroke-width="2" stroke-linecap="square"/></svg></div></div>
      <div class="step" data-anim="seq"><div class="step-top"><span class="t-label">03 / publica</span></div><h3>Uma base, três usos</h3><p class="t-body-sm">{n_tables} tabelas agregadas (sem dado de cliente) com dicionário. Dashboard, agente de IA e estes slides leem a mesma base: os números são sempre os mesmos.</p></div>
    </div>
  </div>
</section>

<!-- 09 · Decisões técnicas -->
<section class="slide" data-section="O que construímos" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:32px;">
    <div class="head" style="max-width:1650px"><span class="overline" data-anim="up">Decisões técnicas, em linguagem de negócio</span><h2 class="t-title" data-anim="up" style="font-size:54px">Cada escolha tem uma evidência <span class="hl" data-anim="hl">e um motivo de negócio</span></h2></div>
    {table_html("1.25fr 1.6fr 1.6fr", ["Decisão", "Por quê (evidência)", "O que garante ao negócio"], decision_rows, 21)}
  </div>
</section>

<!-- 10 · Confiança -->
<section class="slide" data-section="O que construímos" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:48px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">Quanto confiar nos números</span><h2 class="t-title" data-anim="up">{br(n_tests_dbt + n_tests_py)} testes travam <span class="hl" data-anim="hl">os números e as conclusões</span></h2></div>
    <div class="joined kpis">
      {kpi("Reconciliação", br(prof['items_points_reconciled']), "itens com pontos debitados = pagos")}
      {kpi("Relatório do operador", "±1,5 p.p.", "nossa visão reproduz as metas dele")}
      {kpi("Privacidade", "0", "identificadores de cliente publicados")}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px; padding-bottom:40px;">
      <p class="t-body-sm" data-anim="up">{br(n_tests_dbt)} testes no dbt e {br(n_tests_py)} em Python. Além de chaves e relacionamentos, há testes que travam os achados: Pix entre R$ 0,01895 e R$ 0,01905, operador somando todos os status, nenhum ponto do programa novo expirado, nenhum cliente com saldo negativo.</p>
      {meaning("se um dado novo mudar uma conclusão, o processo para antes de o número chegar a um slide ou ao dashboard.")}
    </div>
  </div>
</section>

{chapter(3, "O que os dados<br>mostram", "O que os dados mostram")}

<!-- 11 · Placar -->
<section class="slide" data-section="O que os dados mostram" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:44px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">Metas contratuais · set/2026</span><h2 class="t-title" data-anim="up">Aéreas cumpre. Varejo está abaixo da meta desde junho.</h2></div>
    <div class="joined kpis">
      {kpi("Aéreas (meta ≥ 50%)", f"{br(last['aereas_pct'], 1)}%", f"cumprida em {months_air_ok} de {months_total} meses")}
      {kpi("Varejo (meta ≥ 20%)", f"{br(last['varejo_pct'], 1)}%", f"abaixo em {months_var_below} de {months_total} meses")}
      {kpi("Pix", f"{br(last['pix_pct'], 1)}%", "dos pontos resgatados no mês")}
    </div>
    <div style="display:grid; grid-template-columns:1.6fr 1fr; gap:80px; align-items:end; padding-bottom:40px;">
      {var_bars}
      <div data-anim="up">{meaning(f"a meta de varejo deixou de ser cumprida com o Pix. Sem o Pix no denominador, varejo estaria em {br(ex_pix_var, 1)}%. Na visão estrita (só produto) nunca passou de {br(strict_max, 1)}%.")}{source("mart_goal_attainment_monthly (visão contrato = definição do operador)")}</div>
    </div>
  </div>
</section>

<!-- 12 · Waterfall -->
<section class="slide" data-section="O que os dados mostram" data-template="waterfall" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-columns:1fr 2fr; gap:100px; align-items:center;">
    <div class="head">
      <span class="overline" data-anim="up">Pontos resgatados por mês (mil)</span>
      <h2 class="t-title" data-anim="up">O Pix <span class="hl" data-anim="hl">somou</span>, quase não substituiu</h2>
      <p class="t-body-sm" data-anim="up">Média mensal antes (fev a 26/mai/2026) e depois do Pix (27/mai a set/2026). Aéreas e varejo cresceram em pontos. Só a transferência a parceiros encolheu: quem queria "converter" pontos agora recebe dinheiro.</p>
      {meaning("a queda das metas é efeito do denominador, não perda de resgates em aéreas e varejo. O cliente quer liquidez, e o Pix atendeu uma demanda nova.")}
      {source("mart_redemption_economics (resgates efetivos, líquidos de devoluções)")}
    </div>
    <div class="wf" data-waterfall='{json.dumps(wf_items, ensure_ascii=False)}'></div>
  </div>
</section>

<!-- 13 · 12/01 -->
<section class="slide" data-section="O que os dados mostram" data-template="big-number" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:34px;">
    <span class="overline" data-anim="up">Ponto de atenção · 12/01/2026</span>
    <div class="t-data-xl"><span data-anim="count" data-to="{round(prof['atypical_day_air_points'] / 1e6)}">{round(prof['atypical_day_air_points'] / 1e6)}</span><span class="unit"> mi pontos em um dia</span></div>
    <p class="t-sub" style="max-width:1500px; color:var(--mid)" data-anim="up">{br(prof['atypical_day_air_items'])} resgates aéreos num só dia, espalhados igualmente nas 24h, de clientes com saldo migrado e <span class="hl" data-anim="hl">sem campanha no CRM.</span></p>
    <p class="t-body-sm" style="max-width:1500px" data-anim="up">Leva aéreas a {br(jan_air, 1)}% em jan/2026 ({br(jan_air_ex, 1)}% sem o dia). Hipótese principal: promoção de passagens não registrada no CRM; alternativa: carga em lote do programa anterior. <b style="color:var(--hi)">Precisa ser validado com a área de negócio.</b></p>
    {meaning("o dado não foi apagado, só marcado. A comparação 'antes do Pix' usa fev a mai/2026 para não ser inflada por esse dia.")}
  </div>
</section>

<!-- 14 · CRM -->
<section class="slide" data-section="O que os dados mostram" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:44px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">CRM: "a comunicação de lançamento explica o sucesso do Pix"</span><h2 class="t-title" data-anim="up">Não se sustenta: <span class="hl" data-anim="hl">sem comunicação, a adoção foi a mesma.</span></h2></div>
    <div class="joined kpis">
      {kpi("Recebeu o e-mail", f"{br(email_pct, 1)}%", "adotou o Pix")}
      {kpi("Nenhuma comunicação", f"{br(none_pct, 1)}%", "adotou o Pix")}
      {kpi("Usou até 7 dias após o e-mail", f"{br(week_pct, 1)}%", f"{br(late_pct, 0)}% só depois de 30 dias")}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px; padding-bottom:40px;">
      <p class="t-body-sm" data-anim="up">Quem clicou no e-mail adotou {br(click_pct, 1)}%. O primeiro Pix (27/05, 09:15) é anterior ao primeiro envio (28/05, 10:00), e o link do e-mail levava ao catálogo, não ao Pix. <b style="color:var(--hi)">Ressalva:</b> o CRM não tem grupo de controle ({br(prof['crm_control_group_null_pct'], 0)}% vazio): a leitura é descritiva, não causal.</p>
      <div data-anim="up">{meaning("o produto em si (dinheiro na conta) explica melhor a adoção. Comunicação não é a alavanca para frear ou estimular o Pix; preço e regra são.")}{source("mart_crm_pix_launch_adoption, mart_crm_pix_launch_timing")}</div>
    </div>
  </div>
</section>

<!-- 15 · Operador -->
<section class="slide" data-section="O que os dados mostram" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:44px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">Operador: "o Pix sai a cerca de R$ 0,016 por ponto"</span><h2 class="t-title" data-anim="up">Falso: o Pix custa <span class="hl" data-anim="hl">R$ {br(pix_cost, 4)}</span> em todos os meses.</h2></div>
    <div class="joined kpis">
      {kpi("Custo real", f"R$ {br(pix_cost, 4)}", "R$ creditados ÷ pontos pagos")}
      {kpi("Relatório do operador", f"R$ {br(op_cost, 4)}", "R$ pagos ÷ pontos de todos os pedidos")}
      {kpi("Pontos sem pagamento", f"{br(non_eff_pct, 1)}%", "cancelados, inválidos, estornados")}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px; padding-bottom:40px;">
      <p class="t-body-sm" data-anim="up">O relatório divide os reais efetivamente pagos pelos pontos de todos os pedidos Pix, inclusive os nunca pagos. As transações e os pontos do relatório batem exatamente com essa base (teste automatizado). Em aberto: os reais do operador ficam 0,2% a 0,7% abaixo dos pagos.</p>
      <div data-anim="up">{meaning("o Pix não é mais barato que o anunciado. O banco recebe um relatório com base misturada, e isso precisa ser corrigido na fonte.")}{source("mart_pix_reconciliation_monthly")}</div>
    </div>
  </div>
</section>

<!-- 16 · Breakage -->
<section class="slide" data-section="O que os dados mostram" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:44px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">Diretor: "nosso breakage está em 40%; a meta é não passar de 20%"</span><h2 class="t-title" data-anim="up">Não é 40%. Mas o migrado <span class="hl" data-anim="hl">passa de 20% em outubro.</span></h2></div>
    <div class="joined kpis">
      {kpi("Breakage do programa novo", f"{br(brk_new, 0)}%", "nada venceu: validade de 24 meses")}
      {kpi("Breakage do saldo migrado", f"{br(brk_mig, 1)}%", f"+{br(mig_step, 1)} p.p. por mês")}
      {kpi("Expiração ÷ resgate", f"{br(etr.min(), 0)} a {br(etr.max(), 0)}%", "fev-abr/2026: provável origem do 40%")}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px; padding-bottom:40px;">
      <p class="t-body-sm" data-anim="up">Breakage, pela definição de mercado (IFRS 15), é expirado ÷ emitido por safra. A Multiplus operou entre 21% e 24% (2010-2012) e geria a taxa numa faixa ideal. A razão "expiração do mês ÷ resgate do mês" não é breakage e cai com o Pix só porque o resgate cresceu.</p>
      <div data-anim="up">{meaning("não há excesso de pontos expirando no programa novo. O risco real é o saldo migrado, e o Pix tende a reduzir o breakage futuro, que é margem do programa.")}{source("mart_points_flow_monthly; benchmark em entrega/docs/benchmark_breakage.md")}</div>
    </div>
  </div>
</section>

<!-- 17 · Saúde financeira -->
<section class="slide" data-section="O que os dados mostram" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-columns:1fr 1.3fr; gap:100px; align-items:center;">
    <div class="head">
      <span class="overline" data-anim="up">Custo do programa por ponto resgatado</span>
      <h2 class="t-title" data-anim="up">O Pix é a <span class="hl" data-anim="hl">modalidade mais cara</span></h2>
      <p class="t-body-sm" data-anim="up">O enunciado diz que aéreas já custam mais do que o banco paga por ponto. Cada ponto em Pix custa pelo menos R$ {br(pix_cost - cost['aereas'], 4)} a mais que um ponto em aéreas: ~R$ {br(loss_vs_air / 1e3, 0)} mil/mês sobre ~R$ {br(pix_month_brl / 1e3, 0)} mil pagos em dinheiro em set/26.</p>
      <p class="t-body-sm" data-anim="up"><b style="color:var(--hi)">Hipótese declarada:</b> custo ≈ valor do produto − dinheiro pago pelo cliente. Falta o preço por ponto do contrato com o banco.</p>
      {meaning("estimular o Pix aumenta o custo sem ajudar nenhuma meta. O Pix só se paga com um preço por ponto menor.")}
      {source("mart_redemption_economics (depois do Pix)")}
    </div>
    <div data-anim="up">{cost_bars}</div>
  </div>
</section>

{chapter(4, "O que ainda<br>está em aberto", "Em aberto")}

<!-- 18 · Decisões revisáveis -->
<section class="slide" data-section="Em aberto" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:32px;">
    <div class="head" style="max-width:1650px"><span class="overline" data-anim="up">Decisões revisáveis</span><h2 class="t-title" data-anim="up" style="font-size:54px">As regras estão abertas a ajuste, <span class="hl" data-anim="hl">e o efeito de cada troca já foi medido</span></h2></div>
    {table_html("1.3fr 1.1fr 1.8fr", ["Regra adotada", "Alternativa", "Se trocar, o que muda"], open_rows, 22)}
    {meaning("nenhuma alternativa inverte a recomendação: em todas, o Pix continua sendo a modalidade mais cara e a que mais pressiona a meta de varejo.")}
  </div>
</section>

<!-- 19 · Perguntas pendentes -->
<section class="slide" data-section="Em aberto" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:32px;">
    <div class="head" style="max-width:1650px"><span class="overline" data-anim="up">Perguntas pendentes</span><h2 class="t-title" data-anim="up" style="font-size:54px">O que os dados não respondem <span class="hl" data-anim="hl">e quem pode responder</span></h2></div>
    {table_html("2fr .9fr 1.4fr", ["Pergunta", "Quem responde", "O que muda com a resposta"], question_rows, 21)}
  </div>
</section>

{chapter(5, "O que<br>recomendamos", "Recomendação")}

<!-- 20 · Recomendação -->
<section class="slide" data-section="Recomendação" data-template="sumario-executivo" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:flex-start; gap:28px; padding-top:120px;">
    <div class="head"><span class="overline" data-anim="up">Recomendação</span><h2 class="t-title" data-anim="up">Coibir o Pix com calibragem, não eliminar</h2></div>
    <div class="grid-3" style="grid-template-columns:repeat(3,1fr)">
      {card("1 · Calibrar o Pix", "Taxa menor ou teto mensal", f"Número: R$ {br(pix_cost, 3)}/ponto, o maior custo, {br(last['pix_pct'], 0)}% dos pontos. Falta: preço do banco por ponto e elasticidade da taxa.")}
      {card("2 · Renegociar a meta", "Pix fora do denominador", f"Número: sem o Pix, varejo {br(ex_pix_var, 1)}% e aéreas {br(ex_pix_air, 1)}%. Falta: como o contrato classifica Pix, transferências e agência.")}
      {card("3 · Corrigir o relatório", "Base única no operador", f"Número: {br(non_eff_pct, 1)}% dos pontos Pix do relatório não foram pagos. Falta: a regra de R$ do operador.")}
    </div>
    <div class="grid-3" style="grid-template-columns:repeat(2,1fr)">
      {card("4 · Padronizar o breakage", "Expirado ÷ emitido, por safra", f"Número: migrado em {br(brk_mig, 1)}%, subindo {br(mig_step, 1)} p.p./mês. Falta: a regra de expiração do saldo migrado.")}
      {card("5 · Medir antes de atribuir", "Grupo de controle no CRM", f"Número: {br(none_pct, 1)}% de adoção sem nenhuma comunicação. Falta: teste A/B e explicação para 12/01.")}
    </div>
  </div>
</section>

<!-- 21 · Próximos passos -->
<section class="slide" data-section="Recomendação" data-template="roadmap" data-tagline>
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
    <p class="t-caption" data-anim="up">trecho tracejado = futuro</p>
  </div>
</section>

<!-- 22 · Acompanhamento -->
<section class="slide" data-section="Recomendação" data-template="dashboard" data-tagline>
  {WM}
  <div class="pad" style="display:grid; grid-template-rows:auto auto 1fr; gap:44px; padding-top:110px;">
    <div class="head"><span class="overline" data-anim="up">Como a diretoria acompanha</span><h2 class="t-title" data-anim="up">Um dashboard e um analista de IA <span class="hl" data-anim="hl">sobre a mesma base</span></h2></div>
    <div class="joined kpis">
      {kpi("Dashboard", "4 telas", "visão geral, metas e Pix, breakage e CRM, explorar")}
      {kpi("Base publicada", f"{n_tables} tabelas", "só agregados, com dicionário de cada campo")}
      {kpi("Analista de IA", "Gemini", "responde com SQL, mostra a fonte e recusa dado individual")}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px; padding-bottom:40px;">
      <p class="t-body-sm" data-anim="up"><b style="color:var(--hi)">Exemplo real:</b> "As metas foram cumpridas em setembro?" → "Aéreas {br(last['aereas_pct'], 2)}%, cumprida; varejo {br(last['varejo_pct'], 2)}%, não cumprida (fonte: mart_goal_attainment_monthly)". Pedido de lista de clientes por ID: recusado por privacidade.</p>
      <div data-anim="up">{meaning("as próximas perguntas da diretoria podem ser respondidas sem um novo projeto, com o mesmo número em todos os canais.")}<p class="t-caption" style="margin-top:12px">{APP_URL}</p></div>
    </div>
  </div>
</section>

<!-- 23 · Decisão -->
<section class="slide" data-section="Decisão" data-template="fechamento" data-tagline>
  {WM}
  <div class="pad" style="display:flex; flex-direction:column; justify-content:center; gap:56px;">
    <div class="head"><span class="overline" data-anim="up">Decisão</span><h2 class="t-title" data-anim="up">O que precisamos decidir</h2></div>
    <div class="grid-3">
      {card("01", "Calibrar o Pix", "Taxa por ponto e/ou teto mensal, com teste A/B.")}
      {card("02", "Pauta com o banco", "Denominador das metas e classificação de transferências e agência.")}
      {card("03", "Dono das definições", "Breakage, resgate efetivo e relatório do operador com uma regra só.")}
    </div>
    <div class="cta" data-anim="featured"><p class="t-sub" style="color:#fff">O Pix fica, mas com um preço que o programa consegue pagar.</p></div>
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
