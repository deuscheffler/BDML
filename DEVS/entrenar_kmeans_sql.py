"""
Entrenamiento del modelo K-Means ponderado usando datos de SQL Server.

Este script se ejecuta UNA VEZ (offline, no dentro de Streamlit) para:
  1. Conectarse a SQL Server y traer los datos con sp_DatasetML.
  2. Preparar/codificar las variables (igual que en el pipeline original).
  3. Construir el espacio ponderado y seleccionar k automáticamente.
  4. Entrenar el KMeans final.
  5. Guardar TODO lo necesario para reutilizar el modelo (kmeans, scalers,
     mapas de frecuencia, columnas dummy) en un único archivo .pkl.

Streamlit NO debe reentrenar el modelo en cada carga de página: debe cargar
el .pkl generado aquí y solo transformar/predecir sobre datos nuevos.
"""

import numpy as np
import pandas as pd
import joblib
from sqlalchemy import create_engine, text
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
RANDOM_STATE = 42

SERVER = r"OMEGA-DELL"
DATABASE = "BD_ML_RELACIONAL"

RUTA_MODELO = "modelo_kmeans_artifacts.pkl"

# Pesos (misma lógica que el script original: se prioriza tipo_transaccion)
PESO_NUMERICAS = 0.4
PESO_OTRAS = 0.4
PESO_TX = 1.5

NUMERICAS = [
    "dias_envio_real", "dias_envio_prog", "beneficio_pedido",
    "ventas_cliente", "precio_base", "margen_ganancia_item",
    "cantidad", "ventas",
]
BINARIAS = ["riesgo_retraso"]
NOMINAL_BAJA_CARDINALIDAD = ["tipo_transaccion", "modo_envio"]
NOMINAL_ALTA_CARDINALIDAD = [ "region_destino"]


# ============================================================================
# 1. CARGA DE DATOS DESDE SQL SERVER
# ============================================================================
def cargar_datos_sql() -> pd.DataFrame:
    connection_string = (
        f"mssql+pyodbc://@{SERVER}/{DATABASE}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )
    engine = create_engine(connection_string)
    print("Conexión establecida correctamente.")

    query = text("EXEC sp_DatasetML")
    df = pd.read_sql(query, engine)
    print(f"Datos cargados desde SQL Server: {df.shape}")
    return df


# ============================================================================
# 2. PREPARACIÓN DE FEATURES (guarda todo lo necesario para reproducir)
# ============================================================================
def preparar_features(df: pd.DataFrame):
    columnas_seleccionadas = (
        NUMERICAS + BINARIAS + NOMINAL_BAJA_CARDINALIDAD + NOMINAL_ALTA_CARDINALIDAD
    )
    df_modelo = df[columnas_seleccionadas].copy()

    # Binaria -> 0/1
    df_modelo["riesgo_retraso"] = df_modelo["riesgo_retraso"].astype(int)

    # Baja cardinalidad -> One-Hot Encoding
    df_modelo = pd.get_dummies(df_modelo, columns=NOMINAL_BAJA_CARDINALIDAD, drop_first=True)

    # Guardamos el listado EXACTO de columnas tras el one-hot (numéricas +
    # binaria + dummies de baja cardinalidad + las de alta cardinalidad, que
    # todavía están como texto en este punto). Esto es clave para poder
    # alinear datos nuevos que quizás no traigan todas las categorías.
    columnas_tras_onehot = df_modelo.columns.tolist()

    # Alta cardinalidad -> codificación por frecuencia (se guarda el mapa)
    frecuencias_map = {}
    for col in NOMINAL_ALTA_CARDINALIDAD:
        frecuencias = df_modelo[col].value_counts(normalize=True)
        frecuencias_map[col] = frecuencias
        df_modelo[col] = df_modelo[col].map(frecuencias)

    df_modelo = df_modelo.astype(float)
    print(f"Dimensiones tras codificación: {df_modelo.shape}")

    return df_modelo, frecuencias_map, columnas_tras_onehot


# ============================================================================
# 3. CONSTRUCCIÓN DEL ESPACIO PONDERADO (fit de los scalers)
# ============================================================================
def construir_espacio_ponderado(df: pd.DataFrame, df_modelo: pd.DataFrame):
    tx_dummies_full = pd.get_dummies(df["tipo_transaccion"], prefix="tx").astype(float)

    otras_categoricas = (
        ["riesgo_retraso"]
        + [c for c in df_modelo.columns if c.startswith("modo_envio_")]
        + ["region_destino"]
    )

    scaler_num = StandardScaler().fit(df_modelo[NUMERICAS])
    scaler_otras = StandardScaler().fit(df_modelo[otras_categoricas])
    scaler_tx = StandardScaler().fit(tx_dummies_full)

    X_ponderado = np.hstack([
        scaler_num.transform(df_modelo[NUMERICAS]) * PESO_NUMERICAS,
        scaler_otras.transform(df_modelo[otras_categoricas]) * PESO_OTRAS,
        scaler_tx.transform(tx_dummies_full) * PESO_TX,
    ])

    scalers = {
        "numericas": scaler_num,
        "otras": scaler_otras,
        "otras_cols": otras_categoricas,
        "tx": scaler_tx,
        "tx_cols": tx_dummies_full.columns.tolist(),
    }

    print(f"Espacio de variables ponderado: {X_ponderado.shape}")
    return X_ponderado, scalers


# ============================================================================
# 4. SELECCIÓN DE k Y ENTRENAMIENTO FINAL
# ============================================================================
def seleccionar_k(X_ponderado: np.ndarray, k_range=range(2, 9)) -> int:
    scores = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = km.fit_predict(X_ponderado)
        scores.append(
            silhouette_score(X_ponderado, labels, sample_size=10000, random_state=RANDOM_STATE)
        )
    k_optimo = list(k_range)[int(np.argmax(scores))]
    print(f"k óptimo: {k_optimo} (silhouette={max(scores):.4f})")
    return k_optimo


def entrenar_modelo_final(X_ponderado: np.ndarray, k_optimo: int) -> KMeans:
    kmeans = KMeans(n_clusters=k_optimo, random_state=RANDOM_STATE, n_init=10)
    kmeans.fit(X_ponderado)
    return kmeans


# ============================================================================
# 5. MAIN
# ============================================================================
def main():
    print("=" * 60)
    print("ENTRENAMIENTO K-MEANS PONDERADO (fuente: SQL Server)")
    print("=" * 60)

    df = cargar_datos_sql()
    df_modelo, frecuencias_map, columnas_tras_onehot = preparar_features(df)
    X_ponderado, scalers = construir_espacio_ponderado(df, df_modelo)

    k_optimo = seleccionar_k(X_ponderado)
    kmeans = entrenar_modelo_final(X_ponderado, k_optimo)

    sil = silhouette_score(X_ponderado, kmeans.labels_, sample_size=10000, random_state=RANDOM_STATE)
    print(f"Silhouette final: {sil:.4f}")

    artifacts = {
        "kmeans": kmeans,
        "scalers": scalers,
        "frecuencias_map": frecuencias_map,
        "columnas_tras_onehot": columnas_tras_onehot,
        "k_optimo": k_optimo,
        "pesos": {
            "numericas": PESO_NUMERICAS,
            "otras": PESO_OTRAS,
            "tx": PESO_TX,
        },
        "columnas": {
            "numericas": NUMERICAS,
            "binarias": BINARIAS,
            "nominal_baja": NOMINAL_BAJA_CARDINALIDAD,
            "nominal_alta": NOMINAL_ALTA_CARDINALIDAD,
        },
    }

    joblib.dump(artifacts, RUTA_MODELO)
    print(f"\nModelo y transformadores guardados en: {RUTA_MODELO}")


if __name__ == "__main__":
    main()
