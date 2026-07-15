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


def renderizar_resultado_prediccion(
    resultado: dict,
    chips_extra: list | None = None,
    nota_pie: str = "",
) -> None:
    """
    Muestra el resultado de predecir_estado_pedido() /
    predecir_estado_pedido_existente() como una COMPARATIVA de los dos
    modelos (no supervisado y supervisado) en vez de un solo párrafo,
    más un veredicto de si ambos apuntan en la misma dirección.

    chips_extra: pares (label, valor) adicionales para la tarjeta del
        modelo supervisado (ej. 'Estado real' en la página Predicción).
    nota_pie: texto pequeño y de menor jerarquía (ej. días estimados,
        estado de registro en MongoDB).
    """
    chips_extra = chips_extra or []
    clase_pred = "completado" if resultado["prediccion"] == "COMPLETE" else "cancelado"
    texto_pred = "Se completaría" if resultado["prediccion"] == "COMPLETE" else "Se cancelaría"

    col_no_sup, col_sup = st.columns(2, gap="medium")

    # --- Tarjeta: Modelo No Supervisado ---
    with col_no_sup:
        clase_cluster = (
            "completado" if "COMPLETE" in resultado["cluster_etiqueta"]
            else "cancelado" if "CANCELED" in resultado["cluster_etiqueta"]
            else "mixto"
        )
        st.markdown(
            f"""
            <div class="gdlm-modelo-card">
                <div class="gdlm-modelo-card-header"><span class="icon">🧭</span> Modelo No Supervisado</div>
                <span class="gdlm-cluster-badge {clase_cluster}">{resultado['cluster_etiqueta']}</span>
                <div class="gdlm-modelo-card-fila">
                    <span class="gdlm-modelo-card-fila-label">Cluster asignado</span>
                    <span class="gdlm-modelo-card-fila-valor">{resultado['cluster_kmeans']}</span>
                </div>
                <div class="gdlm-modelo-card-fila">
                    <span class="gdlm-modelo-card-fila-label">Anomalía</span>
                    <span class="gdlm-modelo-card-fila-valor">{'Sí' if resultado['es_anomalia'] else 'No'}</span>
                </div>
                <div class="gdlm-modelo-card-fila">
                    <span class="gdlm-modelo-card-fila-label">Outlier</span>
                    <span class="gdlm-modelo-card-fila-valor">{'Sí' if resultado['es_outlier'] else 'No'}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Tarjeta: Modelo Supervisado ---
    with col_sup:
        filas_extra = "".join(
            f"""<div class="gdlm-modelo-card-fila">
                    <span class="gdlm-modelo-card-fila-label">{label}</span>
                    <span class="gdlm-modelo-card-fila-valor">{valor}</span>
                </div>"""
            for label, valor in chips_extra
        )
        st.markdown(
            f"""
            <div class="gdlm-modelo-card">
                <div class="gdlm-modelo-card-header"><span class="icon">🧠</span> Modelo Supervisado</div>
                <span class="gdlm-resultado-badge {clase_pred}">{texto_pred}</span>
                <div class="gdlm-modelo-card-fila">
                    <span class="gdlm-modelo-card-fila-label">Probabilidad de completado</span>
                    <span class="gdlm-modelo-card-fila-valor">{resultado['probabilidad_completado'] * 100:.1f}%</span>
                </div>
                <div class="gdlm-modelo-card-fila">
                    <span class="gdlm-modelo-card-fila-label">Umbral de alerta</span>
                    <span class="gdlm-modelo-card-fila-valor">{'⚠️ Activado' if resultado['alerta_riesgo'] else 'Normal'}</span>
                </div>
                {filas_extra}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Veredicto de concordancia entre los dos modelos ---
    etiqueta = resultado["cluster_etiqueta"]
    prediccion = resultado["prediccion"]
    if "Mixto" in etiqueta:
        clase_v, texto_v = "mixto_v", "➗ El cluster no tiene una tendencia clara — el no supervisado no aporta una señal fuerte aquí."
    elif ("COMPLETE" in etiqueta and prediccion == "COMPLETE") or ("CANCELED" in etiqueta and prediccion == "CANCELED"):
        clase_v, texto_v = "coincide", "✔️ Ambos modelos apuntan en la misma dirección."
    else:
        clase_v, texto_v = "discrepa", "⚠️ Los modelos difieren: el cluster sugiere una tendencia distinta a la predicción final."

    st.markdown(f'<div class="gdlm-veredicto {clase_v}">{texto_v}</div>', unsafe_allow_html=True)

    if nota_pie:
        st.markdown(f'<div class="gdlm-nota-pie">{nota_pie}</div>', unsafe_allow_html=True)
