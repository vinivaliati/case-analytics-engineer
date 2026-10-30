"""Testes do agente sem chamar o Gemini: guarda-corpos do SQL, prompt e laço de ferramentas (modelo simulado).

    python -m pytest agente/tests -q
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from google.genai import types

from agente.agent import AnalystAgent
from agente.config import Settings
from agente.prompt import build_system_prompt
from agente.config import DATA_DIR
from agente.sql_tool import SqlTool


@pytest.fixture(scope="module")
def tool() -> SqlTool:
    return SqlTool()


def test_carrega_todas_as_tabelas_publicadas(tool):
    assert "mart_goal_attainment_monthly" in tool.tables
    assert "dim_customer" not in tool.tables  # dado por cliente não é publicado
    assert len(tool.tables) == len(list(DATA_DIR.glob("*.parquet")))
    assert "mart_data_profile" in tool.tables


@pytest.mark.parametrize(
    "sql",
    [
        "drop table dim_month",
        "insert into dim_month select * from dim_month",
        "select 1; select 2",
        "copy dim_month to 'saida.csv'",
        "set enable_external_access = true",
        "attach 'outro.duckdb'",
    ],
)
def test_bloqueia_o_que_nao_e_select(tool, sql):
    assert not tool.run(sql).ok


def test_bloqueia_leitura_dos_csvs_linha_a_linha(tool):
    result = tool.run("select * from read_csv('contexto/dados/cards.csv') limit 1")
    assert not result.ok


def test_limita_linhas_devolvidas(tool):
    result = tool.run("select * from range(1000)")
    assert result.ok and result.truncated and len(result.rows) == 200


def test_numero_chave_bate_com_o_mart(tool):
    result = tool.run("select effective_brl_per_point from mart_pix_reconciliation_monthly")
    assert all(abs(row[0] - 0.019) < 0.00005 for row in result.rows)


def test_prompt_traz_regras_e_todas_as_tabelas():
    prompt = build_system_prompt()
    assert "net_redeemed_points" in prompt and "NÃO é breakage" in prompt
    for name in ("agg_redemptions_monthly", "mart_points_flow_monthly", "dim_product"):
        assert name in prompt


class FakeModels:
    """Primeiro pede um SQL; depois responde em texto usando o resultado."""

    def __init__(self) -> None:
        self.calls = 0

    def generate_content(self, model, contents, config):
        self.calls += 1
        if self.calls == 1:
            call = types.FunctionCall(
                name="run_sql",
                args={"query": "select aereas_pct from mart_goal_attainment_monthly where month_start = '2026-09-01'"},
            )
            content = types.Content(role="model", parts=[types.Part(function_call=call)])
            return SimpleNamespace(function_calls=[call], candidates=[SimpleNamespace(content=content)], text=None)
        tool_response = contents[-1].parts[0].function_response.response
        value = tool_response["rows"][0][0]
        return SimpleNamespace(function_calls=None, candidates=[], text=f"Aéreas em set/2026: {value}%")


def test_laco_executa_sql_e_responde_com_o_resultado():
    agent = AnalystAgent(Settings(api_key="fake", model="fake", use_vertexai=False, project=None, location=None))
    agent._client = SimpleNamespace(models=FakeModels())
    answer = agent.ask("Qual o % de aéreas em setembro?")
    assert answer.error is None
    assert len(answer.queries) == 1 and answer.queries[0].ok
    assert "59.09" in answer.text


def test_sem_chave_responde_que_nao_esta_configurado():
    agent = AnalystAgent(Settings(api_key=None, model="x", use_vertexai=False, project=None, location=None))
    assert agent.ask("oi").error == "not_configured"


class BusyThenOkModels:
    """O modelo principal responde 503; o de reserva responde normalmente."""

    def __init__(self) -> None:
        self.models_called: list[str] = []

    def generate_content(self, model, contents, config):
        from google.genai import errors

        self.models_called.append(model)
        if model == "principal":
            raise errors.ServerError(503, {"error": {"code": 503, "message": "high demand", "status": "UNAVAILABLE"}})
        return SimpleNamespace(function_calls=None, candidates=[], text="ok")


def test_usa_modelo_de_reserva_quando_o_principal_esta_indisponivel(monkeypatch):
    import agente.agent as agent_module

    monkeypatch.setattr(agent_module, "BACKOFF_SECONDS", 0)
    agent = AnalystAgent(Settings(api_key="fake", model="principal", use_vertexai=False, project=None, location=None, fallback_model="reserva"))
    fake = BusyThenOkModels()
    agent._client = SimpleNamespace(models=fake)
    answer = agent.ask("oi")
    assert answer.text == "ok" and answer.model == "reserva"
    assert fake.models_called == ["principal"] * agent_module.RETRIES + ["reserva"]
