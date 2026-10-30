"""Explorar: cortes livres sobre o star schema agregado publicado (fatos agg_* + dimensões)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import charts, data, ui
from lib.theme import OTHER

st.title("Explorar")
st.caption("Monte seu corte sobre os dados agregados. Mesmas tabelas que um BI ou o agente usariam.")

month = ui.table("dim_month")[["month_date_key", "year_month", "pix_phase"]]
card = ui.table("dim_card_class")


def base_redemptions() -> pd.DataFrame:
    df = ui.redemptions().copy()
    df["modalidade_meta"] = df["goal_category_contract"]
    df["modalidade_estrita"] = df["goal_category_strict"].map(data.MODALITY_LABELS).fillna(df["goal_category_strict"])
    return df


def base_movements() -> pd.DataFrame:
    return ui.table("agg_points_movements_monthly").merge(ui.table("dim_operation"), on="operation_key").merge(card, on="card_class_key").merge(month, on="month_date_key")


def base_balance() -> pd.DataFrame:
    return ui.table("agg_points_balance_monthly").merge(card, on="card_class_key").merge(month, on="month_date_key")


def base_crm() -> pd.DataFrame:
    return ui.table("agg_crm_events_monthly").merge(ui.table("dim_campaign"), on="campaign_key").merge(month, on="month_date_key")


SOURCES = {
    "Resgates": {
        "loader": base_redemptions,
        "table": "agg_redemptions_monthly",
        "dims": {"Mês": "year_month", "Fase do Pix": "pix_phase", "Modalidade (meta)": "modalidade_meta",
                 "Modalidade (estrita)": "modalidade_estrita", "Fornecedor": "supplier_name", "Tipo de produto": "product_type",
                 "Nível de cartão": "card_class", "Canal": "sales_channel", "Status do item": "item_status"},
        "measures": {"Pontos resgatados (oficial)": "net_redeemed_points", "Itens": "items_count",
                     "Valor dos produtos (R$)": "product_value_brl", "Dinheiro pago pelo cliente (R$)": "customer_cash_brl",
                     "Pontos devolvidos": "refunded_points"},
        "note": "Pontos resgatados oficiais só contam resgates efetivos; itens e valores incluem todos os status (filtre por status).",
    },
    "Movimentos de pontos": {
        "loader": base_movements,
        "table": "agg_points_movements_monthly",
        "dims": {"Mês": "year_month", "Fase do Pix": "pix_phase", "Operação": "operation_name", "Direção": "direction",
                 "Nível de cartão": "card_class"},
        "measures": {"Pontos (com sinal)": "points", "Créditos": "credit_points", "Débitos": "debit_points", "Movimentos": "movements_count"},
        "note": "Ledger completo, inclusive saldo migrado do programa anterior.",
    },
    "Saldo de pontos": {
        "loader": base_balance,
        "table": "agg_points_balance_monthly",
        "dims": {"Mês": "year_month", "Nível de cartão": "card_class"},
        "measures": {"Saldo em aberto": "closing_balance_points", "Clientes com saldo": "customers_with_balance",
                     "Pontos expirados (migrados)": "expired_migrated_points", "Pontos creditados": "credited_points"},
        "note": "Saldo é semi-aditivo: some entre níveis, nunca entre meses. Mantenha 'Mês' no agrupamento.",
    },
    "Eventos de CRM": {
        "loader": base_crm,
        "table": "agg_crm_events_monthly",
        "dims": {"Mês": "year_month", "Evento": "event_name", "Canal": "campaign_type", "Campanha": "campaign_name"},
        "measures": {"Eventos": "events_count"},
        "note": "Horário convertido de UTC para Brasília. Sem grupo de controle.",
    },
}

c1, c2, c3 = st.columns([1.2, 2, 1.4])
with c1:
    source_name = st.selectbox("Dados", list(SOURCES), key="ex_fonte")
src = SOURCES[source_name]
df = src["loader"]()
with c2:
    dims = st.multiselect("Agrupar por", list(src["dims"]), default=["Mês"], key=f"ex_dims_{source_name}")
with c3:
    measure_label = st.selectbox("Medida", list(src["measures"]), key=f"ex_medida_{source_name}")
measure = src["measures"][measure_label]

months = sorted(df["year_month"].dropna().unique())
start, end = ui.month_range(months, f"ex_periodo_{source_name}")
df = df[df["year_month"].between(start, end)]

filter_dims = [d for d in src["dims"] if d not in ("Mês",)]
with st.expander("Filtros", expanded=False):
    cols = st.columns(3)
    for i, label in enumerate(filter_dims):
        col = src["dims"][label]
        options = sorted(df[col].dropna().astype(str).unique())
        with cols[i % 3]:
            chosen = st.multiselect(label, options, placeholder="Todos", key=f"ex_f_{source_name}_{col}")
        if chosen:
            df = df[df[col].astype(str).isin(chosen)]

st.caption(src["note"])
group_cols = [src["dims"][d] for d in dims]
if group_cols:
    result = df.groupby(group_cols, as_index=False)[measure].sum()
else:
    result = pd.DataFrame({measure: [df[measure].sum()]})

if source_name == "Saldo de pontos" and "year_month" not in group_cols:
    st.warning("Saldo somado entre meses não tem significado. Inclua 'Mês' no agrupamento.", icon="⚠️")

pretty = result.rename(columns={v: k for k, v in src["dims"].items()} | {measure: measure_label})

if len(group_cols) == 1:
    xcol = group_cols[0]
    chart_df = result.sort_values(xcol if xcol == "year_month" else measure, ascending=xcol == "year_month")
    st.altair_chart(
        charts.simple_bars(chart_df.astype({xcol: str}), xcol, measure, f"{measure_label} por {dims[0].lower()}", measure_label,
                           color=OTHER["primary"], y_format=",.0f", horizontal=xcol != "year_month"),
        width="stretch", theme=None,
    )
elif len(group_cols) > 1:
    st.info("Com mais de um agrupamento, o resultado aparece só em tabela.")

st.dataframe(pretty, hide_index=True, width="stretch")
st.download_button("Baixar CSV", pretty.to_csv(index=False).encode("utf-8"), file_name="pontua_explorar.csv", mime="text/csv")
ui.source(f"{src['table']} + dimensões (dim_month, dim_card_class, dim_product, dim_operation, dim_campaign)")
