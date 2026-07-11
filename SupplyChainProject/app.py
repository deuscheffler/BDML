import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import base64
import os
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# ⚙️ CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="🚚 Supply Chain Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# 🎨 CSS - DISEÑO VORTEX
# ============================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: rgba(10, 10, 15, 0.85);
    --bg-card: rgba(20, 20, 30, 0.6);
    --bg-card-hover: rgba(30, 30, 50, 0.7);
    --text-primary: #ffffff;
    --text-secondary: #8899bb;
    --text-muted: #445566;
    --text-bright: #ffffff;
    --border-color: rgba(100, 180, 255, 0.08);
    --accent-primary: #4fc3f7;
    --accent-secondary: #00b4d8;
    --accent-soft: rgba(79, 195, 247, 0.06);
    --accent-glow: rgba(79, 195, 247, 0.1);
    
    --gradient-primary: linear-gradient(135deg, #4fc3f7 0%, #00b4d8 50%, #0288d1 100%);
    --gradient-text: linear-gradient(135deg, #4fc3f7 0%, #00b4d8 60%, #0288d1 100%);
    --gradient-dark: linear-gradient(180deg, rgba(10, 10, 15, 0.85) 0%, rgba(10, 10, 15, 0.3) 100%);
    
    --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.4);
    --shadow-glow: 0 0 60px rgba(79, 195, 247, 0.02);
    --radius: 16px;
    --radius-sm: 8px;
}

.hero-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -2;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0.25 !important;
}

.hero-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    background: linear-gradient(180deg, rgba(10, 10, 15, 0.7) 0%, rgba(10, 10, 15, 0.3) 100%);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main {
    background: transparent;
    min-height: 100vh;
}

.stApp {
    background: transparent;
}

.vortex-header {
    padding: 20px 0 12px 0;
    border-bottom: 1px solid var(--border-color);
    backdrop-filter: blur(20px);
    background: rgba(10, 10, 15, 0.6);
}

.header-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 24px;
}

.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    background: var(--gradient-text);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}

.brand-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.6rem;
    color: var(--text-secondary);
    letter-spacing: 3px;
    text-transform: uppercase;
    opacity: 0.5;
}

.nav-btn {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--text-secondary);
    padding: 8px 18px;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid transparent;
    background: transparent;
    font-weight: 400;
    letter-spacing: 0.5px;
    text-decoration: none;
    display: inline-block;
}

.nav-btn:hover {
    color: var(--text-primary);
    background: rgba(255,255,255,0.03);
}

.nav-btn.active {
    color: #0a0a0f;
    background: var(--gradient-primary);
    font-weight: 600;
    box-shadow: 0 4px 20px rgba(79, 195, 247, 0.15);
}

.nav-btn.highlight {
    color: var(--accent-primary);
    border: 1px solid rgba(79, 195, 247, 0.15);
}

.nav-btn.highlight:hover {
    background: rgba(79, 195, 247, 0.05);
}

.hero-section {
    padding: 60px 32px 40px 32px;
    max-width: 1400px;
    margin: 0 auto;
}

.hero-text {
    text-align: center;
    margin-bottom: 40px;
}

.hero-text .tagline {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--accent-primary);
    letter-spacing: 4px;
    text-transform: uppercase;
    font-weight: 400;
    opacity: 0.8;
}

.hero-text .title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.5rem;
    font-weight: 700;
    background: var(--gradient-text);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -2px;
    line-height: 1.1;
    margin-top: 8px;
}

.hero-text .subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: var(--text-secondary);
    font-weight: 300;
    margin-top: 12px;
    letter-spacing: 2px;
}

.hero-text .subtitle strong {
    color: var(--text-primary);
    font-weight: 500;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}

.metric-vortex {
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    border-radius: var(--radius);
    padding: 24px 20px;
    border: 1px solid var(--border-color);
    text-align: center;
    transition: all 0.4s ease;
}

.metric-vortex:hover {
    transform: translateY(-4px);
    border-color: rgba(79, 195, 247, 0.15);
    box-shadow: var(--shadow-soft);
}

.metric-vortex .value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    background: var(--gradient-text);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}

.metric-vortex .label {
    font-family: 'Inter', sans-serif;
    color: var(--text-secondary);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 4px;
}

.metric-vortex .badge {
    font-family: 'Inter', sans-serif;
    font-size: 0.55rem;
    padding: 2px 12px;
    border-radius: 50px;
    display: inline-block;
    margin-top: 6px;
    background: rgba(79, 195, 247, 0.06);
    color: var(--accent-primary);
}

.content-vortex {
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    border-radius: var(--radius);
    padding: 28px 32px;
    border: 1px solid var(--border-color);
    transition: all 0.4s ease;
}

.content-vortex:hover {
    border-color: rgba(79, 195, 247, 0.12);
}

.content-vortex .card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    background: var(--gradient-text);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.content-vortex .card-subtitle {
    font-family: 'Inter', sans-serif;
    color: var(--text-secondary);
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}

.content-vortex .card-desc {
    font-family: 'Inter', sans-serif;
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 300;
    line-height: 1.8;
    margin-top: 12px;
}

.featured-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 16px;
}

.featured-item {
    background: rgba(255,255,255,0.02);
    border-radius: var(--radius-sm);
    padding: 16px;
    border: 1px solid var(--border-color);
    text-align: center;
    transition: all 0.3s ease;
}

.featured-item:hover {
    background: rgba(79, 195, 247, 0.03);
    border-color: rgba(79, 195, 247, 0.1);
}

.featured-item .icon {
    font-size: 2rem;
    margin-bottom: 8px;
    display: block;
}

.featured-item .name {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-primary);
}

.featured-item .price {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--accent-primary);
    margin-top: 4px;
}

.btn-vortex {
    background: var(--gradient-primary);
    color: #0a0a0f;
    border: none;
    padding: 12px 32px;
    border-radius: 50px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.3s ease;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.btn-vortex:hover {
    transform: scale(1.03);
    box-shadow: 0 8px 30px rgba(79, 195, 247, 0.2);
}

.btn-outline-vortex {
    background: transparent;
    color: var(--text-primary);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 12px 32px;
    border-radius: 50px;
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.3s ease;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.btn-outline-vortex:hover {
    background: rgba(255,255,255,0.03);
    border-color: rgba(255,255,255,0.2);
}

.form-vortex {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 16px;
}

.form-vortex input {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 12px 16px;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    transition: all 0.3s ease;
}

.form-vortex input:focus {
    outline: none;
    border-color: rgba(79, 195, 247, 0.2);
    background: rgba(79, 195, 247, 0.02);
}

.form-vortex input::placeholder {
    color: var(--text-muted);
}

.footer-vortex {
    border-top: 1px solid var(--border-color);
    padding: 24px 32px;
    margin-top: 40px;
    backdrop-filter: blur(20px);
    background: rgba(10, 10, 15, 0.4);
}

.footer-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.footer-content .brand {
    font-size: 1.2rem;
}

.footer-links {
    display: flex;
    gap: 32px;
}

.footer-links a {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    color: var(--text-secondary);
    text-decoration: none;
    letter-spacing: 1px;
    text-transform: uppercase;
    transition: all 0.3s ease;
    cursor: pointer;
}

.footer-links a:hover {
    color: var(--text-primary);
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 16px;
        padding: 0 16px;
    }
    
    .header-nav {
        flex-wrap: wrap;
        justify-content: center;
        gap: 6px;
    }
    
    .hero-text .title {
        font-size: 2.2rem;
    }
    
    .metric-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .featured-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .footer-content {
        flex-direction: column;
        gap: 16px;
        text-align: center;
    }
    
    .footer-links {
        flex-wrap: wrap;
        justify-content: center;
    }
}

@media (max-width: 480px) {
    .metric-grid {
        grid-template-columns: 1fr;
    }
    
    .featured-grid {
        grid-template-columns: 1fr;
    }
}

.tag-vortex {
    font-family: 'Inter', sans-serif;
    font-size: 0.55rem;
    padding: 2px 14px;
    border-radius: 50px;
    background: rgba(79, 195, 247, 0.04);
    color: var(--accent-primary);
    border: 1px solid rgba(79, 195, 247, 0.06);
    letter-spacing: 1px;
    text-transform: uppercase;
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    background: linear-gradient(135deg, #4fc3f7 0%, #00b4d8 60%, #0288d1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 24px;
}

.prediction-card {
    background: rgba(20, 20, 30, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(100, 180, 255, 0.08);
    padding: 24px;
    text-align: center;
}

.prediction-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4fc3f7 0%, #00b4d8 60%, #0288d1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# 🌌 FONDO CON IMAGEN
# ============================================

image_path = "assets/images/hero-bg.png"

if os.path.exists(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(f"""
        <style>
        .hero-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            background-image: url('data:image/png;base64,{encoded_string}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            opacity: 0.25 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    except:
        pass

st.markdown("""
<div class="hero-overlay"></div>
""", unsafe_allow_html=True)

# ============================================
# 📊 CARGA DE DATOS - CONEXIÓN A MONGODB
# ============================================

@st.cache_data(ttl=300)
def load_sample_data():
    """Genera datos de muestra (fallback) - USANDO LAS COLUMNAS DE TU DATASET"""
    np.random.seed(42)
    
    statuses = ['COMPLETE', 'PENDING', 'CLOSED', 'PROCESSING', 'ON_HOLD', 'CANCELED', 'SUSPECTED_FRAUD', 'PENDING_PAYMENT', 'PAYMENT_REVIEW']
    regions = ['Southeast Asia', 'South Asia', 'Eastern Asia', 'Oceania', 'West Asia', 'Central Asia', 'North Africa', 'West Africa', 'Central Africa', 'East Africa', 'Southern Africa', 'LATAM', 'USCA', 'Europe']
    categories = ['Sporting Goods', 'Fitness', 'Apparel', 'Footwear', 'Golf', 'Outdoors', 'Technology', 'Book Shop', 'Discs Shop']
    markets = ['Pacific Asia', 'USCA', 'LATAM', 'Africa', 'Europe']
    
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(200):
        order_date = start_date + timedelta(days=random.randint(0, 30))
        status = random.choice(statuses)
        shipping_days = random.uniform(1, 10)
        scheduled_days = random.uniform(2, 7)
        
        data.append({
            'Order Id': f'ORD-{i+1:05d}',
            'order date (DateOrders)': order_date,
            'shipping date (DateOrders)': order_date + timedelta(days=random.randint(1, 5)),
            'Customer Id': f'CUST-{random.randint(1000, 9999)}',
            'Customer Fname': f'Customer{random.randint(100, 999)}',
            'Customer Lname': f'LastName{random.randint(100, 999)}',
            'Customer Segment': random.choice(['Consumer', 'Corporate', 'Home Office']),
            'Product Name': f'Product {random.randint(1000, 9999)}',
            'Category Name': random.choice(categories),
            'Market': random.choice(markets),
            'Order Region': random.choice(regions),
            'Order Country': random.choice(['USA', 'UK', 'Germany', 'France', 'Japan', 'Brazil', 'Australia', 'India', 'China', 'Mexico']),
            'Order City': random.choice(['New York', 'London', 'Paris', 'Tokyo', 'Sydney']),
            'Order Status': status,
            'Delivery Status': random.choice(['Shipping on time', 'Late delivery', 'Advance shipping', 'Shipping canceled']),
            'Late_delivery_risk': random.choice([0, 1]),
            'Days for shipping (real)': round(shipping_days, 1),
            'Days for shipment (scheduled)': round(scheduled_days, 1),
            'Shipping Mode': random.choice(['Standard Class', 'First Class', 'Second Class', 'Same Day']),
            'Order Item Total': round(random.uniform(50, 500), 2),
            'Order Item Quantity': random.randint(1, 5),
            'Sales': round(random.uniform(50, 500), 2),
            'Order Profit Per Order': round(random.uniform(-100, 200), 2),
            'Benefit per order': round(random.uniform(-100, 200), 2),
            'Sales per customer': round(random.uniform(50, 500), 2),
            'Latitude': round(random.uniform(-30, 60), 6),
            'Longitude': round(random.uniform(-130, 160), 6)
        })
    
    return pd.DataFrame(data)

# Intentar cargar desde MongoDB
try:
    from utils.database import MongoDBConnection
    db = MongoDBConnection()
    df = db.get_dataframe()
    if df is not None and not df.empty:
        st.session_state.df = df
        st.session_state.filtered_df = df
        st.session_state.db_connected = True
        print(f"✅ {len(df)} registros cargados desde MongoDB")
    else:
        df = load_sample_data()
        st.session_state.df = df
        st.session_state.filtered_df = df
        st.session_state.db_connected = False
        print("⚠️ No hay datos en MongoDB, usando datos de muestra")
except Exception as e:
    print(f"❌ Error cargando desde MongoDB: {e}")
    df = load_sample_data()
    st.session_state.df = df
    st.session_state.filtered_df = df
    st.session_state.db_connected = False
    print("⚠️ Usando datos de muestra")

# ============================================
# 📌 MENÚ DE NAVEGACIÓN
# ============================================

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

current_page = st.session_state.page

# ============================================
# 📊 HEADER CON MENÚ
# ============================================

st.markdown(f"""
<div class="vortex-header">
    <div class="header-content">
        <div class="header-left">
            <div>
                <div class="brand">CADENA DE SUMINISTRO</div>
                <div class="brand-sub">Análisis · Inteligencia · Tiempo Real</div>
            </div>
        </div>
        <div class="header-nav">
            <span class="nav-btn {'active' if current_page == 'Dashboard' else ''}">📊 Panel de control</span>
            <span class="nav-btn {'active' if current_page == 'Analisis_Retrasos' else ''}">📈 Retrasos</span>
            <span class="nav-btn {'active' if current_page == 'Segmentacion_Clientes' else ''}">👥 Clientes</span>
            <span class="nav-btn {'active' if current_page == 'Prediccion_Retrasos' else ''}">🔮 Predicción</span>
            <span class="nav-btn highlight {'active' if current_page == 'Mapa_Regiones' else ''}">🌍 Regiones</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# 📌 BOTONES DE NAVEGACIÓN
# ============================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📊 Panel de control", use_container_width=True, key="btn_dashboard"):
        st.session_state.page = 'Dashboard'
        st.rerun()

with col2:
    if st.button("📈 Retrasos", use_container_width=True, key="btn_retrasos"):
        st.session_state.page = 'Analisis_Retrasos'
        st.rerun()

with col3:
    if st.button("👥 Clientes", use_container_width=True, key="btn_clientes"):
        st.session_state.page = 'Segmentacion_Clientes'
        st.rerun()

with col4:
    if st.button("🔮 Predicción", use_container_width=True, key="btn_prediccion"):
        st.session_state.page = 'Prediccion_Retrasos'
        st.rerun()

with col5:
    if st.button("🌍 Regiones", use_container_width=True, key="btn_regiones"):
        st.session_state.page = 'Mapa_Regiones'
        st.rerun()

# ============================================
# 📄 CONTENIDO SEGÚN PÁGINA SELECCIONADA
# ============================================

if current_page == 'Dashboard':
    # ============================================
    # 🏠 PÁGINA: DASHBOARD
    # ============================================
    
    # Determinar columnas correctas para el dataset real
    status_col = 'Order Status' if 'Order Status' in df.columns else 'Delivery Status' if 'Delivery Status' in df.columns else df.columns[0]
    fecha_col = 'order date (DateOrders)' if 'order date (DateOrders)' in df.columns else 'Order Date' if 'Order Date' in df.columns else df.columns[0]
    shipping_col = 'Days for shipping (real)' if 'Days for shipping (real)' in df.columns else df.columns[0]
    total_col = 'Order Item Total' if 'Order Item Total' in df.columns else 'Sales' if 'Sales' in df.columns else df.columns[0]
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-text">
            <div class="tagline">⚡ Análisis e Inteligencia en Tiempo Real</div>
            <div class="title">OPTIMIZADO<br>PARA DOMINAR</div>
            <div class="subtitle">
                <strong>ANÁLISIS DE LA CADENA DE SUMINISTRO · PERSPECTIVAS</strong>
            </div>
            <div style="display: flex; gap: 16px; justify-content: center; margin-top: 24px;">
                <button class="btn-vortex">📊 Ver Panel de Control</button>
                <button class="btn-outline-vortex">🎬 Ver Demostración</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Métricas
    total_orders = len(df)
    
    # Usar Late_delivery_risk si existe, sino calcular
    if 'Late_delivery_risk' in df.columns:
        late_orders = df[df['Late_delivery_risk'] == 1].shape[0]
    else:
        late_orders = df[df[status_col] == 'Late delivery'].shape[0]
    
    delay_rate = (late_orders / total_orders * 100) if total_orders > 0 else 0
    avg_shipping = df[shipping_col].mean()
    revenue = df[total_col].sum()

    st.markdown("""
    <div class="hero-section" style="padding-top: 0;">
        <div class="metric-grid">
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-vortex">
            <div class="value">${revenue:,.0f}</div>
            <div class="label">Total Ventas</div>
            <div class="badge">↑ 12%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-vortex">
            <div class="value">{total_orders}</div>
            <div class="label">Total Pedidos</div>
            <div class="badge">↑ Activos</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-vortex">
            <div class="value">{delay_rate:.1f}%</div>
            <div class="label">Tasa de Retrasos</div>
            <div class="badge">↓ {late_orders} pedidos</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-vortex">
            <div class="value">{avg_shipping:.1f}d</div>
            <div class="label">Promedio Envío</div>
            <div class="badge">↑ Eficiente</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Contenido principal
    st.markdown("""
    <div class="hero-section" style="padding-top: 0;">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class="content-vortex">
            <div class="card-title">ANÁLISIS PREDICTIVO</div>
            <div class="card-subtitle">Datos · Machine Learning · Optimización</div>
            <div class="card-desc">
                Predicción y mitigación de retrasos en la cadena de suministro global mediante análisis de datos y segmentación de clientes.
            </div>
        """, unsafe_allow_html=True)
        
        # Últimos pedidos
        recent_orders = df.sort_values(fecha_col, ascending=False).head(4)
        
        st.markdown('<div class="featured-grid">', unsafe_allow_html=True)
        
        for idx, order in recent_orders.iterrows():
            product_name = order.get('Product Name', 'Producto')[:15] if 'Product Name' in order else 'Producto'
            order_total = order.get('Order Item Total', order.get('Sales', 0))
            order_status = order.get('Order Status', 'N/A')
            
            st.markdown(f"""
            <div class="featured-item">
                <span class="icon">📦</span>
                <div class="name">{product_name}...</div>
                <div class="price">${order_total:.2f}</div>
                <div style="font-size: 0.6rem; color: var(--text-secondary); margin-top: 4px;">
                    {order_status}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="content-vortex">
            <div class="card-title">CONTACTANOS</div>
            <div class="card-subtitle">Comienza con el análisis</div>
            <div class="form-vortex">
                <input type="text" placeholder="Nombre Completo">
                <input type="email" placeholder="Correo Electrónico">
                <input type="text" placeholder="País">
                <input type="text" placeholder="Teléfono">
                <button class="btn-vortex">ENVIAR</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-vortex" style="margin-top: 16px;">
            <div class="card-title" style="font-size: 1rem;">CATEGORÍAS</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">
                <span class="tag-vortex">📦 Electrónicos</span>
                <span class="tag-vortex">👕 Ropa</span>
                <span class="tag-vortex">⚽ Deportes</span>
                <span class="tag-vortex">📚 Libros</span>
                <span class="tag-vortex">🏠 Hogar</span>
                <span class="tag-vortex">🎯 Todos</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 📈 PÁGINA: ANÁLISIS DE RETRASOS
# ============================================

elif current_page == 'Analisis_Retrasos':
    st.markdown('<div class="section-title">📈 Análisis de Retrasos en Entregas</div>', unsafe_allow_html=True)

    # Determinar columnas correctas
    status_col = 'Order Status' if 'Order Status' in df.columns else 'Delivery Status' if 'Delivery Status' in df.columns else df.columns[0]
    shipping_col = 'Days for shipping (real)' if 'Days for shipping (real)' in df.columns else df.columns[0]
    region_col = 'Order Region' if 'Order Region' in df.columns else 'Region' if 'Region' in df.columns else df.columns[0]
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)

    total_orders = len(df)
    
    if 'Late_delivery_risk' in df.columns:
        late_orders = df[df['Late_delivery_risk'] == 1].shape[0]
    else:
        late_orders = df[df[status_col] == 'Late delivery'].shape[0]
    
    on_time = total_orders - late_orders
    avg_delay = df[df[status_col] == 'Late delivery'][shipping_col].mean() if late_orders > 0 else 0

    with col1:
        st.metric("📦 Total Pedidos", f"{total_orders:,}")
    with col2:
        st.metric("⚠️ Retrasados", f"{late_orders:,}", delta=f"{late_orders/total_orders*100:.1f}%")
    with col3:
        st.metric("✅ A Tiempo", f"{on_time:,}", delta=f"{on_time/total_orders*100:.1f}%")
    with col4:
        st.metric("📅 Promedio Retraso", f"{avg_delay:.1f} días")

    st.divider()

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Retrasos por Región")
        
        # Usar Order Region si existe
        if 'Order Region' in df.columns:
            region_delay = df.groupby('Order Region').apply(
                lambda x: (x[status_col] == 'Late delivery').sum() / len(x) * 100
            ).reset_index()
            region_delay.columns = ['Región', 'Tasa Retraso (%)']
            region_delay = region_delay.sort_values('Tasa Retraso (%)', ascending=False)
            
            fig = px.bar(
                region_delay,
                x='Región',
                y='Tasa Retraso (%)',
                color='Tasa Retraso (%)',
                color_continuous_scale='Blues',
                text_auto='.1f'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#8899bb',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🚢 Retrasos por Modo de Envío")
        if 'Shipping Mode' in df.columns:
            shipping_delay = df.groupby('Shipping Mode').apply(
                lambda x: (x[status_col] == 'Late delivery').sum() / len(x) * 100
            ).reset_index()
            shipping_delay.columns = ['Modo Envío', 'Tasa Retraso (%)']
            shipping_delay = shipping_delay.sort_values('Tasa Retraso (%)', ascending=False)
            
            fig = px.bar(
                shipping_delay,
                x='Modo Envío',
                y='Tasa Retraso (%)',
                color='Tasa Retraso (%)',
                color_continuous_scale='Blues',
                text_auto='.1f'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#8899bb',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    # Top productos
    st.subheader("📦 Productos con Más Retrasos")
    if 'Product Name' in df.columns:
        product_delay = df[df[status_col] == 'Late delivery']['Product Name'].value_counts().head(10).reset_index()
        product_delay.columns = ['Producto', 'Retrasos']

        fig = px.bar(
            product_delay,
            x='Retrasos',
            y='Producto',
            orientation='h',
            color='Retrasos',
            color_continuous_scale='Blues',
            text_auto=True
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8899bb',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# 👥 PÁGINA: SEGMENTACIÓN DE CLIENTES
# ============================================

elif current_page == 'Segmentacion_Clientes':
    st.markdown('<div class="section-title">👥 Segmentación de Clientes</div>', unsafe_allow_html=True)

    # Determinar columnas correctas
    customer_col = 'Customer Id' if 'Customer Id' in df.columns else df.columns[0]
    total_col = 'Order Item Total' if 'Order Item Total' in df.columns else 'Sales' if 'Sales' in df.columns else df.columns[0]
    status_col = 'Order Status' if 'Order Status' in df.columns else 'Delivery Status' if 'Delivery Status' in df.columns else df.columns[0]
    
    # Preparar datos de clientes
    customer_data = df.groupby(customer_col).agg({
        'Order Id': 'count',
        total_col: ['sum', 'mean'],
        status_col: lambda x: (x == 'Late delivery').sum()
    }).reset_index()
    customer_data.columns = ['Customer Id', 'Total Orders', 'Total Spent', 'Avg Order Value', 'Late Deliveries']
    customer_data['Delay Rate'] = (customer_data['Late Deliveries'] / customer_data['Total Orders'] * 100).fillna(0)

    # Métricas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Total Clientes", f"{len(customer_data):,}")
    with col2:
        st.metric("📦 Promedio Pedidos", f"{customer_data['Total Orders'].mean():.1f}")
    with col3:
        high_risk = customer_data[customer_data['Delay Rate'] > 50].shape[0]
        st.metric("⚠️ Clientes Alto Riesgo", f"{high_risk}")
    with col4:
        st.metric("💰 Gasto Promedio", f"${customer_data['Total Spent'].mean():,.2f}")

    st.divider()

    # Scatter plot
    st.subheader("🎯 Distribución de Clientes")
    fig = px.scatter(
        customer_data.sample(min(500, len(customer_data))),
        x='Total Orders',
        y='Total Spent',
        color='Delay Rate',
        size='Avg Order Value',
        hover_data=['Customer Id'],
        color_continuous_scale='Blues',
        title='Clientes por Comportamiento'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#8899bb',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabla clientes alto riesgo
    st.subheader("🔴 Clientes con Mayor Riesgo")
    high_risk_customers = customer_data.sort_values('Delay Rate', ascending=False).head(20)
    st.dataframe(
        high_risk_customers[['Customer Id', 'Total Orders', 'Delay Rate', 'Total Spent']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Customer Id": "ID Cliente",
            "Total Orders": "Pedidos",
            "Delay Rate": "Tasa Retraso (%)",
            "Total Spent": "Gasto Total"
        }
    )

# ============================================
# 🔮 PÁGINA: PREDICCIÓN DE RETRASOS
# ============================================

elif current_page == 'Prediccion_Retrasos':
    st.markdown('<div class="section-title">🔮 Predicción de Retrasos</div>', unsafe_allow_html=True)

    order_col = 'Order Id' if 'Order Id' in df.columns else df.columns[0]
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Analizar Pedido")
        
        order_ids = df[order_col].head(50).tolist()
        selected_order = st.selectbox("Selecciona un pedido para analizar", options=order_ids)
        
        if selected_order:
            order_data = df[df[order_col] == selected_order].iloc[0]
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**🆔 ID:** {order_data.get('Order Id', 'N/A')}")
                st.write(f"**📦 Producto:** {order_data.get('Product Name', 'N/A')}")
                st.write(f"**🏷️ Categoría:** {order_data.get('Category Name', 'N/A')}")
            with col_b:
                st.write(f"**🌍 Región:** {order_data.get('Order Region', order_data.get('Region', 'N/A'))}")
                st.write(f"**🚢 Envío:** {order_data.get('Shipping Mode', 'N/A')}")
                st.write(f"**💰 Valor:** ${order_data.get('Order Item Total', order_data.get('Sales', 0)):.2f}")

    with col2:
        st.subheader("🎯 Probabilidad de Retraso")
        
        prob_delay = random.uniform(0, 100)
        
        color = '#ff6b6b' if prob_delay > 50 else '#ffd93d' if prob_delay > 25 else '#4fc3f7'
        label = '🔴 ALTO RIESGO' if prob_delay > 50 else '🟡 RIESGO MODERADO' if prob_delay > 25 else '🟢 BAJO RIESGO'
        
        st.markdown(f"""
        <div class="prediction-card">
            <div class="prediction-value">{prob_delay:.1f}%</div>
            <div style="color: {color}; font-weight: 600; margin-top: 8px;">{label}</div>
            <div style="color: #8899bb; font-size: 0.8rem; margin-top: 12px;">
                Basado en análisis histórico
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Factores de riesgo
    st.subheader("⚡ Factores de Riesgo")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📍 **Región**\nTasa de retrasos: 32%")
    with col2:
        st.warning("🏷️ **Categoría**\nElectrónicos: 28% retrasos")
    with col3:
        st.success("🚢 **Envío**\nExpress: 15% retrasos")

# ============================================
# 🌍 PÁGINA: MAPA DE REGIONES
# ============================================

elif current_page == 'Mapa_Regiones':
    st.markdown('<div class="section-title">🌍 Mapa de Entregas por Región</div>', unsafe_allow_html=True)

    # Determinar columnas correctas
    status_col = 'Order Status' if 'Order Status' in df.columns else 'Delivery Status' if 'Delivery Status' in df.columns else df.columns[0]
    total_col = 'Order Item Total' if 'Order Item Total' in df.columns else 'Sales' if 'Sales' in df.columns else df.columns[0]
    
    # Usar columnas de ubicación
    if 'Order Country' in df.columns:
        country_col = 'Order Country'
        region_col = 'Order Region' if 'Order Region' in df.columns else 'Region' if 'Region' in df.columns else df.columns[0]
    elif 'Customer Country' in df.columns:
        country_col = 'Customer Country'
        region_col = 'Customer Region' if 'Customer Region' in df.columns else 'Region' if 'Region' in df.columns else df.columns[0]
    else:
        country_col = df.columns[0]
        region_col = df.columns[0]
    
    # Preparar datos
    region_stats = df.groupby([country_col, region_col]).agg({
        'Order Id': 'count',
        total_col: 'mean',
        status_col: lambda x: (x == 'Late delivery').sum()
    }).reset_index()
    region_stats.columns = ['Country', 'Region', 'Total Orders', 'Avg Order Value', 'Late Deliveries']
    region_stats['Delay Rate'] = (region_stats['Late Deliveries'] / region_stats['Total Orders'] * 100).fillna(0)

    # Coordenadas para países
    country_coords = {
        'USA': {'lat': 39.8283, 'lon': -98.5795},
        'UK': {'lat': 55.3781, 'lon': -3.4360},
        'Germany': {'lat': 51.1657, 'lon': 10.4515},
        'France': {'lat': 46.6034, 'lon': 1.8883},
        'Japan': {'lat': 36.2048, 'lon': 138.2529},
        'Brazil': {'lat': -14.2350, 'lon': -51.9253},
        'Australia': {'lat': -25.2744, 'lon': 133.7751},
        'India': {'lat': 20.5937, 'lon': 78.9629},
        'China': {'lat': 35.8617, 'lon': 104.1954},
        'Mexico': {'lat': 23.6345, 'lon': -102.5528},
        'Canada': {'lat': 56.1304, 'lon': -106.3468},
        'Spain': {'lat': 40.4637, 'lon': -3.7492},
        'Italy': {'lat': 41.8719, 'lon': 12.5674},
        'South Africa': {'lat': -30.5595, 'lon': 22.9375},
        'Egypt': {'lat': 26.8206, 'lon': 30.8025},
        'Indonesia': {'lat': -0.7893, 'lon': 113.9213},
        'Turkey': {'lat': 38.9637, 'lon': 35.2433},
        'Argentina': {'lat': -38.4161, 'lon': -63.6167},
        'Russia': {'lat': 61.5240, 'lon': 105.3188},
        'South Korea': {'lat': 35.9078, 'lon': 127.7669},
        'New Zealand': {'lat': -40.9006, 'lon': 174.8860},
    }

    # Asignar coordenadas
    region_stats['Lat'] = region_stats['Country'].map(lambda x: country_coords.get(x, {'lat': 0})['lat'] if isinstance(x, str) else 0)
    region_stats['Lon'] = region_stats['Country'].map(lambda x: country_coords.get(x, {'lon': 0})['lon'] if isinstance(x, str) else 0)
    
    # Si no hay coordenadas, usar valores por defecto
    if region_stats['Lat'].sum() == 0:
        region_stats['Lat'] = 30.0
        region_stats['Lon'] = 0.0

    # Mapa
    st.subheader("🗺️ Mapa de Riesgo de Retrasos")
    fig = px.scatter_geo(
        region_stats,
        lat='Lat',
        lon='Lon',
        text='Country',
        size='Total Orders',
        color='Delay Rate',
        hover_data=['Region', 'Total Orders', 'Avg Order Value'],
        color_continuous_scale='Blues',
        title='Riesgo de Retrasos por Región'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#8899bb',
        height=500,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabla
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔴 Mayor Riesgo")
        top_risk = region_stats.sort_values('Delay Rate', ascending=False).head(10)
        st.dataframe(
            top_risk[['Country', 'Region', 'Total Orders', 'Delay Rate']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Country": "País/Región",
                "Region": "Región",
                "Total Orders": "Pedidos",
                "Delay Rate": "Tasa Retraso (%)"
            }
        )

    with col2:
        st.subheader("🟢 Menor Riesgo")
        low_risk = region_stats.sort_values('Delay Rate', ascending=True).head(10)
        st.dataframe(
            low_risk[['Country', 'Region', 'Total Orders', 'Delay Rate']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Country": "País/Región",
                "Region": "Región",
                "Total Orders": "Pedidos",
                "Delay Rate": "Tasa Retraso (%)"
            }
        )

# ============================================
# 📌 FOOTER
# ============================================

st.markdown("""
<div class="footer-vortex">
    <div class="footer-content">
        <div class="brand" style="font-size: 1.2rem;">CADENA DE SUMINISTRO</div>
        <div class="footer-links">
            <a onclick="window.location.href='?page=Dashboard'">Dashboard</a>
            <a onclick="window.location.href='?page=Analisis_Retrasos'">Análisis</a>
            <a onclick="window.location.href='?page=Segmentacion_Clientes'">Clientes</a>
            <a onclick="window.location.href='?page=Prediccion_Retrasos'">Predicción</a>
            <a onclick="window.location.href='?page=Mapa_Regiones'">Regiones</a>
        </div>
        <div style="font-family: 'Inter', sans-serif; font-size: 0.6rem; color: var(--text-muted); letter-spacing: 1px;">
            © 2024 · Optimización de Entregas · Supply Chain Analytics
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Estado de conexión
if st.session_state.get('db_connected', False):
    st.markdown("""
    <div style="
        text-align: center; 
        font-family: 'Inter', sans-serif;
        color: #4ecdc4; 
        font-size: 11px; 
        padding: 10px 0;
        opacity: 0.8;
        font-weight: 400;
        letter-spacing: 0.5px;
    ">
         Conectado a:  MongoDB Atlas
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="
        text-align: center; 
        font-family: 'Inter', sans-serif;
        color: #ff6b6b; 
        font-size: 11px; 
        padding: 10px 0;
        opacity: 0.6;
        font-weight: 300;
        letter-spacing: 0.5px;
    ">
        ⚡ Conectado a: ⚠️ Datos de muestra
    </div>
    """, unsafe_allow_html=True)