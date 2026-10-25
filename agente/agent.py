"""Agente analista: Gemini + uma ferramenta (run_sql) sobre os dados agregados publicados.

Ponto de entrada único: ask(pergunta, historico) -> Answer.
Usado pelo dashboard (Streamlit) e pela linha de comando (python -m agente "pergunta").

O laço de chamada de ferramenta é manual (não usa a chamada automática do SDK), para ter
controle do número de passos, registrar cada SQL executado e não depender de mudanças do SDK.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from google import genai
from google.genai import types

from .config import Settings, load_settings
from .prompt import build_system_prompt
from .sql_tool import QueryResult, SqlTool

MAX_TOOL_STEPS = 6

RUN_SQL = types.FunctionDeclaration(
    name="run_sql",
    description=(
        "Executa UMA consulta SQL (dialeto DuckDB) somente leitura sobre as tabelas publicadas do Pontua+ "
        "e devolve colunas e linhas (máx. 200). Use os nomes de tabela e coluna do dicionário."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Um único comando SELECT (ou WITH ... SELECT)."},
            "purpose": {"type": "string", "description": "Em uma frase: o que esta consulta responde."},
        },
        "required": ["query"],
    },
)


@dataclass
class Answer:
    text: str
    queries: list[QueryResult] = field(default_factory=list)
    model: str = ""
    error: str | None = None


class AnalystAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        self.sql = SqlTool()
        self.system_prompt = build_system_prompt()
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            s = self.settings
            if s.use_vertexai:
                self._client = genai.Client(vertexai=True, project=s.project, location=s.location)
            else:
                self._client = genai.Client(api_key=s.api_key)
        return self._client

    def _config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            tools=[types.Tool(function_declarations=[RUN_SQL])],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=0.1,
        )

    def ask(self, question: str, history: list[tuple[str, str]] | None = None) -> Answer:
        if not self.settings.is_configured:
            return Answer(
                text="O agente não está configurado: defina GEMINI_API_KEY no .env (local) ou nos secrets (produção).",
                error="not_configured",
            )

        contents: list[types.Content] = []
        for role, text in (history or [])[-6:]:
            contents.append(types.Content(role="user" if role == "user" else "model", parts=[types.Part(text=text)]))
        contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

        queries: list[QueryResult] = []
        try:
            for _ in range(MAX_TOOL_STEPS + 1):
                response = self.client.models.generate_content(
                    model=self.settings.model, contents=contents, config=self._config()
                )
                calls = response.function_calls or []
                if not calls:
                    return Answer(text=(response.text or "").strip(), queries=queries, model=self.settings.model)

                contents.append(response.candidates[0].content)
                parts = []
                for call in calls:
                    args = dict(call.args or {})
                    result = self.sql.run(str(args.get("query", "")))
                    queries.append(result)
                    parts.append(types.Part.from_function_response(name=call.name, response=result.for_model()))
                contents.append(types.Content(role="user", parts=parts))

            return Answer(
                text="Não consegui concluir a análise dentro do limite de consultas. Tente uma pergunta mais específica.",
                queries=queries,
                model=self.settings.model,
                error="max_steps",
            )
        except Exception as exc:  # erros de rede, cota ou chave inválida
            return Answer(
                text=f"Não foi possível consultar o modelo ({type(exc).__name__}). Verifique a chave e a cota do Gemini.",
                queries=queries,
                model=self.settings.model,
                error=str(exc),
            )


_agent: AnalystAgent | None = None


def ask(question: str, history: list[tuple[str, str]] | None = None) -> Answer:
    global _agent
    if _agent is None:
        _agent = AnalystAgent()
    return _agent.ask(question, history)
