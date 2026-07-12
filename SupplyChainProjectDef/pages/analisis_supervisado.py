"""
📈 Análisis Supervisado - GDLM

Visualización de métricas, comparación de modelos y gráficos
generados durante el entrenamiento supervisado.
"""

from datetime import datetime
from pathlib import Path
import json

import pandas as pd
import streamlit as st


# =============================================================================
# RUTAS DEL PROYECTO
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUTA_BDML = PROJECT_ROOT.parent

RUTA_METADATA = RUTA_BDML / "metadata_modelo.json"

RUTA_GRAFICAS = (
    RUTA_BDML
    / "graficas"
    / "graficas_supervisado"
)


# =============================================================================
# ESTADO GLOBAL
# =============================================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


# =============================================================================
# CSS MEJORADO - ESTILO EJECUTIVO
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
        --shadow-hover: 0 12px 48px rgba(0,0,0,0.60);
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
        --shadow-hover: 0 12px 48px rgba(0,0,0,0.12);
    """

st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    :root {{
        --gold: #D4A574;
        --gold-light: #E8C9A0;
        --emerald: #10B981;
        --ruby: #EF4444;
        --blue: #3B82F6;
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
        --font-primary: 'Inter', -apple-system, sans-serif;
        --font-display: 'Inter', -apple-system, sans-serif;
    }}

    .stApp {{
        {variables_tema}
        background: var(--bg-primary) !important;
        color: var(--text-primary);
        font-family: var(--font-primary);
    }}

    /* Encabezado principal */
    .main-header {{
        background: var(--gradient-dark);
        padding: 2rem 2rem 1.5rem 2rem;
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
        bottom: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(212,165,116,0.03) 0%, transparent 70%);
        border-radius: 50%;
    }}

    .header-content {{
        position: relative;
        z-index: 1;
    }}

    .main-title {{
        color: var(--text-primary);
        font-family: var(--font-display);
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.02em;
        background: var(--gradient-accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .main-subtitle {{
        color: var(--text-secondary);
        font-size: 0.95rem;
        font-weight: 400;
        margin: 0.25rem 0 0 0;
    }}

    .header-divider {{
        width: 65px;
        height: 3px;
        margin-top: 0.7rem;
        border-radius: 6px;
        background: var(--gradient-accent);
    }}

    /* Tarjeta de métricas */
    .metric-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 15px;
        padding: 1.2rem 1rem;
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
        bottom: 0;
        left: 30%;
        right: 30%;
        height: 2px;
        background: var(--gradient-accent);
        opacity: 0;
        transition: all 0.3s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-color: rgba(212,165,116,0.25);
    }}

    .metric-card:hover::after {{
        opacity: 1;
        left: 15%;
        right: 15%;
    }}

    .metric-label {{
        color: var(--text-muted);
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 0.5rem;
    }}

    .metric-value {{
        color: var(--text-primary);
        font-size: 1.75rem;
        font-weight: 900;
        font-family: var(--font-display);
    }}

    .metric-detail {{
        color: var(--text-muted);
        font-size: 0.7rem;
        margin-top: 0.35rem;
    }}

    /* Tarjeta de sección */
    .section-header {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin: 1.8rem 0 1.2rem 0;
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
        font-family: var(--font-display);
    }}

    .section-description {{
        color: var(--text-muted);
        font-size: 0.8rem;
        margin: 0.35rem 0 0 0;
    }}

    /* Tarjeta de modelo */
    .model-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
    }}

    .model-card:hover {{
        box-shadow: var(--shadow-hover);
    }}

    .model-name {{
        color: var(--text-primary);
        font-size: 1rem;
        font-weight: 800;
        margin: 0;
        font-family: var(--font-display);
    }}

    .model-description {{
        color: var(--text-muted);
        font-size: 0.78rem;
        margin: 0.25rem 0 0 0;
    }}

    /* Tarjeta de interpretación */
    .interpretation-card {{
        background: rgba(212,165,116,0.06);
        border: 1px solid rgba(212,165,116,0.15);
        border-left: 4px solid #D4A574;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
    }}

    .interpretation-card p {{
        color: var(--text-secondary);
        font-size: 0.82rem;
        margin: 0;
        line-height: 1.6;
    }}

    /* Tarjeta de advertencia */
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
        font-size: 0.83rem;
        margin: 0;
        line-height: 1.6;
    }}

    /* Tarjeta de gráfica */
    .chart-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        box-shadow: var(--shadow-card);
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }}

    .chart-card:hover {{
        box-shadow: var(--shadow-hover);
        border-color: rgba(212,165,116,0.2);
    }}

    .chart-title {{
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0 0 0.15rem 0;
        font-family: var(--font-display);
    }}

    .chart-description {{
        color: var(--text-muted);
        font-size: 0.75rem;
        margin: 0 0 0.8rem 0;
    }}

    /* Imágenes */
    div[data-testid="stImage"] img {{
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-card);
        width: 100%;
        height: auto;
    }}

    /* Tabla mejorada */
    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }}

    /* Tabs */
    div[data-testid="stTabs"] button {{
        font-weight: 700;
        font-size: 0.9rem;
        font-family: var(--font-primary);
    }}

    /* Scrollbar */
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

@st.cache_data(show_spinner=False)
def cargar_metadata() -> dict:
    """Carga los metadatos reales del modelo supervisado."""

    if not RUTA_METADATA.exists():
        raise FileNotFoundError(
            f"No se encontró metadata_modelo.json en: "
            f"{RUTA_METADATA}"
        )

    with open(
        RUTA_METADATA,
        "r",
        encoding="utf-8",
    ) as archivo:
        return json.load(archivo)


def obtener_ruta_grafica(
    nombre_principal: str,
    nombre_alternativo: str | None = None,
) -> Path | None:
    """
    Busca primero la gráfica principal y luego una alternativa.
    """

    ruta_principal = RUTA_GRAFICAS / nombre_principal

    if ruta_principal.exists():
        return ruta_principal

    if nombre_alternativo:
        ruta_alternativa = (
            RUTA_GRAFICAS / nombre_alternativo
        )

        if ruta_alternativa.exists():
            return ruta_alternativa

    return None


def mostrar_tarjeta_grafica(
    ruta: Path | None,
    titulo: str,
    descripcion: str,
    interpretacion: str,
    columna_ancho: bool = True,
) -> None:
    """
    Muestra una gráfica dentro de una tarjeta elegante
    con título, descripción e interpretación.
    """
    
    # 1. Tarjeta con el título y descripción (completamente cerrada)
    st.markdown(
        f"""
<div class="chart-card">
    <div class="chart-title">{titulo}</div>
    <div class="chart-description">{descripcion}</div>
</div>
""",
        unsafe_allow_html=True,
    )
    
    # 2. Imagen con componente nativo de Streamlit
    if ruta and ruta.exists():
        st.image(
            str(ruta),
            use_container_width=columna_ancho,
        )
    else:
        st.info(
            "⚠️ Gráfica no encontrada en la carpeta "
            "`graficas/graficas_supervisado`."
        )
    
    # 3. Interpretación en tarjeta independiente
    st.markdown(
        f"""
<div class="interpretation-card">
    <p>{interpretacion}</p>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# CARGAR DATOS
# =============================================================================

try:
    metadata = cargar_metadata()

except Exception as error:
    st.error(
        "No fue posible cargar la información del modelo."
    )
    st.exception(error)
    st.stop()


nombre_modelo = metadata.get(
    "modelo",
    "No disponible",
)

fecha_entrenamiento = metadata.get(
    "fecha_entrenamiento",
    "No disponible",
)

requiere_escalado = bool(
    metadata.get(
        "requiere_escalado",
        False,
    )
)

variables_excluidas = metadata.get(
    "features_leakage_excluidas",
    [],
)

metricas = metadata.get(
    "metricas_test",
    {},
)

accuracy = float(
    metricas.get("accuracy", 0.0)
)

f1_score = float(
    metricas.get("f1", 0.0)
)

roc_auc = float(
    metricas.get("roc_auc", 0.0)
)

# Valores reales obtenidos durante el entrenamiento local.
precision = 0.6792
recall = 0.9247


# =============================================================================
# RUTAS DE GRÁFICAS REALES
# =============================================================================

grafica_comparacion = obtener_ruta_grafica(
    "v2_06_comparacion_modelos.png",
    "v1_01_comparacion_modelos.png",
)

grafica_matriz = obtener_ruta_grafica(
    "v2_07_matriz_confusion.png",
    "v1_02_matriz_confusion.png",
)

grafica_roc = obtener_ruta_grafica(
    "v2_08_roc.png",
    "v1_03_roc.png",
)

grafica_importancia = obtener_ruta_grafica(
    "v2_09_importancia_permutacion.png",
)

grafica_calibracion = obtener_ruta_grafica(
    "v2_10_calibracion.png",
)

grafica_estabilidad = obtener_ruta_grafica(
    "v2_11_estabilidad_modelo.png",
)

grafica_distribucion = obtener_ruta_grafica(
    "v2_05_desbalanceo_target.png",
)

grafica_correlacion = obtener_ruta_grafica(
    "v2_02_correlacion.png",
)

grafica_categoricas = obtener_ruta_grafica(
    "v2_03_categoricas_vs_target.png",
)

grafica_violin = obtener_ruta_grafica(
    "v2_04_violin.png",
)


# =============================================================================
# ENCABEZADO
# =============================================================================

st.markdown(
    """
<div class="main-header">
    <div class="header-content">
        <h1 class="main-title">📈 Análisis Supervisado</h1>
        <p class="main-subtitle">
            Evaluación real del modelo utilizado para predecir
            el estado de los pedidos
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
    <div class="metric-label">Accuracy</div>
    <div class="metric-value" style="color:#3B82F6;">
        {accuracy * 100:.2f}%
    </div>
    <div class="metric-detail">Exactitud global</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Precision</div>
    <div class="metric-value" style="color:#D4A574;">
        {precision * 100:.2f}%
    </div>
    <div class="metric-detail">Precisión positiva</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Recall (Sensibilidad)</div>
    <div class="metric-value" style="color:#10B981;">
        {recall * 100:.2f}%
    </div>
    <div class="metric-detail">Capacidad de detección</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">F1-Score</div>
    <div class="metric-value" style="color:#E8C9A0;">
        {f1_score * 100:.2f}%
    </div>
    <div class="metric-detail">Equilibrio global</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">ROC-AUC</div>
    <div class="metric-value" style="color:#EF4444;">
        {roc_auc * 100:.2f}%
    </div>
    <div class="metric-detail">Separación de clases</div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# INFORMACIÓN GENERAL DEL MODELO
# =============================================================================

st.markdown(
    """
<div class="section-header">
    <div class="section-title">🧠 Información del modelo seleccionado</div>
    <div class="section-description">
        Características principales del artefacto utilizado
        actualmente por la aplicación
    </div>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
<div class="model-card">
    <div class="model-name">Modelo seleccionado</div>
    <div class="model-description">{nombre_modelo}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    texto_escalado = (
        "Sí, utiliza StandardScaler"
        if requiere_escalado
        else "No requiere escalado"
    )

    st.markdown(
        f"""
<div class="model-card">
    <div class="model-name">Preprocesamiento</div>
    <div class="model-description">{texto_escalado}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
<div class="model-card">
    <div class="model-name">Fecha de entrenamiento</div>
    <div class="model-description">{fecha_entrenamiento}</div>
</div>
""",
        unsafe_allow_html=True,
    )

if variables_excluidas:
    texto_variables = ", ".join(
        variables_excluidas
    )
else:
    texto_variables = "Ninguna registrada"

st.markdown(
    f"""
<div class="interpretation-card">
    <p>
        <strong>Control de fuga de datos:</strong>
        durante el entrenamiento se excluyeron
        <strong>{texto_variables}</strong> para evitar que el
        modelo utilizara información que revelara directamente
        el resultado real del pedido.
    </p>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# COMPARACIÓN DE MODELOS
# =============================================================================

st.markdown(
    """
<div class="section-header">
    <div class="section-title">🏆 Comparación de algoritmos</div>
    <div class="section-description">
        Resultados reales obtenidos durante el entrenamiento local
    </div>
</div>
""",
    unsafe_allow_html=True,
)

comparacion_modelos = pd.DataFrame(
    {
        "Modelo": [
            "KNN ⭐",
            "Random Forest",
            "Regresión Logística",
            "Árbol de Decisión",
        ],
        "Accuracy": [
            0.6610,
            0.5963,
            0.5743,
            0.5537,
        ],
        "Precision": [
            0.6792,
            0.6850,
            0.6907,
            0.6870,
        ],
        "Recall": [
            0.9247,
            0.7227,
            0.6466,
            0.5989,
        ],
        "F1-Score": [
            0.7832,
            0.7033,
            0.6679,
            0.6399,
        ],
        "ROC-AUC": [
            0.5372,
            0.5535,
            0.5561,
            0.5464,
        ],
    }
)

comparacion_visual = comparacion_modelos.copy()

for columna in [
    "Accuracy",
    "Precision",
    "Recall",
    "F1-Score",
    "ROC-AUC",
]:
    comparacion_visual[columna] = (
        comparacion_visual[columna]
        .mul(100)
        .round(2)
        .astype(str)
        + "%"
    )

st.dataframe(
    comparacion_visual,
    use_container_width=True,
    hide_index=True,
)

st.markdown(
    """
<div class="interpretation-card">
    <p>
        <strong>KNN fue seleccionado por obtener el mayor
        F1-Score.</strong> Su recall es alto, por lo que identifica
        una gran proporción de los pedidos clasificados como
        COMPLETE. Sin embargo, el ROC-AUC es moderado y debe
        interpretarse con cautela.
    </p>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# PESTAÑAS DE ANÁLISIS
# =============================================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🎯 Evaluación del Modelo",
        "🔍 Importancia de Variables",
        "📊 Exploración de Datos",
        "🧪 Robustez y Calibración",
    ]
)


# -----------------------------------------------------------------------------
# TAB 1: EVALUACIÓN DEL MODELO
# -----------------------------------------------------------------------------

with tab1:
    
    col1, col2 = st.columns(2)
    
    with col1:
        mostrar_tarjeta_grafica(
            grafica_comparacion,
            "📊 Comparación visual de modelos",
            "Contrasta el rendimiento obtenido por los algoritmos evaluados",
            "KNN destaca con el mejor F1-Score, aunque todos los modelos "
            "presentan un rendimiento moderado en ROC-AUC."
        )
    
    with col2:
        mostrar_tarjeta_grafica(
            grafica_roc,
            "📈 Curva ROC",
            "Evalúa la capacidad del modelo para distinguir entre clases",
            "El modelo presenta una capacidad moderada para separar "
            "COMPLETE de CANCELED, con un ROC-AUC de 0.5372."
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        mostrar_tarjeta_grafica(
            grafica_matriz,
            "🧩 Matriz de confusión",
            "Presenta aciertos y errores por cada clase del problema",
            "La mayoría de los pedidos COMPLETE fueron identificados "
            "correctamente, con un recall del 92.47%."
        )
    
    with col2:
        mostrar_tarjeta_grafica(
            grafica_estabilidad,
            "🛡️ Estabilidad del modelo",
            "Permite observar la variación del rendimiento en diferentes evaluaciones",
            "El modelo muestra una estabilidad aceptable, aunque se recomienda "
            "monitorear su desempeño periódicamente."
        )
    
    st.markdown(
        """
<div class="warning-card">
    <p>
        <strong>Interpretación honesta:</strong>
        el ROC-AUC de 0.5372 está cerca de una clasificación
        aleatoria. El modelo puede utilizarse como señal de apoyo,
        pero no debe tomar decisiones automáticas sin supervisión.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# TAB 2: IMPORTANCIA DE VARIABLES
# -----------------------------------------------------------------------------

with tab2:
    
    col1, col2 = st.columns(2)
    
    with col1:
        mostrar_tarjeta_grafica(
            grafica_importancia,
            "🌟 Importancia por permutación",
            "Muestra cuánto disminuye el rendimiento al alterar cada variable",
            "Las variables económicas y logísticas tienen mayor influencia "
            "en la predicción del estado del pedido."
        )
    
    with col2:
        mostrar_tarjeta_grafica(
            grafica_correlacion,
            "🔗 Matriz de correlación",
            "Permite identificar relaciones lineales entre variables numéricas",
            "Se observan correlaciones moderadas entre variables económicas, "
            "lo que sugiere cierta redundancia informativa."
        )
    
    st.markdown(
        """
<div class="interpretation-card">
    <p>
        Las variables con mayor importancia deben supervisarse
        durante el uso del sistema. También deben revisarse en cada
        reentrenamiento para detectar cambios en el comportamiento
        de los pedidos.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# TAB 3: EXPLORACIÓN DE DATOS
# -----------------------------------------------------------------------------

with tab3:
    
    col1, col2 = st.columns(2)
    
    with col1:
        mostrar_tarjeta_grafica(
            grafica_distribucion,
            "⚖️ Distribución del target",
            "Muestra el balance entre pedidos COMPLETE y CANCELED",
            "El dataset presenta un 66.2% de pedidos COMPLETE y un 33.8% "
            "de CANCELED, lo que indica un desbalanceo moderado."
        )
    
    with col2:
        mostrar_tarjeta_grafica(
            grafica_categoricas,
            "🏷️ Variables categóricas vs target",
            "Compara distintas categorías con el estado final del pedido",
            "Algunas categorías muestran mayor proporción de pedidos "
            "COMPLETE, lo que las hace relevantes para la predicción."
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        mostrar_tarjeta_grafica(
            grafica_violin,
            "🎻 Distribuciones por clase",
            "Compara la distribución de variables numéricas entre las dos clases",
            "Las distribuciones muestran diferencias notables entre "
            "pedidos COMPLETE y CANCELED en variables clave.",
            columna_ancho=True
        )
    
    st.markdown(
        """
<div class="interpretation-card">
    <p>
        El dataset presenta aproximadamente un 66.2 % de pedidos
        COMPLETE y un 33.8 % de pedidos CANCELED. Esta diferencia
        debe considerarse al interpretar accuracy, precision,
        recall y F1-Score.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# TAB 4: ROBUSTEZ Y CALIBRACIÓN
# -----------------------------------------------------------------------------

with tab4:
    
    col1, col2 = st.columns(2)
    
    with col1:
        mostrar_tarjeta_grafica(
            grafica_calibracion,
            "🎚️ Calibración de probabilidades",
            "Compara las probabilidades predichas con la frecuencia observada",
            "El modelo utiliza calibración sigmoide mediante Platt Scaling, "
            "mejorando la confiabilidad de las probabilidades."
        )
    
    with col2:
        st.markdown(
            """
<div class="chart-card">
    <div class="chart-title">📋 Resumen de robustez</div>
    <div class="chart-description">Evaluación de la confiabilidad del modelo</div>
</div>
""",
            unsafe_allow_html=True,
        )
        
        st.markdown(
            """
<div style="background:var(--bg-input); border-radius:10px; padding:0.8rem 1rem; margin-bottom:0.5rem;">
    <p style="margin:0; font-weight:600;">Calibración</p>
    <p style="margin:0.2rem 0 0 0; font-size:0.85rem; color:var(--text-secondary);">
        ✅ Utiliza Platt Scaling para mejorar las probabilidades
    </p>
</div>
""",
            unsafe_allow_html=True,
        )
        
        st.markdown(
            """
<div style="background:var(--bg-input); border-radius:10px; padding:0.8rem 1rem; margin-bottom:0.5rem;">
    <p style="margin:0; font-weight:600;">Estabilidad</p>
    <p style="margin:0.2rem 0 0 0; font-size:0.85rem; color:var(--text-secondary);">
        ✅ Rendimiento consistente en diferentes evaluaciones
    </p>
</div>
""",
            unsafe_allow_html=True,
        )
        
        st.markdown(
            """
<div style="background:var(--bg-input); border-radius:10px; padding:0.8rem 1rem;">
    <p style="margin:0; font-weight:600;">Recomendación</p>
    <p style="margin:0.2rem 0 0 0; font-size:0.85rem; color:var(--text-secondary);">
        🔄 Monitorear periódicamente el desempeño del modelo
    </p>
</div>
""",
            unsafe_allow_html=True,
        )
    
    st.markdown(
        """
<div class="warning-card">
    <p>
        El modelo utiliza calibración sigmoide mediante Platt
        Scaling. Es recomendable monitorear periódicamente las
        probabilidades, el desempeño y la distribución de las
        variables para detectar degradación.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# CONCLUSIÓN
# =============================================================================

st.markdown(
    """
<div class="section-header">
    <div class="section-title">📝 Conclusión del análisis</div>
    <div class="section-description">
        Resumen ejecutivo del desempeño supervisado
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="interpretation-card">
    <p>
        El modelo <strong>{nombre_modelo}</strong> alcanzó un
        F1-Score de <strong>{f1_score:.4f}</strong>, un recall de
        <strong>{recall:.4f}</strong> y un ROC-AUC de
        <strong>{roc_auc:.4f}</strong>. El recall elevado indica
        una buena capacidad para recuperar pedidos COMPLETE,
        mientras que el ROC-AUC evidencia una separación limitada
        entre clases. Por este motivo, GDLM utiliza la predicción
        como apoyo al seguimiento logístico y no como una decisión
        automática definitiva.
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
        ◆ GDLM · Evaluación del Modelo Supervisado
    </p>
    <p style="font-size:0.58rem; color:var(--text-muted); opacity:0.6; margin:0.3rem 0 0 0;">
        {fecha_actual}
    </p>
</div>
""",
    unsafe_allow_html=True,
)