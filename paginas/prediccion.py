"""
paginas/prediccion.py
========================
Página "Predicción": busca un pedido que YA existe en la base de datos
por su id_pedido y predice su estado, reutilizando el cluster_kmeans/
es_anomalia/es_outlier ya calculados por la última corrida de
KMEANSCERCER_corregido.py (no vuelve a correr KMeans). Como el pedido ya
existe, también se conoce el estado real — se muestra la comparación
predicho vs. real.

Cada consulta se registra en MongoDB, igual que en Realizar Pedido.
"""

import streamlit as st

from componentes import renderizar_resultado_prediccion
from datos import cargar_datos_dashboard, SQL_SERVER, SQL_DATABASE
from load_models import (
    obtener_conexion_sql,
    predecir_estado_pedido_existente,
    cargar_artefactos_kmeans,
    cargar_modelo_supervisado,
    cargar_metadatos_supervisado,
)
from mongo_logger import asegurar_indices, registrar_prediccion


@st.cache_resource(show_spinner=False)
def _inicializar_indices_mongo() -> bool:
    try:
        asegurar_indices()
        return True
    except Exception as e:
        st.warning(f"MongoDB no disponible para el registro de predicciones: {e}")
        return False


def render() -> None:
    st.markdown(
        """
        <p class="gdlm-hero-title" style="margin-bottom:0;">Predicción</p>
        <p class="gdlm-hero-desc">
            Busca un pedido que ya existe en la base de datos por su ID y
            predice su estado, usando el cluster y las señales de anomalía
            ya calculados por el modelo no supervisado — sin recalcular nada.
        </p>
        """,
        unsafe_allow_html=True,
    )

    mongo_disponible = _inicializar_indices_mongo()

    df = cargar_datos_dashboard()
    id_min, id_max = int(df["id_pedido"].min()), int(df["id_pedido"].max())

    st.markdown('<div class="gdlm-section-label">Buscar pedido</div>', unsafe_allow_html=True)
    with st.form("form_prediccion"):
        col_id, col_btn = st.columns([3, 1], gap="medium")
        with col_id:
            id_pedido = st.number_input(
                f"ID de pedido (rango disponible: {id_min:,} – {id_max:,})",
                min_value=id_min, max_value=id_max, value=id_min, step=1,
            )
        with col_btn:
            st.markdown("<br/>", unsafe_allow_html=True)
            buscar = st.form_submit_button("🔍 Buscar y predecir", use_container_width=True)

    if not buscar:
        return

    engine = obtener_conexion_sql(SQL_SERVER, SQL_DATABASE)
    artefactos_kmeans = cargar_artefactos_kmeans()
    modelo_sup, scaler_sup = cargar_modelo_supervisado()
    features, frecuencias, dummies, medianas, metadata_sup = cargar_metadatos_supervisado()

    try:
        resultado = predecir_estado_pedido_existente(
            int(id_pedido), engine, artefactos_kmeans, modelo_sup, scaler_sup,
            features, frecuencias, dummies, medianas, metadata_sup,
        )
    except ValueError as e:
        st.warning(str(e))
        return

    if resultado is None:
        st.info(f"No existe ningún pedido con id_pedido = {int(id_pedido)}.")
        return

    if mongo_disponible:
        registrar_prediccion(
            resultado=resultado,
            pedido_input={"id_pedido": int(id_pedido)},
            usuario="anonimo",
            id_pedido=int(id_pedido),
            modelo_version=metadata_sup.get("fecha_entrenamiento"),
        )

    # --- Resultado ---
    st.markdown('<div class="gdlm-section-label">Resultado</div>', unsafe_allow_html=True)

    acierto = resultado["estado_real"] == resultado["prediccion"]
    texto_acierto = "✔️ La predicción coincide con el estado real" if acierto else "✖️ La predicción NO coincide con el estado real"

    nota_pie = (
        f"{texto_acierto}"
        f"{' · registrado en MongoDB' if mongo_disponible else ' · no se registró en MongoDB (sin conexión)'}"
    )
    renderizar_resultado_prediccion(
        resultado,
        chips_extra=[("Estado real", resultado["estado_real"])],
        nota_pie=nota_pie,
    )
