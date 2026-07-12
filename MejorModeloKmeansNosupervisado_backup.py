import sys
import os
import json
from datetime import date
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN, HDBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.manifold import TSNE
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
RANDOM_STATE = 42

# Obtener la ruta absoluta del directorio donde está el script
directorio_script = os.path.dirname(os.path.abspath(__file__))
os.chdir(directorio_script)  # Cambiar al directorio del script

# Ahora usar el nombre del archivo directamente (está en la misma carpeta)
RUTA_CSV = "DataCoSupplyChain_Limpio.csv"

# Verificar que el archivo existe
if not os.path.exists(RUTA_CSV):
    print(f"ERROR: No se encuentra '{RUTA_CSV}'")
    print(f"Directorio actual: {os.getcwd()}")
    print("\nArchivos disponibles:")
    for archivo in os.listdir('.'):
        if os.path.isfile(archivo):
            print(f"  - {archivo}")
    sys.exit(1)
else:
    print(f"Archivo encontrado: {RUTA_CSV}")
    print(f"Tamaño: {os.path.getsize(RUTA_CSV):,} bytes")
    print(f"Ruta completa: {os.path.abspath(RUTA_CSV)}")


CARPETA_GRAFICAS = "graficas1111"
TAMANO_MUESTRA_TSNE = 5000

# Pesos para dar más importancia a 'tipo_transaccion', la variable con mayor
# correlación encontrada en el diagnóstico (r ~ 0.33 vs |r| < 0.01 del resto)
PESO_NUMERICAS = 0.4
PESO_OTRAS = 0.4
PESO_TX = 1.5

# Columnas de entrada (estado_pedido y estado_entrega quedan fuera)
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
    """Guarda la figura actual en la carpeta de gráficas."""
    os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
    ruta = os.path.join(CARPETA_GRAFICAS, nombre)
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    print(f"  Gráfica guardada: {ruta}")
    plt.close()


# ============================================================================
# 1. CARGA Y PREPARACIÓN DE DATOS
# ============================================================================
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
    print(f"Columnas finales: {df_modelo.columns.tolist()}")

    return df, df_modelo


# ============================================================================
# 2. CONSTRUCCIÓN DEL ESPACIO PONDERADO
# ============================================================================
def construir_espacio_ponderado(df: pd.DataFrame, df_modelo: pd.DataFrame) -> np.ndarray:

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


# ============================================================================
# 3. SELECCIÓN DEL NÚMERO ÓPTIMO DE CLUSTERS
# ============================================================================
def seleccionar_k(X_ponderado: np.ndarray, k_range=range(2, 9)) -> int:

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

    # Gráfica 1: selección de k
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Selección del número óptimo de clusters (k) — espacio ponderado", fontsize=13)

    axes[0].plot(list(k_range), silhouette_scores, "o-", color=COLORES[0])
    axes[0].axvline(k_optimo, color="red", linestyle="--", alpha=0.6, label=f"k óptimo = {k_optimo}")
    axes[0].set_title("Silhouette Score (mayor es mejor)")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Score")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(list(k_range), calinski_scores, "o-", color=COLORES[1])
    axes[1].axvline(k_optimo, color="red", linestyle="--", alpha=0.6)
    axes[1].set_title("Calinski-Harabasz (mayor es mejor)")
    axes[1].set_xlabel("k")
    axes[1].grid(alpha=0.3)

    axes[2].plot(list(k_range), davies_scores, "o-", color=COLORES[2])
    axes[2].axvline(k_optimo, color="red", linestyle="--", alpha=0.6)
    axes[2].set_title("Davies-Bouldin (menor es mejor)")
    axes[2].set_xlabel("k")
    axes[2].grid(alpha=0.3)

    _guardar_figura("01_seleccion_k.png")
    
    # Mostrar tabla de resultados
    tabla_k = pd.DataFrame({
        'k': list(k_range),
        'silhouette': silhouette_scores,
        'calinski_harabasz': calinski_scores,
        'davies_bouldin': davies_scores
    })
    print("\nTabla de selección de k:")
    print(tabla_k.round(4))

    return k_optimo


# ============================================================================
# 4. ENTRENAMIENTO DEL MODELO FINAL
# ============================================================================
def entrenar_modelo_final(X_ponderado: np.ndarray, k_optimo: int) -> tuple[KMeans, np.ndarray]:
    kmeans = KMeans(n_clusters=k_optimo, random_state=RANDOM_STATE, n_init=10)
    labels = kmeans.fit_predict(X_ponderado)
    return kmeans, labels


# ============================================================================
# 5. ANÁLISIS DE PCA Y CARGAS
# ============================================================================
def analizar_pca(X_ponderado: np.ndarray, df_modelo: pd.DataFrame):

    pca = PCA(random_state=RANDOM_STATE)
    pca_resultado = pca.fit_transform(X_ponderado)

    varianza_explicada = pca.explained_variance_ratio_
    varianza_acumulada = np.cumsum(varianza_explicada)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.bar(range(1, len(varianza_explicada) + 1), varianza_explicada)
    plt.xlabel('Componente Principal')
    plt.ylabel('Varianza Explicada')
    plt.title('Varianza Explicada por Componente')

    plt.subplot(1, 2, 2)
    plt.plot(range(1, len(varianza_acumulada) + 1), varianza_acumulada, 'bo-')
    plt.axhline(y=0.85, color='r', linestyle='--', label='85% de varianza')
    plt.xlabel('Número de Componentes')
    plt.ylabel('Varianza Acumulada')
    plt.title('Varianza Acumulada Explicada')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    _guardar_figura("06_pca_varianza.png")

    n_componentes = int(np.argmax(varianza_acumulada >= 0.85) + 1)
    print(f"\nComponentes para 85% de varianza: {n_componentes}")

    # Reducir para visualización 2D de clusters
    pca_2d = PCA(n_components=2, random_state=RANDOM_STATE)
    df_pca_2d = pca_2d.fit_transform(X_ponderado)
    return df_pca_2d, n_componentes


# ============================================================================
# 6. VISUALIZACIONES
# ============================================================================
def graficar_tamano_clusters(tamano: pd.Series):
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


def graficar_composicion_objetivo(porcentaje: pd.DataFrame, tasa_base: float):
    porcentaje = porcentaje.sort_index()
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    clusters = [f"Cluster {i}" for i in porcentaje.index]

    completado = porcentaje["COMPLETE"].values
    cancelado = porcentaje["CANCELED"].values

    ax.bar(clusters, completado, label="COMPLETE", color="#55A868")
    ax.bar(clusters, cancelado, bottom=completado, label="CANCELED", color="#C44E52")

    for i, (c, comp) in enumerate(zip(clusters, completado)):
        ax.text(i, comp / 2, f"{comp:.1f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        if comp < 100:
            ax.text(i, comp + (100 - comp) / 2, f"{100 - comp:.1f}%", ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold")

    ax.axhline(tasa_base, color="black", linestyle="--", alpha=0.6, label=f"Tasa base COMPLETE ({tasa_base:.1f}%)")
    ax.set_ylabel("% de pedidos")
    ax.set_title("Composición COMPLETE / CANCELED por cluster")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    ax.grid(axis="y", alpha=0.3)
    _guardar_figura("03_composicion_objetivo.png")


def graficar_composicion_tx(df: pd.DataFrame, df_modelo: pd.DataFrame):
    tabla_tx = pd.crosstab(df_modelo["cluster_mejorado"], df["tipo_transaccion"])
    porcentaje_tx = tabla_tx.div(tabla_tx.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(8, 4.5))
    clusters = [f"Cluster {i}" for i in porcentaje_tx.index]
    base = np.zeros(len(porcentaje_tx))
    colores_tx = {"CASH": "#C44E52", "TRANSFER": "#DD8452", "DEBIT": "#4C72B0", "PAYMENT": "#55A868"}

    for tx in porcentaje_tx.columns:
        valores = porcentaje_tx[tx].values
        ax.bar(clusters, valores, bottom=base, label=tx, color=colores_tx.get(tx, "#888888"))
        base += valores

    ax.set_ylabel("% del cluster")
    ax.set_title("Composición de tipo_transaccion por cluster")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4)
    ax.grid(axis="y", alpha=0.3)
    _guardar_figura("04_composicion_tx.png")


def graficar_clusters_pca2d(X_ponderado: np.ndarray, labels: np.ndarray, n_muestra: int = 8000):
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
    plt.xlabel("Componente 1")
    plt.ylabel("Componente 2")
    plt.legend(markerscale=3)
    plt.grid(alpha=0.3)
    _guardar_figura("05_clusters_pca2d.png")


def graficar_tsne(X_ponderado: np.ndarray, df_modelo: pd.DataFrame, cluster_col: str):
    """Gráfica t-SNE para visualización no lineal de clusters."""
    def muestreo_estratificado(dataframe, columna_cluster, n_total, random_state):
        frac = n_total / len(dataframe)
        partes = [g.sample(frac=frac, random_state=random_state) for _, g in dataframe.groupby(columna_cluster)]
        return pd.concat(partes)

    TAMANO_MUESTRA_TSNE = 5000
    muestra_tsne = muestreo_estratificado(df_modelo, cluster_col, TAMANO_MUESTRA_TSNE, RANDOM_STATE)
    idx_tsne = muestra_tsne.index
    X_ponderado_tsne = X_ponderado[df_modelo.index.get_indexer(idx_tsne)]

    tsne = TSNE(n_components=2, random_state=RANDOM_STATE, perplexity=30, init='pca')
    emb_tsne = tsne.fit_transform(X_ponderado_tsne)

    plt.figure(figsize=(9, 7))
    scatter = plt.scatter(emb_tsne[:, 0], emb_tsne[:, 1],
                           c=muestra_tsne[cluster_col], cmap='viridis', alpha=0.6, s=15)
    plt.colorbar(scatter, label='Cluster')
    plt.title(f't-SNE de los clusters (muestra de {len(idx_tsne)} puntos)')
    plt.xlabel('Componente t-SNE 1')
    plt.ylabel('Componente t-SNE 2')
    _guardar_figura("07_tsne_clusters.png")


# ============================================================================
# 7. EVALUACIÓN DEL MODELO
# ============================================================================
def evaluar_modelo(df: pd.DataFrame, df_modelo: pd.DataFrame, X_ponderado: np.ndarray,
                    labels: np.ndarray) -> tuple[pd.DataFrame, pd.Series]:
    # Métricas internas
    sil = silhouette_score(X_ponderado, labels, sample_size=10000, random_state=RANDOM_STATE)
    cal = calinski_harabasz_score(X_ponderado, labels)
    dav = davies_bouldin_score(X_ponderado, labels)
    print(f"\n--- Métricas internas ---")
    print(f"Silhouette: {sil:.4f}")
    print(f"Calinski-Harabasz: {cal:.2f}")
    print(f"Davies-Bouldin: {dav:.4f}")

    # Asignar clusters al dataframe
    df_modelo["cluster_mejorado"] = labels

    # Evaluación externa con estado_pedido
    tabla = pd.crosstab(df_modelo["cluster_mejorado"], df["estado_pedido"])
    porcentaje = (tabla.div(tabla.sum(axis=1), axis=0) * 100).round(2)
    tamano = (df_modelo["cluster_mejorado"].value_counts(normalize=True) * 100).round(1)

    print("\n--- Evaluación externa (cruce con estado_pedido) ---")
    print("\nConteos por cluster:")
    print(tabla)
    print("\nPorcentaje por cluster:")
    print(porcentaje)
    print("\nTamaño relativo de cada cluster (%):")
    print(tamano)

    # Composición de tipo_transaccion
    print("\nComposición de tipo_transaccion por cluster:")
    print(pd.crosstab(df_modelo["cluster_mejorado"], df["tipo_transaccion"]))

    # Análisis de diferenciación
    diferenciacion_maxima = porcentaje.max(axis=1)
    clusters_sobre_70 = (diferenciacion_maxima >= 70).sum()
    cobertura = tamano[diferenciacion_maxima >= 70].sum()
    tasa_base = (df["estado_pedido"] == "COMPLETE").mean() * 100

    print(f"\n--- Resumen de diferenciación ---")
    print(f"Tasa base de pedidos COMPLETE: {tasa_base:.2f}%")
    print(f"Clusters con diferenciación >= 70%: {clusters_sobre_70} de {len(diferenciacion_maxima)}")
    print(f"Cobertura de datos en esos clusters: {cobertura:.1f}% del total")
    print(f"Máxima diferenciación alcanzada: {diferenciacion_maxima.max():.1f}%")

    # Generar gráficas
    graficar_tamano_clusters(tamano)
    graficar_composicion_objetivo(porcentaje, tasa_base)
    graficar_composicion_tx(df, df_modelo)
    graficar_clusters_pca2d(X_ponderado, labels)
    graficar_tsne(X_ponderado, df_modelo, "cluster_mejorado")

    return porcentaje, tamano


# ============================================================================
# 8. DETECCIÓN DE ANOMALÍAS
# ============================================================================
def detectar_anomalias(kmeans: KMeans, X_ponderado: np.ndarray, df_modelo: pd.DataFrame):
    """Detección de anomalías basada en distancia al centroide más cercano."""
    distancias = kmeans.transform(X_ponderado)
    distancia_minima = np.min(distancias, axis=1)

    umbral = np.percentile(distancia_minima, 95)
    anomalias = distancia_minima > umbral

    print(f"\n--- Detección de anomalías ---")
    print(f"Anomalías detectadas: {sum(anomalias)} ({sum(anomalias)/len(X_ponderado)*100:.2f}%)")

    df_anomalias = df_modelo[anomalias]
    df_normales = df_modelo[~anomalias]

    print("\nComparación de medias entre anomalías y normales:")
    for col in ['dias_envio_real', 'beneficio_pedido', 'ventas']:
        if col in df_modelo.columns:
            print(f"  {col}:")
            print(f"    Anomalías - media: {df_anomalias[col].mean():.2f}")
            print(f"    Normales  - media: {df_normales[col].mean():.2f}")

    df_modelo['es_anomalia'] = anomalias
    return anomalias


# ============================================================================
# 9. DETECCIÓN DE OUTLIERS UNIVARIADOS
# ============================================================================
def detectar_outliers(df_modelo: pd.DataFrame):
    """Detección de outliers univariados usando IQR."""
    def detectar_outliers_iqr(serie):
        Q1, Q3 = serie.quantile(0.25), serie.quantile(0.75)
        IQR = Q3 - Q1
        return (serie < Q1 - 1.5 * IQR) | (serie > Q3 + 1.5 * IQR)

    columnas_outliers = ['dias_envio_real', 'beneficio_pedido', 'ventas']
    outliers = {}
    
    print("\n--- Detección de outliers univariados ---")
    for col in columnas_outliers:
        if col in df_modelo.columns:
            mask = detectar_outliers_iqr(df_modelo[col])
            outliers[col] = mask
            print(f"{col}: {mask.sum()} outliers ({mask.sum()/len(df_modelo)*100:.2f}%)")

    df_modelo['es_outlier'] = pd.DataFrame(outliers).any(axis=1) if outliers else False
    if outliers:
        print(f"\nRegistros con al menos un outlier: {df_modelo['es_outlier'].sum()} "
              f"({df_modelo['es_outlier'].sum()/len(df_modelo)*100:.2f}%)")
    return outliers


# ============================================================================
# 10. FUNCIÓN PRINCIPAL
# ============================================================================
def main():
    """Ejecuta el flujo completo del modelo no supervisado con K-Means ponderado."""
    print("=" * 60)
    print("MODELO NO SUPERVISADO - K-MEANS PONDERADO")
    print("=" * 60)
    
    # 1. Carga y preparación
    df, df_modelo = cargar_y_preparar(RUTA_CSV)
    
    # 2. Construcción del espacio ponderado
    print("\n[2] Construyendo espacio de variables ponderado...")
    X_ponderado = construir_espacio_ponderado(df, df_modelo)
    
    # 3. Selección de k
    print("\n[3] Seleccionando número óptimo de clusters...")
    k_optimo = seleccionar_k(X_ponderado)
    
    # 4. Entrenamiento del modelo
    kmeans, labels = entrenar_modelo_final(X_ponderado, k_optimo)
    
    # 5. Análisis PCA
    print("\n[5] Analizando PCA...")
    df_pca_2d, n_componentes = analizar_pca(X_ponderado, df_modelo)
    
    # 6. Evaluación del modelo
    print("\n[6] Evaluando modelo...")
    porcentaje, tamano = evaluar_modelo(df, df_modelo, X_ponderado, labels)
    
    # 7. Detección de anomalías
    print("\n[7] Detectando anomalías...")
    detectar_anomalias(kmeans, X_ponderado, df_modelo)
    
    # 8. Detección de outliers
    print("\n[8] Detectando outliers...")
    detectar_outliers(df_modelo)
    
    # 9. Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    print(f"Número de clusters (k): {k_optimo}")
    print(f"Silhouette score: {silhouette_score(X_ponderado, labels, sample_size=10000, random_state=RANDOM_STATE):.4f}")
    print(f"Clusters con diferenciación ≥ 70%: {sum(porcentaje.max(axis=1) >= 70)} de {len(porcentaje)}")
    print(f"Cobertura: {tamano[porcentaje.max(axis=1) >= 70].sum():.1f}% del total")
    print(f"\nTodas las gráficas guardadas en '{CARPETA_GRAFICAS}/'")
    
    return kmeans, df_modelo


# ============================================================================
# EJECUCIÓN
# ============================================================================
if __name__ == "__main__":
    main()