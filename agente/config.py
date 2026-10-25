"""Configuração do agente: lê credenciais do ambiente, do .env local ou dos secrets do Streamlit.

A chave nunca é enviada ao navegador: só este módulo (lado servidor) a lê.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA_DIR = REPO / "entrega" / "dashboard" / "data"
DEFAULT_MODEL = "gemini-3.8-flash"
# Reservas, em ordem, quando o principal está sem cota (429) ou indisponível (503).
# Cada modelo tem cota própria no plano gratuito (ex.: 20 requisições/dia por modelo).
# Não usar "gemini-flash-latest": é um apelido do mesmo modelo principal e divide a cota com ele.
DEFAULT_FALLBACK_MODEL = "gemini-3.6-flash,gemini-3.5-flash,gemini-3.5-flash-lite,gemini-3.1-flash-lite"


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO / ".env", override=False)


def _secrets() -> dict:
    """Secrets do Streamlit como dict comum ({} fora do Streamlit ou sem secrets)."""
    try:
        import streamlit as st

        return {k: (dict(v) if hasattr(v, "keys") else v) for k, v in st.secrets.items()}
    except Exception:
        return {}


def _from_streamlit_secrets(key: str) -> str | None:
    """Procura a chave no topo dos secrets e também dentro de seções (ex.: [gemini]), sem diferenciar
    maiúsculas. Assim GEMINI_API_KEY, gemini_api_key ou [gemini] GEMINI_API_KEY funcionam."""
    secrets = _secrets()
    wanted = key.lower()
    for k, v in secrets.items():
        if k.lower() == wanted and not isinstance(v, dict):
            return str(v).strip()
    for v in secrets.values():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if k2.lower() == wanted:
                    return str(v2).strip()
    return None


def secrets_diagnostic() -> list[str]:
    """Só os NOMES encontrados nos secrets (nunca os valores), para mostrar quando a chave não é achada."""
    names = []
    for k, v in _secrets().items():
        names += [f"[{k}] {k2}" for k2 in v] if isinstance(v, dict) else [k]
    return names


def _get(key: str, default: str | None = None) -> str | None:
    value = os.environ.get(key) or _from_streamlit_secrets(key)
    return value if value not in (None, "") else default


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str
    use_vertexai: bool
    project: str | None
    location: str | None
    fallback_model: str | None = None

    @property
    def is_configured(self) -> bool:
        return (self.use_vertexai and bool(self.project)) or bool(self.api_key)


def load_settings() -> Settings:
    _load_dotenv()
    return Settings(
        api_key=_get("GEMINI_API_KEY"),
        model=_get("GEMINI_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL,
        use_vertexai=(_get("GOOGLE_GENAI_USE_VERTEXAI", "false") or "false").lower() == "true",
        project=_get("GOOGLE_CLOUD_PROJECT"),
        location=_get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        fallback_model=_get("GEMINI_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL),
    )
