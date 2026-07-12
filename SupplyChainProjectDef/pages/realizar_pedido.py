"""
📦 Realizar Pedido - GDLM

Formulario conectado al modelo supervisado real.
Las opciones geográficas se cargan desde DataCoSupplyChain_Limpio.csv.
"""

from datetime import datetime
from pathlib import Path
from uuid import uuid4
import sys

import pandas as pd
import streamlit as st


# =============================================================================
# RUTAS E IMPORTACIÓN DEL MOTOR
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUTA_BDML = PROJECT_ROOT.parent
RUTA_DATASET = RUTA_BDML / "DataCoSupplyChain_Limpio.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.predictor_supervisado import (  # noqa: E402
    ArtefactoNoEncontradoError,
    DatosPrediccionError,
    ErrorPredictorSupervisado,
    obtener_metadata_modelo,
    obtener_opciones_modelo,
    predecir_pedido,
)

# IMPORTAR PREDICTOR NO SUPERVISADO
from utils.predictor_no_supervisado import (  # noqa: E402
    predecir_cluster,
    ArtefactoKMeansNoEncontradoError,
    DatosKMeansError,
    ErrorPredictorNoSupervisado,
)


# =============================================================================
# ESTADO GLOBAL
# =============================================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "resultado_prediccion" not in st.session_state:
    st.session_state.resultado_prediccion = None

if "pedido_actual" not in st.session_state:
    st.session_state.pedido_actual = None

if "datos_modelo_actual" not in st.session_state:
    st.session_state.datos_modelo_actual = None

# INICIALIZAR ESTADO PARA K-MEANS
if "resultado_cluster" not in st.session_state:
    st.session_state.resultado_cluster = None

if "datos_kmeans_actual" not in st.session_state:
    st.session_state.datos_kmeans_actual = None


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
        --text-gold: #FCD34D;
        --border-color: rgba(255,255,255,0.07);
        --shadow-card: 0 4px 24px rgba(0,0,0,0.45);
        --shadow-glow: 0 0 40px rgba(245,158,11,0.1);
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
        --shadow-card: 0 4px 24px rgba(0,0,0,0.08);
        --shadow-glow: 0 0 40px rgba(245,158,11,0.05);
    """

st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    :root {{
        --gold: #D4A574;
        --gold-light: #E8C9A0;
        --gold-dark: #B8860B;
        --emerald: #10B981;
        --ruby: #EF4444;
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
        --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-display: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
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
        border: 1px solid rgba(212, 165, 116, 0.15);
        position: relative;
        overflow: hidden;
    }}

    .main-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(212,165,116,0.05) 0%, transparent 70%);
        border-radius: 50%;
    }}

    .main-header::after {{
        content: '✦';
        position: absolute;
        top: 1rem;
        right: 2rem;
        font-size: 2.5rem;
        color: rgba(212, 165, 116, 0.1);
        font-weight: 300;
    }}

    .header-top {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }}

    .header-brand {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .header-icon {{
        font-size: 2.5rem;
        line-height: 1;
    }}

    .header-title {{
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

    .header-subtitle {{
        color: var(--text-secondary);
        font-size: 0.95rem;
        font-weight: 400;
        margin: 0.25rem 0 0 0;
        position: relative;
        z-index: 1;
    }}

    .header-meta {{
        display: flex;
        gap: 2rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }}

    .header-meta-item {{
        color: var(--text-muted);
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .header-meta-item strong {{
        color: var(--gold-light);
        font-weight: 700;
    }}

    .header-divider {{
        width: 60px;
        height: 3px;
        margin-top: 0.5rem;
        border-radius: 4px;
        background: var(--gradient-accent);
        position: relative;
        z-index: 1;
    }}

    /* Tarjetas de sección */
    .section-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        box-shadow: var(--shadow-card);
        padding: 1.25rem 1.5rem;
        margin: 1rem 0 1.2rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}

    .section-card:hover {{
        border-color: rgba(212, 165, 116, 0.2);
        box-shadow: var(--shadow-glow);
    }}

    .section-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-accent);
        opacity: 0.6;
    }}

    .section-title {{
        color: var(--text-primary);
        font-family: var(--font-display);
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }}

    .section-title .emoji {{
        font-size: 1.2rem;
    }}

    .section-description {{
        color: var(--text-muted);
        font-family: var(--font-primary);
        font-size: 0.8rem;
        margin: 0.3rem 0 0 0;
        font-weight: 400;
    }}

    /* Campos de formulario mejorados */
    div[data-testid="stSelectbox"] > label,
    div[data-testid="stNumberInput"] > label,
    div[data-testid="stSlider"] > label {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.02em;
    }}

    div[data-baseweb="select"] > div,
    div[data-testid="stNumberInput"] input {{
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
        font-family: var(--font-primary);
    }}

    div[data-baseweb="select"] > div:hover,
    div[data-testid="stNumberInput"] input:hover {{
        border-color: rgba(212, 165, 116, 0.3) !important;
    }}

    div[data-baseweb="select"] > div:focus,
    div[data-testid="stNumberInput"] input:focus {{
        border-color: #D4A574 !important;
        box-shadow: 0 0 0 3px rgba(212, 165, 116, 0.1) !important;
    }}

    /* Botón principal */
    div[data-testid="stFormSubmitButton"] button {{
        background: var(--gradient-accent) !important;
        color: #0F172A !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        min-height: 3.2rem !important;
        box-shadow: 0 4px 20px rgba(212, 165, 116, 0.25);
        transition: all 0.3s ease;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        font-family: var(--font-display);
    }}

    div[data-testid="stFormSubmitButton"] button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(212, 165, 116, 0.35);
    }}

    div[data-testid="stFormSubmitButton"] button:active {{
        transform: translateY(0px);
    }}

    /* Tarjeta de resultados */
    .result-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        box-shadow: var(--shadow-card);
        padding: 1.5rem 2rem;
        margin-top: 1.5rem;
        position: relative;
        overflow: hidden;
    }}

    .result-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-accent);
    }}

    .result-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }}

    .result-label {{
        color: var(--text-muted);
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .status-complete {{
        color: #10B981;
        font-family: var(--font-display);
        font-size: 2rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .status-canceled {{
        color: #EF4444;
        font-family: var(--font-display);
        font-size: 2rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .result-id {{
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.5rem 0 0 0;
        font-family: var(--font-primary);
    }}

    .result-id code {{
        background: var(--bg-input);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        color: var(--text-gold);
        font-weight: 600;
        border: 1px solid var(--border-color);
    }}

    /* Métricas elegantes */
    .metric-container {{
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }}

    .metric-box {{
        flex: 1;
        background: var(--bg-input);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }}

    .metric-box:hover {{
        border-color: rgba(212, 165, 116, 0.2);
        transform: translateY(-2px);
    }}

    .metric-label {{
        color: var(--text-muted);
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }}

    .metric-value {{
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 800;
        font-family: var(--font-display);
    }}

    .metric-value.gold {{
        color: var(--gold-light);
    }}

    .metric-value.complete {{
        color: #10B981;
    }}

    .metric-value.canceled {{
        color: #EF4444;
    }}

    /* Expander mejorado */
    .streamlit-expanderHeader {{
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
    }}

    .streamlit-expanderHeader:hover {{
        border-color: rgba(212, 165, 116, 0.2) !important;
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
# FUNCIONES AUXILIARES
# =============================================================================

def generar_customer_id() -> str:
    """Genera un identificador único para el cliente."""

    return f"CUST-{uuid4().hex[:8].upper()}"


def generar_order_id() -> str:
    """Genera un identificador único para el pedido."""

    return f"ORD-{uuid4().hex[:10].upper()}"


def obtener_dias_programados(modo_envio: str) -> int:
    """Asigna días programados según el modo de envío real."""

    mapa_dias = {
        "Same Day": 1,
        "First Class": 2,
        "Second Class": 4,
        "Standard Class": 6,
    }

    return mapa_dias.get(modo_envio, 0)


def limpiar_columna_texto(serie: pd.Series) -> pd.Series:
    """Normaliza una columna de texto sin modificar sus categorías."""

    return (
        serie
        .dropna()
        .astype(str)
        .str.strip()
    )


@st.cache_data(show_spinner=False)
def cargar_opciones_dataset() -> dict:
    """
    Obtiene países, ciudades, regiones, orígenes y pagos
    directamente desde el CSV limpio.
    """

    if not RUTA_DATASET.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en: {RUTA_DATASET}"
        )

    columnas_requeridas = [
        "ciudad_destino",
        "pais_destino",
        "ciudad_cliente",
        "categoria",
        "region_destino",
        "modo_envio",
        "tipo_transaccion",
    ]

    df = pd.read_csv(
        RUTA_DATASET,
        usecols=columnas_requeridas,
        low_memory=False,
    )

    for columna in columnas_requeridas:
        df[columna] = (
            df[columna]
            .astype("string")
            .str.strip()
        )

    ubicaciones_destino = (
        df[
            [
                "pais_destino",
                "ciudad_destino",
                "region_destino",
            ]
        ]
        .dropna()
        .drop_duplicates()
    )

    ciudades_origen = sorted(
        set(
            limpiar_columna_texto(
                df["ciudad_cliente"]
            ).tolist()
        )
        |
        set(
            limpiar_columna_texto(
                df["ciudad_destino"]
            ).tolist()
        )
    )

    metodos_pago = sorted(
        limpiar_columna_texto(
            df["tipo_transaccion"]
        )
        .unique()
        .tolist()
    )

    return {
        "ubicaciones_destino": ubicaciones_destino,
        "paises_destino": sorted(
            ubicaciones_destino[
                "pais_destino"
            ]
            .dropna()
            .unique()
            .tolist()
        ),
        "ciudades_origen": ciudades_origen,
        "metodos_pago": metodos_pago,
    }


def obtener_ciudades_por_pais(
    ubicaciones: pd.DataFrame,
    pais: str,
) -> list[str]:
    """Devuelve únicamente las ciudades del país seleccionado."""

    if pais == "Selecciona un país":
        return []

    ciudades = (
        ubicaciones.loc[
            ubicaciones["pais_destino"] == pais,
            "ciudad_destino",
        ]
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )

    return ciudades


def obtener_region_pais(
    ubicaciones: pd.DataFrame,
    pais: str,
) -> str:
    """
    Calcula la región más frecuente asociada al país
    dentro del dataset.
    """

    if pais == "Selecciona un país":
        return ""

    regiones = (
        ubicaciones.loc[
            ubicaciones["pais_destino"] == pais,
            "region_destino",
        ]
        .dropna()
    )

    if regiones.empty:
        return ""

    return str(regiones.mode().iloc[0])


def validar_formulario(
    pais_destino: str,
    ciudad_destino: str,
    region_destino: str,
    categoria: str,
    precio_base: float,
    cantidad: int,
    margen_ganancia_item: float,
    ventas_cliente: float,
    almacen_origen: str,
    modo_envio: str,
    dias_envio_real: int,
    metodo_pago: str,
) -> list[str]:
    """Valida todos los campos antes de ejecutar el modelo."""

    errores = []

    if pais_destino == "Selecciona un país":
        errores.append(
            "Debes seleccionar un país de destino."
        )

    if ciudad_destino == "Selecciona una ciudad":
        errores.append(
            "Debes seleccionar una ciudad de destino."
        )

    if not region_destino:
        errores.append(
            "No se pudo determinar la región del destino."
        )

    if categoria == "Selecciona una categoría":
        errores.append(
            "Debes seleccionar una categoría de producto."
        )

    if precio_base <= 0:
        errores.append(
            "El precio unitario debe ser mayor que cero."
        )

    if cantidad <= 0:
        errores.append(
            "La cantidad debe ser mayor que cero."
        )

    if margen_ganancia_item < 0:
        errores.append(
            "La ganancia estimada no puede ser negativa."
        )

    if ventas_cliente < 0:
        errores.append(
            "Las ventas históricas no pueden ser negativas."
        )

    if almacen_origen == "Selecciona una ciudad de salida":
        errores.append(
            "Debes seleccionar una ciudad de salida."
        )

    if modo_envio == "Selecciona un modo de envío":
        errores.append(
            "Debes seleccionar un modo de envío."
        )

    if dias_envio_real < 0:
        errores.append(
            "Los días reales del envío no pueden ser negativos."
        )

    if metodo_pago == "Selecciona un método de pago":
        errores.append(
            "Debes seleccionar un método de pago."
        )

    return errores


# =============================================================================
# CARGA DE OPCIONES DEL MODELO Y DATASET
# =============================================================================

try:
    opciones_modelo = obtener_opciones_modelo()
    metadata_modelo = obtener_metadata_modelo()
    opciones_dataset = cargar_opciones_dataset()

except (ErrorPredictorSupervisado, FileNotFoundError) as error:
    st.error(
        "No fue posible cargar los datos necesarios "
        "para la aplicación."
    )
    st.code(str(error))
    st.stop()

except Exception as error:
    st.error(
        "Ocurrió un error al cargar el modelo o el dataset."
    )
    st.exception(error)
    st.stop()


categorias_producto = sorted(
    opciones_modelo.get("categoria", [])
)

modos_envio = sorted(
    opciones_modelo.get("modo_envio", [])
)

regiones_modelo = sorted(
    opciones_modelo.get("region_destino", [])
)

ubicaciones_destino = opciones_dataset[
    "ubicaciones_destino"
]

paises_destino = opciones_dataset[
    "paises_destino"
]

ciudades_origen = opciones_dataset[
    "ciudades_origen"
]

metodos_pago = opciones_dataset[
    "metodos_pago"
]


# =============================================================================
# ENCABEZADO MEJORADO
# =============================================================================

nombre_modelo = metadata_modelo.get(
    "modelo",
    "Modelo supervisado",
)

metricas = metadata_modelo.get(
    "metricas_test",
    {},
)

f1_modelo = float(
    metricas.get("f1", 0)
)

roc_auc_modelo = float(
    metricas.get("roc_auc", 0)
)

st.markdown(
    f"""
<div class="main-header">
    <div class="header-top">
        <div>
            <div class="header-brand">
                <span class="header-icon">✦</span>
                <h1 class="header-title">Realizar Pedido</h1>
            </div>
            <p class="header-subtitle">
                Sistema de Predicción de Estado de Pedidos · GDLM
            </p>
        </div>
    </div>
    <div class="header-divider"></div>
    <div class="header-meta">
        <div class="header-meta-item">
            Modelo: <strong>{nombre_modelo}</strong>
        </div>
        <div class="header-meta-item">
            Precisión F1: <strong>{f1_modelo:.4f}</strong>
        </div>
        <div class="header-meta-item">
            AUC-ROC: <strong>{roc_auc_modelo:.4f}</strong>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# SELECTORES GEOGRÁFICOS
# =============================================================================

st.markdown(
    """
<div class="section-card">
    <div class="section-title">
        <span class="emoji">👤</span> Información del Cliente y Destino
    </div>
    <p class="section-description">
        El Customer ID y el Order ID serán generados automáticamente.
        Selecciona el país para cargar sus ciudades disponibles.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    pais_destino = st.selectbox(
        "País de destino *",
        options=[
            "Selecciona un país",
            *paises_destino,
        ],
        key="pais_destino_pedido",
    )

ciudades_disponibles = obtener_ciudades_por_pais(
    ubicaciones_destino,
    pais_destino,
)

with col2:
    ciudad_destino = st.selectbox(
        "Ciudad de destino *",
        options=[
            "Selecciona una ciudad",
            *ciudades_disponibles,
        ],
        disabled=(
            pais_destino == "Selecciona un país"
        ),
        key="ciudad_destino_pedido",
    )

region_detectada = obtener_region_pais(
    ubicaciones_destino,
    pais_destino,
)

if (
    region_detectada
    and region_detectada not in regiones_modelo
):
    region_detectada = ""

with col3:
    region_destino = st.selectbox(
        "Región de destino del modelo *",
        options=(
            [region_detectada]
            if region_detectada
            else ["No determinada"]
        ),
        disabled=True,
        help=(
            "La región se obtiene automáticamente "
            "según el país seleccionado."
        ),
        key="region_destino_pedido",
    )

if region_destino == "No determinada":
    region_destino = ""


# =============================================================================
# FORMULARIO PRINCIPAL
# =============================================================================

with st.form(
    "formulario_pedido",
    clear_on_submit=False,
):

    # -------------------------------------------------------------------------
    # PRODUCTO
    # -------------------------------------------------------------------------

    st.markdown(
        """
<div class="section-card">
    <div class="section-title">
        <span class="emoji">📦</span> Información del Producto
    </div>
    <p class="section-description">
        Las categorías disponibles provienen directamente
        del conjunto de datos utilizado para entrenar el modelo.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        categoria = st.selectbox(
            "Categoría del producto *",
            options=[
                "Selecciona una categoría",
                *categorias_producto,
            ],
        )

    with col2:
        precio_base = st.number_input(
            "Precio unitario (USD) *",
            min_value=0.01,
            value=100.00,
            step=1.00,
            format="%.2f",
        )

    with col3:
        cantidad = st.number_input(
            "Cantidad de artículos *",
            min_value=1,
            value=1,
            step=1,
        )

    col1, col2 = st.columns(2)

    with col1:
        margen_ganancia_item = st.number_input(
            "Ganancia estimada por artículo (USD) *",
            min_value=0.00,
            value=10.00,
            step=1.00,
            format="%.2f",
            help=(
                "Ganancia monetaria aproximada "
                "obtenida por cada unidad."
            ),
        )

    with col2:
        ventas_cliente = st.number_input(
            "Ventas históricas del cliente (USD) *",
            min_value=0.00,
            value=100.00,
            step=10.00,
            format="%.2f",
            help=(
                "Valor acumulado aproximado de "
                "compras anteriores del cliente."
            ),
        )

    # -------------------------------------------------------------------------
    # LOGÍSTICA
    # -------------------------------------------------------------------------

    st.markdown(
        """
<div class="section-card">
    <div class="section-title">
        <span class="emoji">🚚</span> Información Logística
    </div>
    <p class="section-description">
        La ciudad de origen, el modo de envío y los valores
        logísticos se seleccionan mediante datos controlados.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        almacen_origen = st.selectbox(
            "Ciudad de origen *",
            options=[
                "Selecciona una ciudad de salida",
                *ciudades_origen,
            ],
        )

    with col2:
        modo_envio = st.selectbox(
            "Modo de envío *",
            options=[
                "Selecciona un modo de envío",
                *modos_envio,
            ],
        )

    dias_envio_programado = (
        obtener_dias_programados(modo_envio)
        if modo_envio
        != "Selecciona un modo de envío"
        else 0
    )

    with col3:
        st.number_input(
            "Días de envío programados",
            min_value=0,
            value=dias_envio_programado,
            disabled=True,
            help=(
                "El sistema calcula este valor según "
                "el modo de envío seleccionado."
            ),
        )

    col1, col2 = st.columns(2)

    with col1:
        dias_envio_real = st.number_input(
            "Días reales del envío *",
            min_value=0,
            value=dias_envio_programado,
            step=1,
            help=(
                "Dato operativo utilizado por el modelo. "
                "Posteriormente podrá actualizarse desde "
                "el seguimiento del pedido."
            ),
        )

    with col2:
        umbral_alerta = st.slider(
            "Umbral mínimo para considerar COMPLETE",
            min_value=0.00,
            max_value=1.00,
            value=0.65,
            step=0.05,
            help=(
                "Si la probabilidad de COMPLETE está "
                "por debajo del umbral, se genera una alerta."
            ),
        )

    # -------------------------------------------------------------------------
    # PAGO
    # -------------------------------------------------------------------------

    st.markdown(
        """
<div class="section-card">
    <div class="section-title">
        <span class="emoji">💳</span> Información de Pago
    </div>
    <p class="section-description">
        Los métodos disponibles provienen del dataset real.
        Se almacenarán junto con el pedido.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    metodo_pago = st.selectbox(
        "Método de pago *",
        options=[
            "Selecciona un método de pago",
            *metodos_pago,
        ],
    )

    enviar_formulario = st.form_submit_button(
        "🔮 Predecir Pedido",
        use_container_width=True,
    )


# =============================================================================
# EJECUCIÓN DE LA PREDICCIÓN
# =============================================================================

if enviar_formulario:

    errores = validar_formulario(
        pais_destino=pais_destino,
        ciudad_destino=ciudad_destino,
        region_destino=region_destino,
        categoria=categoria,
        precio_base=float(precio_base),
        cantidad=int(cantidad),
        margen_ganancia_item=float(
            margen_ganancia_item
        ),
        ventas_cliente=float(ventas_cliente),
        almacen_origen=almacen_origen,
        modo_envio=modo_envio,
        dias_envio_real=int(dias_envio_real),
        metodo_pago=metodo_pago,
    )

    if errores:
        for mensaje_error in errores:
            st.error(f"⚠️ {mensaje_error}")

    else:
        customer_id = generar_customer_id()
        order_id = generar_order_id()

        cantidad_entera = int(cantidad)

        ventas = (
            float(precio_base)
            * cantidad_entera
        )

        total_item = ventas

        ganancia_pedido = (
            float(margen_ganancia_item)
            * cantidad_entera
        )

        beneficio_pedido = ganancia_pedido

        riesgo_retraso = int(
            dias_envio_real
            > dias_envio_programado
        )

        # =====================================================================
        # DATOS PARA EL MODELO SUPERVISADO
        # =====================================================================
        
        datos_modelo = {
            "dias_envio_real": int(
                dias_envio_real
            ),
            "dias_envio_prog": int(
                dias_envio_programado
            ),
            "beneficio_pedido": float(
                beneficio_pedido
            ),
            "ventas_cliente": float(
                ventas_cliente
            ),
            "precio_base": float(
                precio_base
            ),
            "margen_ganancia_item": float(
                margen_ganancia_item
            ),
            "cantidad": cantidad_entera,
            "ventas": float(ventas),
            "total_item": float(total_item),
            "ganancia_pedido": float(
                ganancia_pedido
            ),
            "riesgo_retraso": riesgo_retraso,
            "es_anomalia": 0,
            "es_outlier": 0,
            "cluster_kmeans": 0,
            "cluster_dbscan": -1,
            "modo_envio": modo_envio,
            "categoria": categoria,
            "region_destino": region_destino,
        }

        # =====================================================================
        # DATOS PARA EL MODELO K-MEANS (NO SUPERVISADO)
        # =====================================================================
        
        # Construir diccionario con los datos necesarios para K-Means
        datos_kmeans = {
            "dias_envio_real": int(dias_envio_real),
            "dias_envio_prog": int(dias_envio_programado),
            "beneficio_pedido": float(beneficio_pedido),
            "ventas_cliente": float(ventas_cliente),
            "precio_base": float(precio_base),
            "margen_ganancia_item": float(margen_ganancia_item),
            "cantidad": cantidad_entera,
            "ventas": float(ventas),
            "riesgo_retraso": riesgo_retraso,
            "tipo_transaccion": metodo_pago,
            "modo_envio": modo_envio,
            "categoria": categoria,
            "region_destino": region_destino,
        }

        try:
            with st.spinner(
                "Procesando el pedido y ejecutando "
                "el modelo supervisado..."
            ):
                # PREDICCIÓN SUPERVISADA
                resultado = predecir_pedido(
                    datos=datos_modelo,
                    umbral_alerta=float(
                        umbral_alerta
                    ),
                )

            # =================================================================
            # PREDICCIÓN NO SUPERVISADA (K-MEANS)
            # =================================================================
            
            resultado_cluster = predecir_cluster(
                datos=datos_kmeans
            )

            # =================================================================
            # GUARDAR EN SESSION STATE
            # =================================================================
            
            pedido = {
                "order_id": order_id,
                "customer_id": customer_id,
                "ciudad_destino": ciudad_destino,
                "pais_destino": pais_destino,
                "region_destino": region_destino,
                "almacen_origen": almacen_origen,
                "categoria": categoria,
                "precio_base": float(
                    precio_base
                ),
                "cantidad": cantidad_entera,
                "ventas": float(ventas),
                "margen_ganancia_item": float(
                    margen_ganancia_item
                ),
                "ganancia_pedido": float(
                    ganancia_pedido
                ),
                "ventas_cliente": float(
                    ventas_cliente
                ),
                "modo_envio": modo_envio,
                "dias_envio_programado": int(
                    dias_envio_programado
                ),
                "dias_envio_real": int(
                    dias_envio_real
                ),
                "metodo_pago": metodo_pago,
                "fecha_registro": (
                    datetime.now().isoformat()
                ),
            }

            st.session_state.pedido_actual = pedido

            st.session_state.resultado_prediccion = (
                resultado
            )

            st.session_state.datos_modelo_actual = (
                datos_modelo
            )

            # GUARDAR RESULTADOS DE K-MEANS
            st.session_state.resultado_cluster = (
                resultado_cluster
            )

            st.session_state.datos_kmeans_actual = (
                datos_kmeans
            )

            estado = resultado["estado"]

            clase_estado = (
                "status-complete"
                if estado == "COMPLETE"
                else "status-canceled"
            )

            icono_estado = (
                "✅"
                if estado == "COMPLETE"
                else "❌"
            )

            # RESULTADO MEJORADO
            st.markdown(
                f"""
<div class="result-card">
    <div class="result-header">
        <span class="result-label">Resultado de la Predicción</span>
    </div>
    <div class="{clase_estado}">
        {icono_estado} {estado}
    </div>
    <p class="result-id">
        Pedido: <code>{order_id}</code> · Cliente: <code>{customer_id}</code>
    </p>
</div>
""",
                unsafe_allow_html=True,
            )

            # Métricas mejoradas
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f"""
<div class="metric-box">
    <div class="metric-label">Probabilidad COMPLETE</div>
    <div class="metric-value complete">{resultado['porcentaje_complete']:.2f}%</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
<div class="metric-box">
    <div class="metric-label">Probabilidad CANCELED</div>
    <div class="metric-value canceled">{resultado['porcentaje_canceled']:.2f}%</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
<div class="metric-box">
    <div class="metric-label">Nivel de Riesgo</div>
    <div class="metric-value gold">{resultado['nivel_riesgo']}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            if resultado["alerta"]:
                st.warning(
                    "⚠️ La probabilidad de completar "
                    "el pedido es inferior al umbral."
                )
            else:
                st.success(
                    "✅ La predicción supera el "
                    "umbral configurado."
                )

            with st.expander(
                "📋 Ver resumen completo del pedido"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(
                        f"""
**Identificación**

- ID del pedido: `{order_id}`
- ID del cliente: `{customer_id}`

**Destino**

- Ciudad: {ciudad_destino}
- País: {pais_destino}
- Región: {region_destino}

**Producto**

- Categoría: {categoria}
- Precio unitario: ${precio_base:,.2f}
- Cantidad: {cantidad_entera}
- Venta total: ${ventas:,.2f}
"""
                    )

                with col2:
                    retraso_texto = (
                        "Sí"
                        if riesgo_retraso
                        else "No"
                    )

                    alerta_texto = (
                        "Sí"
                        if resultado["alerta"]
                        else "No"
                    )

                    st.markdown(
                        f"""
**Logística**

- Origen: {almacen_origen}
- Modo: {modo_envio}
- Días programados: {dias_envio_programado}
- Días reales: {dias_envio_real}
- Riesgo de retraso: {retraso_texto}

**Pago**

- Método: {metodo_pago}

**Resultado**

- Estado: **{estado}**
- Nivel de riesgo: {resultado["nivel_riesgo"]}
- Alerta: {alerta_texto}
"""
                    )

        except ArtefactoNoEncontradoError as error:
            st.error(
                "Faltan archivos necesarios del modelo."
            )
            st.code(str(error))

        except DatosPrediccionError as error:
            st.error(
                f"Los datos no pudieron procesarse: {error}"
            )

        except ErrorPredictorSupervisado as error:
            st.error(
                f"Falló la predicción del modelo: {error}"
            )

        # MANEJO DE ERRORES PARA K-MEANS
        except ArtefactoKMeansNoEncontradoError as error:
            st.error(
                "Faltan archivos necesarios del modelo K-Means."
            )
            st.code(str(error))

        except DatosKMeansError as error:
            st.error(
                f"Los datos para K-Means no pudieron procesarse: {error}"
            )

        except ErrorPredictorNoSupervisado as error:
            st.error(
                f"Falló la predicción del modelo K-Means: {error}"
            )

        except Exception as error:
            st.error(
                "Ocurrió un error inesperado al "
                "procesar el pedido."
            )
            st.exception(error)


# =============================================================================
# BOTÓN PARA PÁGINA DE PREDICCIÓN
# =============================================================================

if st.session_state.get(
    "resultado_prediccion"
):

    st.markdown("---")

    if st.button(
        "🤖 Ver detalle en la página Predicción",
        use_container_width=True,
    ):
        try:
            st.switch_page(
                "pages/prediccion.py"
            )
        except Exception:
            st.info(
                "La predicción quedó guardada. "
                "Abre Predicción desde el menú."
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
        ◆ GDLM · Sistema Inteligente para Predicción del Estado de Pedidos
    </p>
    <p style="font-size:0.58rem; color:var(--text-muted); opacity:0.6; margin:0.3rem 0 0 0;">
        {fecha_actual}
    </p>
</div>
""",
    unsafe_allow_html=True,
)