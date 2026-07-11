"""
🧠 Análisis No Supervisado - GDLM

Dashboard de evaluación del modelo K-Means ponderado.
Utiliza los artefactos, métricas y gráficas reales
generadas durante el entrenamiento.
"""

from datetime import datetime
from pathlib import Path
from typing import Any
import json

import joblib
import pandas as pd
import streamlit as st


# =============================================================================
# RUTAS DEL PROYECTO
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUTA_BDML = PROJECT_ROOT.parent

RUTA_ARTEFACTOS = (
    RUTA_BDML
    / "modelo_kmeans_artifacts.pkl"
)

RUTA_METADATA = (
    RUTA_BDML
    / "metadata_kmeans.json"
)

RUTA_GRAFICAS = (
    RUTA_BDML
    / "graficas1111"
)


# =============================================================================
# ESTADO GLOBAL
# =============================================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


# =============================================================================
# CSS
# =============================================================================

if st.session_state.get("dark_mode", True):
    variables_tema = """
        --bg-primary: #0A0A12;
        --bg-secondary: #111122;
        --bg-card: #1A1A2E;
        --bg-input: #0F0F1F;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --text-gold: #E8C9A0;
        --border-color: rgba(255,255,255,0.07);
        --shadow-card: 0 8px 32px rgba(0,0,0,0.50);
        --shadow-hover: 0 12px 48px rgba(0,0,0,0.65);
    """
else:
    variables_tema = """
        --bg-primary: #F0F4F8;
        --bg-secondary: #E2E8F0;
        --bg-card: #FFFFFF;
        --bg-input: #F8FAFC;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #64748B;
        --text-gold: #B45309;
        --border-color: rgba(0,0,0,0.08);
        --shadow-card: 0 8px 32px rgba(0,0,0,0.08);
        --shadow-hover: 0 12px 48px rgba(0,0,0,0.14);
    """

st.markdown(
    f"""
<style>
    :root {{
        --gold: #D4A574;
        --gold-light: #E8C9A0;
        --emerald: #10B981;
        --ruby: #EF4444;
        --blue: #3B82F6;
        --violet: #8B5CF6;

        --gradient-accent: linear-gradient(
            135deg,
            #D4A574 0%,
            #E8C9A0 50%,
            #D4A574 100%
        );

        --gradient-dark: linear-gradient(
            135deg,
            #0A0A12 0%,
            #1A1A2E 100%
        );

        --font-primary: 'Inter', -apple-system,
            BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    .stApp {{
        {variables_tema}
        background: var(--bg-primary) !important;
        color: var(--text-primary);
        font-family: var(--font-primary);
    }}

    .main-header {{
        background: var(--gradient-dark);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(212,165,116,0.15);
        box-shadow: var(--shadow-card);
        position: relative;
        overflow: hidden;
    }}

    .main-header::before {{
        content: '✦';
        position: absolute;
        top: 1rem;
        right: 2rem;
        font-size: 3rem;
        color: rgba(212,165,116,0.08);
    }}

    .main-header::after {{
        content: '';
        position: absolute;
        right: -120px;
        bottom: -220px;
        width: 430px;
        height: 430px;
        border-radius: 50%;
        background: radial-gradient(
            circle,
            rgba(212,165,116,0.05) 0%,
            transparent 70%
        );
    }}

    .header-content {{
        position: relative;
        z-index: 1;
    }}

    .main-title {{
        color: var(--text-primary);
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.025em;
        background: var(--gradient-accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .main-subtitle {{
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin: 0.35rem 0 0 0;
    }}

    .header-divider {{
        width: 65px;
        height: 3px;
        margin-top: 0.75rem;
        border-radius: 8px;
        background: var(--gradient-accent);
    }}

    .metric-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 15px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        box-shadow: var(--shadow-card);
        min-height: 125px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}

    .metric-card::after {{
        content: '';
        position: absolute;
        left: 30%;
        right: 30%;
        bottom: 0;
        height: 2px;
        background: var(--gradient-accent);
        opacity: 0;
        transition: all 0.3s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: var(--shadow-hover);
        border-color: rgba(212,165,116,0.25);
    }}

    .metric-card:hover::after {{
        left: 12%;
        right: 12%;
        opacity: 1;
    }}

    .metric-label {{
        color: var(--text-muted);
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }}

    .metric-value {{
        color: var(--text-primary);
        font-size: 1.75rem;
        font-weight: 900;
        margin-top: 0.35rem;
    }}

    .metric-detail {{
        color: var(--text-muted);
        font-size: 0.68rem;
        margin-top: 0.25rem;
    }}

    .section-header {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin: 1.7rem 0 1rem 0;
        box-shadow: var(--shadow-card);
        position: relative;
        overflow: hidden;
    }}

    .section-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-accent);
    }}

    .section-title {{
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 800;
        margin: 0;
    }}

    .section-description {{
        color: var(--text-muted);
        font-size: 0.8rem;
        margin: 0.3rem 0 0 0;
    }}

    .cluster-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 15px;
        padding: 1.5rem 1.2rem;
        min-height: 280px;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }}

    .cluster-card:hover {{
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-color: rgba(212,165,116,0.25);
    }}

    .cluster-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-accent);
        opacity: 0.6;
    }}

    .cluster-number {{
        color: var(--gold-light);
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        margin-bottom: 0.3rem;
    }}

    .cluster-name {{
        color: var(--text-primary);
        font-size: 1.2rem;
        font-weight: 800;
        margin: 0.3rem 0 0.5rem 0;
        line-height: 1.3;
    }}

    .cluster-description {{
        color: var(--text-secondary);
        font-size: 0.8rem;
        line-height: 1.5;
        margin: 0 0 1rem 0;
        flex-grow: 1;
    }}

    .cluster-stats {{
        margin-top: auto;
        border-top: 1px solid var(--border-color);
        padding-top: 0.75rem;
    }}

    .cluster-stat {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.35rem 0;
        font-size: 0.78rem;
    }}

    .cluster-stat:last-child {{
        padding-bottom: 0;
    }}

    .cluster-stat-label {{
        color: var(--text-muted);
        font-weight: 500;
    }}

    .cluster-stat-value {{
        color: var(--text-primary);
        font-weight: 700;
    }}

    .cluster-stat-value.complete {{
        color: #10B981;
    }}

    .cluster-stat-value.canceled {{
        color: #EF4444;
    }}

    .chart-header {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-top: 0.8rem;
        margin-bottom: 0.7rem;
        box-shadow: var(--shadow-card);
    }}

    .chart-title {{
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 800;
        margin: 0;
    }}

    .chart-description {{
        color: var(--text-muted);
        font-size: 0.73rem;
        margin: 0.25rem 0 0 0;
    }}

    .interpretation-card {{
        background: rgba(212,165,116,0.06);
        border: 1px solid rgba(212,165,116,0.16);
        border-left: 4px solid #D4A574;
        border-radius: 12px;
        padding: 0.9rem 1.15rem;
        margin-top: 0.75rem;
        margin-bottom: 0.8rem;
    }}

    .interpretation-card p {{
        color: var(--text-secondary);
        font-size: 0.8rem;
        line-height: 1.55;
        margin: 0;
    }}

    .warning-card {{
        background: rgba(245,158,11,0.08);
        border: 1px solid rgba(245,158,11,0.20);
        border-left: 4px solid #F59E0B;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }}

    .warning-card p {{
        color: var(--text-secondary);
        font-size: 0.82rem;
        line-height: 1.6;
        margin: 0;
    }}

    .success-card {{
        background: rgba(16,185,129,0.07);
        border: 1px solid rgba(16,185,129,0.18);
        border-left: 4px solid #10B981;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }}

    .success-card p {{
        color: var(--text-secondary);
        font-size: 0.82rem;
        line-height: 1.6;
        margin: 0;
    }}

    div[data-testid="stImage"] img {{
        border-radius: 13px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-card);
    }}

    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }}

    div[data-testid="stTabs"] button {{
        font-weight: 700;
        font-family: var(--font-primary);
    }}

    ::-webkit-scrollbar {{
        width: 6px;
    }}

    ::-webkit-scrollbar-track {{
        background: var(--bg-secondary);
    }}

    ::-webkit-scrollbar-thumb {{
        background: var(--gradient-accent);
        border-radius: 10px;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# FUNCIONES DE CARGA
# =============================================================================

@st.cache_resource(show_spinner=False)
def cargar_artefactos() -> dict[str, Any]:
    """Carga el modelo K-Means y todos sus artefactos."""

    if not RUTA_ARTEFACTOS.exists():
        raise FileNotFoundError(
            "No se encontró el archivo de artefactos K-Means en: "
            f"{RUTA_ARTEFACTOS}"
        )

    return joblib.load(RUTA_ARTEFACTOS)


@st.cache_data(show_spinner=False)
def cargar_metadata() -> dict[str, Any]:
    """Carga los metadatos legibles del modelo."""

    if not RUTA_METADATA.exists():
        raise FileNotFoundError(
            "No se encontró metadata_kmeans.json en: "
            f"{RUTA_METADATA}"
        )

    with open(
        RUTA_METADATA,
        "r",
        encoding="utf-8",
    ) as archivo:
        return json.load(archivo)


def obtener_ruta_grafica(nombre: str) -> Path | None:
    """Devuelve la ruta de una gráfica si existe."""

    ruta = RUTA_GRAFICAS / nombre

    if ruta.exists():
        return ruta

    return None


def mostrar_grafica(
    ruta: Path | None,
    titulo: str,
    descripcion: str,
    interpretacion: str,
) -> None:
    """
    Muestra encabezado, gráfica e interpretación
    sin envolver componentes nativos en HTML abierto.
    """

    st.markdown(
        f"""
<div class="chart-header">
    <p class="chart-title">{titulo}</p>
    <p class="chart-description">{descripcion}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if ruta and ruta.exists():
        st.image(
            str(ruta),
            use_container_width=True,
        )
    else:
        st.info(
            "La gráfica no fue encontrada en "
            "`graficas1111`."
        )

    st.markdown(
        f"""
<div class="interpretation-card">
    <p>{interpretacion}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def obtener_valor_cluster(
    mapa: dict,
    cluster_id: int,
    valor_default: float = 0.0,
) -> float:
    """Obtiene un valor aceptando claves enteras o de texto."""

    valor = mapa.get(
        cluster_id,
        mapa.get(
            str(cluster_id),
            valor_default,
        ),
    )

    try:
        return float(valor)
    except (TypeError, ValueError):
        return float(valor_default)


# =============================================================================
# CARGAR DATOS REALES
# =============================================================================

try:
    artefactos = cargar_artefactos()
    metadata = cargar_metadata()

except Exception as error:
    st.error(
        "No fue posible cargar el modelo no supervisado."
    )
    st.code(str(error))
    st.stop()


k_optimo = int(
    artefactos.get(
        "k_optimo",
        metadata.get(
            "k_optimo",
            0,
        ),
    )
)

silhouette = float(
    artefactos.get(
        "silhouette",
        metadata.get(
            "silhouette",
            0.0,
        ),
    )
)

calinski = float(
    artefactos.get(
        "calinski_harabasz",
        metadata.get(
            "calinski_harabasz",
            0.0,
        ),
    )
)

davies = float(
    artefactos.get(
        "davies_bouldin",
        metadata.get(
            "davies_bouldin",
            0.0,
        ),
    )
)

umbral_anomalias = float(
    artefactos.get(
        "umbral_anomalias",
        metadata.get(
            "umbral_anomalias",
            0.0,
        ),
    )
)

fecha_entrenamiento = (
    artefactos.get("fecha_entrenamiento")
    or metadata.get(
        "fecha_entrenamiento",
        "No disponible",
    )
)

tamano_dataset = int(
    metadata.get(
        "tamaño_dataset",
        0,
    )
)

n_features = int(
    artefactos.get(
        "n_features",
        metadata.get(
            "n_features",
            0,
        ),
    )
)

porcentajes_cluster = artefactos.get(
    "porcentaje_complete_por_cluster",
    {},
)

tamano_clusters = artefactos.get(
    "tamano_clusters",
    {},
)

mapa_complete = porcentajes_cluster.get(
    "COMPLETE",
    {},
)

mapa_canceled = porcentajes_cluster.get(
    "CANCELED",
    {},
)


# =============================================================================
# PERFILES DE LOS CLÚSTERES
# =============================================================================

perfiles = {
    0: {
        "nombre": "Alta finalización",
        "descripcion": (
            "Segmento asociado principalmente con transacciones "
            "DEBIT y una proporción elevada de pedidos COMPLETE."
        ),
        "transaccion": "DEBIT",
        "color": "#10B981",
    },
    1: {
        "nombre": "Riesgo intermedio",
        "descripcion": (
            "Segmento con predominio de TRANSFER y una proporción "
            "mayor de pedidos CANCELED que COMPLETE."
        ),
        "transaccion": "TRANSFER",
        "color": "#F59E0B",
    },
    2: {
        "nombre": "Finalización muy alta",
        "descripcion": (
            "Segmento asociado principalmente con PAYMENT y la "
            "mayor proporción de pedidos COMPLETE."
        ),
        "transaccion": "PAYMENT",
        "color": "#3B82F6",
    },
    3: {
        "nombre": "Cancelación crítica",
        "descripcion": (
            "Segmento asociado principalmente con CASH y una "
            "concentración total de pedidos CANCELED."
        ),
        "transaccion": "CASH",
        "color": "#EF4444",
    },
}


# =============================================================================
# RUTAS DE GRÁFICAS
# =============================================================================

grafica_seleccion_k = obtener_ruta_grafica(
    "01_seleccion_k.png"
)

grafica_tamano = obtener_ruta_grafica(
    "02_tamano_clusters.png"
)

grafica_objetivo = obtener_ruta_grafica(
    "03_composicion_objetivo.png"
)

grafica_transaccion = obtener_ruta_grafica(
    "04_composicion_tx.png"
)

grafica_pca = obtener_ruta_grafica(
    "05_clusters_pca2d.png"
)

grafica_varianza = obtener_ruta_grafica(
    "06_pca_varianza.png"
)

grafica_tsne = obtener_ruta_grafica(
    "07_tsne_clusters.png"
)


# =============================================================================
# ENCABEZADO
# =============================================================================

st.markdown(
    """
<div class="main-header">
    <div class="header-content">
        <h1 class="main-title">🧠 Análisis No Supervisado</h1>
        <p class="main-subtitle">
            Evaluación y caracterización real de los segmentos
            identificados mediante K-Means ponderado.
        </p>
        <div class="header-divider"></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# MÉTRICAS PRINCIPALES
# =============================================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">k óptimo</div>
    <div class="metric-value" style="color:#E8C9A0;">
        {k_optimo}
    </div>
    <div class="metric-detail">
        Número de clústeres
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Silhouette</div>
    <div class="metric-value" style="color:#10B981;">
        {silhouette:.4f}
    </div>
    <div class="metric-detail">
        Cohesión y separación
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Calinski-Harabasz</div>
    <div class="metric-value" style="color:#3B82F6; font-size:1.35rem;">
        {calinski:,.2f}
    </div>
    <div class="metric-detail">
        Separación entre grupos
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Davies-Bouldin</div>
    <div class="metric-value" style="color:#D4A574;">
        {davies:.4f}
    </div>
    <div class="metric-detail">
        Menor es mejor
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Variables finales</div>
    <div class="metric-value" style="color:#8B5CF6;">
        {n_features}
    </div>
    <div class="metric-detail">
        Espacio ponderado
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# INFORMACIÓN GENERAL
# =============================================================================

st.markdown(
    """
<div class="section-header">
    <p class="section-title">⚙️ Configuración del modelo</p>
    <p class="section-description">
        Parámetros y características del entrenamiento no supervisado.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Modelo",
        "K-Means",
    )

with col2:
    st.metric(
        "Registros",
        f"{tamano_dataset:,}",
    )

with col3:
    st.metric(
        "Umbral de anomalías",
        f"{umbral_anomalias:.4f}",
    )

with col4:
    fecha_visual = str(
        fecha_entrenamiento
    ).replace(
        "T",
        " ",
    )[:19]

    st.metric(
        "Entrenamiento",
        fecha_visual,
    )

st.markdown(
    """
<div class="success-card">
    <p>
        <strong>Interpretación general:</strong>
        un Silhouette de 0.6051 indica que los grupos presentan
        una separación razonablemente clara. El Davies-Bouldin
        de 0.5991 también respalda una estructura de clústeres
        compacta y diferenciada.
    </p>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# PERFILES DE LOS CLÚSTERES - VERSIÓN CORREGIDA
# =============================================================================

st.markdown(
    """
<div class="section-header">
    <p class="section-title">👥 Perfiles identificados</p>
    <p class="section-description">
        Caracterización real de los cuatro segmentos obtenidos.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

columnas_cluster = st.columns(4)

for cluster_id, columna in enumerate(columnas_cluster):

    perfil = perfiles.get(
        cluster_id,
        {},
    )

    pct_complete = obtener_valor_cluster(
        mapa_complete,
        cluster_id,
    )

    pct_canceled = obtener_valor_cluster(
        mapa_canceled,
        cluster_id,
    )

    pct_tamano = obtener_valor_cluster(
        tamano_clusters,
        cluster_id,
    )

    nombre_perfil = perfil.get("nombre", f"Clúster {cluster_id}")
    descripcion = perfil.get("descripcion", "Perfil no disponible")
    transaccion = perfil.get("transaccion", "N/D")
    color = perfil.get("color", "#E8C9A0")

    with columna:
        st.markdown(
            f"""
<div class="cluster-card">
    <div class="cluster-number">Clúster {cluster_id}</div>
    <div class="cluster-name" style="color:{color};">{nombre_perfil}</div>
    <div class="cluster-description">{descripcion}</div>
    <div class="cluster-stats">
        <div class="cluster-stat">
            <span class="cluster-stat-label">Método predominante</span>
            <span class="cluster-stat-value">{transaccion}</span>
        </div>
        <div class="cluster-stat">
            <span class="cluster-stat-label">Tamaño</span>
            <span class="cluster-stat-value">{pct_tamano:.1f}%</span>
        </div>
        <div class="cluster-stat">
            <span class="cluster-stat-label">COMPLETE</span>
            <span class="cluster-stat-value complete">{pct_complete:.2f}%</span>
        </div>
        <div class="cluster-stat">
            <span class="cluster-stat-label">CANCELED</span>
            <span class="cluster-stat-value canceled">{pct_canceled:.2f}%</span>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )


# =============================================================================
# TABLA RESUMEN
# =============================================================================

filas_clusters = []

for cluster_id in range(k_optimo):

    perfil = perfiles.get(
        cluster_id,
        {},
    )

    filas_clusters.append(
        {
            "Clúster": f"Clúster {cluster_id}",
            "Perfil": perfil.get(
                "nombre",
                "Segmento",
            ),
            "Método predominante": perfil.get(
                "transaccion",
                "N/D",
            ),
            "Tamaño": (
                f"{obtener_valor_cluster(tamano_clusters, cluster_id):.1f}%"
            ),
            "COMPLETE": (
                f"{obtener_valor_cluster(mapa_complete, cluster_id):.2f}%"
            ),
            "CANCELED": (
                f"{obtener_valor_cluster(mapa_canceled, cluster_id):.2f}%"
            ),
        }
    )

df_clusters = pd.DataFrame(
    filas_clusters
)

st.dataframe(
    df_clusters,
    use_container_width=True,
    hide_index=True,
)


# =============================================================================
# PESTAÑAS DEL ANÁLISIS
# =============================================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🎯 Selección de K",
        "📊 Composición",
        "🗺️ PCA y t-SNE",
        "⚠️ Anomalías",
    ]
)


# -----------------------------------------------------------------------------
# TAB 1: SELECCIÓN DE K
# -----------------------------------------------------------------------------

with tab1:

    mostrar_grafica(
        grafica_seleccion_k,
        "🎯 Selección del número óptimo de clústeres",
        (
            "Comparación de Silhouette, Calinski-Harabasz "
            "y Davies-Bouldin para valores de k entre 2 y 8."
        ),
        (
            "El valor k = 4 obtuvo el mayor Silhouette "
            "(0.6051), el mayor Calinski-Harabasz y el menor "
            "Davies-Bouldin entre las alternativas evaluadas."
        ),
    )

    tabla_k = pd.DataFrame(
        {
            "k": [
                2,
                3,
                4,
                5,
                6,
                7,
                8,
            ],
            "Silhouette": [
                0.3411,
                0.4917,
                0.6051,
                0.4563,
                0.4563,
                0.3479,
                0.2637,
            ],
            "Calinski-Harabasz": [
                64922.2121,
                93886.8979,
                202462.7017,
                166820.7950,
                141837.9247,
                125437.0380,
                114068.7295,
            ],
            "Davies-Bouldin": [
                1.2571,
                0.9263,
                0.5991,
                1.1333,
                1.1345,
                1.4036,
                1.7020,
            ],
        }
    )

    tabla_k["Selección"] = [
        "",
        "",
        "⭐ Óptimo",
        "",
        "",
        "",
        "",
    ]

    st.dataframe(
        tabla_k,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
<div class="interpretation-card">
    <p>
        <strong>Decisión:</strong> se seleccionó k = 4 porque
        combina la mayor cohesión interna con la mejor separación
        entre grupos. A partir de k = 5, el Silhouette disminuye
        y Davies-Bouldin aumenta.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# TAB 2: COMPOSICIÓN
# -----------------------------------------------------------------------------

with tab2:

    col1, col2 = st.columns(2)

    with col1:
        mostrar_grafica(
            grafica_tamano,
            "📦 Tamaño relativo de los clústeres",
            (
                "Distribución porcentual de los pedidos "
                "entre los cuatro segmentos."
            ),
            (
                "El Clúster 0 es el de mayor tamaño con 38.4 %, "
                "mientras que el Clúster 3 representa el 10.9 % "
                "de los registros."
            ),
        )

    with col2:
        mostrar_grafica(
            grafica_objetivo,
            "✅ COMPLETE y CANCELED por clúster",
            (
                "Composición histórica del estado de los pedidos "
                "dentro de cada segmento."
            ),
            (
                "Los Clústeres 0 y 2 tienen alta proporción de "
                "COMPLETE. El Clúster 3 concentra únicamente "
                "pedidos CANCELED."
            ),
        )

    mostrar_grafica(
        grafica_transaccion,
        "💳 Tipo de transacción por clúster",
        (
            "Composición de CASH, DEBIT, PAYMENT y TRANSFER "
            "en los segmentos identificados."
        ),
        (
            "La variable tipo_transaccion es el principal factor "
            "de diferenciación: cada clúster se asocia de forma "
            "muy marcada con un método de pago."
        ),
    )

    st.markdown(
        """
<div class="warning-card">
    <p>
        <strong>Consideración metodológica:</strong>
        tipo_transaccion recibió un peso de 1.5, frente a 0.4
        para los demás bloques de variables. Por eso los segmentos
        están fuertemente definidos por el método de pago. Esta fue
        una decisión basada en el análisis previo de diferenciación.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# TAB 3: PCA Y T-SNE
# -----------------------------------------------------------------------------

with tab3:

    col1, col2 = st.columns(2)

    with col1:
        mostrar_grafica(
            grafica_pca,
            "🗺️ Visualización PCA de los clústeres",
            (
                "Proyección bidimensional de una muestra de "
                "pedidos mediante componentes principales."
            ),
            (
                "PCA permite observar la separación global de "
                "los clústeres en un espacio reducido, aunque "
                "solo representa una parte de la varianza total."
            ),
        )

    with col2:
        mostrar_grafica(
            grafica_tsne,
            "🧬 Visualización t-SNE",
            (
                "Representación no lineal de una muestra "
                "estratificada de 5 000 registros."
            ),
            (
                "t-SNE preserva relaciones locales y permite "
                "observar agrupaciones que pueden no distinguirse "
                "claramente en la proyección lineal de PCA."
            ),
        )

    mostrar_grafica(
        grafica_varianza,
        "📈 Varianza explicada por PCA",
        (
            "Cantidad de información conservada por cada "
            "componente principal."
        ),
        (
            "El análisis determinó que se requieren 5 componentes "
            "principales para conservar al menos el 85 % de la "
            "varianza del espacio ponderado."
        ),
    )


# -----------------------------------------------------------------------------
# TAB 4: ANOMALÍAS
# -----------------------------------------------------------------------------

with tab4:

    st.markdown(
        """
<div class="section-header">
    <p class="section-title">⚠️ Detección de comportamientos atípicos</p>
    <p class="section-description">
        Evaluación basada en la distancia al centroide más cercano.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
<div class="metric-card">
    <div class="metric-label">Umbral</div>
    <div class="metric-value" style="color:#E8C9A0;">
        {umbral_anomalias:.4f}
    </div>
    <div class="metric-detail">
        Percentil 95
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
<div class="metric-card">
    <div class="metric-label">Anomalías del entrenamiento</div>
    <div class="metric-value" style="color:#EF4444;">
        5.00%
    </div>
    <div class="metric-detail">
        7 555 registros
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
<div class="metric-card">
    <div class="metric-label">Outliers IQR</div>
    <div class="metric-value" style="color:#F59E0B;">
        0.35%
    </div>
    <div class="metric-detail">
        536 registros
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div class="interpretation-card">
    <p>
        Un pedido se marca como anomalía cuando su distancia al
        centroide más cercano supera el percentil 95 de las
        distancias observadas durante el entrenamiento. Esto
        identifica combinaciones poco frecuentes de variables,
        pero no significa necesariamente que el pedido sea erróneo.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    comparacion_anomalias = pd.DataFrame(
        {
            "Variable": [
                "Días reales de envío",
                "Beneficio del pedido",
                "Ventas",
            ],
            "Media anomalías": [
                0.63,
                40.44,
                202.22,
            ],
            "Media normales": [
                3.65,
                40.67,
                185.59,
            ],
        }
    )

    st.dataframe(
        comparacion_anomalias,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
<div class="warning-card">
    <p>
        Los registros anómalos presentan, en promedio, menos días
        reales de envío y ventas ligeramente superiores. La señal
        debe emplearse como apoyo para revisión, no como criterio
        automático de rechazo.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# DETALLE TÉCNICO
# =============================================================================

with st.expander(
    "🧪 Información técnica del modelo K-Means"
):

    pesos = metadata.get(
        "pesos",
        {},
    )

    st.markdown(
        f"""
**Configuración**

- Algoritmo: K-Means
- Número óptimo de clústeres: {k_optimo}
- Random state: {metadata.get("random_state", 42)}
- Registros utilizados: {tamano_dataset:,}
- Variables finales: {n_features}
- Fecha de entrenamiento: {fecha_visual}

**Métricas internas**

- Silhouette: {silhouette:.6f}
- Calinski-Harabasz: {calinski:.6f}
- Davies-Bouldin: {davies:.6f}

**Pesos del espacio**

- Variables numéricas: {float(pesos.get("PESO_NUMERICAS", 0.0)):.2f}
- Otras variables: {float(pesos.get("PESO_OTRAS", 0.0)):.2f}
- Tipo de transacción: {float(pesos.get("PESO_TX", 0.0)):.2f}

**Anomalías**

- Umbral de distancia: {umbral_anomalias:.6f}
- Criterio: percentil 95 de la distancia mínima al centroide
"""
    )

    columnas_utilizadas = metadata.get(
        "columnas_utilizadas",
        {},
    )

    if columnas_utilizadas:
        st.markdown(
            "**Columnas utilizadas durante el entrenamiento**"
        )

        st.json(
            columnas_utilizadas,
            expanded=False,
        )


# =============================================================================
# CONCLUSIÓN
# =============================================================================

st.markdown(
    """
<div class="section-header">
    <p class="section-title">📝 Conclusión del análisis</p>
    <p class="section-description">
        Resumen ejecutivo del modelo no supervisado.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="success-card">
    <p>
        El modelo K-Means identificó <strong>{k_optimo} segmentos</strong>
        con un Silhouette de <strong>{silhouette:.4f}</strong>.
        Los Clústeres 0 y 2 presentan alta proporción de pedidos
        COMPLETE, mientras que el Clúster 3 concentra pedidos
        CANCELED. La segmentación permite complementar la predicción
        supervisada mediante perfiles históricos, detección de
        anomalías y análisis del comportamiento logístico.
    </p>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# FOOTER
# =============================================================================

fecha_actual = datetime.now().strftime(
    "%d/%m/%Y %H:%M:%S"
)

st.markdown(
    f"""
<div style="text-align:center; padding:2rem 0 0.5rem 0; margin-top:2rem; border-top:1px solid var(--border-color);">
    <p style="font-size:0.7rem; color:var(--text-muted); font-family:var(--font-primary); margin:0;">
        ◆ GDLM · Evaluación del Modelo No Supervisado
    </p>
    <p style="font-size:0.58rem; color:var(--text-muted); opacity:0.6; margin:0.3rem 0 0 0;">
        {fecha_actual}
    </p>
</div>
""",
    unsafe_allow_html=True,
)