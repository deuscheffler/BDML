"""
paginas/modelo_no_supervisado.py
===================================
Página "Modelo No Supervisado": métricas de clustering (desde
metadata_kmeans.json), un explorador interactivo de clusters (usa datos
ya guardados en modelo_kmeans_artifacts.pkl, sin tocar SQL Server), y las
7 gráficas reales generadas por KMEANSCERCER_corregido.py.

Las imágenes viven en graficas_no_supervisado/, junto a app.py.
"""

from functools import partial
from pathlib import Path

import streamlit as st

from componentes import mostrar_imagen
from load_models import cargar_artefactos_kmeans, etiqueta_cluster

DIR_GRAFICAS = Path(__file__).parent.parent / "graficas_no_supervisado"
_mostrar_imagen = partial(mostrar_imagen, DIR_GRAFICAS)

_CLASE_BADGE = {
    "Predominantemente COMPLETE": "completado",
    "Predominantemente CANCELED": "cancelado",
    "Mixto": "mixto",
}


def render() -> None:
    artefactos = cargar_artefactos_kmeans()
    k_optimo = artefactos["k_optimo"]

    # --- Encabezado ---
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:0.3rem;">
            <p class="gdlm-hero-title" style="margin-bottom:0;">Modelo No Supervisado</p>
            <span class="gdlm-model-badge">🧭 KMeans · k={k_optimo}</span>
        </div>
        <p class="gdlm-hero-desc">
            Segmentación de pedidos por comportamiento (envío, ganancia, tipo de
            transacción) y detección de anomalías/outliers, sobre el mismo
            dataset relacional.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # --- Tarjetas de métricas ---
    st.markdown('<div class="gdlm-section-label">Métricas del modelo</div>', unsafe_allow_html=True)
    etiquetas = [
        ("Silhouette", f"{artefactos['silhouette']:.4f}"),
        ("Calinski-Harabasz", f"{artefactos['calinski_harabasz']:,.0f}"),
        ("Davies-Bouldin", f"{artefactos['davies_bouldin']:.4f}"),
        ("k óptimo", str(k_optimo)),
        ("Features usadas", str(artefactos["n_features"])),
    ]
    cols = st.columns(5, gap="medium")
    for col, (nombre, valor) in zip(cols, etiquetas):
        with col:
            st.markdown(
                f"""<div class="gdlm-metric-chip">
                    <div class="gdlm-metric-chip-label">{nombre}</div>
                    <div class="gdlm-metric-chip-value">{valor}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    # --- Explorador interactivo de clusters ---
    st.markdown('<div class="gdlm-section-label">Explorador de clusters</div>', unsafe_allow_html=True)
    with st.container(border=True):
        col_sel, col_info = st.columns([1, 3], gap="large")

        with col_sel:
            cluster_sel = st.selectbox(
                "Selecciona un cluster",
                options=list(range(k_optimo)),
                format_func=lambda c: f"Cluster {c}",
            )

        info = etiqueta_cluster(cluster_sel, artefactos)
        tamano_pct = artefactos["tamano_clusters"].get(str(cluster_sel), 0.0)
        clase_badge = _CLASE_BADGE.get(info["etiqueta"], "mixto")

        with col_info:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
                    <span class="gdlm-cluster-badge {clase_badge}">{info['etiqueta']}</span>
                    <span class="gdlm-img-caption" style="margin:0;">
                        Tamaño: <b>{tamano_pct}%</b> del dataset
                        &nbsp;·&nbsp; Completado: <b>{info['pct_complete']}%</b>
                        &nbsp;·&nbsp; Cancelado: <b>{info['pct_cancelado']}%</b>
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --- Selección de k óptimo ---
    st.markdown('<div class="gdlm-section-label">Selección de k óptimo</div>', unsafe_allow_html=True)
    _mostrar_imagen(
        "01_seleccion_k.png", "img_card_seleccion_k",
        "Silhouette, Calinski-Harabasz y Davies-Bouldin por número de clusters evaluado.",
    )

    # --- Composición de clusters ---
    st.markdown('<div class="gdlm-section-label">Composición de clusters</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        _mostrar_imagen("02_tamano_clusters.png", "img_card_tamano", "Tamaño relativo de cada cluster.")
    with col_b:
        _mostrar_imagen(
            "03_composicion_objetivo.png", "img_card_composicion_obj",
            "% Completado vs Cancelado por cluster.",
        )


    # --- Reducción de dimensionalidad ---
    st.markdown('<div class="gdlm-section-label">Reducción de dimensionalidad</div>', unsafe_allow_html=True)
    col_c, col_d = st.columns(2, gap="medium")
    with col_c:
        _mostrar_imagen("05_clusters_pca2d.png", "img_card_pca2d", "Clusters proyectados en 2 componentes principales.")
    with col_d:
        _mostrar_imagen("06_pca_varianza.png", "img_card_pca_var", "Varianza explicada acumulada por componente PCA.")

    _mostrar_imagen("07_tsne_clusters.png", "img_card_tsne", "Proyección t-SNE de los clusters.")
