"""
paginas/modelo_supervisado.py
================================
Página "Modelo Supervisado": tarjetas de métricas del modelo ganador
(desde metadata_modelo.json, sin valores hardcodeados) + las gráficas
reales generadas durante el entrenamiento (comparación de modelos, matriz
de confusión, curva ROC, importancia por permutación, calibración,
estabilidad y EDA). No incluye predicción interactiva a propósito — eso
vive en las páginas de Predicción / Realizar Pedido.

Las imágenes viven en graficas_supervisado/, junto a app.py.
"""

from pathlib import Path

import streamlit as st

from load_models import cargar_metadatos_supervisado

DIR_GRAFICAS = Path(__file__).parent.parent / "graficas_supervisado"


def _mostrar_imagen(nombre_archivo: str, key: str, caption: str) -> None:
    ruta = DIR_GRAFICAS / nombre_archivo
    if not ruta.exists():
        st.warning(f"No se encontró {nombre_archivo} en graficas_supervisado/.")
        return
    with st.container(key=key):
        st.image(str(ruta), use_container_width=True)
    st.markdown(f'<div class="gdlm-img-caption">{caption}</div>', unsafe_allow_html=True)


def render() -> None:
    _, _, _, _, metadata_sup = cargar_metadatos_supervisado()

    # --- Encabezado ---
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:0.3rem;">
            <p class="gdlm-hero-title" style="margin-bottom:0;">Modelo Supervisado</p>
            <span class="gdlm-model-badge">🧠 {metadata_sup['modelo']}</span>
        </div>
        <p class="gdlm-hero-desc">
            Clasificación binaria del estado del pedido (Completado / Cancelado)
            entrenada sobre {metadata_sup.get('dataset_origen', 'SQL Server')}.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # --- Tarjetas de métricas ---
    st.markdown('<div class="gdlm-section-label">Métricas del modelo ganador</div>', unsafe_allow_html=True)
    metricas = metadata_sup["metricas_test"]
    etiquetas = [
        ("Accuracy", metricas["accuracy"]),
        ("Precision", metricas["precision"]),
        ("Recall", metricas["recall"]),
        ("F1-Score", metricas["f1"]),
        ("ROC-AUC", metricas["roc_auc"]),
    ]
    cols = st.columns(5, gap="medium")
    for col, (nombre, valor) in zip(cols, etiquetas):
        with col:
            st.markdown(
                f"""<div class="gdlm-metric-chip">
                    <div class="gdlm-metric-chip-label">{nombre}</div>
                    <div class="gdlm-metric-chip-value">{valor * 100:.1f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""<p class="gdlm-img-caption" style="margin-top:0.8rem;">
            Umbral de alerta recomendado: <b>{metadata_sup.get('umbral_alerta_recomendado', 0.5)}</b>
            &nbsp;·&nbsp; Variables excluidas por fuga de datos:
            <b>{', '.join(metadata_sup.get('features_leakage_excluidas', []))}</b>
        </p>""",
        unsafe_allow_html=True,
    )

    # --- Comparación de modelos ---
    st.markdown('<div class="gdlm-section-label">Comparación de modelos evaluados</div>', unsafe_allow_html=True)
    _mostrar_imagen(
        "v2_06_comparacion_modelos.png", "img_card_comparacion",
        "KNN, Random Forest, SVM, Regresión Logística, XGBoost y Árbol de Decisión — accuracy, precision, recall, F1 y ROC-AUC.",
    )

    # --- Evaluación del modelo ganador ---
    st.markdown('<div class="gdlm-section-label">Evaluación del modelo ganador (KNN)</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        _mostrar_imagen("v2_07_matriz_confusion.png", "img_card_matriz", "Matriz de confusión sobre el conjunto de prueba.")
    with col_b:
        _mostrar_imagen("v2_08_roc.png", "img_card_roc", "Curva ROC — AUC ≈ 0.87.")

    # --- Diagnóstico avanzado ---
    st.markdown('<div class="gdlm-section-label">Diagnóstico avanzado</div>', unsafe_allow_html=True)
    col_c, col_d, col_e = st.columns(3, gap="medium")
    with col_c:
        _mostrar_imagen(
            "v2_09_importancia_permutacion.png", "img_card_importancia",
            "Importancia por permutación — riesgo_retraso domina la predicción.",
        )
    with col_d:
        _mostrar_imagen(
            "v2_10_calibracion.png", "img_card_calibracion",
            "Calibración de probabilidades antes/después del ajuste sigmoid.",
        )
    with col_e:
        _mostrar_imagen(
            "v2_11_estabilidad_modelo.png", "img_card_estabilidad",
            "Estabilidad del F1-score según el % de datos de entrenamiento usados.",
        )

    # --- Análisis exploratorio de datos ---
    st.markdown('<div class="gdlm-section-label">Análisis exploratorio de datos</div>', unsafe_allow_html=True)
    col_f, col_g = st.columns(2, gap="medium")
    with col_f:
        _mostrar_imagen(
            "v2_05_desbalanceo_target.png", "img_card_desbalanceo",
            "Distribución de la variable objetivo: 66.2% Completado vs 33.8% Cancelado.",
        )
    with col_g:
        _mostrar_imagen("v2_02_correlacion.png", "img_card_correlacion", "Correlación entre variables numéricas y el target.")

    _mostrar_imagen(
        "v2_01_eda_distribuciones.png", "img_card_distribuciones",
        "Distribución y boxplot de días de envío, beneficio y ventas del cliente.",
    )
    _mostrar_imagen(
        "v2_03_categoricas_vs_target.png", "img_card_categoricas",
        "Modo de envío, categoría y riesgo de retraso vs. estado del pedido.",
    )
    _mostrar_imagen(
        "v2_04_violin.png", "img_card_violin",
        "Distribución de días de envío y beneficio del pedido, por estado.",
    )
