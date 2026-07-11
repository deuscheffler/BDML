import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Predicción de estado de envío", page_icon="📦", layout="centered")

UMBRAL_ALERTA_DEFECTO = 0.65


# ----------------------------------------------------------------------
# Carga de artefactos (con caché para no recargar en cada interacción)
# ----------------------------------------------------------------------
@st.cache_resource
def cargar_artefactos():
    modelo = joblib.load("modelo_prediccion_envios.pkl")
    scaler = joblib.load("scaler_envios.pkl")

    with open("features_modelo.json", encoding="utf-8") as f:
        features = json.load(f)
    with open("frecuencias_categoricas.json", encoding="utf-8") as f:
        frecuencias_categoricas = json.load(f)
    with open("categorias_dummies.json", encoding="utf-8") as f:
        categorias_dummies = json.load(f)
    with open("medianas_imputacion.json", encoding="utf-8") as f:
        medianas = json.load(f)
    with open("metadata_modelo.json", encoding="utf-8") as f:
        metadata = json.load(f)

    return modelo, scaler, features, frecuencias_categoricas, categorias_dummies, medianas, metadata


try:
    (modelo, scaler, features, frecuencias_categoricas,
     categorias_dummies, medianas, metadata) = cargar_artefactos()
except FileNotFoundError as e:
    st.error(
        "No se encontraron los artefactos del modelo en esta carpeta.\n\n"
        f"Falta: `{e.filename}`.\n\n"
        "Ejecuta primero `python entrenar_modelo.py --csv tu_archivo.csv` y copia "
        "los archivos generados (.pkl y .json) a la misma carpeta que esta app."
    )
    st.stop()


# ----------------------------------------------------------------------
# Réplica de la ingeniería de features y codificación del notebook
# (Secciones 4 y 5 de ModeloSupervisado_V2.ipynb)
# ----------------------------------------------------------------------
def construir_fila_modelo(datos: dict) -> pd.DataFrame:
    df = pd.DataFrame([datos])

    # --- Variables derivadas (Sección 4) ---
    df["diferencia_envio"] = df["dias_envio_real"] - df["dias_envio_prog"]

    dividendo = df["dias_envio_prog"].replace(0, np.nan)
    ratio = df["dias_envio_real"] / dividendo
    df["ratio_envio"] = ratio.fillna(medianas["ratio_envio"])

    df["cumple_plazo"] = (df["dias_envio_real"] <= df["dias_envio_prog"]).astype(int)

    cantidad_div = df["cantidad"].replace(0, np.nan)
    precio_prom = df["ventas"] / cantidad_div
    df["precio_promedio_item"] = precio_prom.fillna(medianas["precio_promedio_item"])

    ventas_div = df["ventas"].replace(0, np.nan)
    margen = df["ganancia_pedido"] / ventas_div
    df["margen_total"] = margen.fillna(0)

    eficiencia = df["ventas_cliente"] / cantidad_div
    df["eficiencia_cliente"] = eficiencia.fillna(medianas["eficiencia_cliente"])

    df["riesgo_por_precio"] = df["riesgo_retraso"].astype(int) * df["precio_base"]

    # --- Codificación (Sección 5) ---
    binarias = ["riesgo_retraso", "es_anomalia", "es_outlier", "cumple_plazo"]
    for col in binarias:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # One-hot manual para las columnas de baja cardinalidad, usando
    # exactamente las categorías vistas en entrenamiento (drop_first=True)
    for col, categorias in categorias_dummies.items():
        valor_actual = df.at[0, col]
        # drop_first=True -> la primera categoría (orden alfabético en train)
        # no genera columna propia; se reconstruye la misma convención aquí.
        for cat in categorias[1:]:
            nombre_col = f"{col}_{cat}"
            df[nombre_col] = 1 if valor_actual == cat else 0
        df = df.drop(columns=[col])

    # Codificación por frecuencia para columnas de alta cardinalidad
    for col, mapa_frecuencias in frecuencias_categoricas.items():
        valor_actual = datos[col]
        df[col] = mapa_frecuencias.get(valor_actual, 0.0)  # categoría no vista en train -> frecuencia 0

    # Reordenar / completar columnas exactamente como en entrenamiento
    for col in features:
        if col not in df.columns:
            df[col] = 0.0
    df = df[features].astype(float)

    return df


def predecir(datos: dict):
    fila = construir_fila_modelo(datos)
    fila_proc = scaler.transform(fila) if metadata["requiere_escalado"] else fila
    probabilidad = modelo.predict_proba(fila_proc)[:, 1][0]
    return probabilidad, fila


# ----------------------------------------------------------------------
# Interfaz
# ----------------------------------------------------------------------
st.title("📦 Predicción de estado del pedido")
st.caption(
    f"Modelo: **{metadata['modelo']}** · F1 (test): **{metadata['metricas_test']['f1']}** · "
    f"ROC-AUC (test): **{metadata['metricas_test']['roc_auc']}**"
)
st.info(
    "⚠️ Nota honesta heredada del notebook: tras eliminar las variables con fuga de datos "
    "(`estado_entrega`, `tipo_transaccion`), el poder predictivo real de este modelo es modesto. "
    "Úsalo como señal de apoyo, no como decisión automática."
)

with st.form("form_prediccion"):
    st.subheader("Datos del pedido")

    col1, col2 = st.columns(2)
    with col1:
        dias_envio_real = st.number_input("Días de envío real", min_value=0, value=3)
        dias_envio_prog = st.number_input("Días de envío programado", min_value=0, value=4)
        cantidad = st.number_input("Cantidad de artículos", min_value=1, value=1)
        precio_base = st.number_input("Precio base", min_value=0.0, value=100.0, format="%.2f")
        margen_ganancia_item = st.number_input("Margen de ganancia por item", value=10.0, format="%.2f")
        ventas = st.number_input("Ventas del pedido", min_value=0.0, value=100.0, format="%.2f")
    with col2:
        total_item = st.number_input("Total del item", min_value=0.0, value=100.0, format="%.2f")
        ganancia_pedido = st.number_input("Ganancia del pedido", value=10.0, format="%.2f")
        beneficio_pedido = st.number_input("Beneficio del pedido", value=10.0, format="%.2f")
        ventas_cliente = st.number_input("Ventas del cliente (histórico)", min_value=0.0, value=100.0, format="%.2f")
        riesgo_retraso = st.checkbox("¿Riesgo de retraso?", value=False)

    st.subheader("Categorías")
    col3, col4 = st.columns(2)
    with col3:
        modo_envio = st.selectbox(
            "Modo de envío",
            options=categorias_dummies.get("modo_envio", ["Standard Class"]),
        )
        categoria = st.selectbox(
            "Categoría del producto",
            options=list(frecuencias_categoricas.get("categoria", {"Otros": 0}).keys()),
        )
    with col4:
        region_destino = st.selectbox(
            "Región de destino",
            options=list(frecuencias_categoricas.get("region_destino", {"Otros": 0}).keys()),
        )

    with st.expander("Variables del modelo no supervisado (opcional / avanzado)"):
        cluster_kmeans = st.selectbox(
            "Cluster K-Means", options=categorias_dummies.get("cluster_kmeans", [0]),
        )
        cluster_dbscan = st.selectbox(
            "Cluster DBSCAN", options=categorias_dummies.get("cluster_dbscan", [-1]),
        )
        es_anomalia = st.checkbox("¿Marcado como anomalía?", value=False)
        es_outlier = st.checkbox("¿Marcado como outlier?", value=False)

    umbral = st.slider(
        "Umbral de alerta (probabilidad mínima de 'COMPLETE' para no generar alerta)",
        min_value=0.0, max_value=1.0, value=UMBRAL_ALERTA_DEFECTO, step=0.01,
    )

    enviado = st.form_submit_button("Predecir")

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
        "total_item": total_item,
        "ganancia_pedido": ganancia_pedido,
        "riesgo_retraso": riesgo_retraso,
        "es_anomalia": es_anomalia,
        "es_outlier": es_outlier,
        "modo_envio": modo_envio,
        "cluster_kmeans": cluster_kmeans,
        "cluster_dbscan": cluster_dbscan,
        "categoria": categoria,
        "region_destino": region_destino,
    }

    probabilidad, fila_procesada = predecir(datos)
    prediccion = "COMPLETE" if probabilidad >= 0.5 else "CANCELED"

    st.subheader("Resultado")
    c1, c2 = st.columns(2)
    c1.metric("Probabilidad de COMPLETE", f"{probabilidad:.1%}")
    c2.metric("Predicción", prediccion)

    if probabilidad < umbral:
        st.warning(
            f"🔔 Alerta: probabilidad de completado ({probabilidad:.1%}) por debajo del umbral "
            f"({umbral:.0%}). Este pedido merece seguimiento operativo."
        )
    else:
        st.success("Sin alerta: probabilidad de completado por encima del umbral.")

    with st.expander("Ver features procesadas enviadas al modelo"):
        st.dataframe(fila_procesada.T.rename(columns={0: "valor"}))

st.divider()
st.caption(
    "Recomendaciones heredadas del notebook: reentrenar periódicamente y repetir la revisión "
    "de fuga de datos en cada reentrenamiento; monitorear las variables top de importancia "
    "(región de destino, márgenes, ganancia y beneficio del pedido)."
)
