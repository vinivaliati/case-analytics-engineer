"""Camada de dados do dashboard: lê só os Parquets agregados publicados pelo build.

As funções de cálculo (ex.: participação nas metas) são puras e testadas contra os marts,
para garantir que o número do dashboard sem filtro = número oficial do dbt.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

VIEWS = {
    "Contrato (oficial)": "goal_category_contract",
    "Estrita (varejo só produto)": "goal_category_strict",
}
MODALITY_LABELS = {
    "aereas": "Aéreas",
    "varejo": "Varejo",
    "pix": "Pix",
    "agencia_viagens": "Agência de viagens",
    "transferencia_parceiro": "Transferência a parceiro",
}
GOALS = {"aereas": 50.0, "varejo": 20.0}
PIX_LAUNCH_MONTH = "2026-05"


def read(name: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    df = pd.read_parquet(data_dir / f"{name}.parquet")
    # Colunas DECIMAL (R$, %) chegam como objetos Decimal; float simplifica as contas do dashboard.
    for col in df.columns:
        if df[col].dtype == object and isinstance(df[col].dropna().iloc[0] if df[col].notna().any() else None, Decimal):
            df[col] = df[col].astype(float)
    return df


def dictionary(data_dir: Path = DATA_DIR) -> dict:
    return json.loads((data_dir / "data_dictionary.json").read_text(encoding="utf-8"))


def redemptions(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """agg_redemptions_monthly desnormalizado com produto, nível e mês (ainda agregado)."""
    fact = read("agg_redemptions_monthly", data_dir)
    product = read("dim_product", data_dir)
    card = read("dim_card_class", data_dir)
    month = read("dim_month", data_dir)
    df = (
        fact.merge(product, on="product_key", how="left")
        .merge(card, on="card_class_key", how="left")
        .merge(month[["month_date_key", "year_month", "month_start", "pix_phase"]], on="month_date_key", how="left")
    )
    return df


def effective(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["is_effective_redemption"] & df["is_redemption"]]


def goal_shares(df: pd.DataFrame, view_col: str = "goal_category_contract", exclude_pix: bool = False) -> pd.DataFrame:
    """% de cada categoria nos pontos resgatados por mês. Mesma regra do mart_goal_attainment_monthly."""
    base = effective(df)
    if exclude_pix:
        base = base[base["goal_category_contract"] != "pix"]
    pivot = base.pivot_table(index="year_month", columns=view_col, values="net_redeemed_points", aggfunc="sum", fill_value=0)
    total = pivot.sum(axis=1)
    shares = pivot.div(total.where(total != 0), axis=0) * 100
    shares["redeemed_points"] = total
    return shares.reset_index()


def monthly_points_by_modality(df: pd.DataFrame) -> pd.DataFrame:
    base = effective(df)
    out = base.groupby(["year_month", "goal_category_strict"], as_index=False)["net_redeemed_points"].sum()
    out["modalidade"] = out["goal_category_strict"].map(MODALITY_LABELS)
    return out
