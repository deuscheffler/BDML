"""
Módulo de inferencia para Streamlit.

NO reentrena el modelo. Carga el .pkl generado por entrenar_kmeans_sql.py
y lo usa para:
  - Traer datos nuevos desde SQL Server (sp_DatasetML).
  - Transformarlos EXACTAMENTE igual que en el entrenamiento (mismos
    scalers, mismo mapa de frecuencias, mismas columnas dummy).
  - Predecir el cluster de cada fila con kmeans.predict().

Uso típico dentro de app.py (Streamlit):

    from modelo_kmeans_streamlit import cargar_datos_sql, predecir_clusters

    df = cargar_datos_sql()
    df["cluster"] = predecir_clusters(df)
    st.dataframe(df)
"""

import numpy as np
import pandas as pd
import joblib
import streamlit as st
from sqlalchemy import create_engine, text

SERVER = r"OMEGA-DELL"
DATABASE = "BD_ML_RELACIONAL"
RUTA_MODELO = "modelo_kmeans_artifacts.pkl"


# ============================================================================
# CONEXIÓN Y CARGA DE DATOS (cacheadas para no repetir trabajo en cada rerun)
# ============================================================================
@st.cache_resource
def _obtener_engine():
    connection_string = (
        f"mssql+pyodbc://@{SERVER}/{DATABASE}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )
    return create_engine(connection_string)


@st.cache_data(ttl=600)  # refresca cada 10 min; ajusta a tu necesidad
def cargar_datos_sql() -> pd.DataFrame:
    engine = _obtener_engine()
    query = text("EXEC sp_DatasetML")
    df = pd.read_sql(query, engine)
    return df


@st.cache_resource
def cargar_modelo():
    """Carga el modelo entrenado y sus transformadores una sola vez por sesión."""
    return joblib.load(RUTA_MODELO)


# ============================================================================
# TRANSFORMACIÓN DE DATOS NUEVOS (usa los transformadores ya ajustados)
# ============================================================================
def _preparar_features(df: pd.DataFrame, artifacts: dict) -> pd.DataFrame:
    cols = artifacts["columnas"]
    columnas_seleccionadas = (
        cols["numericas"] + cols["binarias"] + cols["nominal_baja"] + cols["nominal_alta"]
    )
    df_modelo = df[columnas_seleccionadas].copy()
    df_modelo["riesgo_retraso"] = df_modelo["riesgo_retraso"].astype(int)

    # One-hot de baja cardinalidad, alineado a las columnas vistas en entrenamiento
    df_modelo = pd.get_dummies(df_modelo, columns=cols["nominal_baja"], drop_first=True)
    df_modelo = df_modelo.reindex(columns=artifacts["columnas_tras_onehot"], fill_value=0)

    # Alta cardinalidad -> frecuencias aprendidas en entrenamiento
    # (categorías nunca vistas quedan en 0, no se inventan frecuencias nuevas)
    for col in cols["nominal_alta"]:
        frecuencias = artifacts["frecuencias_map"][col]
        df_modelo[col] = df[col].map(frecuencias).fillna(0.0)

    return df_modelo.astype(float)


def _construir_espacio_ponderado(df: pd.DataFrame, df_modelo: pd.DataFrame, artifacts: dict) -> np.ndarray:
    scalers = artifacts["scalers"]
    pesos = artifacts["pesos"]

    tx_dummies = pd.get_dummies(df["tipo_transaccion"], prefix="tx").astype(float)
    tx_dummies = tx_dummies.reindex(columns=scalers["tx_cols"], fill_value=0)

    X_num = scalers["numericas"].transform(df_modelo[artifacts["columnas"]["numericas"]])
    X_otras = scalers["otras"].transform(df_modelo[scalers["otras_cols"]])
    X_tx = scalers["tx"].transform(tx_dummies)

    return np.hstack([
        X_num * pesos["numericas"],
        X_otras * pesos["otras"],
        X_tx * pesos["tx"],
    ])


# ============================================================================
# API PÚBLICA
# ============================================================================
def predecir_clusters(df: pd.DataFrame) -> np.ndarray:
    """Devuelve un array con el cluster asignado a cada fila de df."""
    artifacts = cargar_modelo()
    df_modelo = _preparar_features(df, artifacts)
    X_ponderado = _construir_espacio_ponderado(df, df_modelo, artifacts)
    return artifacts["kmeans"].predict(X_ponderado)


def distancia_a_centroides(df: pd.DataFrame) -> np.ndarray:
    """Útil para detección de anomalías: distancia de cada fila a cada centroide."""
    artifacts = cargar_modelo()
    df_modelo = _preparar_features(df, artifacts)
    X_ponderado = _construir_espacio_ponderado(df, df_modelo, artifacts)
    return artifacts["kmeans"].transform(X_ponderado)
