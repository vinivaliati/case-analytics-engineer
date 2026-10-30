"""Dashboard Pontua+ (Streamlit).

    streamlit run entrega/dashboard/app.py

Lê só os Parquets agregados em entrega/dashboard/data/ (gerados por entrega/scripts/build.py).
O agente (pasta agente/ na raiz) roda no servidor; a chave do Gemini nunca vai para o navegador.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))  # raiz do repo, para importar agente/

from lib.theme import css  # noqa: E402

st.set_page_config(page_title="Pontua+ · Diretoria", page_icon="📊", layout="wide")
st.markdown(css(), unsafe_allow_html=True)

pages = [
    st.Page(HERE / "views" / "visao_geral.py", title="Visão geral", icon="🏠", default=True),
    st.Page(HERE / "views" / "metas_pix.py", title="Metas e Pix", icon="🎯"),
    st.Page(HERE / "views" / "breakage_crm.py", title="Breakage e CRM", icon="⏳"),
    st.Page(HERE / "views" / "explorar.py", title="Explorar", icon="🔎"),
]
st.navigation(pages).run()

st.sidebar.caption(
    "Dados fictícios do case, extraídos em 01/10/2026. Só dados agregados. "
    "Regras e definições: entrega/docs/ e data_dictionary.json."
)
