"""Agente analista: Gemini + uma ferramenta (run_sql) sobre os dados agregados publicados.

Ponto de entrada único: ask(pergunta, historico) -> Answer.
Usado pelo dashboard (Streamlit) e pela linha de comando (python -m agente "pergunta").

O laço de chamada de ferramenta é manual (não usa a chamada automática do SDK), para ter
controle do número de passos, registrar cada SQL executado e não depender de mudanças do SDK.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from .config import Settings, load_settings
from .prompt import build_system_prompt
from .sql_tool import QueryResult, SqlTool

MAX_TOOL_STEPS = 6
# Erros temporários do Gemini (cota por minuto e alta demanda): tenta de novo e depois usa o modelo de reserva.
TRANSIENT_CODES = {408, 429, 500, 503, 504}
RETRIES = 2
BACKOFF_SECONDS = 2.0
REQUEST_TIMEOUT_MS = 45_000

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
        self._exhausted: set[str] = set()  # modelos que devolveram 429 (cota) nesta sessão

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            s = self.settings
            # Timeout por chamada e sem tentativas internas do SDK: as tentativas e a troca para o
            # modelo de reserva ficam em _generate, para o usuário não esperar minutos sob alta demanda.
            http = types.HttpOptions(timeout=REQUEST_TIMEOUT_MS, retry_options=types.HttpRetryOptions(attempts=1))
            if s.use_vertexai:
                self._client = genai.Client(vertexai=True, project=s.project, location=s.location, http_options=http)
            else:
                self._client = genai.Client(api_key=s.api_key, http_options=http)
        return self._client

    def _config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            tools=[types.Tool(function_declarations=[RUN_SQL])],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=0.1,
        )

    def _generate(self, contents: list[types.Content], used: dict) -> types.GenerateContentResponse:
        """Chama o modelo com novas tentativas para erros temporários (429/503) e cai para o modelo
        de reserva se o principal continuar indisponível. used['model'] registra quem respondeu."""
        fallbacks = [m.strip() for m in (self.settings.fallback_model or "").split(",") if m.strip()]
        models = [m for m in dict.fromkeys([self.settings.model, *fallbacks]) if m not in self._exhausted]
        last_exc: Exception | None = None
        for model in models:
            for attempt in range(RETRIES):
                try:
                    response = self.client.models.generate_content(model=model, contents=contents, config=self._config())
                    used["model"] = model
                    return response
                except genai_errors.APIError as exc:
                    code = getattr(exc, "code", None)
                    if code not in TRANSIENT_CODES:
                        raise
                    last_exc = exc
                    if code == 429:
                        # Cota esgotada: insistir no mesmo modelo só gasta tempo. Marca e vai para o próximo.
                        self._exhausted.add(model)
                        break
                except httpx.TransportError as exc:  # timeout ou queda de conexão
                    last_exc = exc
                time.sleep(BACKOFF_SECONDS * (2**attempt))
        if last_exc is None:
            raise RuntimeError("Todos os modelos configurados estão sem cota nesta sessão.")
        raise last_exc

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
        used = {"model": self.settings.model}
        try:
            for _ in range(MAX_TOOL_STEPS + 1):
                response = self._generate(contents, used)
                calls = response.function_calls or []
                if not calls:
                    return Answer(text=(response.text or "").strip(), queries=queries, model=used["model"])

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
            code = getattr(exc, "code", None)
            busy = code in TRANSIENT_CODES or isinstance(exc, httpx.TransportError) or isinstance(exc, RuntimeError)
            return Answer(
                text=(
                    "A cota do Gemini acabou para os modelos configurados. Tente mais tarde ou use outra chave."
                    if code == 429 or isinstance(exc, RuntimeError)
                    else "O Gemini está com alta demanda agora. Tente de novo em instantes."
                    if busy
                    else f"Não foi possível consultar o modelo ({type(exc).__name__}). Verifique a chave e a cota do Gemini."
                ),
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
