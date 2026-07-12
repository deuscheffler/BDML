"""
🤖 Predicción - GDLM

Página de detalle para visualizar la última predicción
generada desde realizar_pedido.py.
"""

from datetime import datetime
import streamlit as st


# =============================================================================
# ESTADO GLOBAL
# =============================================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


# =============================================================================
# CSS MEJORADO - ESTILO EJECUTIVO MODERNO
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
        --shadow-card: 0 8px 32px rgba(0,0,0,0.5);
        --shadow-hover: 0 12px 48px rgba(0,0,0,0.6);
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
        color: rgba(212, 165, 116, 0.08);
        font-weight: 300;
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
        width: 60px;
        height: 3px;
        margin-top: 0.6rem;
        border-radius: 4px;
        background: var(--gradient-accent);
    }}

    /* Tarjeta de estado */
    .status-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 18px;
        padding: 1.8rem;
        box-shadow: var(--shadow-card);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}

    .status-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-accent);
    }}

    .status-card:hover {{
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }}

    .status-label {{
        color: var(--text-muted);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}

    .status-value {{
        font-family: var(--font-display);
        font-weight: 900;
        font-size: 2.5rem;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .status-complete {{
        color: #10B981;
    }}

    .status-canceled {{
        color: #EF4444;
    }}

    .status-id {{
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.75rem;
        font-weight: 500;
    }}

    .status-id code {{
        background: var(--bg-input);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
        color: var(--text-gold);
        font-weight: 600;
        border: 1px solid var(--border-color);
        font-family: 'SF Mono', monospace;
    }}

    /* Tarjeta de métricas */
    .metric-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }}

    .metric-card::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 25%;
        right: 25%;
        height: 2px;
        background: var(--gradient-accent);
        opacity: 0;
        transition: all 0.3s ease;
    }}

    .metric-card:hover {{
        box-shadow: var(--shadow-hover);
        transform: translateY(-4px);
    }}

    .metric-card:hover::after {{
        opacity: 1;
        left: 10%;
        right: 10%;
    }}

    .metric-label {{
        color: var(--text-muted);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }}

    .metric-value {{
        font-family: var(--font-display);
        font-size: 1.8rem;
        font-weight: 900;
        margin-top: 0.2rem;
    }}

    /* Tarjeta de sección - solo el encabezado */
    .section-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
    }}

    .section-card:hover {{
        box-shadow: var(--shadow-hover);
    }}

    .section-title {{
        color: var(--text-primary);
        font-family: var(--font-display);
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0 0 0.2rem 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }}

    .section-subtitle {{
        color: var(--text-muted);
        font-size: 0.8rem;
        margin: 0;
    }}

    /* Tarjeta vacía */
    .empty-card {{
        background: var(--bg-card);
        border: 2px dashed var(--border-color);
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        color: var(--text-secondary);
        box-shadow: var(--shadow-card);
    }}

    .empty-icon {{
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }}

    .empty-title {{
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: var(--text-primary);
    }}

    /* Botones */
    div[data-testid="stButton"] button {{
        background: var(--gradient-accent) !important;
        color: #0F172A !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        min-height: 3rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(212, 165, 116, 0.2) !important;
    }}

    div[data-testid="stButton"] button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(212, 165, 116, 0.35) !important;
    }}

    /* Expander mejorado */
    .streamlit-expanderHeader {{
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        font-size: 1rem !important;
    }}

    .streamlit-expanderHeader:hover {{
        border-color: rgba(212, 165, 116, 0.3) !important;
    }}

    /* Código en JSON */
    .stJson {{
        background: var(--bg-input) !important;
        border-radius: 10px !important;
        border: 1px solid var(--border-color) !important;
        padding: 0.5rem !important;
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

    /* Spinner personalizado */
    .stSpinner > div {{
        border-color: var(--gold) !important;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# OBTENER DATOS DE SESSION STATE
# =============================================================================

pedido = st.session_state.get("pedido_actual")
resultado = st.session_state.get("resultado_prediccion")
datos_modelo = st.session_state.get("datos_modelo_actual")

# OBTENER DATOS DEL MODELO K-MEANS
resultado_cluster = st.session_state.get("resultado_cluster")
datos_kmeans = st.session_state.get("datos_kmeans_actual")


# =============================================================================
# ENCABEZADO
# =============================================================================

st.markdown(
    """
<div class="main-header">
    <div class="header-content">
        <h1 class="main-title">🤖 Resultado del Modelo</h1>
        <p class="main-subtitle">
            Detalle completo de la predicción generada por el modelo supervisado
        </p>
        <div class="header-divider"></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# SIN PREDICCIÓN DISPONIBLE
# =============================================================================

if not pedido or not resultado:

    st.markdown(
        """
<div class="empty-card">
    <div class="empty-icon">🔮</div>
    <div class="empty-title">No hay una predicción disponible</div>
    <p style="color:var(--text-secondary); margin:0.5rem 0 1rem 0;">
        Primero debes registrar y predecir un pedido en la página
    </p>
    <p style="font-weight:600; color:var(--text-gold); margin:0;">
        📦 Realizar Pedido
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "📦 Ir a Realizar Pedido",
            use_container_width=True,
        ):
            try:
                st.switch_page("pages/realizar_pedido.py")
            except Exception:
                st.info(
                    "Abre la página Realizar Pedido desde el menú lateral."
                )

    st.stop()


# =============================================================================
# VARIABLES DEL RESULTADO
# =============================================================================

estado = resultado.get("estado", "DESCONOCIDO")
prob_complete = float(
    resultado.get("porcentaje_complete", 0)
)
prob_canceled = float(
    resultado.get("porcentaje_canceled", 0)
)
nivel_riesgo = resultado.get(
    "nivel_riesgo",
    "No determinado",
)
alerta = bool(
    resultado.get("alerta", False)
)

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

order_id = pedido.get("order_id", "N/D")
customer_id = pedido.get("customer_id", "N/D")


# =============================================================================
# 1. ESTADO PRINCIPAL
# =============================================================================

st.markdown(
    f"""
<div class="status-card">
    <div class="status-label">Estado Predicho</div>
    <div class="status-value {clase_estado}">
        {icono_estado} {estado}
    </div>
    <div class="status-id">
        ID del pedido: <code>{order_id}</code>
        &nbsp;&nbsp;·&nbsp;&nbsp;
        ID del cliente: <code>{customer_id}</code>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 2. MÉTRICAS PRINCIPALES (4 TARJETAS)
# =============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Probabilidad COMPLETE</div>
    <div class="metric-value" style="color:#10B981;">
        {prob_complete:.2f}%
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Probabilidad CANCELED</div>
    <div class="metric-value" style="color:#EF4444;">
        {prob_canceled:.2f}%
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Nivel de Riesgo</div>
    <div class="metric-value" style="color:#E8C9A0;">
        {nivel_riesgo}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col4:
    color_alerta = (
        "#EF4444"
        if alerta
        else "#10B981"
    )
    texto_alerta = "Sí" if alerta else "No"
    
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Alerta Activa</div>
    <div class="metric-value" style="color:{color_alerta};">
        {texto_alerta}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# 3. DISTRIBUCIÓN DE PROBABILIDADES
# =============================================================================

# Encabezado de la sección (completamente cerrado)
st.markdown(
    """
<div class="section-card">
    <div class="section-title">📊 Distribución de Probabilidades</div>
    <div class="section-subtitle">Comparativa visual de las probabilidades de cada estado</div>
</div>
""",
    unsafe_allow_html=True,
)

# Componentes nativos fuera del div
col1, col2 = st.columns([1, 4])
with col1:
    st.write("**COMPLETE**")
with col2:
    st.progress(prob_complete / 100, text=f"{prob_complete:.2f}%")

col1, col2 = st.columns([1, 4])
with col1:
    st.write("**CANCELED**")
with col2:
    st.progress(prob_canceled / 100, text=f"{prob_canceled:.2f}%")


# =============================================================================
# 4. INTERPRETACIÓN
# =============================================================================

if alerta:
    st.warning(
        "⚠️ **Alerta activa:** La probabilidad de completar el pedido está "
        "por debajo del umbral configurado. Se recomienda realizar "
        "seguimiento operativo."
    )
else:
    st.success(
        "✅ **Estado favorable:** La probabilidad de completar el pedido "
        "supera el umbral configurado."
    )


# =============================================================================
# 5. SEGMENTACIÓN NO SUPERVISADA (K-MEANS)
# =============================================================================

if resultado_cluster is not None:
    
    # Encabezado de la sección (completamente cerrado)
    st.markdown(
        """
<div class="section-card">
    <div class="section-title">🧠 Segmentación No Supervisada</div>
    <div class="section-subtitle">Perfil asignado por el modelo K-Means al pedido actual</div>
</div>
""",
        unsafe_allow_html=True,
    )
    
    # Componentes nativos fuera del div
    # Extraer datos del cluster
    cluster = resultado_cluster.get("cluster", "N/D")
    perfil = resultado_cluster.get("perfil", {})
    distancia = resultado_cluster.get("distancia_centroide", 0.0)
    umbral = resultado_cluster.get("umbral_anomalias", 0.0)
    es_anomalia = resultado_cluster.get("es_anomalia", False)
    
    # Datos del perfil
    nombre_perfil = perfil.get("nombre", f"Cluster {cluster}")
    descripcion = perfil.get("descripcion", "Perfil no disponible")
    pct_complete_hist = perfil.get("porcentaje_complete", 0.0)
    pct_canceled_hist = perfil.get("porcentaje_canceled", 0.0)
    tamano_cluster = perfil.get("tamano_cluster", 0.0)
    
    # 5.1 Métricas K-Means
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
<div class="metric-card">
    <div class="metric-label">Cluster Asignado</div>
    <div class="metric-value" style="color:#E8C9A0;">
        {cluster}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            f"""
<div class="metric-card">
    <div class="metric-label">Perfil</div>
    <div class="metric-value" style="font-size:1.2rem; color:#94A3B8;">
        {nombre_perfil}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    
    with col3:
        texto_anomalia = "Sí" if es_anomalia else "No"
        color_anomalia = "#EF4444" if es_anomalia else "#10B981"
        
        st.markdown(
            f"""
<div class="metric-card">
    <div class="metric-label">Anomalía</div>
    <div class="metric-value" style="color:{color_anomalia};">
        {texto_anomalia}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    
    with col4:
        st.markdown(
            f"""
<div class="metric-card">
    <div class="metric-label">Distancia al Centroide</div>
    <div class="metric-value" style="color:#94A3B8; font-size:1.4rem;">
        {distancia:.4f}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    
    # 5.2 Descripción y estadísticas del cluster
    st.markdown(f"""
**📋 Descripción del Segmento**

{descripcion}

**📊 Estadísticas Históricas del Cluster**
- Tamaño relativo: **{tamano_cluster:.1f}%** del total de pedidos
- COMPLETE histórico: **{pct_complete_hist:.2f}%**
- CANCELED histórico: **{pct_canceled_hist:.2f}%**
""")
    
    # 5.3 Barras de progreso históricas
    st.markdown("**Distribución histórica del cluster**")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.write("**COMPLETE**")
    with col2:
        st.progress(pct_complete_hist / 100, text=f"{pct_complete_hist:.2f}%")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.write("**CANCELED**")
    with col2:
        st.progress(pct_canceled_hist / 100, text=f"{pct_canceled_hist:.2f}%")
    
    # 5.4 Anomalías
    if es_anomalia:
        st.warning(
            "⚠️ El pedido presenta una combinación atípica respecto a los "
            "datos usados para entrenar K-Means."
        )
    else:
        st.success(
            "✅ El pedido se encuentra dentro del comportamiento esperado "
            "de su cluster."
        )
    
    # 5.5 Expander técnico K-Means
    with st.expander("🧪 Información Técnica K-Means"):
        
        st.markdown(f"""
**Modelo**
- Algoritmo: **KMeans**
- k óptimo: **{resultado_cluster.get('k_optimo', 'N/D')}**

**Métricas del modelo**
- Silhouette Score: **{resultado_cluster.get('silhouette', 0.0):.4f}**
- Calinski-Harabasz: **{resultado_cluster.get('calinski_harabasz', 0.0):.2f}**
- Davies-Bouldin: **{resultado_cluster.get('davies_bouldin', 0.0):.4f}**

**Detección de anomalías**
- Umbral de anomalías: **{umbral:.4f}**
- Distancia mínima del pedido: **{distancia:.4f}**
- ¿Es anomalía? **{"Sí" if es_anomalia else "No"}**

**Fecha de entrenamiento**
- {resultado_cluster.get('fecha_entrenamiento', 'No disponible')}
""")
        
        if datos_kmeans:
            st.markdown("**Variables enviadas al modelo K-Means**")
            st.json(datos_kmeans, expanded=False)

else:
    # Mensaje discreto si no hay resultado K-Means
    st.info(
        "ℹ️ No hay una segmentación K-Means disponible para este pedido. "
        "Asegúrate de que el modelo no supervisado esté configurado correctamente."
    )


# =============================================================================
# 6. INFORMACIÓN DEL PEDIDO
# =============================================================================

# Encabezado de la sección (completamente cerrado)
st.markdown(
    """
<div class="section-card">
    <div class="section-title">📦 Información del Pedido</div>
    <div class="section-subtitle">Datos completos del pedido analizado por el modelo</div>
</div>
""",
    unsafe_allow_html=True,
)

# Componentes nativos fuera del div
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
**Identificación**
- ID del pedido: `{order_id}`
- ID del cliente: `{customer_id}`

**Destino**
- País: {pedido.get("pais_destino", "N/D")}
- Ciudad: {pedido.get("ciudad_destino", "N/D")}
- Región: {pedido.get("region_destino", "N/D")}

**Producto**
- Categoría: {pedido.get("categoria", "N/D")}
- Precio unitario: ${pedido.get("precio_base", 0):,.2f}
- Cantidad: {pedido.get("cantidad", 0)}
- Venta total: ${pedido.get("ventas", 0):,.2f}
"""
    )

with col2:
    st.markdown(
        f"""
**Logística**
- Ciudad de origen: {pedido.get("almacen_origen", "N/D")}
- Modo de envío: {pedido.get("modo_envio", "N/D")}
- Días programados: {pedido.get("dias_envio_programado", 0)}
- Días reales: {pedido.get("dias_envio_real", 0)}

**Información Económica**
- Ganancia por artículo: ${pedido.get("margen_ganancia_item", 0):,.2f}
- Ganancia total: ${pedido.get("ganancia_pedido", 0):,.2f}
- Ventas históricas: ${pedido.get("ventas_cliente", 0):,.2f}

**Pago**
- Método: {pedido.get("metodo_pago", "N/D")}
"""
    )


# =============================================================================
# 7. INFORMACIÓN TÉCNICA SUPERVISADA (EXPANDER)
# =============================================================================

with st.expander("🧠 Información Técnica del Modelo Supervisado"):
    
    st.markdown(
        f"""
**Modelo Utilizado**
- Modelo: {resultado.get("modelo", "N/D")}
- Fecha de entrenamiento: {resultado.get("fecha_entrenamiento", "N/D")}
- Umbral de alerta: {resultado.get("umbral_alerta", 0):.2f}

**Resultados Técnicos**
- Probabilidad COMPLETE: {resultado.get("probabilidad_complete", 0):.6f}
- Probabilidad CANCELED: {resultado.get("probabilidad_canceled", 0):.6f}
- Nivel de riesgo: {nivel_riesgo}
- Alerta activa: {"Sí" if alerta else "No"}

**Fecha de consulta**: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
"""
    )
    
    if datos_modelo:
        st.markdown("**Variables enviadas al modelo supervisado**")
        st.json(datos_modelo, expanded=False)


# =============================================================================
# 8. ACCIONES
# =============================================================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "📦 Realizar otro pedido",
        use_container_width=True,
    ):
        try:
            st.switch_page("pages/realizar_pedido.py")
        except Exception:
            st.info(
                "Abre Realizar Pedido desde el menú lateral."
            )

with col2:
    if st.button(
        "🧹 Limpiar predicción actual",
        use_container_width=True,
    ):
        # Limpiar supervisado
        st.session_state.pedido_actual = None
        st.session_state.resultado_prediccion = None
        st.session_state.datos_modelo_actual = None
        
        # Limpiar no supervisado
        st.session_state.resultado_cluster = None
        st.session_state.datos_kmeans_actual = None
        
        st.rerun()


# =============================================================================
# 9. FOOTER
# =============================================================================

fecha_actual = datetime.now().strftime(
    "%d/%m/%Y %H:%M:%S"
)

st.markdown(
    f"""
<div style="text-align:center; padding:2rem 0 0.5rem 0; margin-top:2rem; border-top:1px solid var(--border-color);">
    <p style="font-size:0.7rem; color:var(--text-muted); font-family:var(--font-primary); margin:0;">
        ◆ GDLM · Detalle de Predicción Supervisada
    </p>
    <p style="font-size:0.58rem; color:var(--text-muted); opacity:0.6; margin:0.3rem 0 0 0;">
        {fecha_actual}
    </p>
</div>
""",
    unsafe_allow_html=True,
)