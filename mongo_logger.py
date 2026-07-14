"""
mongo_logger.py
================
Módulo de logging y versionado en MongoDB. Complementa a SQL Server dentro
de la arquitectura híbrida del proyecto:

    - SQL Server  -> gobierna los datos relacionales (pedidos, catálogo,
                      resultados de ML persistidos, auditoría a nivel de fila).
    - MongoDB     -> log de cada predicción hecha desde Streamlit, e
                      historial de versiones de modelo en cada reentrenamiento.
                      Datos semi-estructurados, sin esquema fijo, de alto
                      volumen de escritura -> encajan mejor aquí que en una
                      tabla relacional nueva.

CONFIGURACIÓN
-------------
Ajusta MONGO_URI según tu despliegue (variable de entorno recomendada en
producción; el valor por defecto es solo para desarrollo local):

    MongoDB local:
        mongodb://localhost:27017/

    MongoDB local con autenticación:
        mongodb://<usuario>:<password>@localhost:27017/?authSource=admin

    MongoDB Atlas (nube):
        mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/

No dejes credenciales reales escritas en este archivo si lo vas a subir a
un repositorio: usa `os.environ["MONGO_URI"]` o `st.secrets["mongo_uri"]`.

Uso típico dentro de app.py, después de una predicción:

    from mongo_logger import asegurar_indices, registrar_prediccion

    asegurar_indices()  # una vez al arrancar la app

    resultado = predecir_estado_pedido(pedido, ...)  # load_models.py
    registrar_prediccion(
        resultado=resultado,
        pedido_input=pedido,
        usuario=st.session_state.get("usuario", "anonimo"),
        id_pedido=None,  # None porque fue un pedido hipotético del formulario
        modelo_version=metadata_sup["fecha_entrenamiento"],
    )
"""

import os
from datetime import datetime, timezone

import streamlit as st
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://app_streamlit:Grupodelamuerte2@localhost:27017/?authSource=BD_ML_LOGS",
)
MONGO_DB_NAME = "BD_ML_LOGS"

COLECCION_PREDICCIONES = "predicciones"
COLECCION_HISTORIAL_MODELOS = "historial_modelos"

# Antigüedad máxima de un log de predicción antes de expirar automáticamente
# vía índice TTL de MongoDB. None = no expiran nunca.
DIAS_RETENCION_PREDICCIONES = 180


# ============================================================================
# CONEXIÓN (cacheada — una sola conexión por sesión de Streamlit)
# ============================================================================
@st.cache_resource(show_spinner="Conectando a MongoDB...")
def conectar_mongo() -> MongoClient:
    cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    cliente.admin.command("ping")  # falla rápido si Mongo no está disponible
    return cliente


def obtener_db(cliente: MongoClient = None):
    cliente = cliente or conectar_mongo()
    return cliente[MONGO_DB_NAME]


# ============================================================================
# ÍNDICES (idempotente — se puede llamar en cada arranque de la app)
# ============================================================================
def asegurar_indices(cliente: MongoClient = None) -> None:
    """
    Crea los índices necesarios si no existen todavía. create_index() es
    idempotente en MongoDB, así que es seguro llamar esto en cada arranque
    de la app sin duplicar índices.
    """
    db = obtener_db(cliente)

    # --- Colección de predicciones ---
    coleccion = db[COLECCION_PREDICCIONES]
    coleccion.create_index([("id_pedido", ASCENDING)])
    coleccion.create_index([("fecha_prediccion", DESCENDING)])
    coleccion.create_index([("usuario", ASCENDING)])
    coleccion.create_index([("prediccion", ASCENDING)])

    if DIAS_RETENCION_PREDICCIONES is not None:
        # Índice TTL: MongoDB borra automáticamente los documentos cuyo
        # 'fecha_prediccion' supera esta antigüedad. Útil para no acumular
        # logs indefinidamente en un proyecto de clase.
        coleccion.create_index(
            [("fecha_prediccion", ASCENDING)],
            expireAfterSeconds=DIAS_RETENCION_PREDICCIONES * 86400,
            name="ttl_fecha_prediccion",
        )

    # --- Colección de historial de modelos ---
    historial = db[COLECCION_HISTORIAL_MODELOS]
    historial.create_index([("fecha_registro", DESCENDING)])
    historial.create_index([("tipo_modelo", ASCENDING)])


# ============================================================================
# LOG DE PREDICCIONES
# ============================================================================
def registrar_prediccion(
    resultado: dict,
    pedido_input: dict,
    usuario: str = "anonimo",
    id_pedido: int | None = None,
    modelo_version: str | None = None,
    cliente: MongoClient = None,
) -> str | None:
    """
    Guarda una predicción hecha desde Streamlit, ya sea de un pedido
    hipotético (formulario) o de uno existente en la BD.

    resultado: el dict que retorna predecir_estado_pedido() o
        predecir_estado_pedido_existente() en load_models.py.
    pedido_input: los datos crudos usados para predecir (permite auditar
        exactamente qué se capturó, sin depender de que exista en SQL).
    id_pedido: el id_pedido real si ya existía en SQL Server; None si fue
        un pedido hipotético del formulario (así distinguimos ambos casos
        sin necesitar dos colecciones separadas).
    modelo_version: 'fecha_entrenamiento' del modelo usado, para poder
        saber después con qué versión se hizo cada predicción histórica.

    Retorna el _id del documento insertado (como string) o None si falló.
    Un fallo aquí NUNCA debe interrumpir el flujo de la app: la predicción
    ya se calculó y se le debe mostrar al usuario aunque el log falle.
    """
    documento = {
        "id_pedido": id_pedido,
        "es_pedido_hipotetico": id_pedido is None,
        "fecha_prediccion": datetime.now(timezone.utc),
        "usuario": usuario,
        "modelo_version": modelo_version,
        "input": pedido_input,
        "cluster_kmeans": resultado.get("cluster_kmeans"),
        "cluster_etiqueta": resultado.get("cluster_etiqueta"),
        "es_anomalia": resultado.get("es_anomalia"),
        "es_outlier": resultado.get("es_outlier"),
        "probabilidad_completado": resultado.get("probabilidad_completado"),
        "prediccion": resultado.get("prediccion"),
        "alerta_riesgo": resultado.get("alerta_riesgo"),
    }

    try:
        db = obtener_db(cliente)
        insercion = db[COLECCION_PREDICCIONES].insert_one(documento)
        return str(insercion.inserted_id)
    except PyMongoError as e:
        print(f"⚠️ No se pudo registrar la predicción en MongoDB: {e}")
        return None


def obtener_historial_predicciones(
    id_pedido: int | None = None,
    usuario: str | None = None,
    limite: int = 50,
    cliente: MongoClient = None,
) -> list[dict]:
    """
    Consulta el historial de predicciones, más recientes primero.
    Filtra por id_pedido y/o usuario si se especifican.
    """
    filtro = {}
    if id_pedido is not None:
        filtro["id_pedido"] = id_pedido
    if usuario is not None:
        filtro["usuario"] = usuario

    db = obtener_db(cliente)
    cursor = (
        db[COLECCION_PREDICCIONES]
        .find(filtro)
        .sort("fecha_prediccion", DESCENDING)
        .limit(limite)
    )
    return list(cursor)


# ============================================================================
# HISTORIAL DE VERSIONES DE MODELO
# ============================================================================
def registrar_version_modelo(
    tipo_modelo: str,
    metadata: dict,
    cliente: MongoClient = None,
) -> str | None:
    """
    Guarda una copia de la metadata de entrenamiento (metadata_kmeans.json
    o metadata_modelo.json) como documento versionado cada vez que se
    reentrena. Permite comparar métricas entre corridas sin depender de
    revisar archivos JSON sueltos en disco.

    tipo_modelo: 'kmeans' o 'supervisado'.
    """
    documento = {
        "tipo_modelo": tipo_modelo,
        "fecha_registro": datetime.now(timezone.utc),
        **metadata,
    }
    try:
        db = obtener_db(cliente)
        insercion = db[COLECCION_HISTORIAL_MODELOS].insert_one(documento)
        return str(insercion.inserted_id)
    except PyMongoError as e:
        print(f"⚠️ No se pudo registrar la versión del modelo en MongoDB: {e}")
        return None


def obtener_historial_modelos(
    tipo_modelo: str | None = None,
    limite: int = 20,
    cliente: MongoClient = None,
) -> list[dict]:
    """Consulta el historial de versiones de modelo, más reciente primero."""
    filtro = {"tipo_modelo": tipo_modelo} if tipo_modelo else {}
    db = obtener_db(cliente)
    cursor = (
        db[COLECCION_HISTORIAL_MODELOS]
        .find(filtro)
        .sort("fecha_registro", DESCENDING)
        .limit(limite)
    )
    return list(cursor)
