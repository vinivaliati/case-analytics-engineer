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


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO / ".env", override=False)


def _from_streamlit_secrets(key: str) -> str | None:
    try:
        import streamlit as st

        return st.secrets.get(key)  # type: ignore[no-any-return]
    except Exception:
        return None


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

    @property
    def is_configured(self) -> bool:
        return self.use_vertexai and bool(self.project) or bool(self.api_key)


def load_settings() -> Settings:
    _load_dotenv()
    return Settings(
        api_key=_get("GEMINI_API_KEY"),
        model=_get("GEMINI_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL,
        use_vertexai=(_get("GOOGLE_GENAI_USE_VERTEXAI", "false") or "false").lower() == "true",
        project=_get("GOOGLE_CLOUD_PROJECT"),
        location=_get("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )
