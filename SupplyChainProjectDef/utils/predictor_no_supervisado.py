"""
Motor de predicción no supervisada para GDLM.

Carga el modelo K-Means entrenado y sus artefactos,
prepara un pedido nuevo, asigna un cluster real
y detecta posibles anomalías.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any
import json

import joblib
import numpy as np
import pandas as pd


# =============================================================================
# RUTAS
# =============================================================================

RUTA_BDML = Path(__file__).resolve().parents[2]

RUTA_ARTEFACTOS = (
    RUTA_BDML / "modelo_kmeans_artifacts.pkl"
)

RUTA_METADATA = (
    RUTA_BDML / "metadata_kmeans.json"
)


# =============================================================================
# EXCEPCIONES
# =============================================================================

class ErrorPredictorNoSupervisado(Exception):
    """Error general del predictor no supervisado."""


class ArtefactoKMeansNoEncontradoError(
    ErrorPredictorNoSupervisado
):
    """Se lanza cuando faltan archivos del modelo K-Means."""


class DatosKMeansError(
    ErrorPredictorNoSupervisado
):
    """Se lanza cuando los datos recibidos son inválidos."""


# =============================================================================
# CARGA DE ARTEFACTOS
# =============================================================================

@lru_cache(maxsize=1)
def cargar_artefactos_kmeans() -> dict[str, Any]:
    """Carga una sola vez el modelo K-Means y su metadata."""

    faltantes = []

    if not RUTA_ARTEFACTOS.exists():
        faltantes.append(str(RUTA_ARTEFACTOS))

    if not RUTA_METADATA.exists():
        faltantes.append(str(RUTA_METADATA))

    if faltantes:
        detalle = "\n".join(
            f"- {ruta}"
            for ruta in faltantes
        )

        raise ArtefactoKMeansNoEncontradoError(
            "Faltan archivos necesarios para usar K-Means:\n"
            f"{detalle}\n\n"
            "Ejecuta nuevamente "
            "MejorModeloKmeansNosupervisado.py"
        )

    try:
        artefactos = joblib.load(
            RUTA_ARTEFACTOS
        )

        with open(
            RUTA_METADATA,
            "r",
            encoding="utf-8",
        ) as archivo:
            metadata = json.load(archivo)

    except Exception as error:
        raise ErrorPredictorNoSupervisado(
            "No fue posible cargar los artefactos "
            f"del modelo K-Means: {error}"
        ) from error

    artefactos["metadata"] = metadata

    return artefactos


# =============================================================================
# VALIDACIÓN
# =============================================================================

CAMPOS_REQUERIDOS = [
    "dias_envio_real",
    "dias_envio_prog",
    "beneficio_pedido",
    "ventas_cliente",
    "precio_base",
    "margen_ganancia_item",
    "cantidad",
    "ventas",
    "riesgo_retraso",
    "tipo_transaccion",
    "modo_envio",
    "categoria",
    "region_destino",
]


def validar_datos_kmeans(
    datos: dict[str, Any],
) -> None:
    """Valida los datos necesarios para asignar un cluster."""

    faltantes = [
        campo
        for campo in CAMPOS_REQUERIDOS
        if campo not in datos
        or datos[campo] is None
    ]

    if faltantes:
        raise DatosKMeansError(
            "Faltan campos para ejecutar K-Means: "
            + ", ".join(faltantes)
        )

    if float(datos["cantidad"]) <= 0:
        raise DatosKMeansError(
            "La cantidad debe ser mayor que cero."
        )

    if float(datos["precio_base"]) < 0:
        raise DatosKMeansError(
            "El precio base no puede ser negativo."
        )

    if float(datos["ventas"]) < 0:
        raise DatosKMeansError(
            "Las ventas no pueden ser negativas."
        )

    if float(datos["dias_envio_real"]) < 0:
        raise DatosKMeansError(
            "Los días reales de envío no pueden ser negativos."
        )

    if float(datos["dias_envio_prog"]) < 0:
        raise DatosKMeansError(
            "Los días programados no pueden ser negativos."
        )


# =============================================================================
# PREPARACIÓN DEL PEDIDO
# =============================================================================

def construir_espacio_pedido(
    datos: dict[str, Any],
) -> np.ndarray:
    """
    Replica exactamente el preprocesamiento
    utilizado durante el entrenamiento.
    """

    validar_datos_kmeans(datos)

    artefactos = cargar_artefactos_kmeans()

    numericas = artefactos["NUMERICAS"]
    otras_categoricas = artefactos[
        "otras_categoricas"
    ]
    tx_columns = artefactos[
        "tx_columns"
    ]
    modo_envio_dummies = artefactos[
        "modo_envio_dummies"
    ]

    scaler_numericas = artefactos[
        "scaler_numericas"
    ]
    scaler_otras = artefactos[
        "scaler_otras"
    ]
    scaler_tx = artefactos[
        "scaler_tx"
    ]

    freq_categoria = artefactos[
        "freq_categoria"
    ]
    freq_region = artefactos[
        "freq_region"
    ]

    peso_numericas = float(
        artefactos["PESO_NUMERICAS"]
    )
    peso_otras = float(
        artefactos["PESO_OTRAS"]
    )
    peso_tx = float(
        artefactos["PESO_TX"]
    )

    # -------------------------------------------------------------------------
    # BLOQUE NUMÉRICO
    # -------------------------------------------------------------------------

    fila_numerica = pd.DataFrame(
        [
            {
                columna: float(
                    datos[columna]
                )
                for columna in numericas
            }
        ]
    )

    fila_numerica = fila_numerica[
        numericas
    ]

    X_numericas = scaler_numericas.transform(
        fila_numerica
    )

    # -------------------------------------------------------------------------
    # BLOQUE DE OTRAS VARIABLES
    # -------------------------------------------------------------------------

    fila_otras = {
        "riesgo_retraso": int(
            datos["riesgo_retraso"]
        ),
        "categoria": float(
            freq_categoria.get(
                str(datos["categoria"]),
                0.0,
            )
        ),
        "region_destino": float(
            freq_region.get(
                str(datos["region_destino"]),
                0.0,
            )
        ),
    }

    modo_envio_actual = str(
        datos["modo_envio"]
    )

    for columna_dummy in modo_envio_dummies:
        categoria_dummy = (
            columna_dummy.replace(
                "modo_envio_",
                "",
                1,
            )
        )

        fila_otras[columna_dummy] = int(
            modo_envio_actual
            == categoria_dummy
        )

    fila_otras_df = pd.DataFrame(
        [fila_otras]
    )

    for columna in otras_categoricas:
        if columna not in fila_otras_df.columns:
            fila_otras_df[columna] = 0.0

    fila_otras_df = fila_otras_df[
        otras_categoricas
    ].astype(float)

    X_otras = scaler_otras.transform(
        fila_otras_df
    )

    # -------------------------------------------------------------------------
    # BLOQUE TIPO DE TRANSACCIÓN
    # -------------------------------------------------------------------------

    tipo_transaccion_actual = str(
        datos["tipo_transaccion"]
    )

    fila_tx = {}

    for columna_tx in tx_columns:
        categoria_tx = columna_tx.replace(
            "tx_",
            "",
            1,
        )

        fila_tx[columna_tx] = int(
            tipo_transaccion_actual
            == categoria_tx
        )

    fila_tx_df = pd.DataFrame(
        [fila_tx]
    )

    fila_tx_df = fila_tx_df[
        tx_columns
    ].astype(float)

    X_tx = scaler_tx.transform(
        fila_tx_df
    )

    # -------------------------------------------------------------------------
    # ESPACIO FINAL PONDERADO
    # -------------------------------------------------------------------------

    X_ponderado = np.hstack(
        [
            X_numericas * peso_numericas,
            X_otras * peso_otras,
            X_tx * peso_tx,
        ]
    )

    return X_ponderado


# =============================================================================
# PERFILES DE CLUSTER
# =============================================================================

def obtener_perfil_cluster(
    cluster_id: int,
    artefactos: dict[str, Any],
) -> dict[str, Any]:
    """
    Devuelve una descripción basada en los resultados reales
    obtenidos durante el entrenamiento.
    """

    porcentaje_dict = artefactos.get(
        "porcentaje_complete_por_cluster",
        {},
    )

    tamano_dict = artefactos.get(
        "tamano_clusters",
        {},
    )

    porcentaje_complete = None
    porcentaje_canceled = None

    # Al guardar DataFrame.to_dict(), la estructura queda:
    # {
    #   "CANCELED": {0: ..., 1: ...},
    #   "COMPLETE": {0: ..., 1: ...}
    # }
    complete_map = porcentaje_dict.get(
        "COMPLETE",
        {},
    )

    canceled_map = porcentaje_dict.get(
        "CANCELED",
        {},
    )

    porcentaje_complete = complete_map.get(
        cluster_id,
        complete_map.get(
            str(cluster_id)
        ),
    )

    porcentaje_canceled = canceled_map.get(
        cluster_id,
        canceled_map.get(
            str(cluster_id)
        ),
    )

    tamano_cluster = tamano_dict.get(
        cluster_id,
        tamano_dict.get(
            str(cluster_id)
        ),
    )

    descripciones = {
        0: {
            "nombre": "Pedidos con alta finalización",
            "descripcion": (
                "Segmento predominantemente asociado a "
                "transacciones DEBIT y alta proporción "
                "de pedidos COMPLETE."
            ),
        },
        1: {
            "nombre": "Pedidos de riesgo intermedio",
            "descripcion": (
                "Segmento con mayor proporción de pedidos "
                "CANCELED y predominio de TRANSFER."
            ),
        },
        2: {
            "nombre": "Pedidos con finalización muy alta",
            "descripcion": (
                "Segmento predominantemente asociado a "
                "PAYMENT y elevada proporción de COMPLETE."
            ),
        },
        3: {
            "nombre": "Pedidos de cancelación crítica",
            "descripcion": (
                "Segmento predominantemente asociado a CASH "
                "y alta concentración de pedidos CANCELED."
            ),
        },
    }

    perfil_base = descripciones.get(
        cluster_id,
        {
            "nombre": f"Cluster {cluster_id}",
            "descripcion": (
                "Segmento identificado por el modelo "
                "K-Means."
            ),
        },
    )

    return {
        "cluster": cluster_id,
        "nombre": perfil_base["nombre"],
        "descripcion": perfil_base[
            "descripcion"
        ],
        "porcentaje_complete": (
            float(porcentaje_complete)
            if porcentaje_complete is not None
            else None
        ),
        "porcentaje_canceled": (
            float(porcentaje_canceled)
            if porcentaje_canceled is not None
            else None
        ),
        "tamano_cluster": (
            float(tamano_cluster)
            if tamano_cluster is not None
            else None
        ),
    }


# =============================================================================
# PREDICCIÓN
# =============================================================================

def predecir_cluster(
    datos: dict[str, Any],
) -> dict[str, Any]:
    """
    Asigna un cluster real a un pedido nuevo
    y detecta si es una anomalía.
    """

    artefactos = cargar_artefactos_kmeans()

    modelo = artefactos["kmeans"]

    X_ponderado = construir_espacio_pedido(
        datos
    )

    try:
        cluster_id = int(
            modelo.predict(
                X_ponderado
            )[0]
        )

        distancias = modelo.transform(
            X_ponderado
        )[0]

    except Exception as error:
        raise ErrorPredictorNoSupervisado(
            "El modelo K-Means no pudo procesar "
            f"el pedido: {error}"
        ) from error

    distancia_minima = float(
        np.min(distancias)
    )

    distancia_centroide = float(
        distancias[cluster_id]
    )

    umbral_anomalias = float(
        artefactos.get(
            "umbral_anomalias",
            np.inf,
        )
    )

    es_anomalia = (
        distancia_minima
        > umbral_anomalias
    )

    perfil = obtener_perfil_cluster(
        cluster_id,
        artefactos,
    )

    metadata = artefactos.get(
        "metadata",
        {},
    )

    return {
        "cluster": cluster_id,
        "perfil": perfil,
        "distancia_centroide": (
            distancia_centroide
        ),
        "distancia_minima": (
            distancia_minima
        ),
        "umbral_anomalias": (
            umbral_anomalias
        ),
        "es_anomalia": bool(
            es_anomalia
        ),
        "k_optimo": int(
            artefactos.get(
                "k_optimo",
                metadata.get(
                    "k_optimo",
                    0,
                ),
            )
        ),
        "silhouette": float(
            artefactos.get(
                "silhouette",
                metadata.get(
                    "silhouette",
                    0.0,
                ),
            )
        ),
        "calinski_harabasz": float(
            artefactos.get(
                "calinski_harabasz",
                metadata.get(
                    "calinski_harabasz",
                    0.0,
                ),
            )
        ),
        "davies_bouldin": float(
            artefactos.get(
                "davies_bouldin",
                metadata.get(
                    "davies_bouldin",
                    0.0,
                ),
            )
        ),
        "fecha_entrenamiento": (
            artefactos.get(
                "fecha_entrenamiento"
            )
            or metadata.get(
                "fecha_entrenamiento"
            )
        ),
        "modelo": "KMeans",
    }


# =============================================================================
# UTILIDADES
# =============================================================================

def obtener_metadata_kmeans() -> dict[str, Any]:
    """Devuelve la metadata legible del modelo."""

    artefactos = cargar_artefactos_kmeans()

    metadata = artefactos.get(
        "metadata",
        {},
    ).copy()

    metadata.update(
        {
            "k_optimo": artefactos.get(
                "k_optimo",
                metadata.get(
                    "k_optimo"
                ),
            ),
            "silhouette": artefactos.get(
                "silhouette",
                metadata.get(
                    "silhouette"
                ),
            ),
            "calinski_harabasz": artefactos.get(
                "calinski_harabasz",
                metadata.get(
                    "calinski_harabasz"
                ),
            ),
            "davies_bouldin": artefactos.get(
                "davies_bouldin",
                metadata.get(
                    "davies_bouldin"
                ),
            ),
        }
    )

    return metadata


def comprobar_motor_kmeans() -> dict[str, Any]:
    """Comprueba que el predictor pueda cargar todo."""

    artefactos = cargar_artefactos_kmeans()

    return {
        "correcto": True,
        "modelo": "KMeans",
        "k_optimo": artefactos.get(
            "k_optimo"
        ),
        "silhouette": artefactos.get(
            "silhouette"
        ),
        "n_features": artefactos.get(
            "n_features"
        ),
        "ruta_artefactos": str(
            RUTA_ARTEFACTOS
        ),
    }