"""
Motor de predicción supervisada para GDLM.

Este módulo carga los artefactos entrenados con
ModeloSupervisadoLocal.py y permite realizar predicciones
sin depender de la interfaz supervisadoapp_streamlit.py.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import json
import joblib
import numpy as np
import pandas as pd


# =============================================================================
# RUTAS DEL PROYECTO
# =============================================================================

# predictor_supervisado.py está en:
# BDML/SupplyChainProjectDef/utils/predictor_supervisado.py
#
# Los artefactos están en:
# BDML/modelo_prediccion_envios.pkl
# BDML/scaler_envios.pkl
# BDML/*.json

RUTA_BDML = Path(__file__).resolve().parents[2]

RUTAS_ARTEFACTOS = {
    "modelo": RUTA_BDML / "modelo_prediccion_envios.pkl",
    "scaler": RUTA_BDML / "scaler_envios.pkl",
    "features": RUTA_BDML / "features_modelo.json",
    "frecuencias": RUTA_BDML / "frecuencias_categoricas.json",
    "categorias": RUTA_BDML / "categorias_dummies.json",
    "medianas": RUTA_BDML / "medianas_imputacion.json",
    "metadata": RUTA_BDML / "metadata_modelo.json",
}


# =============================================================================
# EXCEPCIONES PERSONALIZADAS
# =============================================================================

class ErrorPredictorSupervisado(Exception):
    """Error general del motor de predicción supervisada."""


class ArtefactoNoEncontradoError(ErrorPredictorSupervisado):
    """Se produce cuando falta algún archivo entrenado."""


class DatosPrediccionError(ErrorPredictorSupervisado):
    """Se produce cuando faltan datos necesarios para predecir."""


# =============================================================================
# CARGA DE ARTEFACTOS
# =============================================================================

@lru_cache(maxsize=1)
def cargar_artefactos() -> dict[str, Any]:
    """
    Carga una sola vez el modelo, scaler y archivos JSON.

    Returns:
        Diccionario con todos los artefactos del modelo.

    Raises:
        ArtefactoNoEncontradoError: si falta algún archivo.
        ErrorPredictorSupervisado: si un artefacto no puede cargarse.
    """

    faltantes = [
        str(ruta)
        for ruta in RUTAS_ARTEFACTOS.values()
        if not ruta.exists()
    ]

    if faltantes:
        lista = "\n".join(f"- {archivo}" for archivo in faltantes)
        raise ArtefactoNoEncontradoError(
            "Faltan artefactos necesarios para realizar la predicción:\n"
            f"{lista}\n\n"
            "Ejecuta nuevamente: python ModeloSupervisadoLocal.py"
        )

    try:
        modelo = joblib.load(RUTAS_ARTEFACTOS["modelo"])
        scaler = joblib.load(RUTAS_ARTEFACTOS["scaler"])

        with open(RUTAS_ARTEFACTOS["features"], encoding="utf-8") as archivo:
            features = json.load(archivo)

        with open(RUTAS_ARTEFACTOS["frecuencias"], encoding="utf-8") as archivo:
            frecuencias_categoricas = json.load(archivo)

        with open(RUTAS_ARTEFACTOS["categorias"], encoding="utf-8") as archivo:
            categorias_dummies = json.load(archivo)

        with open(RUTAS_ARTEFACTOS["medianas"], encoding="utf-8") as archivo:
            medianas = json.load(archivo)

        with open(RUTAS_ARTEFACTOS["metadata"], encoding="utf-8") as archivo:
            metadata = json.load(archivo)

    except Exception as error:
        raise ErrorPredictorSupervisado(
            f"No fue posible cargar los artefactos del modelo: {error}"
        ) from error

    return {
        "modelo": modelo,
        "scaler": scaler,
        "features": features,
        "frecuencias_categoricas": frecuencias_categoricas,
        "categorias_dummies": categorias_dummies,
        "medianas": medianas,
        "metadata": metadata,
    }


# =============================================================================
# VALIDACIÓN DE DATOS
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
    "total_item",
    "ganancia_pedido",
    "riesgo_retraso",
    "es_anomalia",
    "es_outlier",
    "modo_envio",
    "cluster_kmeans",
    "cluster_dbscan",
    "categoria",
    "region_destino",
]


def validar_datos(datos: dict[str, Any]) -> None:
    """
    Comprueba que estén presentes todos los campos necesarios.
    """

    faltantes = [
        campo
        for campo in CAMPOS_REQUERIDOS
        if campo not in datos or datos[campo] is None
    ]

    if faltantes:
        raise DatosPrediccionError(
            "Faltan campos necesarios para realizar la predicción: "
            + ", ".join(faltantes)
        )

    if float(datos["cantidad"]) <= 0:
        raise DatosPrediccionError(
            "La cantidad debe ser mayor que cero."
        )

    if float(datos["precio_base"]) < 0:
        raise DatosPrediccionError(
            "El precio base no puede ser negativo."
        )

    if float(datos["dias_envio_real"]) < 0:
        raise DatosPrediccionError(
            "Los días de envío real no pueden ser negativos."
        )

    if float(datos["dias_envio_prog"]) < 0:
        raise DatosPrediccionError(
            "Los días de envío programado no pueden ser negativos."
        )


# =============================================================================
# PREPARACIÓN DE FEATURES
# =============================================================================

def construir_fila_modelo(datos: dict[str, Any]) -> pd.DataFrame:
    """
    Replica la ingeniería de variables y codificación utilizada
    durante el entrenamiento del modelo.
    """

    validar_datos(datos)

    artefactos = cargar_artefactos()

    features = artefactos["features"]
    frecuencias_categoricas = artefactos["frecuencias_categoricas"]
    categorias_dummies = artefactos["categorias_dummies"]
    medianas = artefactos["medianas"]

    df = pd.DataFrame([datos.copy()])

    # -------------------------------------------------------------------------
    # VARIABLES DERIVADAS
    # -------------------------------------------------------------------------

    df["diferencia_envio"] = (
        df["dias_envio_real"] - df["dias_envio_prog"]
    )

    divisor_dias = df["dias_envio_prog"].replace(0, np.nan)

    df["ratio_envio"] = (
        df["dias_envio_real"] / divisor_dias
    ).fillna(medianas["ratio_envio"])

    df["cumple_plazo"] = (
        df["dias_envio_real"] <= df["dias_envio_prog"]
    ).astype(int)

    divisor_cantidad = df["cantidad"].replace(0, np.nan)

    df["precio_promedio_item"] = (
        df["ventas"] / divisor_cantidad
    ).fillna(medianas["precio_promedio_item"])

    divisor_ventas = df["ventas"].replace(0, np.nan)

    df["margen_total"] = (
        df["ganancia_pedido"] / divisor_ventas
    ).fillna(0)

    df["eficiencia_cliente"] = (
        df["ventas_cliente"] / divisor_cantidad
    ).fillna(medianas["eficiencia_cliente"])

    df["riesgo_por_precio"] = (
        df["riesgo_retraso"].astype(int) * df["precio_base"]
    )

    # -------------------------------------------------------------------------
    # CONVERSIÓN DE VARIABLES BINARIAS
    # -------------------------------------------------------------------------

    columnas_binarias = [
        "riesgo_retraso",
        "es_anomalia",
        "es_outlier",
        "cumple_plazo",
    ]

    for columna in columnas_binarias:
        if columna in df.columns:
            df[columna] = df[columna].astype(int)

    # -------------------------------------------------------------------------
    # ONE-HOT ENCODING
    # -------------------------------------------------------------------------

    for columna, categorias in categorias_dummies.items():
        if columna not in df.columns:
            continue

        valor_actual = df.at[0, columna]

        # En entrenamiento se utilizó drop_first=True,
        # por eso la primera categoría no genera columna.
        for categoria in categorias[1:]:
            nombre_columna = f"{columna}_{categoria}"
            df[nombre_columna] = int(valor_actual == categoria)

        df = df.drop(columns=[columna])

    # -------------------------------------------------------------------------
    # CODIFICACIÓN POR FRECUENCIA
    # -------------------------------------------------------------------------

    for columna, mapa_frecuencias in frecuencias_categoricas.items():
        if columna not in datos:
            raise DatosPrediccionError(
                f"No se recibió el campo categórico '{columna}'."
            )

        valor_actual = datos[columna]

        # Una categoría nueva recibe frecuencia 0.
        df[columna] = float(
            mapa_frecuencias.get(valor_actual, 0.0)
        )

    # -------------------------------------------------------------------------
    # COMPLETAR Y ORDENAR COLUMNAS
    # -------------------------------------------------------------------------

    for columna in features:
        if columna not in df.columns:
            df[columna] = 0.0

    df = df[features].astype(float)

    return df


# =============================================================================
# PREDICCIÓN
# =============================================================================

def predecir_pedido(
    datos: dict[str, Any],
    umbral_alerta: float = 0.65,
) -> dict[str, Any]:
    """
    Realiza una predicción real con el modelo supervisado.

    Args:
        datos:
            Diccionario con los datos requeridos por el modelo.
        umbral_alerta:
            Probabilidad mínima de COMPLETE para no generar alerta.

    Returns:
        Diccionario con estado, probabilidades, alerta, metadata
        y features procesadas.
    """

    if not 0 <= umbral_alerta <= 1:
        raise DatosPrediccionError(
            "El umbral de alerta debe estar entre 0 y 1."
        )

    artefactos = cargar_artefactos()

    modelo = artefactos["modelo"]
    scaler = artefactos["scaler"]
    metadata = artefactos["metadata"]

    fila = construir_fila_modelo(datos)

    requiere_escalado = bool(
        metadata.get("requiere_escalado", False)
    )

    fila_modelo = (
        scaler.transform(fila)
        if requiere_escalado
        else fila
    )

    try:
        probabilidades = modelo.predict_proba(fila_modelo)[0]
    except Exception as error:
        raise ErrorPredictorSupervisado(
            f"El modelo no pudo realizar la predicción: {error}"
        ) from error

    # Durante el entrenamiento:
    # COMPLETE = 1
    # CANCELED = 0
    probabilidad_canceled = float(probabilidades[0])
    probabilidad_complete = float(probabilidades[1])

    estado = (
        "COMPLETE"
        if probabilidad_complete >= 0.5
        else "CANCELED"
    )

    genera_alerta = probabilidad_complete < umbral_alerta

    if probabilidad_complete >= 0.75:
        nivel_riesgo = "Bajo"
    elif probabilidad_complete >= 0.50:
        nivel_riesgo = "Medio"
    else:
        nivel_riesgo = "Alto"

    return {
        "estado": estado,
        "probabilidad_complete": probabilidad_complete,
        "probabilidad_canceled": probabilidad_canceled,
        "porcentaje_complete": round(
            probabilidad_complete * 100, 2
        ),
        "porcentaje_canceled": round(
            probabilidad_canceled * 100, 2
        ),
        "alerta": genera_alerta,
        "nivel_riesgo": nivel_riesgo,
        "umbral_alerta": umbral_alerta,
        "modelo": metadata.get("modelo", "Desconocido"),
        "metricas_test": metadata.get("metricas_test", {}),
        "fecha_entrenamiento": metadata.get(
            "fecha_entrenamiento"
        ),
        "features_procesadas": fila,
    }


# =============================================================================
# FUNCIONES AUXILIARES PARA LA INTERFAZ
# =============================================================================

def obtener_opciones_modelo() -> dict[str, list[Any]]:
    """
    Devuelve categorías reales guardadas durante el entrenamiento.
    Servirá para llenar selectbox en Streamlit.
    """

    artefactos = cargar_artefactos()

    frecuencias = artefactos["frecuencias_categoricas"]
    categorias = artefactos["categorias_dummies"]

    return {
        "modo_envio": categorias.get("modo_envio", []),
        "categoria": list(
            frecuencias.get("categoria", {}).keys()
        ),
        "region_destino": list(
            frecuencias.get("region_destino", {}).keys()
        ),
        "cluster_kmeans": categorias.get(
            "cluster_kmeans", [0]
        ),
        "cluster_dbscan": categorias.get(
            "cluster_dbscan", [-1]
        ),
    }


def obtener_metadata_modelo() -> dict[str, Any]:
    """
    Devuelve la información del modelo entrenado.
    """

    return cargar_artefactos()["metadata"].copy()


def comprobar_motor() -> dict[str, Any]:
    """
    Comprueba que todos los artefactos puedan cargarse correctamente.
    """

    artefactos = cargar_artefactos()

    return {
        "correcto": True,
        "modelo": artefactos["metadata"].get(
            "modelo", "Desconocido"
        ),
        "cantidad_features": len(artefactos["features"]),
        "ruta_artefactos": str(RUTA_BDML),
    }