"""
datos.py
==========
Acceso a datos y utilidades compartidas entre páginas: conexión a SQL
Server, carga cacheada del dataset base, cálculo de KPIs, formateo, y las
funciones de gráficas Plotly reutilizables en más de una página.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from load_models import conectar_sql_server

# ============================================================================
# CONFIGURACIÓN DE CONEXIÓN — ajustar si tu servidor/BD tienen otro nombre
# ============================================================================
SQL_SERVER = "OMEGA-DELL"
SQL_DATABASE = "BD_ML_RELACIONAL"


# ============================================================================
# CARGA DE DATOS (cacheada)
# ============================================================================
@st.cache_data(ttl=600, show_spinner="Cargando datos desde SQL Server...")
def cargar_datos_dashboard() -> pd.DataFrame:
    engine = conectar_sql_server(SQL_SERVER, SQL_DATABASE)
    query = "SELECT * FROM vw_ML_DataCoSupplyChain"
    df = pd.read_sql(query, engine)
    df["fecha_pedido"] = pd.to_datetime(df["fecha_pedido"])
    return df


def calcular_kpis(df: pd.DataFrame) -> dict:
    """Función pura (sin Streamlit/SQL) para poder probarla de forma
    aislada. Recibe el DataFrame YA filtrado."""
    total_pedidos = len(df)
    if total_pedidos == 0:
        return {
            "total_pedidos": 0, "pct_completado": 0.0, "pct_cancelado": 0.0,
            "ventas_totales": 0.0, "ganancia_total": 0.0, "tiempo_promedio_envio": 0.0,
        }

    completados = int((df["estado_pedido"] == "COMPLETE").sum())
    cancelados = int((df["estado_pedido"] == "CANCELED").sum())

    return {
        "total_pedidos": total_pedidos,
        "pct_completado": round(completados / total_pedidos * 100, 1),
        "pct_cancelado": round(cancelados / total_pedidos * 100, 1),
        "ventas_totales": float(df["ventas"].sum()),
        "ganancia_total": float(df["ganancia_pedido"].sum()),
        "tiempo_promedio_envio": round(float(df["dias_envio_real"].mean()), 2),
    }


def formatear_moneda(valor: float) -> str:
    return f"${valor:,.0f}"


def promedio_envio_por_modo(df: pd.DataFrame) -> dict:
    """
    Promedio histórico de dias_envio_real agrupado por modo_envio. Se usa
    en 'Realizar Pedido' para ESTIMAR el tiempo de envío de un pedido
    hipotético (dato que no puede conocerse de antemano — solo se sabe
    después de despachar), en vez de pedírselo al usuario.
    """
    return df.groupby("modo_envio")["dias_envio_real"].mean().round(1).to_dict()


# ============================================================================
# GRÁFICAS — layout base compartido: fondo transparente (se funde con la
# tarjeta), tipografía Inter, sin barra de herramientas de Plotly.
# ============================================================================
PLOTLY_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#B7C1DE", size=12),
    margin=dict(l=8, r=8, t=8, b=8),
    height=220,
)

COLOR_CYAN = "#22D3EE"
COLOR_AMBER = "#F5A623"


def grafica_estado_pedidos(kpis: dict):
    fig = go.Figure(data=[go.Pie(
        labels=["Completado", "Cancelado"],
        values=[kpis["pct_completado"], kpis["pct_cancelado"]],
        hole=0.62,
        marker=dict(colors=[COLOR_CYAN, COLOR_AMBER]),
        textinfo="percent",
        textfont=dict(family="IBM Plex Mono, monospace", size=12),
        sort=False,
    )])
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, font=dict(size=11)),
    )
    return fig


def grafica_tendencia_ventas(df: pd.DataFrame):
    serie = df.set_index("fecha_pedido").resample("MS")["ventas"].sum().reset_index()
    fig = px.area(serie, x="fecha_pedido", y="ventas")
    fig.update_traces(line_color=COLOR_CYAN, fillcolor="rgba(34, 211, 238, 0.15)")
    fig.update_layout(**PLOTLY_LAYOUT_BASE, xaxis_title=None, yaxis_title=None)
    fig.update_xaxes(showgrid=False, color="#6E7AA0")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#6E7AA0")
    return fig


def grafica_top_paises(df: pd.DataFrame, top_n: int = 5):
    top = (
        df.groupby("pais_destino")["ventas"].sum()
        .sort_values(ascending=False).head(top_n)
        .sort_values(ascending=True)
    )
    fig = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h", marker_color=COLOR_CYAN))
    fig.update_layout(**PLOTLY_LAYOUT_BASE, xaxis_title=None, yaxis_title=None)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#6E7AA0")
    fig.update_yaxes(showgrid=False, color="#B7C1DE")
    return fig
