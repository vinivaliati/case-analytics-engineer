"""Visão geral: big numbers do mês, agente e tendências."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import charts, data, ui

st.title("Pontua+ · Visão geral")

red = ui.redemptions()
months = sorted(red["year_month"].unique())

# ------------------------------------------------------------------ filtros
f1, f2, f3 = st.columns([1, 2, 1])
with f1:
    ref = st.selectbox("Mês de referência", months[::-1], index=0, key="vg_mes")
with f2:
    classes = ui.multiselect_all(
        "Nível de cartão", list(red.sort_values("card_class_rank")["card_class"].dropna().unique()), "vg_nivel",
        help="Nível atual do cliente (decisão documentada).",
    )
with f3:
    channels = ui.multiselect_all("Canal", sorted(red["sales_channel"].dropna().unique()), "vg_canal")

filtered = red[red["card_class"].isin(classes) & red["sales_channel"].isin(channels)]
shares = data.goal_shares(filtered).set_index("year_month")
baseline_months = ["2026-02", "2026-03", "2026-04"]  # meses cheios da linha de base antes do Pix

# ------------------------------------------------------------------ big numbers
row = shares.loc[ref] if ref in shares.index else None
eff = data.effective(filtered)
pix_brl = eff[(eff["year_month"] == ref) & eff["is_pix"]]["product_value_brl"].sum()
base_points = shares.loc[[m for m in baseline_months if m in shares.index], "redeemed_points"].mean()

balance = ui.table("agg_points_balance_monthly").merge(ui.table("dim_card_class"), on="card_class_key")
balance = balance.merge(ui.table("dim_month")[["month_date_key", "year_month"]], on="month_date_key")
ref_balance = balance[(balance["year_month"] == ref) & balance["card_class"].isin(classes)]["closing_balance_points"].sum()

flow = ui.table("mart_points_flow_monthly")
flow["year_month"] = pd.to_datetime(flow["month_start"]).dt.strftime("%Y-%m")
brk = flow.set_index("year_month").get("breakage_migrated_realized_pct", pd.Series(dtype=float)).get(ref)


def goal_status(value: float, goal: float) -> tuple[str, str]:
    return ("good", f"Meta ≥ {goal:.0f}% cumprida") if value >= goal else ("critical", f"Abaixo da meta de {goal:.0f}%")


if row is not None:
    delta = (row["redeemed_points"] / base_points - 1) * 100 if base_points else 0
    ui.kpi_row([
        ui.kpi("Pontos resgatados no mês", ui.br_compact(row["redeemed_points"]),
               f"{'+' if delta >= 0 else ''}{ui.br(delta, 0)}% vs média fev-abr/2026 (antes do Pix)"),
        ui.kpi("Aéreas", f"{ui.br(row.get('aereas', 0), 1)}%", "dos pontos resgatados", goal_status(row.get("aereas", 0), 50)),
        ui.kpi("Varejo", f"{ui.br(row.get('varejo', 0), 1)}%", "dos pontos resgatados", goal_status(row.get("varejo", 0), 20)),
        ui.kpi("Pix", f"{ui.br(row.get('pix', 0), 1)}%", f"R$ {ui.br_compact(pix_brl)} pagos em dinheiro no mês"),
    ])

brk_card = ""
if brk is not None and pd.notna(brk):
    level = "critical" if brk > 20 else "warning" if brk >= 18 else "good"
    brk_card = ui.kpi("Breakage do saldo migrado", f"{ui.br(brk, 1)}%", "expirados ÷ migrados (acumulado)",
                      (level, "Limite de 20%: " + ("ultrapassado" if brk > 20 else "próximo" if brk >= 18 else "ok")))
brk_new = flow.set_index("year_month")["breakage_new_program_realized_pct"].get(ref)
brk_new_card = (
    ui.kpi("Breakage do programa novo", f"{ui.br(brk_new, 1)}%", "nenhum crédito venceu ainda (validade de 24 meses)")
    if brk_new is not None and pd.notna(brk_new) else ""
)
pix = ui.table("mart_pix_reconciliation_monthly").copy()
pix["year_month"] = pd.to_datetime(pix["month_start"]).dt.strftime("%Y-%m")
pix_row = pix.set_index("year_month").loc[ref] if ref in set(pix["year_month"]) else None
pix_card = (
    ui.kpi("Custo do Pix por ponto", f"R$ {ui.br(pix_row['effective_brl_per_point'], 4)}",
           f"real; o operador reporta R$ {ui.br(pix_row['operator_brl_per_point'], 4)} (mistura bases)")
    if pix_row is not None else ui.kpi("Custo do Pix por ponto", "—", "Pix lançado em 27/05/2026")
)
ui.kpi_row([
    ui.kpi("Saldo de pontos em aberto", ui.br_compact(ref_balance), "passivo ao fim do mês"),
    brk_card,
    brk_new_card,
    pix_card,
])
ui.source("agg_redemptions_monthly, agg_points_balance_monthly, mart_points_flow_monthly, mart_pix_reconciliation_monthly. "
          "Breakage e custo do Pix não variam com os filtros de nível e canal.")

# ------------------------------------------------------------------ agente
st.divider()
st.subheader("Pergunte ao analista")
st.caption("Responde com SQL sobre os dados agregados publicados. Mostra a consulta usada. Não acessa dados de clientes.")

from agente.config import load_settings  # noqa: E402

if "chat" not in st.session_state:
    st.session_state.chat = []

examples = [
    "As metas de aéreas e varejo foram cumpridas em setembro?",
    "Quanto o Pix custa por ponto e por que o operador diz R$ 0,016?",
    "Qual é o breakage do programa?",
    "Quais clientes mais resgataram via Pix?",
]
clicked = None
for i in range(0, len(examples), 2):
    cols = st.columns(2)
    for col, q in zip(cols, examples[i : i + 2]):
        if col.button(q, width="stretch", key=f"ex_{q}"):
            clicked = q

# Container com altura fixa: o chat fica entre os big numbers e os gráficos, e não preso no rodapé.
chat_area = st.container(border=True)
with chat_area:
    chat_box = st.container(height=360 if st.session_state.chat else 90)
    with chat_box:
        if not st.session_state.chat:
            st.caption("As respostas aparecem aqui. Clique num exemplo ou escreva sua pergunta.")
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["text"])
                for sql in msg.get("sql", []):
                    with st.expander("SQL executado"):
                        st.code(sql, language="sql")
    typed = st.chat_input("Ex.: qual foi o % de varejo por nível de cartão em agosto?")

prompt = typed or clicked
if prompt:
    settings = load_settings()
    history = [(m["role"], m["text"]) for m in st.session_state.chat]
    st.session_state.chat.append({"role": "user", "text": prompt})
    with chat_box:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            if not settings.is_configured:
                from agente.config import secrets_diagnostic  # noqa: E402

                found = secrets_diagnostic()
                text = (
                    "O agente não está configurado: a chave `GEMINI_API_KEY` não foi encontrada.\n\n"
                    f"Nomes encontrados nos secrets: {', '.join(f'`{n}`' for n in found) if found else 'nenhum'}.\n\n"
                    "No Streamlit Cloud: *Manage app › Settings › Secrets*, cole `GEMINI_API_KEY = \"sua_chave\"` "
                    "(com aspas), salve e reinicie o app (*Reboot app*)."
                )
                sqls = []
                st.warning(text)
            else:
                from agente.agent import ask

                with st.spinner("Consultando os dados..."):
                    answer = ask(prompt, history)
                text, sqls = answer.text, [q.sql for q in answer.queries]
                st.markdown(text)
                for sql in sqls:
                    with st.expander("SQL executado"):
                        st.code(sql, language="sql")
    st.session_state.chat.append({"role": "assistant", "text": text, "sql": sqls})
    st.rerun()

# ------------------------------------------------------------------ tendências
st.divider()
c1, c2 = st.columns(2)
labels = data.MODALITY_LABELS
with c1:
    st.altair_chart(
        charts.share_lines(shares.reset_index(), ["aereas", "varejo", "pix"], labels, data.GOALS,
                           "Participação nos pontos resgatados (visão contrato)",
                           events={"2026-01": "pico 12/01", "2026-05": "Pix"}),
        width="stretch", theme=None,
    )
    ui.source("agg_redemptions_monthly + dim_product (goal_category_contract)")
with c2:
    pts = data.monthly_points_by_modality(filtered)
    st.altair_chart(
        charts.stacked_bars(pts, "net_redeemed_points", "goal_category_strict", labels,
                            "Pontos resgatados por modalidade: o Pix somou volume", "Pontos"),
        width="stretch", theme=None,
    )
    ui.source("agg_redemptions_monthly (resgates efetivos, líquidos de devoluções)")
