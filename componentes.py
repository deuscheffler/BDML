"""
componentes.py
================
Piezas de UI reutilizables entre páginas (por ahora, el marco de imagen
usado en Modelo Supervisado y Modelo No Supervisado para las gráficas
estáticas generadas por los scripts de entrenamiento).
"""

from pathlib import Path

import streamlit as st


def mostrar_imagen(dir_graficas: Path, nombre_archivo: str, key: str, caption: str) -> None:
    """Muestra una imagen enmarcada en una tarjeta clara (las gráficas de
    matplotlib tienen fondo blanco por defecto). Si el archivo no existe,
    avisa en vez de romper la página."""
    ruta = dir_graficas / nombre_archivo
    if not ruta.exists():
        st.warning(f"No se encontró {nombre_archivo} en {dir_graficas.name}/.")
        return
    with st.container(key=key):
        st.image(str(ruta), use_container_width=True)
    st.markdown(f'<div class="gdlm-img-caption">{caption}</div>', unsafe_allow_html=True)
