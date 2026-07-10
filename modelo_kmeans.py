"""
Modelo No Supervisado - K-Means Mejorado (ponderado)
=====================================================
Mejor modelo obtenido en ModeloNoSupervisado_corregido.ipynb (sección 12).

Silhouette score: 0.6051 (vs. 0.1959 del K-Means sin ponderar)
3 de 4 clusters con >= 70% de diferenciación COMPLETE / CANCELED,
cubriendo ~72% de los pedidos del dataset.

La variable objetivo 'estado_pedido' NUNCA se usa como entrada del
algoritmo de clustering: solo se usó, en un paso previo de diagnóstico,
para decidir qué variable ponderar más (tipo_transaccion), y aquí se
usa únicamente para validar el resultado (evaluación externa).

Este script genera además las gráficas necesarias para interpretar el
modelo (guardadas en la carpeta 'graficas/'):
  01_seleccion_k.png            -> silhouette / calinski / davies vs. k
  02_tamano_clusters.png        -> tamaño de cada cluster
  03_composicion_objetivo.png   -> % COMPLETE / CANCELED por cluster
  04_composicion_tx.png         -> composición de tipo_transaccion por cluster
  05_clusters_pca2d.png         -> visualización 2D de los clusters (PCA)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

RANDOM_STATE = 42
RUTA_CSV = "DataCoSupplyChain_Limpio.csv"
from pathlib import Path
RUTA_CSV = Path(__file__).parent / 'DataCoSupplyChain_Limpio.csv'
CARPETA_GRAFICAS = "graficas"

# Pesos usados para dar más importancia a 'tipo_transaccion', la variable
# con mayor correlación encontrada en el diagnóstico (r ~ 0.33 vs |r| < 0.01
# del resto de variables numéricas).
PESO_NUMERICAS = 0.4
PESO_OTRAS = 0.4
PESO_TX = 1.5

# Columnas de entrada (estado_pedido y estado_entrega quedan fuera:
# la primera es el objetivo, la segunda es fuga de datos)
NUMERICAS = [
    "dias_envio_real", "dias_envio_prog", "beneficio_pedido",
    "ventas_cliente", "precio_base", "margen_ganancia_item",
    "cantidad", "ventas",
]
BINARIAS = ["riesgo_retraso"]
NOMINAL_BAJA_CARDINALIDAD = ["tipo_transaccion", "modo_envio"]
NOMINAL_ALTA_CARDINALIDAD = ["categoria", "region_destino"]

COLORES = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860", "#DA8BC3", "#8C8C8C"]


def _guardar_figura(nombre: str):
    os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
    ruta = os.path.join(CARPETA_GRAFICAS, nombre)
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    print(f"  Gráfica guardada: {ruta}")
    plt.close()


def cargar_y_preparar(ruta_csv: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga el CSV limpio y construye df_modelo (features codificadas)."""
    df = pd.read_csv(ruta_csv)
    print(f"Dimensiones: {df.shape}")
    print(f"Valores nulos: {df.isnull().sum().sum()}")

    columnas_seleccionadas = (
        NUMERICAS + BINARIAS + NOMINAL_BAJA_CARDINALIDAD + NOMINAL_ALTA_CARDINALIDAD
    )
    df_modelo = df[columnas_seleccionadas].copy()

    # Binaria -> 0/1
    df_modelo["riesgo_retraso"] = df_modelo["riesgo_retraso"].astype(int)

    # Baja cardinalidad -> One-Hot Encoding
    df_modelo = pd.get_dummies(df_modelo, columns=NOMINAL_BAJA_CARDINALIDAD, drop_first=True)

    # Alta cardinalidad -> codificación por frecuencia
    for col in NOMINAL_ALTA_CARDINALIDAD:
        frecuencias = df_modelo[col].value_counts(normalize=True)
        df_modelo[col] = df_modelo[col].map(frecuencias)

    df_modelo = df_modelo.astype(float)
    print(f"Dimensiones después de codificación: {df_modelo.shape}")

    return df, df_modelo


def construir_espacio_ponderado(df: pd.DataFrame, df_modelo: pd.DataFrame) -> np.ndarray:
    """Construye el espacio de variables ponderado (tipo_transaccion con más peso)."""
    tx_dummies_full = pd.get_dummies(df["tipo_transaccion"], prefix="tx").astype(float)

    otras_categoricas = (
        ["riesgo_retraso"]
        + [c for c in df_modelo.columns if c.startswith("modo_envio_")]
        + ["categoria", "region_destino"]
    )

    X_numericas = StandardScaler().fit_transform(df_modelo[NUMERICAS])
    X_otras = StandardScaler().fit_transform(df_modelo[otras_categoricas])
    X_tx = StandardScaler().fit_transform(tx_dummies_full)

    X_ponderado = np.hstack(
        [X_numericas * PESO_NUMERICAS, X_otras * PESO_OTRAS, X_tx * PESO_TX]
    )
    print(f"Espacio de variables ponderado: {X_ponderado.shape}")
    return X_ponderado


def seleccionar_k(X_ponderado: np.ndarray, k_range=range(2, 9)) -> int:
    """Selecciona k óptimo según silhouette score y grafica los 3 criterios vs. k."""
    silhouette_scores, calinski_scores, davies_scores = [], [], []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = km.fit_predict(X_ponderado)
        silhouette_scores.append(
            silhouette_score(X_ponderado, labels, sample_size=10000, random_state=RANDOM_STATE)
        )
        calinski_scores.append(calinski_harabasz_score(X_ponderado, labels))
        davies_scores.append(davies_bouldin_score(X_ponderado, labels))

    k_optimo = list(k_range)[int(np.argmax(silhouette_scores))]
    print(f"k óptimo (espacio ponderado): {k_optimo}  (silhouette={max(silhouette_scores):.4f})")

    # --- Gráfica 1: selección de k ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Selección del número óptimo de clusters (k) — espacio ponderado", fontsize=13)

    axes[0].plot(list(k_range), silhouette_scores, "o-", color=COLORES[0])
    axes[0].axvline(k_optimo, color="red", linestyle="--", alpha=0.6, label=f"k óptimo = {k_optimo}")
    axes[0].set_title("Silhouette Score")
    axes[0].set_xlabel("k"); axes[0].set_ylabel("Score"); axes[0].legend(); axes[0].grid(alpha=0.3)

    axes[1].plot(list(k_range), calinski_scores, "o-", color=COLORES[1])
    axes[1].axvline(k_optimo, color="red", linestyle="--", alpha=0.6)
    axes[1].set_title("Calinski-Harabasz")
    axes[1].set_xlabel("k"); axes[1].grid(alpha=0.3)

    axes[2].plot(list(k_range), davies_scores, "o-", color=COLORES[2])
    axes[2].axvline(k_optimo, color="red", linestyle="--", alpha=0.6)
    axes[2].set_title("Davies-Bouldin (menor es mejor)")
    axes[2].set_xlabel("k"); axes[2].grid(alpha=0.3)

    _guardar_figura("01_seleccion_k.png")

    return k_optimo


def entrenar_modelo_final(X_ponderado: np.ndarray, k_optimo: int) -> tuple[KMeans, np.ndarray]:
    """Entrena el K-Means final con el k óptimo."""
    kmeans_mejorado = KMeans(n_clusters=k_optimo, random_state=RANDOM_STATE, n_init=10)
    labels = kmeans_mejorado.fit_predict(X_ponderado)
    return kmeans_mejorado, labels


def graficar_tamano_clusters(tamano: pd.Series):
    """Gráfica 2: tamaño relativo de cada cluster."""
    plt.figure(figsize=(7, 4.5))
    tamano_ordenado = tamano.sort_index()
    barras = plt.bar(
        [f"Cluster {i}" for i in tamano_ordenado.index],
        tamano_ordenado.values,
        color=COLORES[: len(tamano_ordenado)],
    )
    for barra, valor in zip(barras, tamano_ordenado.values):
        plt.text(barra.get_x() + barra.get_width() / 2, valor + 0.5, f"{valor:.1f}%",
                  ha="center", fontsize=10)
    plt.ylabel("% del total de pedidos")
    plt.title("Tamaño relativo de cada cluster")
    plt.ylim(0, max(tamano_ordenado.values) + 8)
    plt.grid(axis="y", alpha=0.3)
    _guardar_figura("02_tamano_clusters.png")


def graficar_composicion_objetivo(porcentaje: pd.DataFrame):
    """Gráfica 3: % COMPLETE vs CANCELED por cluster (barras apiladas)."""
    porcentaje = porcentaje.sort_index()
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    clusters = [f"Cluster {i}" for i in porcentaje.index]

    completado = porcentaje["COMPLETE"].values
    cancelado = porcentaje["CANCELED"].values

    ax.bar(clusters, completado, label="COMPLETE", color="#55A868")
    ax.bar(clusters, cancelado, bottom=completado, label="CANCELED", color="#C44E52")

    for i, (c, comp) in enumerate(zip(clusters, completado)):
        ax.text(i, comp / 2, f"{comp:.1f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        ax.text(i, comp + (100 - comp) / 2, f"{100 - comp:.1f}%", ha="center", va="center",
                color="white", fontsize=9, fontweight="bold")

    ax.axhline(66.21, color="black", linestyle="--", alpha=0.6, label="Tasa base COMPLETE (66.2%)")
    ax.set_ylabel("% de pedidos")
    ax.set_title("Composición COMPLETE / CANCELED por cluster")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    ax.grid(axis="y", alpha=0.3)
    _guardar_figura("03_composicion_objetivo.png")


def graficar_composicion_tx(df: pd.DataFrame, df_modelo: pd.DataFrame):
    """Gráfica 4: composición de tipo_transaccion por cluster (barras apiladas)."""
    tabla_tx = pd.crosstab(df_modelo["cluster_mejorado"], df["tipo_transaccion"])
    porcentaje_tx = tabla_tx.div(tabla_tx.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(8, 4.5))
    clusters = [f"Cluster {i}" for i in porcentaje_tx.index]
    base = np.zeros(len(porcentaje_tx))
    colores_tx = {"CASH": "#C44E52", "TRANSFER": "#DD8452", "DEBIT": "#4C72B0", "PAYMENT": "#55A868"}

    for tx in porcentaje_tx.columns:
        valores = porcentaje_tx[tx].values
        ax.bar(clusters, valores, bottom=base, label=tx, color=colores_tx.get(tx))
        base += valores

    ax.set_ylabel("% del cluster")
    ax.set_title("Composición de tipo_transaccion por cluster")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4)
    ax.grid(axis="y", alpha=0.3)
    _guardar_figura("04_composicion_tx.png")


def graficar_clusters_pca2d(X_ponderado: np.ndarray, labels: np.ndarray, n_muestra: int = 8000):
    """Gráfica 5: visualización 2D de los clusters, reduciendo el espacio ponderado con PCA."""
    rng = np.random.default_rng(RANDOM_STATE)
    n_muestra = min(n_muestra, len(X_ponderado))
    idx = rng.choice(len(X_ponderado), size=n_muestra, replace=False)

    coords_2d = PCA(n_components=2, random_state=RANDOM_STATE).fit_transform(X_ponderado[idx])
    labels_muestra = labels[idx]

    plt.figure(figsize=(7.5, 6))
    for cluster_id in sorted(np.unique(labels_muestra)):
        mask = labels_muestra == cluster_id
        plt.scatter(coords_2d[mask, 0], coords_2d[mask, 1], s=6, alpha=0.5,
                    color=COLORES[cluster_id % len(COLORES)], label=f"Cluster {cluster_id}")

    plt.title(f"Visualización 2D de los clusters (PCA, muestra de {n_muestra:,} pedidos)")
    plt.xlabel("Componente 1"); plt.ylabel("Componente 2")
    plt.legend(markerscale=3)
    plt.grid(alpha=0.3)
    _guardar_figura("05_clusters_pca2d.png")


def evaluar_modelo(df: pd.DataFrame, df_modelo: pd.DataFrame, X_ponderado: np.ndarray,
                    labels: np.ndarray) -> pd.DataFrame:
    """Evaluación interna (silhouette, etc.), externa (cruce con estado_pedido) y gráficas."""
    sil = silhouette_score(X_ponderado, labels, sample_size=10000, random_state=RANDOM_STATE)
    cal = calinski_harabasz_score(X_ponderado, labels)
    dav = davies_bouldin_score(X_ponderado, labels)
    print(f"\nSilhouette: {sil:.4f} | Calinski-Harabasz: {cal:.2f} | Davies-Bouldin: {dav:.4f}")

    df_modelo["cluster_mejorado"] = labels

    tabla = pd.crosstab(df_modelo["cluster_mejorado"], df["estado_pedido"])
    porcentaje = (tabla.div(tabla.sum(axis=1), axis=0) * 100).round(2)
    tamano = (df_modelo["cluster_mejorado"].value_counts(normalize=True) * 100).round(1)

    print("\nConteos por cluster:")
    print(tabla)
    print("\nPorcentaje por cluster:")
    print(porcentaje)
    print("\nTamaño relativo de cada cluster (%):")
    print(tamano)

    print("\nComposición de tipo_transaccion por cluster:")
    print(pd.crosstab(df_modelo["cluster_mejorado"], df["tipo_transaccion"]))

    diferenciacion_maxima = porcentaje.max(axis=1)
    clusters_sobre_70 = (diferenciacion_maxima >= 70).sum()
    cobertura = tamano[diferenciacion_maxima >= 70].sum()
    print(f"\nClusters con diferenciación >= 70%: {clusters_sobre_70} de {len(diferenciacion_maxima)}")
    print(f"Cobertura de datos en esos clusters: {cobertura:.1f}% del total")

    print("\nGenerando gráficas...")
    graficar_tamano_clusters(tamano)
    graficar_composicion_objetivo(porcentaje)
    graficar_composicion_tx(df, df_modelo)
    graficar_clusters_pca2d(X_ponderado, labels)

    return porcentaje


def main():
    df, df_modelo = cargar_y_preparar(RUTA_CSV)
    X_ponderado = construir_espacio_ponderado(df, df_modelo)
    k_optimo = seleccionar_k(X_ponderado)  # genera 01_seleccion_k.png
    kmeans_mejorado, labels = entrenar_modelo_final(X_ponderado, k_optimo)
    evaluar_modelo(df, df_modelo, X_ponderado, labels)  # genera gráficas 02-05
    print(f"\nTodas las gráficas quedaron guardadas en la carpeta '{CARPETA_GRAFICAS}/'.")
    return kmeans_mejorado, df_modelo


if __name__ == "__main__":
    main()
