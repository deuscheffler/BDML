"""
app_streamlit.py
=================
App de Streamlit para predecir si un pedido será COMPLETO o CANCELADO
usando el modelo KMeans ponderado ya entrenado.

Requisito previo: haber corrido 'entrenar_y_guardar_modelo.py' en la carpeta
que contiene 'DataCoSupplyChain_Limpio.csv'. Eso genera la carpeta
'modelo_artifacts/' con el modelo y los objetos de preprocesamiento.

Coloca este archivo en la MISMA carpeta que 'modelo_artifacts/' y ejecuta:
    streamlit run app_streamlit.py
"""

import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st

CARPETA_ARTIFACTS = "modelo_artifacts"

st.set_page_config(page_title="Predicción de Pedido", page_icon="📦", layout="centered")


# ============================================================================
# CARGA DE ARTEFACTOS (una sola vez, cacheado)
# ============================================================================
@st.cache_resource
def cargar_artefactos():
    ruta = CARPETA_ARTIFACTS
    kmeans = joblib.load(os.path.join(ruta, "kmeans.joblib"))
    scaler_numericas = joblib.load(os.path.join(ruta, "scaler_numericas.joblib"))
    scaler_otras = joblib.load(os.path.join(ruta, "scaler_otras.joblib"))
    scaler_tx = joblib.load(os.path.join(ruta, "scaler_tx.joblib"))
    metadata = joblib.load(os.path.join(ruta, "metadata.joblib"))
    return kmeans, scaler_numericas, scaler_otras, scaler_tx, metadata


if not os.path.exists(CARPETA_ARTIFACTS):
    st.error(
        f"No se encontró la carpeta '{CARPETA_ARTIFACTS}/'. "
        f"Primero ejecuta 'entrenar_y_guardar_modelo.py' en la carpeta con tu CSV, "
        f"y copia la carpeta '{CARPETA_ARTIFACTS}/' junto a esta app."
    )
    st.stop()

kmeans, scaler_numericas, scaler_otras, scaler_tx, meta = cargar_artefactos()

NUMERICAS = meta["numericas"]
MODO_ENVIO_COLS = meta["modo_envio_cols"]
OTRAS_CATEGORICAS_COLS = meta["otras_categoricas_cols"]
TX_COLS = meta["tx_cols"]
FRECUENCIAS = meta["frecuencias"]
PESO_NUMERICAS = meta["peso_numericas"]
PESO_OTRAS = meta["peso_otras"]
PESO_TX = meta["peso_tx"]
MAPA_RESULTADO = meta["mapa_resultado"]  # {0:"Cancelado", 1:"Completo", 2:"Completo", 3:"Completo"}


# ============================================================================
# FUNCIÓN DE PREPROCESAMIENTO PARA UN SOLO PEDIDO NUEVO
# (replica exactamente la lógica de construir_espacio_ponderado)
# ============================================================================
def construir_vector_pedido(datos: dict) -> np.ndarray:
    # --- Bloque numéricas ---
    fila_numericas = pd.DataFrame([{col: datos[col] for col in NUMERICAS}])
    X_numericas = scaler_numericas.transform(fila_numericas)

    # --- Bloque "otras": riesgo_retraso + modo_envio dummy + categoria/region freq ---
    fila_otras = {}
    fila_otras["riesgo_retraso"] = int(datos["riesgo_retraso"])

    # dummy de modo_envio (drop_first): todo en 0 salvo la columna correspondiente
    for col in MODO_ENVIO_COLS:
        fila_otras[col] = 0
    col_modo = f"modo_envio_{datos['modo_envio']}"
    if col_modo in fila_otras:
        fila_otras[col_modo] = 1
    # si el valor elegido es la categoría base (la que quedó fuera del drop_first),
    # todas las columnas quedan en 0 correctamente.

    fila_otras["categoria"] = FRECUENCIAS["categoria"].get(datos["categoria"], 0.0)
    fila_otras["region_destino"] = FRECUENCIAS["region_destino"].get(datos["region_destino"], 0.0)

    fila_otras_df = pd.DataFrame([fila_otras])[OTRAS_CATEGORICAS_COLS].astype(float)
    X_otras = scaler_otras.transform(fila_otras_df)

    # --- Bloque tx: one-hot completo de tipo_transaccion ---
    fila_tx = {col: 0 for col in TX_COLS}
    col_tx = f"tx_{datos['tipo_transaccion']}"
    if col_tx in fila_tx:
        fila_tx[col_tx] = 1
    fila_tx_df = pd.DataFrame([fila_tx])[TX_COLS].astype(float)
    X_tx = scaler_tx.transform(fila_tx_df)

    # --- Concatenar con los mismos pesos del entrenamiento ---
    X_ponderado = np.hstack(
        [X_numericas * PESO_NUMERICAS, X_otras * PESO_OTRAS, X_tx * PESO_TX]
    )
    return X_ponderado


def predecir_pedido(datos: dict):
    X = construir_vector_pedido(datos)
    cluster = int(kmeans.predict(X)[0])
    distancias = kmeans.transform(X)[0]
    resultado = MAPA_RESULTADO.get(cluster, "Desconocido")
    return cluster, resultado, distancias


# ============================================================================
# INTERFAZ
# ============================================================================
st.title("📦 Predicción de estado del pedido")
st.caption(
    "Modelo no supervisado (KMeans ponderado). "
    "Cluster 0 → Cancelado · Clusters 1, 2, 3 → Completo"
)

with st.form("form_pedido"):
    st.subheader("Datos del pedido")

    c1, c2 = st.columns(2)
    with c1:
        dias_envio_real = st.number_input("Días de envío real", min_value=0, value=3)
        beneficio_pedido = st.number_input("Beneficio del pedido", value=0.0, format="%.2f")
        precio_base = st.number_input("Precio base", min_value=0.0, value=50.0, format="%.2f")
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
    with c2:
        dias_envio_prog = st.number_input("Días de envío programado", min_value=0, value=4)
        ventas_cliente = st.number_input("Ventas del cliente", value=0.0, format="%.2f")
        margen_ganancia_item = st.number_input("Margen de ganancia del ítem", value=0.0, format="%.2f")
        ventas = st.number_input("Ventas", value=0.0, format="%.2f")

    st.divider()
    c3, c4 = st.columns(2)
    with c3:
        riesgo_retraso = st.selectbox("¿Riesgo de retraso?", options=[0, 1],
                                       format_func=lambda x: "Sí" if x == 1 else "No")
        tipo_transaccion = st.selectbox("Tipo de transacción", options=meta["categorias_tipo_transaccion"])
        modo_envio = st.selectbox("Modo de envío", options=meta["categorias_modo_envio"])
    with c4:
        categoria = st.selectbox("Categoría", options=meta["categorias_categoria"])
        region_destino = st.selectbox("Región de destino", options=meta["categorias_region_destino"])

    enviado = st.form_submit_button("Predecir", use_container_width=True)

if enviado:
    datos = {
        "dias_envio_real": dias_envio_real,
        "dias_envio_prog": dias_envio_prog,
        "beneficio_pedido": beneficio_pedido,
        "ventas_cliente": ventas_cliente,
        "precio_base": precio_base,
        "margen_ganancia_item": margen_ganancia_item,
        "cantidad": cantidad,
        "ventas": ventas,
        "riesgo_retraso": riesgo_retraso,
        "tipo_transaccion": tipo_transaccion,
        "modo_envio": modo_envio,
        "categoria": categoria,
        "region_destino": region_destino,
    }

    cluster, resultado, distancias = predecir_pedido(datos)

    st.divider()
    if resultado == "Cancelado":
        st.error(f"❌ Predicción: **PEDIDO CANCELADO** (cluster {cluster})")
    elif resultado == "Completo":
        st.success(f"✅ Predicción: **PEDIDO COMPLETO** (cluster {cluster})")
    else:
        st.warning(f"Resultado no mapeado (cluster {cluster})")

    with st.expander("Ver detalle técnico"):
        st.write("Distancia a cada centroide (menor = más cercano):")
        st.dataframe(
            pd.DataFrame({"cluster": range(len(distancias)), "distancia": distancias})
            .sort_values("distancia")
            .reset_index(drop=True)
        )
