"""
app.py — GDLM
================
Diseño e Implementación de una Solución de Analítica Predictiva e
Infraestructura de Persistencia Híbrida para la Optimización de Cadenas
de Suministro.

Punto de entrada de la app: configuración de página, inyección de
estilos, barra de navegación y enrutamiento. La lógica de cada sección
vive en su propio módulo dentro de paginas/, para mantener esto legible
a medida que se agregan más páginas.
"""

import streamlit as st

from estilos import inyectar_estilos, cargar_logo_html
from paginas import inicio, modelo_supervisado, modelo_no_supervisado, realizar_pedido

st.set_page_config(
    page_title="GDLM",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inyectar_estilos()

# ============================================================================
# ESTADO DE NAVEGACIÓN
# ============================================================================
PAGINAS = ["Inicio", "Modelo Supervisado", "Modelo No Supervisado", "Predicción", "Realizar Pedido"]

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "Inicio"


def ir_a(pagina: str) -> None:
    st.session_state.pagina_actual = pagina


# ============================================================================
# RENDER — Barra de navegación
# ============================================================================
with st.container(key="nav_bar"):
    col_marca, col_nav = st.columns([1.5, 4], gap="large")

    with col_marca:
        st.markdown(
            f"""
            <div class="gdlm-brand-row">
                {cargar_logo_html()}
                <span class="gdlm-status-pill">
                    <span class="gdlm-pulse">
                        <span class="gdlm-pulse-ring"></span>
                        <span class="gdlm-pulse-dot"></span>
                    </span>
                    EN LÍNEA
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_nav:
        nav_cols = st.columns([len(p) + 3 for p in PAGINAS])
        for col, pagina in zip(nav_cols, PAGINAS):
            with col:
                st.button(
                    pagina,
                    key=f"nav_{pagina}",
                    on_click=ir_a,
                    args=(pagina,),
                    use_container_width=True,
                )


# ============================================================================
# ENRUTAMIENTO
# ============================================================================
def render_placeholder(nombre_pagina: str) -> None:
    st.info(f"La página **{nombre_pagina}** se construye en el siguiente paso.")


PAGINA_ACTUAL = st.session_state.pagina_actual

if PAGINA_ACTUAL == "Inicio":
    inicio.render()
elif PAGINA_ACTUAL == "Modelo Supervisado":
    modelo_supervisado.render()
elif PAGINA_ACTUAL == "Modelo No Supervisado":
    modelo_no_supervisado.render()
elif PAGINA_ACTUAL == "Realizar Pedido":
    realizar_pedido.render()
else:
    render_placeholder(PAGINA_ACTUAL)
