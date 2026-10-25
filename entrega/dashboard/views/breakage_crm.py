"""Breakage e CRM: as afirmações do diretor (40%) e do CRM (comunicação explica o Pix)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import charts, ui
from lib.theme import MUTED, OTHER, SERIES

st.title("Breakage e CRM")

flow = ui.table("mart_points_flow_monthly").copy()
flow["year_month"] = pd.to_datetime(flow["month_start"]).dt.strftime("%Y-%m")
months = sorted(flow["year_month"].unique())

f1, f2 = st.columns([2, 2])
with f1:
    start, end = ui.month_range(months, "bc_periodo", default_start="2025-10")
with f2:
    card = ui.table("dim_card_class").sort_values("card_class_rank")
    classes = ui.multiselect_all("Nível de cartão (saldo)", [c for c in card["card_class"] if c != "Desconhecido"], "bc_nivel")
flow = flow[flow["year_month"].between(start, end)]

# ------------------------------------------------------------------ breakage
st.subheader("Breakage: o número correto não é 40%")
last = flow.iloc[-1]
k = st.columns(3)
with k[0]:
    ui.kpi("Breakage do programa novo", f"{ui.br(last['breakage_new_program_realized_pct'], 1)}%",
           "expirados ÷ creditados. Nada venceu: validade de 24 meses, 1º vencimento em 25/09/2027")
with k[1]:
    v = last["breakage_migrated_realized_pct"]
    ui.kpi("Breakage do saldo migrado", f"{ui.br(v, 1)}%", f"expirados ÷ migrados, acumulado até {last['year_month']}",
           ("critical", "Acima do limite de 20%") if v > 20 else ("warning", "Perto do limite de 20%") if v >= 18 else ("good", "Abaixo de 20%"))
with k[2]:
    pre = flow[flow["year_month"].isin(["2026-02", "2026-03", "2026-04"])]["expired_to_redeemed_pct"]
    if not pre.empty:
        ui.kpi("Expiração ÷ resgate (fev-abr/2026)", f"{ui.br(pre.min(), 0)}% a {ui.br(pre.max(), 0)}%",
               "provável origem do '40%'", ("warning", "Não é breakage: compara com resgate, não com emissão"))

c1, c2 = st.columns(2)
with c1:
    long = flow.melt(id_vars="year_month", value_vars=["breakage_migrated_realized_pct", "breakage_new_program_realized_pct"], var_name="k", value_name="v")
    chart = charts.lines(long, "v", "k",
                         {"breakage_migrated_realized_pct": "Saldo migrado", "breakage_new_program_realized_pct": "Programa novo"},
                         {"breakage_migrated_realized_pct": OTHER["primary"], "breakage_new_program_realized_pct": OTHER["secondary"]},
                         "Breakage realizado (expirados ÷ emitidos, acumulado)", "%")
    goal = pd.DataFrame({"y": [20]})
    import altair as alt

    st.altair_chart(alt.layer(chart, alt.Chart(goal).mark_rule(strokeDash=[4, 4], color=MUTED).encode(y="y:Q")),
                    width="stretch", theme=None)
    ui.source("mart_points_flow_monthly. Linha tracejada: limite de 20% da diretoria. Definição de mercado: docs/benchmark_breakage.md (Multiplus: 21% a 24%).")
with c2:
    st.altair_chart(
        charts.simple_bars(flow, "year_month", "expired_to_redeemed_pct",
                           "Expiração do mês ÷ resgate do mês (não é breakage)", "%", color=MUTED),
        width="stretch", theme=None,
    )
    ui.source("mart_points_flow_monthly. Cai depois do Pix só porque o resgate cresceu: lida como breakage, faria o Pix parecer positivo.")

balance = ui.table("agg_points_balance_monthly").merge(card, on="card_class_key").merge(ui.table("dim_month")[["month_date_key", "year_month"]], on="month_date_key")
balance = balance[balance["card_class"].isin(classes) & balance["year_month"].between(start, end)]
bal = balance.groupby("year_month", as_index=False)[["closing_balance_points", "migrated_points"]].sum()
st.altair_chart(
    charts.simple_bars(bal, "year_month", "closing_balance_points", "Saldo de pontos em aberto ao fim do mês", "Pontos", color=OTHER["primary"], y_format=",.0f"),
    width="stretch", theme=None,
)
migrated_total = balance["migrated_points"].sum() if "migrated_points" in balance else 0
ui.source(f"agg_points_balance_monthly (saldo por cliente, somado por nível). Saldo migrado do programa anterior no período: {ui.br_compact(migrated_total)} pontos.")

# ------------------------------------------------------------------ CRM
st.divider()
st.subheader("CRM: a comunicação de lançamento explica o Pix?")
st.warning("Análise descritiva: o export do CRM não tem grupo de controle (control_group 100% vazio). Não mede efeito causal.", icon="⚠️")

adoption = ui.table("mart_crm_pix_launch_adoption").copy()
prior = st.segmented_control("Clientes", ["Todos", "Já resgatavam antes do Pix", "Nunca tinham resgatado"], default="Todos", key="bc_prior")
if prior == "Já resgatavam antes do Pix":
    adoption = adoption[adoption["had_prior_redemption"]]
elif prior == "Nunca tinham resgatado":
    adoption = adoption[~adoption["had_prior_redemption"]]
seg = adoption.groupby("exposure_segment", as_index=False)[["customers", "pix_adopters"]].sum().sort_values("exposure_segment")
seg["pix_adoption_pct"] = seg["pix_adopters"] / seg["customers"] * 100
seg["segmento"] = seg["exposure_segment"].str[3:] + " (" + seg["customers"].map(ui.br) + " clientes)"

c1, c2 = st.columns(2)
with c1:
    st.altair_chart(
        charts.simple_bars(seg, "segmento", "pix_adoption_pct", "Adoção do Pix por exposição à comunicação (27/05 a 04/06)",
                           "% que usou o Pix", color=SERIES["pix"], horizontal=True),
        width="stretch", theme=None,
    )
    ui.source("mart_crm_pix_launch_adoption. Quem não recebeu nenhuma comunicação adotou na mesma taxa.")
with c2:
    timing = ui.table("mart_crm_pix_launch_timing").sort_values("timing_window").copy()
    timing["janela"] = timing["timing_window"].str[3:]
    st.altair_chart(
        charts.simple_bars(timing, "janela", "customers_pct", "Quando quem recebeu o e-mail usou o Pix pela 1ª vez",
                           "% dos clientes", color=SERIES["pix"]),
        width="stretch", theme=None,
    )
    week = timing.loc[timing["timing_window"].str.startswith(("0.", "1.")), "customers_pct"].sum()
    ui.source(f"mart_crm_pix_launch_timing. Só {ui.br(week, 1)}% usaram até 7 dias após o e-mail (ou antes dele).")

crm = ui.table("agg_crm_events_monthly").merge(ui.table("dim_month")[["month_date_key", "year_month"]], on="month_date_key")
e1, e2 = st.columns(2)
with e1:
    event = st.selectbox("Evento", sorted(crm["event_name"].unique()), index=sorted(crm["event_name"].unique()).index("Notification Sent"), key="bc_evento")
with e2:
    ch = ui.multiselect_all("Canal da campanha", sorted(crm["campaign_type"].unique()), "bc_canal")
vol = crm[(crm["event_name"] == event) & crm["campaign_type"].isin(ch) & crm["year_month"].between(start, end)]
vol = vol.groupby("year_month", as_index=False)["events_count"].sum()
st.altair_chart(
    charts.simple_bars(vol, "year_month", "events_count", f"Volume de '{event}' por mês", "Eventos", color=OTHER["primary"], y_format=",.0f"),
    width="stretch", theme=None,
)
ui.source("agg_crm_events_monthly (horário convertido de UTC para Brasília)")
