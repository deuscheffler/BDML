"""
entrenar_y_guardar_modelo.py
=============================
Entrena el KMeans ponderado (k=4) sobre DataCoSupplyChain_Limpio.csv y
guarda TODOS los artefactos necesarios para poder predecir después,
sin volver a tocar el CSV, desde la app de Streamlit.

Ejecutar UNA vez (o cada vez que cambie el CSV de entrenamiento):
    python entrenar_y_guardar_modelo.py

Debe correr en la misma carpeta donde está 'DataCoSupplyChain_Limpio.csv'.
Genera la carpeta 'modelo_artifacts/' con:
    - kmeans.joblib
    - scaler_numericas.joblib
    - scaler_otras.joblib
    - scaler_tx.joblib
    - metadata.joblib   (columnas, frecuencias, categorías, pesos, k)
"""

import os
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# ============================================================================
# CONFIGURACIÓN (debe coincidir EXACTO con el script original de análisis)
# ============================================================================
RANDOM_STATE = 42
K_OPTIMO = 4  # confirmado: 0 = Cancelado, 1/2/3 = Completo

RUTA_CSV = "DataCoSupplyChain_Limpio.csv"
CARPETA_ARTIFACTS = "modelo_artifacts"

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
NOMINAL_ALTA_CARDINALIDAD = ["categoria", "region_destino"]


def main():
    if not os.path.exists(RUTA_CSV):
        raise FileNotFoundError(
            f"No se encuentra '{RUTA_CSV}'. Coloca este script en la misma "
            f"carpeta que el CSV de entrenamiento."
        )

    print(f"Cargando {RUTA_CSV} ...")
    df = pd.read_csv(RUTA_CSV)
    print(f"Dimensiones: {df.shape}")

    columnas_seleccionadas = (
        NUMERICAS + BINARIAS + NOMINAL_BAJA_CARDINALIDAD + NOMINAL_ALTA_CARDINALIDAD
    )
    df_modelo = df[columnas_seleccionadas].copy()
    df_modelo["riesgo_retraso"] = df_modelo["riesgo_retraso"].astype(int)

    # --- One-Hot (drop_first) para baja cardinalidad, igual que el original ---
    df_modelo = pd.get_dummies(df_modelo, columns=NOMINAL_BAJA_CARDINALIDAD, drop_first=True)

    # --- Codificación por frecuencia para alta cardinalidad ---
    freq_categoria = df_modelo["categoria"].value_counts(normalize=True).to_dict() \
        if "categoria" in df_modelo.columns else {}
    freq_region = None
    frecuencias_guardadas = {}
    for col in NOMINAL_ALTA_CARDINALIDAD:
        frecuencias = df_modelo[col].value_counts(normalize=True)
        frecuencias_guardadas[col] = frecuencias.to_dict()
        df_modelo[col] = df_modelo[col].map(frecuencias)

    df_modelo = df_modelo.astype(float)
    print(f"Dimensiones después de codificación: {df_modelo.shape}")

    # ------------------------------------------------------------------
    # Espacio ponderado (idéntico a construir_espacio_ponderado original)
    # ------------------------------------------------------------------
    tx_dummies_full = pd.get_dummies(df["tipo_transaccion"], prefix="tx").astype(float)
    tx_cols = list(tx_dummies_full.columns)

    modo_envio_cols = [c for c in df_modelo.columns if c.startswith("modo_envio_")]
    otras_categoricas_cols = ["riesgo_retraso"] + modo_envio_cols + ["categoria", "region_destino"]

    scaler_numericas = StandardScaler()
    X_numericas = scaler_numericas.fit_transform(df_modelo[NUMERICAS])

    scaler_otras = StandardScaler()
    X_otras = scaler_otras.fit_transform(df_modelo[otras_categoricas_cols])

    scaler_tx = StandardScaler()
    X_tx = scaler_tx.fit_transform(tx_dummies_full)

    import numpy as np
    X_ponderado = np.hstack(
        [X_numericas * PESO_NUMERICAS, X_otras * PESO_OTRAS, X_tx * PESO_TX]
    )
    print(f"Espacio ponderado: {X_ponderado.shape}")

    # ------------------------------------------------------------------
    # Entrenamiento del KMeans final (k fijo = 4, confirmado por el usuario)
    # ------------------------------------------------------------------
    kmeans = KMeans(n_clusters=K_OPTIMO, random_state=RANDOM_STATE, n_init=10)
    labels = kmeans.fit_predict(X_ponderado)
    print("Distribución de clusters:")
    print(pd.Series(labels).value_counts().sort_index())

    # Verificación rápida contra estado_pedido, si existe la columna
    if "estado_pedido" in df.columns:
        tabla = pd.crosstab(labels, df["estado_pedido"])
        porcentaje = (tabla.div(tabla.sum(axis=1), axis=0) * 100).round(2)
        print("\nComposición COMPLETE/CANCELED por cluster (%):")
        print(porcentaje)

    # ------------------------------------------------------------------
    # Guardar artefactos
    # ------------------------------------------------------------------
    os.makedirs(CARPETA_ARTIFACTS, exist_ok=True)

    joblib.dump(kmeans, os.path.join(CARPETA_ARTIFACTS, "kmeans.joblib"))
    joblib.dump(scaler_numericas, os.path.join(CARPETA_ARTIFACTS, "scaler_numericas.joblib"))
    joblib.dump(scaler_otras, os.path.join(CARPETA_ARTIFACTS, "scaler_otras.joblib"))
    joblib.dump(scaler_tx, os.path.join(CARPETA_ARTIFACTS, "scaler_tx.joblib"))

    metadata = {
        "k_optimo": K_OPTIMO,
        "peso_numericas": PESO_NUMERICAS,
        "peso_otras": PESO_OTRAS,
        "peso_tx": PESO_TX,
        "numericas": NUMERICAS,
        "binarias": BINARIAS,
        "nominal_baja_cardinalidad": NOMINAL_BAJA_CARDINALIDAD,
        "nominal_alta_cardinalidad": NOMINAL_ALTA_CARDINALIDAD,
        "modo_envio_cols": modo_envio_cols,          # columnas dummy (drop_first) esperadas
        "otras_categoricas_cols": otras_categoricas_cols,  # orden exacto para X_otras
        "tx_cols": tx_cols,                          # columnas dummy completas (tx_*)
        "frecuencias": frecuencias_guardadas,        # {"categoria": {...}, "region_destino": {...}}
        # listas de categorías reales para poblar los selectbox de Streamlit
        "categorias_tipo_transaccion": sorted(df["tipo_transaccion"].dropna().unique().tolist()),
        "categorias_modo_envio": sorted(df["modo_envio"].dropna().unique().tolist()),
        "categorias_categoria": sorted(df["categoria"].dropna().unique().tolist()),
        "categorias_region_destino": sorted(df["region_destino"].dropna().unique().tolist()),
        "mapa_resultado": {0: "Cancelado", 1: "Completo", 2: "Completo", 3: "Completo"},
    }
    joblib.dump(metadata, os.path.join(CARPETA_ARTIFACTS, "metadata.joblib"))

    print(f"\nListo. Artefactos guardados en '{CARPETA_ARTIFACTS}/':")
    for f in os.listdir(CARPETA_ARTIFACTS):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
