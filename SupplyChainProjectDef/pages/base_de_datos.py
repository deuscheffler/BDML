"""
🗄️ Base de Datos - GDLM

Página de monitoreo y consulta de las bases de datos
utilizadas por el sistema GDLM.
"""

from datetime import datetime
import streamlit as st


# =============================================================================
# ESTADO GLOBAL
# =============================================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


# =============================================================================
# CSS - MISMO ESTILO DEL PROYECTO
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    :root {{
        --gold: #D4A574;
        --gold-light: #E8C9A0;
        --emerald: #10B981;
        --ruby: #EF4444;
        --blue: #3B82F6;
        --violet: #8B5CF6;
        --amber: #F59E0B;
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

    .section-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin: 1.5rem 0 1rem 0;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}

    .section-card:hover {{
        border-color: rgba(212,165,116,0.2);
        box-shadow: var(--shadow-hover);
    }}

    .section-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-accent);
        opacity: 0.6;
    }}

    .section-title {{
        color: var(--text-primary);
        font-family: var(--font-display);
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }}

    .section-description {{
        color: var(--text-muted);
        font-size: 0.8rem;
        margin: 0.3rem 0 0 0;
    }}

    .metric-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 15px;
        padding: 1.2rem 1rem;
        text-align: center;
        box-shadow: var(--shadow-card);
        min-height: 120px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        cursor: default;
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
        font-size: 1.4rem;
        font-weight: 900;
        margin-top: 0.35rem;
    }}

    .metric-status {{
        font-size: 0.75rem;
        margin-top: 0.25rem;
        font-weight: 600;
    }}

    .status-connected {{
        color: #10B981;
    }}

    .status-disconnected {{
        color: #EF4444;
    }}

    .status-pending {{
        color: #F59E0B;
    }}

    .info-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 1.2rem;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }}

    .info-card:hover {{
        transform: translateY(-3px);
        box-shadow: var(--shadow-hover);
        border-color: rgba(212,165,116,0.25);
    }}

    .info-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-accent);
        opacity: 0.4;
    }}

    .info-card-title {{
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
    }}

    .info-card-subtitle {{
        color: var(--text-muted);
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0 0 0.5rem 0;
    }}

    .info-card-description {{
        color: var(--text-secondary);
        font-size: 0.78rem;
        line-height: 1.5;
        margin: 0;
    }}

    .info-card-icon {{
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
    }}

    .table-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 1.2rem;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
        min-height: 140px;
    }}

    .table-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
        border-color: rgba(212,165,116,0.25);
    }}

    .table-card-title {{
        color: var(--text-primary);
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .table-card-description {{
        color: var(--text-secondary);
        font-size: 0.75rem;
        line-height: 1.4;
        margin: 0.3rem 0 0 0;
    }}

    .divider {{
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 1.5rem 0;
    }}

    .placeholder-text {{
        color: var(--text-muted);
        font-size: 0.85rem;
        text-align: center;
        padding: 1.5rem 0;
    }}

    .system-badge {{
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        background: var(--bg-input);
        border: 1px solid var(--border-color);
        color: var(--text-secondary);
    }}

    .interactive-hover {{
        transition: all 0.3s ease;
        cursor: pointer;
    }}

    .interactive-hover:hover {{
        transform: translateY(-2px);
    }}

    .pulse {{
        animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
        0% {{
            opacity: 1;
        }}
        50% {{
            opacity: 0.5;
        }}
        100% {{
            opacity: 1;
        }}
    }}

    div[data-testid="stImage"] img {{
        border-radius: 13px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-card);
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
# ENCABEZADO
# =============================================================================

st.markdown(
    """
<div class="main-header">
    <div class="header-content">
        <h1 class="main-title">🗄️ Base de Datos</h1>
        <p class="main-subtitle">
            Monitoreo y consulta de las bases de datos del sistema GDLM
        </p>
        <div class="header-divider"></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# SECCIÓN 1: ESTADO DE CONEXIONES
# =============================================================================

st.markdown(
    """
<div class="section-card">
    <div class="section-title">🔌 Estado de Conexiones</div>
    <div class="section-description">Estado actual de las conexiones a las bases de datos</div>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
<div class="metric-card">
    <div class="metric-label">SQL Server</div>
    <div class="metric-value" style="font-size:1.2rem; color:#E8C9A0;">OMEGA-DELL</div>
    <div class="metric-status status-pending">🟡 Pendiente de conexión</div>
    <div style="font-size:0.7rem; color:var(--text-muted); margin-top:0.3rem;">
        Base: BD_ML_RELACIONAL
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="metric-card">
    <div class="metric-label">MongoDB Atlas</div>
    <div class="metric-value" style="font-size:1.2rem; color:#E8C9A0;">Atlas Cluster</div>
    <div class="metric-status status-pending">🟡 Pendiente de conexión</div>
    <div style="font-size:0.7rem; color:var(--text-muted); margin-top:0.3rem;">
        Base: supply_chain · Colección: orders
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# SECCIÓN 2: ARQUITECTURA HÍBRIDA
# =============================================================================

st.markdown(
    """
<div class="section-card">
    <div class="section-title">🏗️ Arquitectura Híbrida</div>
    <div class="section-description">Distribución de datos entre bases relacionales y NoSQL</div>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
<div class="info-card">
    <div class="info-card-icon">🗄️</div>
    <div class="info-card-title">SQL Server</div>
    <div class="info-card-subtitle">Información transaccional del negocio</div>
    <div class="info-card-description">
        <strong>Almacena:</strong><br>
        • Categorías<br>
        • Productos<br>
        • Destinos<br>
        • Ubicación del cliente<br>
        • Pedidos
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="info-card">
    <div class="info-card-icon">🍃</div>
    <div class="info-card-title">MongoDB Atlas</div>
    <div class="info-card-subtitle">Resultados del Machine Learning</div>
    <div class="info-card-description">
        <strong>Almacena:</strong><br>
        • Predicciones<br>
        • Probabilidades<br>
        • Clusters<br>
        • Riesgo<br>
        • Anomalías<br>
        • Fecha de ejecución
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# SECCIÓN 3: TABLAS RELACIONALES
# =============================================================================

st.markdown(
    """
<div class="section-card">
    <div class="section-title">📋 Tablas Relacionales</div>
    <div class="section-description">Estructura de las tablas en SQL Server</div>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        """
<div class="table-card">
    <div class="table-card-title">📂 Categoria</div>
    <div class="table-card-description">
        Clasificación de productos
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="table-card">
    <div class="table-card-title">📦 Producto</div>
    <div class="table-card-description">
        Catálogo de productos
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
<div class="table-card">
    <div class="table-card-title">📍 Destino</div>
    <div class="table-card-description">
        Ubicaciones de entrega
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
<div class="table-card">
    <div class="table-card-title">👤 UbicacionCliente</div>
    <div class="table-card-description">
        Ubicaciones de clientes
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        """
<div class="table-card">
    <div class="table-card-title">📄 Pedido</div>
    <div class="table-card-description">
        Registro de pedidos
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# SECCIÓN 4: VISTAS DISPONIBLES
# =============================================================================

st.markdown(
    """
<div class="section-card">
    <div class="section-title">👁️ Vistas Disponibles</div>
    <div class="section-description">Vistas predefinidas en SQL Server</div>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
<div class="info-card">
    <div class="info-card-title">📊 vw_ETL_Pedido</div>
    <div class="info-card-description">
        Vista ETL para el procesamiento de pedidos
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="info-card">
    <div class="info-card-title">🤖 vw_ML_DataCoSupplyChain</div>
    <div class="info-card-description">
        Vista preparada para los modelos de Machine Learning
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
<div class="info-card">
    <div class="info-card-title">📈 vw_ResumenPedidos</div>
    <div class="info-card-description">
        Vista de resumen y métricas de pedidos
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# SECCIÓN 5: PROCEDIMIENTOS ALMACENADOS
# =============================================================================

st.markdown(
    """
<div class="section-card">
    <div class="section-title">⚙️ Procedimientos Almacenados</div>
    <div class="section-description">Procedimientos disponibles en SQL Server</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="info-card">
    <div class="info-card-title">🧠 sp_DatasetML</div>
    <div class="info-card-description">
        Procedimiento encargado de generar el conjunto analítico utilizado por los modelos de Machine Learning del sistema GDLM.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# SECCIÓN 6: RESUMEN DEL SISTEMA
# =============================================================================

st.markdown(
    """
<div class="section-card">
    <div class="section-title">📊 Resumen del Sistema</div>
    <div class="section-description">Componentes principales del ecosistema GDLM</div>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        """
<div class="metric-card" style="min-height:100px;">
    <div class="metric-label">Modelo Supervisado</div>
    <div class="metric-value" style="font-size:1.5rem; color:#10B981;">KNN</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="metric-card" style="min-height:100px;">
    <div class="metric-label">Modelo No Supervisado</div>
    <div class="metric-value" style="font-size:1.5rem; color:#E8C9A0;">K-Means</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
<div class="metric-card" style="min-height:100px;">
    <div class="metric-label">Base Relacional</div>
    <div class="metric-value" style="font-size:1.3rem; color:#3B82F6;">SQL Server</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
<div class="metric-card" style="min-height:100px;">
    <div class="metric-label">Base NoSQL</div>
    <div class="metric-value" style="font-size:1.3rem; color:#8B5CF6;">MongoDB Atlas</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        """
<div class="metric-card" style="min-height:100px;">
    <div class="metric-label">Arquitectura</div>
    <div class="metric-value" style="font-size:1.3rem; color:#D4A574;">Híbrida</div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# SECCIÓN 7: CONSULTAS Y REGISTROS
# =============================================================================

st.markdown(
    """
<div class="section-card">
    <div class="section-title">🔍 Consultas y Registros</div>
    <div class="section-description">Espacio preparado para consultas de datos</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="info-card" style="text-align:center; padding:2rem;">
    <div style="font-size:2.5rem; margin-bottom:0.5rem;">📊</div>
    <div class="info-card-title" style="font-size:1rem;">Próximamente</div>
    <div class="info-card-description" style="font-size:0.85rem; max-width:600px; margin:0 auto;">
        Próximamente esta sección permitirá consultar los registros almacenados en 
        <strong>SQL Server</strong> y <strong>MongoDB Atlas</strong>, incluyendo pedidos, 
        predicciones, segmentación K-Means y métricas históricas del sistema.
    </div>
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
<hr class="divider">
<div style="text-align:center; padding:1rem 0 0.5rem 0;">
    <p style="font-size:0.7rem; color:var(--text-muted); font-family:var(--font-primary); margin:0;">
        ◆ GDLM · Monitoreo de Bases de Datos
    </p>
    <p style="font-size:0.58rem; color:var(--text-muted); opacity:0.6; margin:0.3rem 0 0 0;">
        {fecha_actual}
    </p>
</div>
""",
    unsafe_allow_html=True,
)