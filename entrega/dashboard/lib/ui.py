"""Componentes de interface: carregamento em cache, filtros, cartões de KPI e rodapé de fonte."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from . import data
from .theme import STATUS


@st.cache_data(show_spinner=False)
def table(name: str) -> pd.DataFrame:
    return data.read(name)


@st.cache_data(show_spinner=False)
def redemptions() -> pd.DataFrame:
    return data.redemptions()


def br(value: float, decimals: int = 0) -> str:
    """Número no padrão brasileiro."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def br_compact(value: float) -> str:
    if abs(value) >= 1e6:
        return f"{br(value / 1e6, 1)} mi"
    if abs(value) >= 1e3:
        return f"{br(value / 1e3, 1)} mil"
    return br(value)


def month_range(months: list[str], key: str, default_start: str | None = None) -> tuple[str, str]:
    start = default_start if default_start in months else months[0]
    return st.select_slider("Período", options=months, value=(start, months[-1]), key=key)


def multiselect_all(label: str, options: list[str], key: str, help: str | None = None) -> list[str]:
    chosen = st.multiselect(label, options, placeholder="Todos", key=key, help=help)
    return chosen or options


def kpi(label: str, value: str, sub: str = "", status: tuple[str, str] | None = None) -> str:
    """HTML de um cartão de KPI. status = (nível, texto), nível em good/warning/critical; sempre com ícone + texto.
    Não desenha sozinho: passe uma lista de cartões para kpi_row()."""
    status_html = ""
    if status:
        level, text = status
        icon = {"good": "✓", "warning": "!", "critical": "✕"}[level]
        status_html = (
            f'<div class="status"><span class="dot" style="background:{STATUS[level]}"></span>{icon} {text}</div>'
        )
    return (
        f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div>'
        f'<div class="sub">{sub}</div>{status_html}</div>'
    )


def kpi_row(cards: list[str]) -> None:
    """Uma linha de big numbers num único grid: todos com a mesma altura, quebra de linha automática
    em telas estreitas e nada sobrepõe o que vem abaixo."""
    cards = [c for c in cards if c]
    st.markdown(f'<div class="kpi-row" style="--n:{len(cards)}">{"".join(cards)}</div>', unsafe_allow_html=True)


def source(text: str) -> None:
    st.markdown(f'<div class="source">Fonte: {text}</div>', unsafe_allow_html=True)


def show_table(df: pd.DataFrame, label: str = "Ver tabela") -> None:
    with st.expander(label):
        st.dataframe(df, hide_index=True, width="stretch")
