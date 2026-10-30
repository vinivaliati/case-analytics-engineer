"""Gráficos (Altair) seguindo as regras da skill de dataviz: um eixo, linhas de 2px, barras finas com
cantos de 4px no topo, separação de 2px entre segmentos, tooltip em toda marca, legenda para >= 2 séries
e cor fixa por entidade."""

from __future__ import annotations

import altair as alt
import pandas as pd

from .theme import BASELINE, INK_2, MUTED, SERIES, SERIES_ORDER, SURFACE

PT_NUMBER = ",.0f"
# Eixo de meses curto ("out/25") para não sobrepor rótulos.
MONTH_AXIS = alt.Axis(
    labelAngle=0,
    labelExpr="['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'][toNumber(slice(datum.value, 5, 7)) - 1] + '/' + slice(datum.value, 2, 4)",
)


def _color(labels: dict[str, str], present: list[str]) -> alt.Color:
    domain = [labels.get(k, k) for k in SERIES_ORDER if k in present]
    rng = [SERIES[k] for k in SERIES_ORDER if k in present]
    return alt.Color("serie:N", title=None, scale=alt.Scale(domain=domain, range=rng), sort=domain)


def share_lines(
    shares: pd.DataFrame,
    series: list[str],
    labels: dict[str, str],
    goals: dict[str, float] | None = None,
    title: str = "",
    events: dict[str, str] | None = None,
) -> alt.Chart:
    """% por mês (eixo único 0-100) com linhas de meta e marcações de eventos."""
    present = [s for s in series if s in shares.columns]
    long = shares.melt(id_vars="year_month", value_vars=present, var_name="key", value_name="pct")
    long["serie"] = long["key"].map(lambda k: labels.get(k, k))
    color = _color(labels, present)
    hover = alt.selection_point(fields=["year_month"], nearest=True, on="pointerover", empty=False)

    x = alt.X("year_month:O", title=None, axis=MONTH_AXIS)
    base = alt.Chart(long).encode(x=x)
    lines = base.mark_line(strokeWidth=2).encode(
        y=alt.Y("pct:Q", title="% dos pontos resgatados", scale=alt.Scale(domain=[0, 100])), color=color
    )
    points = base.mark_point(filled=True, size=70, stroke=SURFACE, strokeWidth=2).encode(
        y="pct:Q", color=color, opacity=alt.condition(hover, alt.value(1), alt.value(0))
    )
    rule = (
        alt.Chart(long)
        .mark_rule(color=BASELINE)
        .encode(
            x=x,
            opacity=alt.condition(hover, alt.value(1), alt.value(0)),
            tooltip=[alt.Tooltip("year_month:O", title="Mês")]
            + [alt.Tooltip(f"{labels.get(s, s)}:Q", format=".1f") for s in present],
        )
        .transform_pivot("serie", value="pct", groupby=["year_month"])
        .add_params(hover)
    )
    layers = [lines, points, rule]

    for key, value in (goals or {}).items():
        if key not in present:
            continue
        last_month = shares["year_month"].max()
        goal_df = pd.DataFrame({"y": [value], "year_month": [last_month], "label": [f"Meta {labels.get(key, key).lower()} ≥ {value:.0f}%"]})
        layers.append(alt.Chart(goal_df).mark_rule(strokeDash=[4, 4], color=SERIES[key], opacity=0.8).encode(y="y:Q"))
        # Rótulo da meta na ponta direita, acima da linha tracejada, longe do início das séries.
        layers.append(
            alt.Chart(goal_df)
            .mark_text(align="right", dx=8, dy=-8, color=INK_2, fontSize=11)
            .encode(y="y:Q", x="year_month:O", text="label:N")
        )
    layers += _event_marks(events, shares["year_month"].tolist())
    return alt.layer(*layers).properties(title=title, height=320)


def _event_marks(events: dict[str, str] | None, months: list[str]) -> list[alt.Chart]:
    marks = []
    for month, label in (events or {}).items():
        if month not in months:
            continue
        df = pd.DataFrame({"year_month": [month], "label": [label]})
        marks.append(alt.Chart(df).mark_rule(color=MUTED, strokeDash=[2, 3]).encode(x="year_month:O"))
        marks.append(
            alt.Chart(df)
            .mark_text(align="left", dx=4, y=8, color=MUTED, fontSize=11)
            .encode(x="year_month:O", text="label:N")
        )
    return marks


def stacked_bars(
    df: pd.DataFrame,
    value: str,
    key: str,
    labels: dict[str, str],
    title: str,
    y_title: str,
    colors: dict[str, str] | None = None,
) -> alt.Chart:
    """Barras empilhadas por mês, com 2px de separação entre segmentos e tooltip por segmento.
    colors: cores próprias por chave (ex.: neutro para 'não pago'); padrão = cor fixa da modalidade."""
    df = df.copy()
    if colors:
        present = [k for k in colors if k in df[key].unique()]
        color = alt.Color(
            "serie:N", title=None,
            scale=alt.Scale(domain=[labels[k] for k in present], range=[colors[k] for k in present]),
        )
    else:
        present = [k for k in SERIES_ORDER if k in df[key].unique()]
        color = _color(labels, present)
    df["serie"] = df[key].map(lambda k: labels.get(k, k))
    df["ordem"] = df[key].map({k: i for i, k in enumerate(present)})
    return (
        alt.Chart(df)
        .mark_bar(stroke=SURFACE, strokeWidth=2, cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=22)
        .encode(
            x=alt.X("year_month:O", title=None, axis=MONTH_AXIS),
            y=alt.Y(f"{value}:Q", title=y_title, axis=alt.Axis(format="~s")),
            color=color,
            order=alt.Order("ordem:Q"),
            tooltip=[
                alt.Tooltip("year_month:O", title="Mês"),
                alt.Tooltip("serie:N", title="Modalidade"),
                alt.Tooltip(f"{value}:Q", title=y_title, format=PT_NUMBER),
            ],
        )
        .properties(title=title, height=320)
    )


def simple_bars(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    y_title: str,
    color: str = SERIES["aereas"],
    y_format: str = ",.1f",
    horizontal: bool = False,
    reference: float | None = None,
    reference_label: str | None = None,
) -> alt.Chart:
    """Uma série: uma cor só (sem rampa em categorias nominais). A ordem das barras é a ordem das linhas do df."""
    order = list(df[x].astype(str))
    value_axis = alt.Axis(format="~s") if y_format.endswith(".0f") else alt.Axis()
    if horizontal:
        enc = {
            "y": alt.Y(f"{x}:N", title=None, sort=order, axis=alt.Axis(labelLimit=320)),
            "x": alt.X(f"{y}:Q", title=y_title, axis=value_axis),
        }
        mark = alt.Chart(df).mark_bar(color=color, cornerRadiusTopRight=4, cornerRadiusBottomRight=4, size=18)
    else:
        enc = {
            "x": alt.X(f"{x}:O", title=None, sort=order, axis=MONTH_AXIS if x == "year_month" else alt.Axis(labelAngle=0)),
            "y": alt.Y(f"{y}:Q", title=y_title, axis=value_axis),
        }
        mark = alt.Chart(df).mark_bar(color=color, cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=22)
    chart = mark.encode(**enc, tooltip=[alt.Tooltip(f"{x}:N", title=" "), alt.Tooltip(f"{y}:Q", title=y_title, format=y_format)])
    layers = [chart]
    if reference is not None:
        ref = pd.DataFrame({"v": [reference], "label": [reference_label or ""]})
        axis = "x" if horizontal else "y"
        layers.append(alt.Chart(ref).mark_rule(color=MUTED, strokeDash=[4, 4]).encode(**{axis: "v:Q"}))
    return alt.layer(*layers).properties(title=title, height=300 if not horizontal else max(160, 40 * len(df)))


def lines(df: pd.DataFrame, value: str, key: str, labels: dict[str, str], colors: dict[str, str], title: str, y_title: str, y_format: str = ",.1f") -> alt.Chart:
    """Várias séries da MESMA unidade num eixo só."""
    df = df.copy()
    df["serie"] = df[key].map(lambda k: labels.get(k, k))
    domain = [labels[k] for k in colors]
    color = alt.Color("serie:N", title=None, scale=alt.Scale(domain=domain, range=list(colors.values())))
    hover = alt.selection_point(fields=["year_month"], nearest=True, on="pointerover", empty=False)
    base = alt.Chart(df).encode(x=alt.X("year_month:O", title=None, axis=MONTH_AXIS))
    line = base.mark_line(strokeWidth=2).encode(y=alt.Y(f"{value}:Q", title=y_title), color=color)
    pts = base.mark_point(filled=True, size=70, stroke=SURFACE, strokeWidth=2).encode(
        y=f"{value}:Q",
        color=color,
        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
        tooltip=[alt.Tooltip("year_month:O", title="Mês"), alt.Tooltip("serie:N", title=" "), alt.Tooltip(f"{value}:Q", title=y_title, format=y_format)],
    ).add_params(hover)
    return alt.layer(line, pts).properties(title=title, height=300)
