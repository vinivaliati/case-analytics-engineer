"""Tema visual do dashboard (modo escuro).

Cores: paleta de referência validada da skill de dataviz (passos do modo escuro), sem alteração.
- Slots 1-3 (aéreas, varejo, Pix) validados em todos os pares; slots 4-5 só em gráficos de pares adjacentes.
- A cor segue a entidade: aéreas é sempre azul, varejo sempre laranja, Pix sempre verde-água, em qualquer filtro.
- Status (meta cumprida / abaixo) tem cores próprias e sempre vem com ícone + texto.
"""

from __future__ import annotations

import altair as alt

SURFACE = "#1a1a19"
PAGE = "#0d0d0d"
INK = "#f0efec"
INK_2 = "#c3c2b7"
MUTED = "#898781"
GRID = "#2c2c2a"
BASELINE = "#383835"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

SERIES = {
    "aereas": "#3987e5",
    "varejo": "#d95926",
    "pix": "#199e70",
    "agencia_viagens": "#c98500",
    "transferencia_parceiro": "#d55181",
}
SERIES_ORDER = ["aereas", "varejo", "pix", "agencia_viagens", "transferencia_parceiro"]
# Séries que NÃO são modalidade (saldo, breakage, volume de CRM) usam slots livres da paleta (7 e 6),
# para não confundir com as cores das modalidades.
OTHER = {"primary": "#9085e9", "secondary": "#008300"}
STATUS = {"good": "#0ca30c", "warning": "#fab219", "critical": "#d03b3b"}
NEUTRAL = MUTED


@alt.theme.register("pontua_dark", enable=True)
def _pontua_dark() -> alt.theme.ThemeConfig:
    return {
        "config": {
            "background": SURFACE,
            "view": {"stroke": None},
            "font": FONT,
            "title": {"color": INK, "fontSize": 15, "fontWeight": 600, "anchor": "start", "offset": 12},
            "axis": {
                "labelColor": MUTED,
                "titleColor": INK_2,
                "gridColor": GRID,
                "domainColor": BASELINE,
                "tickColor": BASELINE,
                "labelFontSize": 12,
                "titleFontSize": 12,
                "titleFontWeight": 400,
            },
            "axisX": {"grid": False},
            "legend": {"labelColor": INK_2, "titleColor": INK_2, "orient": "top", "labelFontSize": 12},
            "line": {"strokeWidth": 2},
            "point": {"size": 64},
        }
    }


def css() -> str:
    return f"""
    <style>
      /* Cards de big number com tamanho padrão: mesma altura mínima para todos, conteúdo empilhado
         e o status sempre no rodapé do card. A altura cresce se o texto precisar, sem invadir o que vem abaixo. */
      /* Linha de big numbers = um grid: as células de uma linha têm sempre a mesma altura (a do card mais alto),
         e em telas estreitas os cards descem para a linha de baixo em vez de espremer o texto. */
      .kpi-row {{ display:grid; grid-template-columns:repeat(var(--n), minmax(0, 1fr)); gap:16px;
                  align-items:stretch; margin:0 0 16px 0; }}
      @media (max-width: 1100px) {{ .kpi-row {{ grid-template-columns:repeat(2, minmax(0, 1fr)); }} }}
      @media (max-width: 640px) {{ .kpi-row {{ grid-template-columns:1fr; }} }}
      .kpi {{ background:{SURFACE}; border:1px solid rgba(255,255,255,0.10); border-radius:10px; padding:14px 16px;
              box-sizing:border-box; min-height:200px; height:100%;
              display:flex; flex-direction:column; overflow-wrap:anywhere; }}
      .kpi .label {{ color:{INK_2}; font-size:0.85rem; line-height:1.3; }}
      .kpi .value {{ color:{INK}; font-size:1.9rem; font-weight:600; line-height:1.2; margin-top:4px; }}
      .kpi .sub {{ color:{MUTED}; font-size:0.8rem; line-height:1.35; margin-top:4px; }}
      .kpi .status {{ font-size:0.8rem; line-height:1.35; margin-top:auto; padding-top:8px; color:{INK_2}; }}
      .kpi .dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; vertical-align:middle; }}
      .source {{ color:{MUTED}; font-size:0.78rem; margin-top:4px; margin-bottom:8px; }}
    </style>
    """
