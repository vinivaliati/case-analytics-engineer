"""Metas e Pix: o que o Pix fez com as metas e quanto ele custa."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import charts, data, ui
from lib.theme import MUTED, SERIES

st.title("Metas e Pix")

red = ui.redemptions()
months = sorted(red["year_month"].unique())
labels = data.MODALITY_LABELS

# ------------------------------------------------------------------ filtros
f1, f2, f3, f4 = st.columns([2, 1.3, 1.5, 1])
with f1:
    start, end = ui.month_range(months, "mp_periodo")
with f2:
    view = st.selectbox(
        "Visão das metas", ["Contrato (oficial)", "Estrita (varejo só produto)", "Sem Pix no denominador"], key="mp_visao",
        help="Contrato = definição do operador. Estrita e Sem Pix são cenários de sensibilidade.",
    )
with f3:
    classes = ui.multiselect_all("Nível de cartão", list(red.sort_values("card_class_rank")["card_class"].dropna().unique()), "mp_nivel")
with f4:
    channels = ui.multiselect_all("Canal", sorted(red["sales_channel"].dropna().unique()), "mp_canal")

in_period = red["year_month"].between(start, end)
filtered = red[in_period & red["card_class"].isin(classes) & red["sales_channel"].isin(channels)]

view_col = "goal_category_strict" if view.startswith("Estrita") else "goal_category_contract"
shares = data.goal_shares(filtered, view_col, exclude_pix=view.startswith("Sem Pix"))

# ------------------------------------------------------------------ metas
st.subheader("Metas contratuais")
months_below = int((shares.get("varejo", pd.Series(dtype=float)) < 20).sum())
months_air_ok = int((shares.get("aereas", pd.Series(dtype=float)) >= 50).sum())
last = shares.iloc[-1] if len(shares) else None
ui.kpi_row([
    ui.kpi("Meses com aéreas ≥ 50%", f"{months_air_ok} de {len(shares)}", view),
    ui.kpi("Meses com varejo < 20%", f"{months_below} de {len(shares)}", view),
    ui.kpi(f"Varejo em {last['year_month']}", f"{ui.br(last.get('varejo', 0), 1)}%", view,
           ("good", "Meta cumprida") if last.get("varejo", 0) >= 20 else ("critical", "Abaixo da meta de 20%"))
    if last is not None else "",
])

c1, c2 = st.columns(2)
with c1:
    series = ["aereas", "varejo"] if view.startswith("Sem Pix") else ["aereas", "varejo", "pix"]
    st.altair_chart(
        charts.share_lines(shares, series, labels, data.GOALS, f"Participação nos pontos resgatados · {view}",
                           events={"2026-01": "pico 12/01", "2026-05": "Pix"}),
        width="stretch", theme=None,
    )
    ui.source(f"agg_redemptions_monthly + dim_product ({view_col}). 12/01/2026: dia atípico, causa a validar com o negócio.")
with c2:
    pts = data.monthly_points_by_modality(filtered)
    st.altair_chart(
        charts.stacked_bars(pts, "net_redeemed_points", "goal_category_strict", labels,
                            "Pontos por modalidade: aéreas e varejo não caíram, o Pix somou", "Pontos"),
        width="stretch", theme=None,
    )
    ui.source("agg_redemptions_monthly (resgates efetivos). A queda dos % vem do denominador maior.")
ui.show_table(shares.round(2), "Ver tabela das participações")

# ------------------------------------------------------------------ Pix
st.divider()
st.subheader("Pix: custo real e relatório do operador")
pix = ui.table("mart_pix_reconciliation_monthly").copy()
pix["year_month"] = pd.to_datetime(pix["month_start"]).dt.strftime("%Y-%m")
pix = pix[pix["year_month"].between(start, end)]

if pix.empty:
    st.info("O Pix foi lançado em 27/05/2026: escolha um período que inclua mai a set/2026.")
else:
    share_bad = pix["non_effective_points"].sum() / pix["all_status_points"].sum() * 100
    ui.kpi_row([
        ui.kpi("Custo real por ponto", f"R$ {ui.br(pix['effective_brl'].sum() / pix['effective_points'].sum(), 4)}",
               "R$ creditados ÷ pontos dos resgates efetivos"),
        ui.kpi("Operador reporta", f"R$ {ui.br(pix['operator_brl'].sum() / pix['operator_points'].sum(), 4)}",
               "R$ pagos ÷ pontos de todos os status", ("critical", "Mistura bases diferentes")),
        ui.kpi("Pontos Pix não pagos", f"{ui.br(share_bad, 1)}%", "contados pelo operador: cancelados, inválidos, estornados e aguardando"),
        ui.kpi("Dinheiro pago via Pix", f"R$ {ui.br_compact(pix['effective_brl'].sum())}", f"{start} a {end}"),
    ])

    c1, c2 = st.columns(2)
    with c1:
        long = pix.melt(id_vars="year_month", value_vars=["effective_brl_per_point", "operator_brl_per_point"], var_name="k", value_name="v")
        st.altair_chart(
            charts.lines(long, "v", "k", {"effective_brl_per_point": "Custo real", "operator_brl_per_point": "Relatório do operador"},
                         {"effective_brl_per_point": SERIES["pix"], "operator_brl_per_point": MUTED},
                         "R$ por ponto do Pix", "R$ por ponto", ",.4f"),
            width="stretch", theme=None,
        )
        ui.source("mart_pix_reconciliation_monthly (testado: custo real entre 0,01895 e 0,01905 em todos os meses)")
    with c2:
        stack = pd.concat([
            pix[["year_month", "effective_points"]].rename(columns={"effective_points": "pts"}).assign(k="pix"),
            pix[["year_month", "non_effective_points"]].rename(columns={"non_effective_points": "pts"}).assign(k="nao_pago"),
        ])
        st.altair_chart(
            charts.stacked_bars(stack, "pts", "k", {"pix": "Pagos (efetivos)", "nao_pago": "Não pagos"},
                                "Pontos Pix que o operador soma", "Pontos",
                                colors={"pix": SERIES["pix"], "nao_pago": MUTED}),
            width="stretch", theme=None,
        )
        ui.source("mart_pix_reconciliation_monthly: pontos e transações do operador = itens de todos os status (bate exato)")

    by_class = data.effective(filtered[filtered["is_pix"]]).groupby(["card_class", "card_class_rank"], as_index=False)["net_redeemed_points"].sum()
    total_class = data.effective(filtered).groupby("card_class", as_index=False)["net_redeemed_points"].sum().rename(columns={"net_redeemed_points": "total"})
    by_class = by_class.merge(total_class, on="card_class").sort_values("card_class_rank")
    by_class["pix_pct"] = by_class["net_redeemed_points"] / by_class["total"] * 100
    st.altair_chart(
        charts.simple_bars(by_class, "card_class", "pix_pct", "Peso do Pix nos resgates de cada nível de cartão (período)",
                           "% dos pontos resgatados", color=SERIES["pix"]),
        width="stretch", theme=None,
    )
    ui.source("agg_redemptions_monthly. Nível = nível atual do cliente.")
    ui.show_table(pix.drop(columns=["month_start"]), "Ver reconciliação mês a mês")
