"""O dashboard sem filtro precisa mostrar exatamente os números oficiais dos marts do dbt.

    python -m pytest entrega/dashboard/tests -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import data  # noqa: E402


@pytest.fixture(scope="module")
def redemptions() -> pd.DataFrame:
    return data.redemptions()


@pytest.fixture(scope="module")
def mart() -> pd.DataFrame:
    df = data.read("mart_goal_attainment_monthly")
    df["year_month"] = pd.to_datetime(df["month_start"]).dt.strftime("%Y-%m")
    return df.set_index("year_month")


def test_participacao_contrato_bate_com_o_mart(redemptions, mart):
    shares = data.goal_shares(redemptions).set_index("year_month")
    for col in ("aereas", "varejo", "pix"):
        diff = (shares[col].round(2) - mart[f"{col}_pct"]).abs().max()
        assert diff <= 0.01, col


def test_visao_estrita_bate_com_o_mart(redemptions, mart):
    shares = data.goal_shares(redemptions, "goal_category_strict").set_index("year_month")
    assert (shares["varejo"].round(2) - mart["varejo_strict_pct"]).abs().max() <= 0.01


def test_visao_sem_pix_bate_com_o_mart(redemptions, mart):
    shares = data.goal_shares(redemptions, exclude_pix=True).set_index("year_month")
    assert (shares["aereas"].round(2) - mart["aereas_pct_ex_pix"]).abs().max() <= 0.01


def test_total_de_pontos_bate_com_o_mart(redemptions, mart):
    shares = data.goal_shares(redemptions).set_index("year_month")
    assert (shares["redeemed_points"] - mart["redeemed_points"]).abs().max() == 0


def test_nenhuma_tabela_publicada_tem_dado_de_cliente():
    for path in data.DATA_DIR.glob("*.parquet"):
        cols = set(pd.read_parquet(path).columns)
        assert not cols & {"user_id", "account_id", "customer_key", "account_key", "order_id", "order_item_id"}, path.name
