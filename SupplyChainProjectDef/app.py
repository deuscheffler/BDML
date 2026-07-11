"""
GDLM - Gestión Dinámica de Logística y Mercancía
Sistema Inteligente para Predicción del Estado de Pedidos mediante Machine Learning
Ingeniería en Ciencia de Datos e Inteligencia Artificial

Versión 4.0 - Dashboard Ejecutivo
"""

import streamlit as st
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="GDLM | Intelligence Platform",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# =============================================================================
# INICIALIZACIÓN DE ESTADO PARA MODO OSCURO/CLARO
# =============================================================================
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# =============================================================================
# CSS - SISTEMA DE DISEÑO EJECUTIVO (MANTENIDO IDÉNTICO)
# =============================================================================
st.markdown("""
    <style>
        /* ========================================
           SISTEMA DE DISEÑO - GDLM BRAND
           ======================================== */
        
        /* ===== VARIABLES GLOBALES ===== */
        :root {
            --gold: #F59E0B;
            --gold-light: #FCD34D;
            --navy: #1E293B;
            --navy-light: #334155;
            --emerald: #10B981;
            --ruby: #EF4444;
            --gradient-main: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
            --gradient-accent: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
            --gradient-glow: linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(252,211,77,0.05) 100%);
            
            --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            --font-display: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-serif: 'Georgia', 'Times New Roman', serif;
        }
        
        /* ===== MODO OSCURO (POR DEFECTO) ===== */
        .dark-mode {
            --bg-primary: #0A0A12;
            --bg-secondary: #111122;
            --bg-card: #1A1A2E;
            --bg-card-hover: #222244;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --text-gold: #FCD34D;
            --border-color: rgba(255,255,255,0.06);
            --border-hover: rgba(255,255,255,0.12);
            --shadow-card: 0 4px 24px rgba(0,0,0,0.5);
            --shadow-hover: 0 8px 40px rgba(0,0,0,0.7);
            --shadow-glow: 0 0 60px rgba(245,158,11,0.05);
        }
        
        /* ===== MODO CLARO ===== */
        .light-mode {
            --bg-primary: #F1F5F9;
            --bg-secondary: #E2E8F0;
            --bg-card: #FFFFFF;
            --bg-card-hover: #F8FAFC;
            --text-primary: #0F172A;
            --text-secondary: #475569;
            --text-muted: #94A3B8;
            --text-gold: #B45309;
            --border-color: rgba(0,0,0,0.06);
            --border-hover: rgba(0,0,0,0.12);
            --shadow-card: 0 4px 24px rgba(0,0,0,0.06);
            --shadow-hover: 0 8px 32px rgba(0,0,0,0.12);
            --shadow-glow: 0 0 60px rgba(245,158,11,0.08);
        }
        
        /* ===== ESTILOS BASE ===== */
        .stApp {
            background: var(--bg-primary) !important;
            transition: background 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: var(--bg-secondary); }
        ::-webkit-scrollbar-thumb { 
            background: linear-gradient(180deg, #F59E0B, #D97706);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover { background: #FCD34D; }
        
        /* ========================================
           HEADER - EJECUTIVO
           ======================================== */
        .gdlm-header {
            background: var(--gradient-main);
            padding: 2.5rem 3rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(245,158,11,0.1);
            box-shadow: 0 8px 40px rgba(0,0,0,0.3), var(--shadow-glow);
        }
        .gdlm-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(245,158,11,0.05) 0%, transparent 70%);
            pointer-events: none;
        }
        .gdlm-header::after {
            content: '◆';
            position: absolute;
            bottom: -80px;
            right: 40px;
            font-size: 300px;
            color: rgba(245,158,11,0.03);
            pointer-events: none;
        }
        .gdlm-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
            position: relative;
            z-index: 1;
        }
        .gdlm-logo {
            font-size: 3.2rem;
            font-weight: 900;
            color: white;
            letter-spacing: -0.02em;
            font-family: var(--font-display);
            text-shadow: 0 2px 20px rgba(0,0,0,0.3);
        }
        .gdlm-logo span {
            background: var(--gradient-accent);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .gdlm-logo-icon {
            font-size: 2.5rem;
            color: #FCD34D;
            filter: drop-shadow(0 0 20px rgba(245,158,11,0.3));
        }
        .gdlm-tagline {
            font-size: 1rem;
            color: rgba(255,255,255,0.7);
            font-weight: 300;
            margin: 0.5rem 0 0 0;
            letter-spacing: 0.05em;
            font-family: var(--font-primary);
            font-style: italic;
        }
        .gdlm-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(245,158,11,0.15);
            backdrop-filter: blur(20px);
            padding: 0.4rem 1.2rem;
            border-radius: 30px;
            font-size: 0.7rem;
            color: #FCD34D;
            font-weight: 500;
            margin-top: 0.75rem;
            border: 1px solid rgba(245,158,11,0.15);
            position: relative;
            z-index: 1;
            font-family: var(--font-primary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .gdlm-badge .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #34D399;
            animation: pulse-dot 2s infinite;
        }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.7); }
        }
        
        /* ========================================
           TARJETAS - LUXURY STYLE
           ======================================== */
        .card-gdlm {
            background: var(--bg-card);
            padding: 1.75rem;
            border-radius: 16px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-card);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
            position: relative;
            overflow: hidden;
        }
        .card-gdlm::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-accent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .card-gdlm:hover::before { opacity: 1; }
        .card-gdlm:hover {
            transform: translateY(-6px);
            border-color: rgba(245,158,11,0.2);
            box-shadow: var(--shadow-hover), 0 0 40px rgba(245,158,11,0.05);
            background: var(--bg-card-hover);
        }
        .card-icon-gdlm {
            font-size: 2.2rem;
            margin-bottom: 0.75rem;
            display: block;
        }
        .card-label-gdlm {
            font-size: 0.7rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 0 0 0.3rem 0;
            font-family: var(--font-primary);
        }
        .card-value-gdlm {
            font-size: 2.4rem;
            font-weight: 800;
            color: var(--text-primary);
            margin: 0;
            letter-spacing: -0.02em;
            font-family: var(--font-display);
        }
        .card-value-gdlm.gold {
            background: var(--gradient-accent);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .card-sub-gdlm {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin: 0.3rem 0 0 0;
            font-family: var(--font-primary);
        }
        
        .card-badge-gold {
            display: inline-block;
            padding: 0.2rem 1rem;
            border-radius: 20px;
            font-size: 0.6rem;
            font-weight: 700;
            background: var(--gradient-accent);
            color: #0F172A;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* ========================================
           SIDEBAR - EJECUTIVA
           ======================================== */
        [data-testid="stSidebar"] {
            background: var(--bg-secondary) !important;
            border-right: 1px solid var(--border-color) !important;
            transition: all 0.4s ease;
        }
        .sidebar-gdlm {
            padding: 1.5rem 0.5rem;
        }
        .sidebar-brand {
            text-align: center;
            padding: 1.5rem 1rem 1.5rem 1rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 1.5rem;
        }
        .sidebar-brand-name {
            font-size: 2.2rem;
            font-weight: 900;
            background: var(--gradient-accent);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            font-family: var(--font-display);
            letter-spacing: -0.02em;
        }
        .sidebar-brand-sub {
            font-size: 0.6rem;
            color: var(--text-secondary);
            letter-spacing: 0.2em;
            text-transform: uppercase;
            margin-top: 0.25rem;
            font-family: var(--font-primary);
        }
        .sidebar-brand-version {
            display: inline-block;
            background: var(--bg-card);
            padding: 0.2rem 0.8rem;
            border-radius: 12px;
            font-size: 0.55rem;
            color: var(--text-muted);
            border: 1px solid var(--border-color);
            margin-top: 0.5rem;
            font-family: var(--font-primary);
        }
        
        .sidebar-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.7rem 1rem;
            border-radius: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
            cursor: default;
        }
        .sidebar-item:hover {
            border-color: rgba(245,158,11,0.2);
            transform: translateX(4px);
            box-shadow: 0 0 20px rgba(245,158,11,0.05);
        }
        .sidebar-item-icon { font-size: 1.2rem; width: 32px; text-align: center; }
        .sidebar-item-text { 
            font-size: 0.82rem; 
            color: var(--text-primary);
            margin: 0;
            font-family: var(--font-primary);
        }
        .sidebar-item-text small {
            display: block;
            color: var(--text-secondary);
            font-size: 0.6rem;
            margin-top: 0.1rem;
            font-weight: 300;
        }
        
        /* ===== TOGGLE MODO OSCURO/CLARO ===== */
        .theme-toggle {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 0.6rem 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }
        .theme-toggle:hover { border-color: rgba(245,158,11,0.2); }
        .theme-toggle-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-family: var(--font-primary);
        }
        .toggle-switch {
            width: 44px;
            height: 24px;
            background: var(--bg-secondary);
            border-radius: 12px;
            position: relative;
            transition: all 0.3s ease;
            border: 1px solid var(--border-color);
        }
        .toggle-switch.active {
            background: var(--gradient-accent);
            border-color: transparent;
        }
        .toggle-switch::after {
            content: '';
            width: 18px;
            height: 18px;
            background: white;
            border-radius: 50%;
            position: absolute;
            top: 2px;
            left: 2px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .toggle-switch.active::after { left: 22px; }
        
        /* ========================================
           NAVEGACIÓN - ETIQUETAS CLARAS
           ======================================== */
        .nav-grid-gdlm {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 1.2rem;
            margin: 1.5rem 0;
        }
        .nav-card-gdlm {
            background: var(--bg-card);
            padding: 1.75rem 1.2rem;
            border-radius: 14px;
            border: 1px solid var(--border-color);
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            text-decoration: none;
            color: var(--text-primary);
            display: block;
            position: relative;
            overflow: hidden;
        }
        .nav-card-gdlm::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-accent);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        .nav-card-gdlm:hover::before { transform: scaleX(1); }
        .nav-card-gdlm:hover {
            transform: translateY(-6px) scale(1.02);
            border-color: rgba(245,158,11,0.2);
            box-shadow: 0 8px 30px rgba(245,158,11,0.1);
            background: var(--bg-card-hover);
        }
        .nav-card-icon { 
            font-size: 2.4rem; 
            display: block; 
            margin-bottom: 0.5rem;
        }
        .nav-card-label { 
            font-size: 0.8rem; 
            font-weight: 700; 
            color: var(--text-primary);
            font-family: var(--font-display);
            letter-spacing: 0.02em;
        }
        .nav-card-desc { 
            font-size: 0.65rem; 
            color: var(--text-secondary);
            margin-top: 0.3rem;
            font-family: var(--font-primary);
            font-weight: 300;
        }
        
        /* ========================================
           FOOTER - CORPORATIVO
           ======================================== */
        .footer-gdlm {
            text-align: center;
            padding: 2.5rem 0 0.5rem 0;
            border-top: 1px solid var(--border-color);
            margin-top: 2.5rem;
            position: relative;
        }
        .footer-gdlm::before {
            content: '◆';
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-primary);
            padding: 0 1rem;
            color: #FCD34D;
            font-size: 1.2rem;
        }
        .footer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 2rem;
            text-align: left;
            margin-bottom: 1.5rem;
        }
        .footer-col h4 {
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--text-gold);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 0 0 0.5rem 0;
            font-family: var(--font-primary);
        }
        .footer-col p {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin: 0.3rem 0;
            font-family: var(--font-primary);
            font-weight: 300;
            line-height: 1.6;
        }
        .footer-col p strong {
            color: var(--text-primary);
            font-weight: 500;
        }
        .footer-divider {
            width: 60px;
            height: 2px;
            background: var(--gradient-accent);
            margin: 0 auto 1rem auto;
            border-radius: 2px;
        }
        .footer-text-gdlm {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-family: var(--font-primary);
        }
        .footer-text-gdlm strong {
            color: var(--text-gold);
            font-weight: 600;
        }
        
        /* ========================================
           ANIMACIONES
           ======================================== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in-gdlm {
            animation: fadeInUp 0.7s ease-out forwards;
        }
        .delay-1 { animation-delay: 0.1s; opacity: 0; }
        .delay-2 { animation-delay: 0.2s; opacity: 0; }
        .delay-3 { animation-delay: 0.3s; opacity: 0; }
        .delay-4 { animation-delay: 0.4s; opacity: 0; }
        .delay-5 { animation-delay: 0.5s; opacity: 0; }
        .delay-6 { animation-delay: 0.6s; opacity: 0; }
        
        /* ========================================
           RESPONSIVE
           ======================================== */
        @media (max-width: 768px) {
            .gdlm-header { padding: 1.5rem; }
            .gdlm-logo { font-size: 2.2rem; }
            .gdlm-logo-icon { font-size: 1.8rem; }
            .card-value-gdlm { font-size: 1.8rem; }
            .nav-grid-gdlm { grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); }
            .footer-grid { grid-template-columns: 1fr; text-align: center; }
        }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# APLICAR MODO OSCURO/CLARO
# =============================================================================
mode_class = "dark-mode" if st.session_state.dark_mode else "light-mode"
st.markdown(f'<body class="{mode_class}">', unsafe_allow_html=True)

# =============================================================================
# TOGGLE MODO OSCURO/CLARO
# =============================================================================
def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# =============================================================================
# SIDEBAR - GDLM
# =============================================================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-gdlm">
            <div class="sidebar-brand">
                <h1 class="sidebar-brand-name">◆ GDLM</h1>
                <div class="sidebar-brand-sub">Gestión Dinámica de Logística</div>
                <span class="sidebar-brand-version">v4.0 · Enterprise</span>
            </div>
    """, unsafe_allow_html=True)
    
    # Información del Sistema
    st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <p style="font-size:0.6rem; color:#64748B; text-transform:uppercase; letter-spacing:0.15em; margin:0 0 0.5rem 0; font-weight:600; font-family:'Inter',sans-serif;">
                ⚡ Sistema de Predicción
            </p>
            <div class="sidebar-item">
                <span class="sidebar-item-icon">◆</span>
                <p class="sidebar-item-text">
                    Machine Learning
                    <small>Predicción de Estado de Pedidos</small>
                </p>
            </div>
            <div class="sidebar-item">
                <span class="sidebar-item-icon">🧠</span>
                <p class="sidebar-item-text">
                    2 Modelos
                    <small>Supervisado + K-Means</small>
                </p>
            </div>
            <div class="sidebar-item">
                <span class="sidebar-item-icon">🗄️</span>
                <p class="sidebar-item-text">
                    SQL + MongoDB
                    <small>Dual Database Architecture</small>
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="border-top:1px solid var(--border-color); margin:1rem 0 1rem 0;"></div>
    """, unsafe_allow_html=True)
    
    # Información Académica
    st.markdown(f"""
        <div style="margin-bottom:1rem;">
            <p style="font-size:0.6rem; color:#64748B; text-transform:uppercase; letter-spacing:0.15em; margin:0 0 0.5rem 0; font-weight:600; font-family:'Inter',sans-serif;">
                🏛️ Institutional
            </p>
            <div class="sidebar-item">
                <span class="sidebar-item-icon">🎓</span>
                <p class="sidebar-item-text">
                    UNACH
                    <small>Data Science & AI Engineering</small>
                </p>
            </div>
            <div class="sidebar-item">
                <span class="sidebar-item-icon">📅</span>
                <p class="sidebar-item-text">
                    Semester IV
                    <small>Database Administration</small>
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="border-top:1px solid var(--border-color); margin:1rem 0 1rem 0;"></div>
    """, unsafe_allow_html=True)
    
    # Toggle Modo Oscuro/Claro
    icon = "🌙" if st.session_state.dark_mode else "☀️"
    label = "Dark Mode" if st.session_state.dark_mode else "Light Mode"
    active_class = "active" if st.session_state.dark_mode else ""
    
    st.markdown(f"""
        <div class="theme-toggle">
            <span style="display:flex; align-items:center; gap:0.5rem;">
                <span>{icon}</span>
                <span class="theme-toggle-label">{label}</span>
            </span>
            <div class="toggle-switch {active_class}"></div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Toggle Theme", use_container_width=True, key="theme_btn"):
        toggle_theme()
        st.rerun()
    
    st.markdown("""
        <div style="margin-top:1rem; text-align:center;">
            <p style="font-size:0.55rem; color:#64748B; margin:0; font-family:'Inter',sans-serif; letter-spacing:0.05em;">
                © 2026 GDLM · All Rights Reserved
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# CONTENIDO PRINCIPAL - PÁGINA DE INICIO
# =============================================================================

# ===== HEADER =====
st.markdown("""
    <div class="gdlm-header fade-in-gdlm">
        <div style="position:relative; z-index:1;">
            <div class="gdlm-brand">
                <span class="gdlm-logo-icon">◆</span>
                <span class="gdlm-logo">GD<span>LM</span></span>
            </div>
            <p class="gdlm-tagline">"Gestión Dinámica de Logística y Mercancía"</p>
            <span class="gdlm-badge">
                <span class="dot"></span>
                Sistema Inteligente para Predicción del Estado de Pedidos
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ===== TARJETAS DE COMPONENTES DEL SISTEMA =====
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="card-gdlm fade-in-gdlm delay-1">
            <span class="card-icon-gdlm">🧠</span>
            <p class="card-label-gdlm">Modelo Supervisado</p>
            <p class="card-value-gdlm gold">ML</p>
            <p class="card-sub-gdlm">Clasificación de Pedidos</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="card-gdlm fade-in-gdlm delay-2">
            <span class="card-icon-gdlm">🔬</span>
            <p class="card-label-gdlm">K-Means</p>
            <p class="card-value-gdlm">Cluster</p>
            <p class="card-sub-gdlm">Agrupamiento No Supervisado</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="card-gdlm fade-in-gdlm delay-3">
            <span class="card-icon-gdlm">🗄️</span>
            <p class="card-label-gdlm">SQL Server</p>
            <p class="card-value-gdlm gold">DB</p>
            <p class="card-sub-gdlm">Almacenamiento Estructurado</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="card-gdlm fade-in-gdlm delay-4">
            <span class="card-icon-gdlm">☁️</span>
            <p class="card-label-gdlm">MongoDB Atlas</p>
            <p class="card-value-gdlm">NoSQL</p>
            <p class="card-sub-gdlm">Historial de Predicciones</p>
        </div>
    """, unsafe_allow_html=True)

# ===== NAVEGACIÓN =====
st.markdown("""
    <div style="margin:2rem 0 1rem 0;">
        <h3 style="color:var(--text-primary); font-weight:700; font-size:1.3rem; margin:0; font-family:'SF Pro Display',sans-serif;">
            ✦ Navegación del Sistema
        </h3>
        <p style="color:var(--text-secondary); font-size:0.85rem; margin:0.25rem 0 0 0; font-family:'Inter',sans-serif;">
            Accede a las funcionalidades del sistema de predicción
        </p>
    </div>
""", unsafe_allow_html=True)

nav_items = [
    ("🏠", "Inicio", "Página principal"),
    ("📦", "Realizar Pedido", "Ingresar datos del pedido"),
    ("🤖", "Predicción", "Resultado Supervisado + No Supervisado"),
    ("📈", "Análisis Supervisado", "ROC, Matriz, Variables Importantes"),
    ("🧠", "Análisis No Supervisado", "Selección K, PCA, t-SNE"),
    ("🗄️", "Base de Datos", "SQL Server + MongoDB Atlas"),
]

cols = st.columns(len(nav_items))
for idx, (icon, label, desc) in enumerate(nav_items):
    with cols[idx]:
        st.markdown(f"""
            <a href="#" style="text-decoration:none;">
                <div class="nav-card-gdlm fade-in-gdlm delay-{idx+1}">
                    <span class="nav-card-icon">{icon}</span>
                    <div class="nav-card-label">{label}</div>
                    <div class="nav-card-desc">{desc}</div>
                </div>
            </a>
        """, unsafe_allow_html=True)

# ===== SECCIÓN DE BIENVENIDA =====
st.markdown(f"""
    <div style="margin:2rem 0 1rem 0; padding:1.75rem; background:var(--bg-card); 
                border-radius:16px; border:1px solid var(--border-color); 
                box-shadow:var(--shadow-card); transition:all 0.3s ease;">
        <div style="display:flex; align-items:flex-start; gap:1.5rem; flex-wrap:wrap;">
            <div style="flex:1; min-width:250px;">
                <h3 style="color:var(--text-primary); margin:0 0 0.5rem 0; font-size:1.2rem; font-weight:700; font-family:'SF Pro Display',sans-serif;">
                    👋 Bienvenido a GDLM
                </h3>
                <p style="color:var(--text-secondary); line-height:1.8; margin:0; font-size:0.95rem; font-family:'Inter',sans-serif;">
                    Este sistema utiliza <strong style="color:#FCD34D;">Machine Learning</strong> para predecir 
                    el estado final de los pedidos en la cadena de suministro.
                </p>
                <div style="margin-top:0.75rem; display:grid; grid-template-columns:1fr 1fr; gap:0.5rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem; background:var(--bg-secondary); padding:0.4rem 0.75rem; border-radius:8px;">
                        <span style="color:#34D399;">✅</span>
                        <span style="font-size:0.75rem; color:var(--text-secondary);">Predicción <strong style="color:#34D399;">COMPLETED</strong></span>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.5rem; background:var(--bg-secondary); padding:0.4rem 0.75rem; border-radius:8px;">
                        <span style="color:#F87171;">❌</span>
                        <span style="font-size:0.75rem; color:var(--text-secondary);">Predicción <strong style="color:#F87171;">CANCELED</strong></span>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.5rem; background:var(--bg-secondary); padding:0.4rem 0.75rem; border-radius:8px;">
                        <span style="color:#FCD34D;">◆</span>
                        <span style="font-size:0.75rem; color:var(--text-secondary);">Cluster K-Means</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.5rem; background:var(--bg-secondary); padding:0.4rem 0.75rem; border-radius:8px;">
                        <span style="color:#60A5FA;">☁️</span>
                        <span style="font-size:0.75rem; color:var(--text-secondary);">Historial en MongoDB</span>
                    </div>
                </div>
                <p style="color:var(--text-muted); font-size:0.8rem; margin:0.75rem 0 0 0; font-style:italic; font-family:'Inter',sans-serif;">
                    💡 "Scientia Potentia Est" — Knowledge is Power
                </p>
            </div>
            <div style="background:var(--bg-secondary); padding:0.75rem 1.5rem; border-radius:12px; 
                        border:1px solid var(--border-color); display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
                <span style="font-size:1.8rem;">◆</span>
                <div>
                    <p style="margin:0; font-size:0.6rem; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.1em;">Flujo del Sistema</p>
                    <p style="margin:0; font-weight:600; color:var(--text-gold); font-size:0.9rem;">Pedido → Predicción → Análisis</p>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ===== FOOTER =====
st.markdown("""
    <div class="footer-gdlm">
        <div class="footer-divider"></div>
        <div class="footer-grid">
            <div class="footer-col">
                <h4>◆ GDLM Platform</h4>
                <p><strong>Versión:</strong> 4.0.0 Enterprise</p>
                <p><strong>Estado:</strong> <span style="color:#34D399;">● Operativo</span></p>
                <p><strong>Framework:</strong> Streamlit</p>
            </div>
            <div class="footer-col">
                <h4>🤖 Machine Learning</h4>
                <p><strong>Modelos:</strong> Supervisado + K-Means</p>
                <p><strong>Librerías:</strong> Scikit-Learn</p>
                <p><strong>Procesamiento:</strong> Pandas, NumPy</p>
            </div>
            <div class="footer-col">
                <h4>🗄️ Databases</h4>
                <p><strong>SQL Server:</strong> Datos Estructurados</p>
                <p><strong>MongoDB Atlas:</strong> Historial de Predicciones</p>
                <p><strong>Arquitectura:</strong> Dual Database</p>
            </div>
            <div class="footer-col">
                <h4>🏛️ Academic</h4>
                <p><strong>Institución:</strong> UNACH</p>
                <p><strong>Programa:</strong> Data Science & AI</p>
                <p><strong>Semestre:</strong> IV · 2026</p>
            </div>
        </div>
        <div style="text-align:center; border-top:1px solid var(--border-color); padding-top:1rem;">
            <p class="footer-text-gdlm">
                <strong>◆ GDLM</strong> · Gestión Dinámica de Logística y Mercancía<br>
                <span style="font-size:0.65rem; color:var(--text-muted);">
                    Sistema Inteligente para Predicción del Estado de Pedidos mediante Machine Learning
                </span>
            </p>
            <p style="font-size:0.55rem; color:var(--text-muted); margin:0.5rem 0 0 0; opacity:0.5; font-family:'Inter',sans-serif;">
                Python · Streamlit · Scikit-Learn · SQL Server · MongoDB Atlas · Pandas · NumPy
            </p>
            <p style="font-size:0.5rem; color:var(--text-muted); margin:0.25rem 0 0 0; opacity:0.4; font-family:'Inter',sans-serif;">
                © 2026 GDLM · All Rights Reserved · """ + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + """
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)