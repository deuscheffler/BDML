"""
load_models.py
================
Módulo de carga e inferencia para la interfaz de Streamlit.

Carga los 9 artefactos generados por KMEANSCERCER_corregido.py y
ModeloSupervisado_corregido.py, y expone funciones de predicción que
replican EXACTAMENTE el preprocesamiento usado en el entrenamiento
(mismos renames, mismos pesos, mismas imputaciones de NULL).

Todos los .pkl/.json deben estar en la misma carpeta que la app de
Streamlit (o ajustar las rutas de la sección CONFIGURACIÓN).

Uso típico dentro de app.py:

    from load_models import (
        cargar_artefactos_kmeans, cargar_modelo_supervisado,
        cargar_metadatos_supervisado, predecir_estado_pedido,
    )

    artefactos_kmeans = cargar_artefactos_kmeans()
    modelo_sup, scaler_sup = cargar_modelo_supervisado()
    features, frecuencias, dummies, medianas, metadata_sup = cargar_metadatos_supervisado()

    pedido = {
        "dias_envio_real": 3, "dias_envio_prog": 4,
        "beneficio_pedido": 45.2, "ventas_cliente": 320.0,
        "precio_base": 59.99, "margen_ganancia_item": 0.18,
        "cantidad": 2, "ventas": 199.98, "total_item": 199.98,
        "ganancia_pedido": 36.0,
        "riesgo_retraso": 0,
        "modo_envio": "Standard Class",
        "tipo_transaccion": "DEBIT",
        "categoria": "Cleats",
        "region_destino": "Central America",
    }

    resultado = predecir_estado_pedido(
        pedido, artefactos_kmeans, modelo_sup, scaler_sup,
        features, frecuencias, dummies, medianas, metadata_sup,
    )
    # {'cluster_kmeans': 1, 'es_anomalia': False, 'es_outlier': False,
    #  'distancia_centroide': 1.83, 'probabilidad_completado': 0.87,
    #  'prediccion': 'COMPLETE'}
"""

import json
import os

import joblib
import numpy as np
import pandas as pd
import streamlit as st

# ============================================================================
# CONFIGURACIÓN — rutas de los 9 artefactos
# ============================================================================
DIRECTORIO_ARTEFACTOS = os.path.dirname(os.path.abspath(__file__))

RUTA_KMEANS_PKL = os.path.join(DIRECTORIO_ARTEFACTOS, "modelo_kmeans_artifacts.pkl")
RUTA_META_KMEANS_JSON = os.path.join(DIRECTORIO_ARTEFACTOS, "metadata_kmeans.json")

RUTA_SUP_PKL = os.path.join(DIRECTORIO_ARTEFACTOS, "modelo_prediccion_envios.pkl")
RUTA_SCALER_SUP_PKL = os.path.join(DIRECTORIO_ARTEFACTOS, "scaler_envios.pkl")
RUTA_FEATURES_JSON = os.path.join(DIRECTORIO_ARTEFACTOS, "features_modelo.json")
RUTA_FREQ_JSON = os.path.join(DIRECTORIO_ARTEFACTOS, "frecuencias_categoricas.json")
RUTA_DUMMIES_JSON = os.path.join(DIRECTORIO_ARTEFACTOS, "categorias_dummies.json")
RUTA_MEDIANAS_JSON = os.path.join(DIRECTORIO_ARTEFACTOS, "medianas_imputacion.json")
RUTA_META_SUP_JSON = os.path.join(DIRECTORIO_ARTEFACTOS, "metadata_modelo.json")


# ============================================================================
# CARGA DE ARTEFACTOS (cacheada — se ejecuta una sola vez por sesión)
# ============================================================================
@st.cache_resource(show_spinner="Cargando modelo no supervisado (KMeans)...")
def cargar_artefactos_kmeans() -> dict:
    """Carga el diccionario completo guardado por guardar_artefactos() en
    KMEANSCERCER_corregido.py: modelo, 3 scalers, columnas, pesos, mapas de
    frecuencia y umbral de anomalías."""
    return joblib.load(RUTA_KMEANS_PKL)


@st.cache_resource(show_spinner="Cargando modelo supervisado...")
def cargar_modelo_supervisado():
    """Carga el clasificador calibrado y su scaler."""
    modelo = joblib.load(RUTA_SUP_PKL)
    scaler = joblib.load(RUTA_SCALER_SUP_PKL)
    return modelo, scaler


@st.cache_data(show_spinner=False)
def cargar_metadatos_supervisado():
    """Carga los 5 JSON asociados al modelo supervisado."""
    with open(RUTA_FEATURES_JSON, encoding="utf-8") as f:
        features = json.load(f)
    with open(RUTA_FREQ_JSON, encoding="utf-8") as f:
        frecuencias = json.load(f)
    with open(RUTA_DUMMIES_JSON, encoding="utf-8") as f:
        dummies = json.load(f)
    with open(RUTA_MEDIANAS_JSON, encoding="utf-8") as f:
        medianas = json.load(f)
    with open(RUTA_META_SUP_JSON, encoding="utf-8") as f:
        metadata = json.load(f)
    return features, frecuencias, dummies, medianas, metadata


@st.cache_data(show_spinner=False)
def cargar_metadata_kmeans() -> dict:
    with open(RUTA_META_KMEANS_JSON, encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
# PREPROCESAMIENTO — NO SUPERVISADO (replica construir_espacio_ponderado)
# ============================================================================
def preprocesar_para_kmeans(pedido: dict, artefactos: dict) -> np.ndarray:
    """
    Construye el espacio ponderado para UN pedido, en el mismo orden y con
    los mismos scalers ya entrenados que usó KMEANSCERCER_corregido.py.

    pedido debe traer: dias_envio_real, dias_envio_prog, beneficio_pedido,
    ventas_cliente, precio_base, margen_ganancia_item, cantidad, ventas,
    riesgo_retraso (0/1 o bool), modo_envio (str), tipo_transaccion (str),
    categoria (str), region_destino (str).
    """
    numericas = artefactos["NUMERICAS"]
    otras_categoricas = artefactos["otras_categoricas"]
    tx_columns = artefactos["tx_columns"]
    modo_envio_dummies = artefactos["modo_envio_dummies"]

    # 1) Numéricas
    X_num = pd.DataFrame([{c: pedido[c] for c in numericas}])
    X_num_esc = artefactos["scaler_numericas"].transform(X_num) * artefactos["PESO_NUMERICAS"]

    # 2) Otras categóricas: riesgo_retraso + dummies de modo_envio + freq(categoria/region)
    fila_otras = {"riesgo_retraso": int(bool(pedido["riesgo_retraso"]))}
    for col in modo_envio_dummies:
        valor = col.replace("modo_envio_", "", 1)
        fila_otras[col] = 1 if pedido["modo_envio"] == valor else 0
    fila_otras["categoria"] = artefactos["freq_categoria"].get(pedido["categoria"], 0.0)
    fila_otras["region_destino"] = artefactos["freq_region"].get(pedido["region_destino"], 0.0)
    X_otras = pd.DataFrame([fila_otras])[otras_categoricas]
    X_otras_esc = artefactos["scaler_otras"].transform(X_otras) * artefactos["PESO_OTRAS"]

    # 3) tipo_transaccion -> one-hot completo (sin drop_first), prefijo 'tx_'
    fila_tx = {col: 0 for col in tx_columns}
    col_tx = f"tx_{pedido['tipo_transaccion']}"
    if col_tx in fila_tx:
        fila_tx[col_tx] = 1
    X_tx = pd.DataFrame([fila_tx])[tx_columns]
    X_tx_esc = artefactos["scaler_tx"].transform(X_tx) * artefactos["PESO_TX"]

    return np.hstack([X_num_esc, X_otras_esc, X_tx_esc])


def calcular_es_outlier(pedido: dict, artefactos: dict) -> bool:
    """
    Recalcula es_outlier para un pedido nuevo usando los límites IQR
    (Q1/Q3 sobre el dataset de entrenamiento) guardados en el artefacto,
    igual que detectar_outliers() en KMEANSCERCER_corregido.py: un pedido
    es outlier si CUALQUIERA de sus columnas cae fuera de [cota_inferior,
    cota_superior] en 'dias_envio_real', 'beneficio_pedido' o 'ventas'.
    """
    limites = artefactos.get("limites_outliers", {})
    for col, bordes in limites.items():
        if col not in pedido:
            continue
        valor = pedido[col]
        if valor < bordes["cota_inferior"] or valor > bordes["cota_superior"]:
            return True
    return False


def etiqueta_cluster(cluster_id: int, artefactos: dict, umbral: float = 70.0) -> dict:
    """
    Clasifica un cluster como 'Predominantemente COMPLETE',
    'Predominantemente CANCELED' o 'Mixto', usando el % real guardado en
    porcentaje_complete_por_cluster (calculado en evaluar_modelo() durante
    el entrenamiento) — NUNCA se asume qué representa cada número de
    cluster de antemano, porque esa asignación es arbitraria y puede
    cambiar entre corridas de KMeans.

    umbral: mismo criterio de diferenciación que ya usa el script de
    entrenamiento (>=70% para considerar un cluster "diferenciado").
    """
    porcentajes = artefactos["porcentaje_complete_por_cluster"]
    cid = str(cluster_id)

    pct_complete = porcentajes["COMPLETE"].get(cid, porcentajes["COMPLETE"].get(cluster_id))
    pct_cancelado = porcentajes["CANCELED"].get(cid, porcentajes["CANCELED"].get(cluster_id))

    if pct_complete is None or pct_cancelado is None:
        return {"etiqueta": "Desconocido", "pct_complete": None, "pct_cancelado": None}

    if pct_complete >= umbral:
        etiqueta = "Predominantemente COMPLETE"
    elif pct_cancelado >= umbral:
        etiqueta = "Predominantemente CANCELED"
    else:
        etiqueta = "Mixto"

    return {
        "etiqueta": etiqueta,
        "pct_complete": round(float(pct_complete), 2),
        "pct_cancelado": round(float(pct_cancelado), 2),
    }


def mapa_etiquetas_clusters(artefactos: dict, umbral: float = 70.0) -> dict:
    """
    Retorna el mapeo {cluster_id: etiqueta_cluster(...)} para TODOS los
    clusters del modelo. Útil para pintar leyendas/colores en Streamlit
    sin tener que llamar etiqueta_cluster() cluster por cluster.
    """
    k = artefactos["k_optimo"]
    return {c: etiqueta_cluster(c, artefactos, umbral) for c in range(k)}


def predecir_cluster(pedido: dict, artefactos: dict) -> dict:
    """
    Retorna cluster_kmeans, distancia al centroide, es_anomalia y
    es_outlier para un pedido nuevo (hipotético o existente).

    es_outlier se calcula con los límites IQR guardados en el artefacto
    (ver calcular_es_outlier). Para pedidos que ya existen en la BD,
    también puedes usar directamente el valor real desde
    ResultadoModeloNoSupervisado en vez de recalcularlo aquí — ambos
    deberían coincidir salvo que el modelo se haya reentrenado desde
    entonces con datos distintos.
    """
    X_ponderado = preprocesar_para_kmeans(pedido, artefactos)
    kmeans = artefactos["kmeans"]

    cluster = int(kmeans.predict(X_ponderado)[0])
    distancias = kmeans.transform(X_ponderado)[0]
    distancia_minima = float(distancias.min())
    es_anomalia = distancia_minima > artefactos["umbral_anomalias"]
    info_etiqueta = etiqueta_cluster(cluster, artefactos)

    return {
        "cluster_kmeans": cluster,
        "cluster_etiqueta": info_etiqueta["etiqueta"],
        "cluster_pct_complete": info_etiqueta["pct_complete"],
        "distancia_centroide": round(distancia_minima, 4),
        "es_anomalia": bool(es_anomalia),
        "es_outlier": calcular_es_outlier(pedido, artefactos),
    }


# ============================================================================
# PREPROCESAMIENTO — SUPERVISADO (replica ingenieria_features + construir_X_y)
# ============================================================================
def preprocesar_para_supervisado(
    pedido: dict,
    cluster_info: dict,
    features: list,
    frecuencias: dict,
    dummies: dict,
    medianas: dict,
) -> pd.DataFrame:
    """
    Construye el vector de features (1 fila, columnas en el orden exacto de
    features_modelo.json) para un pedido, replicando ingenieria_features()
    y construir_X_y() de ModeloSupervisado_corregido.py.

    pedido debe traer, además de lo usado por preprocesar_para_kmeans:
    total_item, ganancia_pedido.
    cluster_info es la salida de predecir_cluster().
    """
    fila = dict(pedido)

    # --- Ingeniería de features (Sección 4 del notebook) ---
    fila["diferencia_envio"] = fila["dias_envio_real"] - fila["dias_envio_prog"]

    if fila["dias_envio_prog"] == 0:
        fila["ratio_envio"] = medianas["ratio_envio"]
    else:
        fila["ratio_envio"] = fila["dias_envio_real"] / fila["dias_envio_prog"]

    fila["cumple_plazo"] = int(fila["dias_envio_real"] <= fila["dias_envio_prog"])

    if fila["cantidad"] == 0:
        fila["precio_promedio_item"] = medianas["precio_promedio_item"]
        fila["eficiencia_cliente"] = medianas["eficiencia_cliente"]
    else:
        fila["precio_promedio_item"] = fila["ventas"] / fila["cantidad"]
        fila["eficiencia_cliente"] = fila["ventas_cliente"] / fila["cantidad"]

    fila["margen_total"] = 0.0 if fila["ventas"] == 0 else fila["ganancia_pedido"] / fila["ventas"]

    fila["riesgo_por_precio"] = int(bool(fila["riesgo_retraso"])) * fila["precio_base"]
    fila["riesgo_retraso"] = int(bool(fila["riesgo_retraso"]))

    # --- Resultados del modelo no supervisado ---
    fila["es_anomalia"] = int(bool(cluster_info.get("es_anomalia", False)))
    fila["es_outlier"] = int(bool(cluster_info.get("es_outlier", False)))
    cluster_val = cluster_info["cluster_kmeans"]

    # --- Dummies (drop_first=True -> se omite el primer valor de cada lista) ---
    for valor in dummies["modo_envio"][1:]:
        fila[f"modo_envio_{valor}"] = 1 if fila["modo_envio"] == valor else 0

    for valor in dummies["cluster_kmeans"][1:]:
        fila[f"cluster_kmeans_{valor}"] = 1 if cluster_val == valor else 0

    # --- Codificación por frecuencia (categoría no vista en train -> 0.0) ---
    fila["categoria"] = frecuencias["categoria"].get(fila["categoria"], 0.0)
    fila["region_destino"] = frecuencias["region_destino"].get(fila["region_destino"], 0.0)

    # --- Ensamblar en el orden exacto de entrenamiento ---
    X = pd.DataFrame([{col: fila.get(col, 0) for col in features}])[features]
    return X.astype(float)


def predecir_estado_pedido(
    pedido: dict,
    artefactos_kmeans: dict,
    modelo_sup,
    scaler_sup,
    features: list,
    frecuencias: dict,
    dummies: dict,
    medianas: dict,
    metadata_sup: dict,
) -> dict:
    """
    Pipeline de inferencia end-to-end: no supervisado -> supervisado.
    Retorna cluster, anomalía, probabilidad y predicción final.
    """
    cluster_info = predecir_cluster(pedido, artefactos_kmeans)

    X = preprocesar_para_supervisado(
        pedido, cluster_info, features, frecuencias, dummies, medianas
    )

    # Solo se escala si el modelo ganador lo requiere (KNN/SVM/Regresión
    # Logística sí; Random Forest/XGBoost no) — se decide con la metadata,
    # no hardcodeado, para que siga funcionando si se reentrena con otro
    # modelo ganador.
    X_entrada = scaler_sup.transform(X) if metadata_sup["requiere_escalado"] else X.values

    proba = float(modelo_sup.predict_proba(X_entrada)[0, 1])
    umbral = metadata_sup.get("umbral_alerta_recomendado", 0.5)
    prediccion = "COMPLETE" if proba >= 0.5 else "CANCELED"

    return {
        "cluster_kmeans": cluster_info["cluster_kmeans"],
        "cluster_etiqueta": cluster_info["cluster_etiqueta"],
        "distancia_centroide": cluster_info["distancia_centroide"],
        "es_anomalia": cluster_info["es_anomalia"],
        "es_outlier": cluster_info["es_outlier"],
        "probabilidad_completado": round(proba, 4),
        "prediccion": prediccion,
        "alerta_riesgo": proba < umbral,
    }


# ============================================================================
# ACCESO A SQL SERVER — pedidos ya existentes en la base de datos
# ============================================================================
# Se usa para el caso "consultar/predecir un pedido que ya está en la BD":
# se trae cluster_kmeans/es_anomalia/es_outlier YA CALCULADOS por la última
# corrida de KMEANSCERCER_corregido.py (columna de vw_ML_DataCoSupplyChain),
# en vez de tener que volver a ejecutar el modelo no supervisado.
# Para pedidos hipotéticos capturados a mano en un formulario, en cambio, se
# usa predecir_estado_pedido() (arriba), que sí corre KMeans en vivo.
from sqlalchemy import create_engine, text  # noqa: E402


def conectar_sql_server(server: str, database: str):
    connection_string = (
        f"mssql+pyodbc://@{server}/{database}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )
    return create_engine(connection_string)


@st.cache_resource(show_spinner=False)
def obtener_conexion_sql(server: str = "OMEGA-DELL", database: str = "BD_ML_RELACIONAL"):
    return conectar_sql_server(server, database)


def obtener_pedido_por_id(_engine, id_pedido: int) -> dict | None:
    """
    Trae un pedido existente desde vw_ML_DataCoSupplyChain, con
    cluster_kmeans/es_anomalia/es_outlier ya calculados. Retorna None si
    no existe ese id_pedido.
    """
    query = text("SELECT * FROM vw_ML_DataCoSupplyChain WHERE id_pedido = :id_pedido")
    with _engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"id_pedido": id_pedido})
    if df.empty:
        return None
    fila = df.iloc[0].to_dict()

    # El SP/vista devuelve 'nombre_categoria' (columna real de la tabla
    # Categoria), no 'categoria'. Se renombra aquí para que coincida con
    # lo que espera preprocesar_para_supervisado/preprocesar_para_kmeans
    # -- el mismo criterio que ya aplican los scripts de entrenamiento.
    if "nombre_categoria" in fila and "categoria" not in fila:
        fila["categoria"] = fila.pop("nombre_categoria")

    # cluster_kmeans puede venir NULL si ese pedido nunca pasó por una
    # corrida de KMeans (LEFT JOIN en la vista); se avisa en vez de fallar.
    if pd.isna(fila.get("cluster_kmeans")):
        fila["_cluster_pendiente"] = True
    return fila


def predecir_estado_pedido_existente(
    id_pedido: int,
    engine,
    artefactos_kmeans: dict,
    modelo_sup,
    scaler_sup,
    features: list,
    frecuencias: dict,
    dummies: dict,
    medianas: dict,
    metadata_sup: dict,
) -> dict | None:
    """
    Predice el estado de un pedido que YA existe en la base de datos,
    reutilizando el cluster_kmeans/es_anomalia/es_outlier ya calculados
    (no vuelve a correr KMeans). Retorna None si el id_pedido no existe.
    """
    fila = obtener_pedido_por_id(engine, id_pedido)
    if fila is None:
        return None

    if fila.get("_cluster_pendiente"):
        raise ValueError(
            f"El pedido {id_pedido} todavía no tiene cluster_kmeans asignado "
            "(no ha pasado por una corrida de KMEANSCERCER_corregido.py)."
        )

    cluster_info = {
        "cluster_kmeans": int(fila["cluster_kmeans"]),
        "es_anomalia": bool(fila["es_anomalia"]),
        "es_outlier": bool(fila["es_outlier"]),
    }
    info_etiqueta = etiqueta_cluster(cluster_info["cluster_kmeans"], artefactos_kmeans)

    X = preprocesar_para_supervisado(
        fila, cluster_info, features, frecuencias, dummies, medianas
    )
    X_entrada = scaler_sup.transform(X) if metadata_sup["requiere_escalado"] else X.values

    proba = float(modelo_sup.predict_proba(X_entrada)[0, 1])
    umbral = metadata_sup.get("umbral_alerta_recomendado", 0.5)
    prediccion = "COMPLETE" if proba >= 0.5 else "CANCELED"

    return {
        "id_pedido": id_pedido,
        "estado_real": fila.get("estado_pedido"),
        "cluster_kmeans": cluster_info["cluster_kmeans"],
        "cluster_etiqueta": info_etiqueta["etiqueta"],
        "es_anomalia": cluster_info["es_anomalia"],
        "es_outlier": cluster_info["es_outlier"],
        "probabilidad_completado": round(proba, 4),
        "prediccion": prediccion,
        "alerta_riesgo": proba < umbral,
    }