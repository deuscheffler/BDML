"""
estilos.py
============
Sistema de diseño de GDLM: tema oscuro tecnológico con acentos cian,
derivado del logo. Centralizado aquí para que todas las páginas
(paginas/*.py) hereden exactamente los mismos tokens de color, tipografía
y componentes (tarjetas de KPI, tarjetas de gráfica, panel de arquitectura,
etiquetas de sección, etc.) sin duplicar CSS en cada archivo.

Uso en app.py (una sola vez, al inicio):
    from estilos import inyectar_estilos, cargar_logo_html
    inyectar_estilos()

Uso en cualquier página (paginas/*.py):
    Solo se reutilizan las clases CSS ya inyectadas (gdlm-kpi-card,
    gdlm-section-label, etc.) directamente en el HTML de cada página.
"""

import base64
from pathlib import Path

import streamlit as st

# Ruta del logo: debe estar en la misma carpeta que app.py.
RUTA_LOGO = Path(__file__).parent / "logover.png"

# ============================================================================
# CSS — paleta derivada del logo (GDLM): fondo navy casi negro (#0B1220),
# superficies (#121A2E), cian eléctrico (#22D3EE) como acento principal,
# ámbar (#F5A623) reservado para señales de riesgo/cancelación.
# Tipografía: Space Grotesk (display) + Inter (cuerpo) + IBM Plex Mono
# (cifras y datos).
# ============================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {
    --color-bg: #0B1220;
    --color-surface: #121A2E;
    --color-surface-hover: #172140;
    --color-navy: #0B1220;
    --color-navy-soft: #16213E;
    --color-cyan: #22D3EE;
    --color-cyan-soft: #67E8F9;
    --color-amber: #F5A623;
    --color-green: #22C55E;
    --color-mongo: #34E7B4;
    --color-text: #E7ECF7;
    --color-muted: #8B96B8;
    --color-border: rgba(255, 255, 255, 0.08);
    --color-border-cyan: rgba(34, 211, 238, 0.22);
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
        radial-gradient(circle at 88% 4%, rgba(34, 211, 238, 0.10), transparent 42%),
        radial-gradient(circle at 8% 80%, rgba(34, 211, 238, 0.05), transparent 40%),
        var(--color-bg);
}
#MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; height: 0; }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1200px; }

/* ---------- Barra de navegación ---------- */
.st-key-nav_bar {
    background: linear-gradient(135deg, var(--color-navy-soft) 0%, var(--color-navy) 100%);
    border: 1px solid var(--color-border-cyan);
    border-radius: 20px;
    padding: 1.1rem 1.7rem;
    margin-bottom: 2.2rem;
    box-shadow: 0 10px 34px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(34, 211, 238, 0.04);
}

.gdlm-brand-row { display: flex; align-items: center; gap: 0.85rem; }
.gdlm-logo-img {
    height: 46px; width: auto; display: block;
    filter: drop-shadow(0 0 10px rgba(34, 211, 238, 0.35));
}
.gdlm-logo-fallback {
    font-family: 'Space Grotesk', sans-serif; font-weight: 700;
    font-size: 1.4rem; color: #FFFFFF;
}
.gdlm-status-pill {
    display: inline-flex; align-items: center; gap: 0.35rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; color: #8FE3C7;
    background: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(34, 197, 94, 0.35);
    padding: 0.15rem 0.55rem; border-radius: 999px;
    margin-top: 0.3rem;
}
.gdlm-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.76rem;
    color: #8B96B8;
    margin: 0.55rem 0 0 0;
    max-width: 620px;
    line-height: 1.45;
}

.gdlm-pulse { position: relative; width: 8px; height: 8px; flex-shrink: 0; }
.gdlm-pulse-dot {
    position: absolute; top: 1px; left: 1px;
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--color-green);
    box-shadow: 0 0 6px var(--color-green);
}
.gdlm-pulse-ring {
    position: absolute; top: -2px; left: -2px;
    width: 8px; height: 8px; border-radius: 50%;
    border: 2px solid var(--color-green);
    animation: gdlm-radar 1.8s ease-out infinite;
}
@keyframes gdlm-radar {
    0%   { transform: scale(0.6); opacity: 0.9; }
    100% { transform: scale(3.2); opacity: 0; }
}

.st-key-nav_bar .stButton > button {
    background: transparent;
    border: none;
    color: #A7B2CE;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.82rem;
    padding: 0.55rem 0.6rem;
    border-radius: 8px;
    white-space: nowrap;
    transition: background 0.15s ease, color 0.15s ease;
}
.st-key-nav_bar .stButton > button p { white-space: nowrap; margin: 0; }
.st-key-nav_bar .stButton > button:hover {
    background: rgba(34, 211, 238, 0.1);
    color: var(--color-cyan-soft);
}
.st-key-nav_bar .stButton > button:focus:not(:active) { color: var(--color-cyan-soft); }

/* ---------- Hero ---------- */
.gdlm-hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.9rem;
    line-height: 1.18;
    margin-bottom: 0.6rem;
    background: linear-gradient(90deg, #FFFFFF 0%, var(--color-cyan-soft) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.gdlm-hero-desc {
    font-family: 'Inter', sans-serif;
    color: var(--color-muted);
    font-size: 0.95rem;
    max-width: 560px;
    line-height: 1.55;
}

/* Panel "Arquitectura de datos" */
.gdlm-arch-panel {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 14px;
    padding: 1rem 1.1rem;
}
.gdlm-arch-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    color: var(--color-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.7rem;
}
.gdlm-engine-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.6rem 0;
}
.gdlm-engine-row + .gdlm-engine-row { border-top: 1px solid var(--color-border); }
.gdlm-engine-icon {
    width: 34px; height: 34px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.gdlm-engine-icon.sql {
    background: rgba(34, 211, 238, 0.1);
    border: 1px solid rgba(34, 211, 238, 0.25);
    color: var(--color-cyan);
}
.gdlm-engine-icon.mongo {
    background: rgba(52, 231, 180, 0.1);
    border: 1px solid rgba(52, 231, 180, 0.25);
    color: var(--color-mongo);
}
.gdlm-engine-name { font-size: 0.83rem; font-weight: 600; color: var(--color-text); }
.gdlm-engine-role { font-size: 0.72rem; color: var(--color-muted); }
.gdlm-engine-tag {
    margin-left: auto;
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; color: var(--color-green);
    white-space: nowrap;
}
.gdlm-engine-tag .dot {
    width: 6px; height: 6px; border-radius: 50%; background: var(--color-green);
    box-shadow: 0 0 5px var(--color-green);
}

/* ---------- Total de pedidos ---------- */
.gdlm-total-card {
    background: linear-gradient(135deg, var(--color-navy-soft) 0%, var(--color-navy) 100%);
    border: 1px solid var(--color-border-cyan);
    border-radius: 16px;
    padding: 1.3rem 1.6rem;
    display: flex; align-items: center; gap: 1.2rem;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.3);
    margin: 1.8rem 0;
}
.gdlm-total-icon {
    width: 54px; height: 54px; border-radius: 14px;
    background: rgba(34, 211, 238, 0.1);
    border: 1px solid rgba(34, 211, 238, 0.25);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; flex-shrink: 0;
}
.gdlm-total-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem; color: #8B96B8; text-transform: uppercase; letter-spacing: 0.04em;
}
.gdlm-total-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem; font-weight: 700; color: #FFFFFF; line-height: 1.15;
}
.gdlm-total-caption { font-size: 0.74rem; color: #6E7AA0; margin-top: 0.15rem; }

/* Etiqueta de sección con línea divisoria */
.gdlm-section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem; color: var(--color-muted);
    text-transform: uppercase; letter-spacing: 0.06em;
    margin: 2.2rem 0 0.9rem 0;
    display: flex; align-items: center; gap: 0.6rem;
}
.gdlm-section-label::after {
    content: ""; flex: 1; height: 1px; background: var(--color-border);
}

/* ---------- KPIs ---------- */
.gdlm-kpi-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-top: 3px solid var(--color-cyan);
    border-radius: 14px;
    padding: 1.2rem 1.3rem;
    height: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}
.gdlm-kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 26px rgba(0, 0, 0, 0.35);
    background: var(--color-surface-hover);
}
.gdlm-kpi-icon { font-size: 1.15rem; margin-bottom: 0.55rem; }
.gdlm-kpi-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: var(--color-muted);
    font-weight: 500;
    margin-bottom: 0.45rem;
}
.gdlm-kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.7rem;
    font-weight: 600;
    color: #F1F5FB;
    line-height: 1;
}
.gdlm-kpi-value.amber { color: var(--color-amber); }
.gdlm-kpi-caption { font-size: 0.7rem; color: var(--color-muted); margin-top: 0.5rem; }

/* Variante compacta de tarjeta, para paneles con más densidad de datos
   (ej. Modelo Supervisado / No Supervisado) */
.gdlm-metric-chip {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    text-align: center;
}
.gdlm-metric-chip-label {
    font-family: 'Inter', sans-serif; font-size: 0.72rem;
    color: var(--color-muted); margin-bottom: 0.3rem;
}
.gdlm-metric-chip-value {
    font-family: 'IBM Plex Mono', monospace; font-size: 1.3rem;
    font-weight: 600; color: #F1F5FB;
}

/* Badge de modelo (nombre del algoritmo ganador) */
.gdlm-model-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(34, 211, 238, 0.1);
    border: 1px solid rgba(34, 211, 238, 0.3);
    color: var(--color-cyan-soft);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
}

/* Badge de etiqueta de cluster — color según composición real, no el
   número de cluster (que es arbitrario) */
.gdlm-cluster-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
}
.gdlm-cluster-badge.completado {
    background: rgba(34, 211, 238, 0.1); border: 1px solid rgba(34, 211, 238, 0.3); color: var(--color-cyan-soft);
}
.gdlm-cluster-badge.cancelado {
    background: rgba(245, 166, 35, 0.12); border: 1px solid rgba(245, 166, 35, 0.35); color: var(--color-amber);
}
.gdlm-cluster-badge.mixto {
    background: rgba(139, 150, 184, 0.12); border: 1px solid rgba(139, 150, 184, 0.3); color: var(--color-muted);
}

/* ---------- Gráficas / tarjetas genéricas con key dinámico ---------- */
div[class*="st-key-chart_card_"] {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 14px;
    padding: 1.1rem 1.2rem 0.3rem 1.2rem;
}
.gdlm-chart-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 0.3rem;
}

/* ---------- Tarjetas de imagen (gráficas matplotlib con fondo claro) ---------- */
/* Las gráficas del notebook tienen fondo blanco por defecto; en vez de
   dejarlas flotando sobre el tema oscuro, se enmarcan en una tarjeta clara
   a propósito -> se ve como una "ficha técnica" deliberada, no un parche. */
div[class*="st-key-img_card_"] {
    background: #F8FAFC;
    border-radius: 14px;
    padding: 0.9rem 0.9rem 0.3rem 0.9rem;
    border: 1px solid rgba(255, 255, 255, 0.06);
}
.gdlm-img-caption {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: var(--color-muted);
    text-align: center;
    margin-top: 0.5rem;
}

/* ---------- Resultado de simulación (Realizar Pedido) ---------- */
.gdlm-resultado-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 1.3rem;
    padding: 0.6rem 1.2rem;
    border-radius: 12px;
}
.gdlm-resultado-badge.completado {
    background: rgba(34, 211, 238, 0.12); border: 1px solid rgba(34, 211, 238, 0.35); color: var(--color-cyan-soft);
}
.gdlm-resultado-badge.cancelado {
    background: rgba(245, 166, 35, 0.12); border: 1px solid rgba(245, 166, 35, 0.4); color: var(--color-amber);
}
.gdlm-resultado-detalle {
    font-family: 'Inter', sans-serif; font-size: 0.85rem; color: var(--color-muted);
    margin-top: 0.5rem; line-height: 1.6;
}

/* ---------- Ajuste de widgets nativos de Streamlit para el tema oscuro ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--color-surface);
    border-radius: 14px !important;
    border-color: var(--color-border) !important;
}
</style>
"""


def inyectar_estilos() -> None:
    """Inyecta el CSS del tema. Llamar UNA vez, al inicio de app.py."""
    st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data
def cargar_logo_html() -> str:
    """Embebe logover.png como base64 dentro de un <img>. Si el archivo no
    está junto a app.py, cae a un texto de respaldo en vez de romper la
    página."""
    if RUTA_LOGO.exists():
        b64 = base64.b64encode(RUTA_LOGO.read_bytes()).decode("utf-8")
        return f'<img src="data:image/png;base64,{b64}" class="gdlm-logo-img" alt="GDLM" />'
    return '<div class="gdlm-logo-fallback">GDLM</div>'
