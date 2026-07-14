"""
paginas/realizar_pedido.py
=============================
Página "Realizar Pedido": simulador de un pedido hipotético. El usuario
llena solo los campos que realmente se conocen al momento de crear un
pedido (categoría, región, modo de envío, tipo de transacción, días
programados, cantidad, precio, margen esperado). Los campos que NO se
pueden conocer de antemano se resuelven así:

- dias_envio_real: se ESTIMA con el promedio histórico de ese modo_envio
  (no se le pide al usuario, porque es un dato que solo existe después
  de despachar el pedido).
- ventas / total_item / ventas_cliente / beneficio_pedido / ganancia_pedido:
  se calculan a partir de cantidad, precio unitario y margen esperado, en
  vez de pedir 6 campos financieros redundantes por separado.

Cada simulación se registra en MongoDB vía mongo_logger.py.
"""

import streamlit as st

from datos import cargar_datos_dashboard, promedio_envio_por_modo
from load_models import (
    cargar_artefactos_kmeans,
    cargar_modelo_supervisado,
    cargar_metadatos_supervisado,
    predecir_estado_pedido,
)
from mongo_logger import asegurar_indices, registrar_prediccion

MODOS_ENVIO = ["First Class", "Same Day", "Second Class", "Standard Class"]
TIPOS_TRANSACCION = ["CASH", "DEBIT", "PAYMENT", "TRANSFER"]


@st.cache_resource(show_spinner=False)
def _inicializar_indices_mongo() -> bool:
    """Se ejecuta una sola vez por sesión (cacheado): crea los índices de
    MongoDB si no existen. Si Mongo no está disponible, no rompe la
    página — solo deja de loguear."""
    try:
        asegurar_indices()
        return True
    except Exception as e:
        st.warning(f"MongoDB no disponible para el registro de predicciones: {e}")
        return False


def render() -> None:
    st.markdown(
        """
        <p class="gdlm-hero-title" style="margin-bottom:0;">Realizar Pedido</p>
        <p class="gdlm-hero-desc">
            Simula un pedido hipotético y predice si se completaría o se
            cancelaría. Los campos que aún no existen al momento de crear
            un pedido (tiempo real de envío, cifras financieras derivadas)
            se estiman automáticamente a partir del histórico — no se
            piden porque en la realidad todavía no se conocen.
        </p>
        """,
        unsafe_allow_html=True,
    )

    mongo_disponible = _inicializar_indices_mongo()

    # Datos para poblar los selectores (mismas categorías que vio el
    # modelo en entrenamiento) y para estimar dias_envio_real.
    features, frecuencias, dummies, medianas, metadata_sup = cargar_metadatos_supervisado()
    df_historico = cargar_datos_dashboard()
    promedios_envio = promedio_envio_por_modo(df_historico)

    categorias_opciones = sorted(frecuencias["categoria"].keys())
    regiones_opciones = sorted(frecuencias["region_destino"].keys())

    st.markdown('<div class="gdlm-section-label">Datos del pedido</div>', unsafe_allow_html=True)

    with st.form("form_realizar_pedido"):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            categoria_sel = st.selectbox("Categoría del producto", categorias_opciones)
            region_sel = st.selectbox("Región destino", regiones_opciones)
            modo_envio_sel = st.selectbox("Modo de envío", MODOS_ENVIO)
            tipo_transaccion_sel = st.selectbox("Tipo de transacción", TIPOS_TRANSACCION)

        with col2:
            dias_prog = st.number_input("Días de envío programados", min_value=0, max_value=15, value=4)
            cantidad = st.number_input("Cantidad", min_value=1, max_value=50, value=1)
            precio_unitario = st.number_input("Precio unitario ($)", min_value=0.0, value=59.99, step=1.0)
            margen_pct = st.slider("Margen de ganancia esperado (%)", min_value=0, max_value=60, value=20)

        riesgo_retraso = st.checkbox("Marcar como envío de riesgo (opcional)", value=False)

        enviado = st.form_submit_button("🔮 Simular pedido", use_container_width=True)

    if not enviado:
        return

    # --- Días de envío real: NO se pregunta, se estima con el promedio
    # histórico de ese modo_envio (o el promedio global si el modo no
    # tiene historial suficiente). ---
    dias_real_estimado = promedios_envio.get(
        modo_envio_sel, float(df_historico["dias_envio_real"].mean())
    )

    # --- Campos financieros: se derivan de cantidad + precio + margen,
    # en vez de pedir 6 campos redundantes por separado. ---
    ventas = float(cantidad * precio_unitario)
    ganancia = ventas * (margen_pct / 100)

    pedido = {
        "dias_envio_real": dias_real_estimado,
        "dias_envio_prog": dias_prog,
        "beneficio_pedido": ganancia,
        "ventas_cliente": ventas,
        "precio_base": precio_unitario,
        "margen_ganancia_item": margen_pct / 100,
        "cantidad": cantidad,
        "ventas": ventas,
        "total_item": ventas,
        "ganancia_pedido": ganancia,
        "riesgo_retraso": riesgo_retraso,
        "modo_envio": modo_envio_sel,
        "tipo_transaccion": tipo_transaccion_sel,
        "categoria": categoria_sel,
        "region_destino": region_sel,
    }

    artefactos_kmeans = cargar_artefactos_kmeans()
    modelo_sup, scaler_sup = cargar_modelo_supervisado()

    resultado = predecir_estado_pedido(
        pedido, artefactos_kmeans, modelo_sup, scaler_sup,
        features, frecuencias, dummies, medianas, metadata_sup,
    )

    # --- Registro en MongoDB (no bloquea la página si falla) ---
    if mongo_disponible:
        registrar_prediccion(
            resultado=resultado,
            pedido_input=pedido,
            usuario="anonimo",
            id_pedido=None,
            modelo_version=metadata_sup.get("fecha_entrenamiento"),
        )

    # --- Resultado ---
    st.markdown('<div class="gdlm-section-label">Resultado de la simulación</div>', unsafe_allow_html=True)

    clase = "completado" if resultado["prediccion"] == "COMPLETE" else "cancelado"
    texto_resultado = "✅ Se completaría" if resultado["prediccion"] == "COMPLETE" else "⚠️ Se cancelaría"

    with st.container(border=True):
        col_badge, col_prob = st.columns([2, 1], gap="large")
        with col_badge:
            st.markdown(
                f'<span class="gdlm-resultado-badge {clase}">{texto_resultado}</span>',
                unsafe_allow_html=True,
            )
        with col_prob:
            st.markdown(
                f"""<div class="gdlm-metric-chip">
                    <div class="gdlm-metric-chip-label">Probabilidad de completado</div>
                    <div class="gdlm-metric-chip-value">{resultado['probabilidad_completado'] * 100:.1f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )

        alerta_txt = "⚠️ Por debajo del umbral de alerta" if resultado["alerta_riesgo"] else "Dentro de un rango normal"
        st.markdown(
            f"""
            <div class="gdlm-resultado-detalle">
                Cluster asignado: <b>{resultado['cluster_kmeans']}</b> ({resultado['cluster_etiqueta']})
                &nbsp;·&nbsp; Anomalía: <b>{'Sí' if resultado['es_anomalia'] else 'No'}</b>
                &nbsp;·&nbsp; Outlier: <b>{'Sí' if resultado['es_outlier'] else 'No'}</b>
                <br/>
                Días de envío real estimados (promedio histórico para "{modo_envio_sel}"): <b>{dias_real_estimado:.1f} días</b>
                &nbsp;·&nbsp; {alerta_txt}
                {' · registrado en MongoDB' if mongo_disponible else ' · no se registró en MongoDB (sin conexión)'}
            </div>
            """,
            unsafe_allow_html=True,
        )
