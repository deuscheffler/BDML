"""
📊 Módulo de Base de Datos - GDLM

Módulo central para la comunicación entre Streamlit,
SQL Server y MongoDB Atlas.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from urllib.parse import quote_plus
from pathlib import Path

from dotenv import load_dotenv
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CARGA DE VARIABLES DE ENTORNO
# =============================================================================

# Cargar .env desde SupplyChainProjectDef/.env
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)

# =============================================================================
# CONFIGURACIÓN SQL SERVER
# =============================================================================

SQL_SERVER = os.getenv('SQL_SERVER', 'OMEGA-DELL')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'BD_ML_RELACIONAL')
SQL_DRIVER = os.getenv('SQL_DRIVER', 'ODBC Driver 18 for SQL Server')
SQL_TRUSTED_CONNECTION = os.getenv('SQL_TRUSTED_CONNECTION', 'yes')
SQL_TRUST_SERVER_CERTIFICATE = os.getenv('SQL_TRUST_SERVER_CERTIFICATE', 'yes')

# =============================================================================
# CONFIGURACIÓN MONGODB ATLAS
# =============================================================================

MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'supply_chain')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'orders')

# =============================================================================
# VARIABLES GLOBALES (SINGLETON)
# =============================================================================

_sql_engine: Optional[Engine] = None
_mongo_client: Optional[MongoClient] = None
_mongo_collection: Optional[Collection] = None


# =============================================================================
# FUNCIONES DE CONEXIÓN
# =============================================================================

def get_sql_engine() -> Engine:
    """
    Devuelve el engine SQLAlchemy para SQL Server.
    Implementa singleton para reutilizar la conexión.
    
    Returns:
        Engine: Engine de SQLAlchemy configurado
    
    Raises:
        Exception: Si falla la creación del engine
    """
    global _sql_engine
    
    if _sql_engine is not None:
        return _sql_engine
    
    try:
        # Codificar el driver para manejar espacios
        driver_encoded = quote_plus(SQL_DRIVER)
        
        connection_string = (
            f"mssql+pyodbc://@{SQL_SERVER}/{SQL_DATABASE}"
            f"?driver={driver_encoded}"
            f"&trusted_connection={SQL_TRUSTED_CONNECTION}"
            f"&TrustServerCertificate={SQL_TRUST_SERVER_CERTIFICATE}"
        )
        
        _sql_engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        
        logger.info("Engine SQL Server creado correctamente")
        return _sql_engine
        
    except Exception as e:
        logger.error(f"Error al crear el engine SQL Server: {e}")
        raise


def get_mongo_collection() -> Collection:
    """
    Devuelve la colección MongoDB Atlas.
    Implementa singleton para reutilizar la conexión.
    
    Returns:
        Collection: Colección de MongoDB
    
    Raises:
        ValueError: Si MONGODB_URI no está configurada
        Exception: Si falla la conexión
    """
    global _mongo_client, _mongo_collection
    
    if _mongo_collection is not None:
        return _mongo_collection
    
    if not MONGODB_URI:
        raise ValueError(
            "MONGODB_URI no está configurada en el archivo .env"
        )
    
    try:
        _mongo_client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000
        )
        db = _mongo_client[DATABASE_NAME]
        _mongo_collection = db[COLLECTION_NAME]
        
        logger.info(f"Conexión MongoDB establecida: {DATABASE_NAME}.{COLLECTION_NAME}")
        return _mongo_collection
        
    except Exception as e:
        logger.error(f"Error al conectar con MongoDB: {e}")
        raise


# =============================================================================
# FUNCIONES DE PRUEBA DE CONEXIÓN
# =============================================================================

def test_sql_connection() -> Tuple[bool, str]:
    """
    Prueba la conexión a SQL Server.
    
    Returns:
        Tuple[bool, str]: (Éxito, Mensaje)
    """
    try:
        engine = get_sql_engine()
        with engine.connect() as conn:
            # Obtener información del servidor
            result = conn.execute(text("""
                SELECT
                    @@SERVERNAME AS servidor,
                    DB_NAME() AS base_datos
            """))
            row = result.fetchone()
            
            if row:
                server_name = row[0]
                db_name = row[1]
                logger.info(f"Conexión SQL Server exitosa - Servidor: {server_name}, Base: {db_name}")
                return True, f"Conexión exitosa - Servidor: {server_name}, Base: {db_name}"
            else:
                return False, "Respuesta inesperada de SQL Server"
                
    except pyodbc.Error as e:
        error_msg = f"Error de pyodbc: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Error al conectar con SQL Server: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def test_mongo_connection() -> Tuple[bool, str]:
    """
    Prueba la conexión a MongoDB Atlas.
    
    Returns:
        Tuple[bool, str]: (Éxito, Mensaje)
    """
    try:
        if not MONGODB_URI:
            return False, "MONGODB_URI no está configurada"
        
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000
        )
        
        # Probar conexión con ping
        client.admin.command("ping")
        
        logger.info("Conexión MongoDB Atlas exitosa")
        return True, "Conexión MongoDB Atlas exitosa - Ping exitoso"
        
    except ConnectionFailure as e:
        error_msg = f"Error de conexión a MongoDB: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
        
    except ServerSelectionTimeoutError as e:
        error_msg = f"Timeout al conectar con MongoDB: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Error al conectar con MongoDB: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


# =============================================================================
# FUNCIONES AUXILIARES - SQL (CON TRANSACCIÓN)
# =============================================================================

def obtener_o_crear_categoria(
    conn: Any,
    nombre_categoria: str
) -> int:
    """
    Busca o crea una categoría en la tabla Categoria.
    
    Args:
        conn: Conexión SQLAlchemy activa
        nombre_categoria: Nombre de la categoría
        
    Returns:
        int: ID de la categoría
        
    Raises:
        Exception: Si falla la operación
    """
    try:
        # Buscar categoría existente
        query = text("SELECT id_categoria FROM Categoria WHERE nombre_categoria = :nombre")
        result = conn.execute(query, {"nombre": nombre_categoria})
        row = result.fetchone()
        
        if row:
            logger.info(f"Categoría encontrada: {nombre_categoria} (ID: {row[0]})")
            return row[0]
        
        # Insertar nueva categoría
        insert_query = text("""
            INSERT INTO Categoria (nombre_categoria)
            OUTPUT INSERTED.id_categoria
            VALUES (:nombre)
        """)
        
        result = conn.execute(insert_query, {"nombre": nombre_categoria})
        id_categoria = result.scalar()
        logger.info(f"Categoría creada: {nombre_categoria} (ID: {id_categoria})")
        return id_categoria
        
    except Exception as e:
        logger.error(f"Error en obtener_o_crear_categoria: {e}")
        raise


def obtener_o_crear_producto(
    conn: Any,
    nombre_producto: str,
    id_categoria: int
) -> int:
    """
    Busca o crea un producto en la tabla Producto.
    
    Args:
        conn: Conexión SQLAlchemy activa
        nombre_producto: Nombre del producto
        id_categoria: ID de la categoría
        
    Returns:
        int: ID del producto
        
    Raises:
        Exception: Si falla la operación
    """
    try:
        # Buscar producto existente
        query = text("""
            SELECT id_producto FROM Producto 
            WHERE nombre_producto = :nombre AND id_categoria = :id_categoria
        """)
        result = conn.execute(query, {
            "nombre": nombre_producto,
            "id_categoria": id_categoria
        })
        row = result.fetchone()
        
        if row:
            logger.info(f"Producto encontrado: {nombre_producto} (ID: {row[0]})")
            return row[0]
        
        # Insertar nuevo producto
        insert_query = text("""
            INSERT INTO Producto (nombre_producto, id_categoria)
            OUTPUT INSERTED.id_producto
            VALUES (:nombre, :id_categoria)
        """)
        
        result = conn.execute(insert_query, {
            "nombre": nombre_producto,
            "id_categoria": id_categoria
        })
        id_producto = result.scalar()
        logger.info(f"Producto creado: {nombre_producto} (ID: {id_producto})")
        return id_producto
        
    except Exception as e:
        logger.error(f"Error en obtener_o_crear_producto: {e}")
        raise


def obtener_o_crear_destino(
    conn: Any,
    pais_destino: Optional[str],
    estado_destino: Optional[str],
    ciudad_destino: Optional[str],
    region_destino: Optional[str]
) -> int:
    """
    Busca o crea un destino en la tabla Destino.
    
    Args:
        conn: Conexión SQLAlchemy activa
        pais_destino: País de destino
        estado_destino: Estado/Provincia de destino
        ciudad_destino: Ciudad de destino
        region_destino: Región de destino
        
    Returns:
        int: ID del destino
        
    Raises:
        Exception: Si falla la operación
    """
    try:
        # Buscar destino existente
        query = text("""
            SELECT id_destino FROM Destino 
            WHERE (pais_destino = :pais OR (pais_destino IS NULL AND :pais IS NULL))
            AND (estado_destino = :estado OR (estado_destino IS NULL AND :estado IS NULL))
            AND (ciudad_destino = :ciudad OR (ciudad_destino IS NULL AND :ciudad IS NULL))
            AND (region_destino = :region OR (region_destino IS NULL AND :region IS NULL))
        """)
        result = conn.execute(query, {
            "pais": pais_destino,
            "estado": estado_destino,
            "ciudad": ciudad_destino,
            "region": region_destino
        })
        row = result.fetchone()
        
        if row:
            logger.info(f"Destino encontrado (ID: {row[0]})")
            return row[0]
        
        # Insertar nuevo destino
        insert_query = text("""
            INSERT INTO Destino (pais_destino, estado_destino, ciudad_destino, region_destino)
            OUTPUT INSERTED.id_destino
            VALUES (:pais, :estado, :ciudad, :region)
        """)
        
        result = conn.execute(insert_query, {
            "pais": pais_destino,
            "estado": estado_destino,
            "ciudad": ciudad_destino,
            "region": region_destino
        })
        id_destino = result.scalar()
        logger.info(f"Destino creado (ID: {id_destino})")
        return id_destino
        
    except Exception as e:
        logger.error(f"Error en obtener_o_crear_destino: {e}")
        raise


def obtener_o_crear_ubicacion(
    conn: Any,
    pais_cliente: str,
    ciudad_cliente: str,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None
) -> int:
    """
    Busca o crea una ubicación de cliente en la tabla UbicacionCliente.
    
    Args:
        conn: Conexión SQLAlchemy activa
        pais_cliente: País del cliente
        ciudad_cliente: Ciudad del cliente
        latitud: Latitud (opcional)
        longitud: Longitud (opcional)
        
    Returns:
        int: ID de la ubicación
        
    Raises:
        Exception: Si falla la operación
    """
    try:
        # Buscar ubicación existente
        query = text("""
            SELECT id_ubicacion_cliente FROM UbicacionCliente 
            WHERE pais_cliente = :pais 
            AND ciudad_cliente = :ciudad
            AND (latitud = :latitud OR (latitud IS NULL AND :latitud IS NULL))
            AND (longitud = :longitud OR (longitud IS NULL AND :longitud IS NULL))
        """)
        result = conn.execute(query, {
            "pais": pais_cliente,
            "ciudad": ciudad_cliente,
            "latitud": latitud,
            "longitud": longitud
        })
        row = result.fetchone()
        
        if row:
            logger.info(f"Ubicación encontrada: {pais_cliente}, {ciudad_cliente} (ID: {row[0]})")
            return row[0]
        
        # Insertar nueva ubicación
        insert_query = text("""
            INSERT INTO UbicacionCliente (pais_cliente, ciudad_cliente, latitud, longitud)
            OUTPUT INSERTED.id_ubicacion_cliente
            VALUES (:pais, :ciudad, :latitud, :longitud)
        """)
        
        result = conn.execute(insert_query, {
            "pais": pais_cliente,
            "ciudad": ciudad_cliente,
            "latitud": latitud,
            "longitud": longitud
        })
        id_ubicacion = result.scalar()
        logger.info(f"Ubicación creada: {pais_cliente}, {ciudad_cliente} (ID: {id_ubicacion})")
        return id_ubicacion
        
    except Exception as e:
        logger.error(f"Error en obtener_o_crear_ubicacion: {e}")
        raise


# =============================================================================
# FUNCIÓN PRINCIPAL - GUARDAR PEDIDO
# =============================================================================

def guardar_pedido_sql(
    id_raw: int,
    order_id: str,
    customer_id: str,
    fecha_pedido: datetime,
    fecha_envio: datetime,
    tipo_transaccion: Optional[str],
    estado_pedido: Optional[str],
    estado_entrega: Optional[str],
    modo_envio: Optional[str],
    dias_envio_real: Optional[int],
    dias_envio_prog: Optional[int],
    precio_producto: Optional[float],
    precio_base: Optional[float],
    latitud: Optional[float],
    longitud: Optional[float],
    beneficio_pedido: Optional[float],
    ventas_cliente: Optional[float],
    margen_ganancia_item: Optional[float],
    cantidad: Optional[int],
    ventas: Optional[float],
    total_item: Optional[float],
    ganancia_pedido: Optional[float],
    riesgo_retraso: Optional[bool],
    pais_destino: Optional[str],
    estado_destino: Optional[str],
    ciudad_destino: Optional[str],
    region_destino: Optional[str],
    pais_cliente: str,
    ciudad_cliente: str,
    categoria: str,
    producto: str
) -> int:
    """
    Guarda un pedido completo en SQL Server dentro de una transacción.
    
    Esta función orquesta todas las operaciones de búsqueda/creación
    de las tablas relacionadas y finalmente inserta el pedido.
    
    NOTA: id_raw debe resolverse antes de integrar el guardado desde Streamlit,
    porque los pedidos creados por la aplicación no provienen necesariamente
    de DataCoSupplyChain_RAW.
    
    Args:
        id_raw: ID del registro original (NOT NULL)
        order_id: Identificador único del pedido (para MongoDB)
        customer_id: Identificador único del cliente (para MongoDB)
        fecha_pedido: Fecha del pedido
        fecha_envio: Fecha de envío
        tipo_transaccion: Tipo de transacción
        estado_pedido: Estado del pedido
        estado_entrega: Estado de entrega
        modo_envio: Modo de envío
        dias_envio_real: Días reales de envío
        dias_envio_prog: Días programados de envío
        precio_producto: Precio del producto
        precio_base: Precio base
        latitud: Latitud
        longitud: Longitud
        beneficio_pedido: Beneficio del pedido
        ventas_cliente: Ventas históricas del cliente
        margen_ganancia_item: Margen de ganancia por item
        cantidad: Cantidad
        ventas: Ventas totales
        total_item: Total por item
        ganancia_pedido: Ganancia del pedido
        riesgo_retraso: Riesgo de retraso
        pais_destino: País de destino
        estado_destino: Estado/Provincia de destino
        ciudad_destino: Ciudad de destino
        region_destino: Región de destino
        pais_cliente: País del cliente
        ciudad_cliente: Ciudad del cliente
        categoria: Categoría del producto
        producto: Nombre del producto
        
    Returns:
        int: ID del pedido generado
        
    Raises:
        Exception: Si falla alguna operación
    """
    engine = get_sql_engine()
    
    try:
        with engine.begin() as conn:
            # Obtener o crear las entidades relacionadas
            id_categoria = obtener_o_crear_categoria(conn, categoria)
            id_producto = obtener_o_crear_producto(conn, producto, id_categoria)
            id_destino = obtener_o_crear_destino(
                conn,
                pais_destino,
                estado_destino,
                ciudad_destino,
                region_destino
            )
            id_ubicacion = obtener_o_crear_ubicacion(
                conn,
                pais_cliente,
                ciudad_cliente,
                latitud,
                longitud
            )
            
            # Insertar el pedido
            insert_query = text("""
                INSERT INTO Pedido (
                    id_raw,
                    fecha_pedido,
                    fecha_envio,
                    tipo_transaccion,
                    estado_pedido,
                    estado_entrega,
                    modo_envio,
                    dias_envio_real,
                    dias_envio_prog,
                    precio_producto,
                    precio_base,
                    latitud,
                    longitud,
                    beneficio_pedido,
                    ventas_cliente,
                    margen_ganancia_item,
                    cantidad,
                    ventas,
                    total_item,
                    ganancia_pedido,
                    riesgo_retraso,
                    id_producto,
                    id_destino,
                    id_ubicacion_cliente
                )
                OUTPUT INSERTED.id_pedido
                VALUES (
                    :id_raw,
                    :fecha_pedido,
                    :fecha_envio,
                    :tipo_transaccion,
                    :estado_pedido,
                    :estado_entrega,
                    :modo_envio,
                    :dias_envio_real,
                    :dias_envio_prog,
                    :precio_producto,
                    :precio_base,
                    :latitud,
                    :longitud,
                    :beneficio_pedido,
                    :ventas_cliente,
                    :margen_ganancia_item,
                    :cantidad,
                    :ventas,
                    :total_item,
                    :ganancia_pedido,
                    :riesgo_retraso,
                    :id_producto,
                    :id_destino,
                    :id_ubicacion
                )
            """)
            
            result = conn.execute(insert_query, {
                "id_raw": id_raw,
                "fecha_pedido": fecha_pedido,
                "fecha_envio": fecha_envio,
                "tipo_transaccion": tipo_transaccion,
                "estado_pedido": estado_pedido,
                "estado_entrega": estado_entrega,
                "modo_envio": modo_envio,
                "dias_envio_real": dias_envio_real,
                "dias_envio_prog": dias_envio_prog,
                "precio_producto": precio_producto,
                "precio_base": precio_base,
                "latitud": latitud,
                "longitud": longitud,
                "beneficio_pedido": beneficio_pedido,
                "ventas_cliente": ventas_cliente,
                "margen_ganancia_item": margen_ganancia_item,
                "cantidad": cantidad,
                "ventas": ventas,
                "total_item": total_item,
                "ganancia_pedido": ganancia_pedido,
                "riesgo_retraso": riesgo_retraso,
                "id_producto": id_producto,
                "id_destino": id_destino,
                "id_ubicacion": id_ubicacion
            })
            
            id_pedido = result.scalar()
            logger.info(f"Pedido guardado en SQL Server (ID: {id_pedido}, ID Raw: {id_raw})")
            
            # Guardar también los IDs en las variables de logging
            logger.info(f"Order ID: {order_id}, Customer ID: {customer_id}")
            
            return id_pedido
            
    except Exception as e:
        logger.error(f"Error en guardar_pedido_sql: {e}")
        raise


# =============================================================================
# FUNCIONES - MONGODB
# =============================================================================

def guardar_prediccion_mongo(
    id_pedido_sql: int,
    order_id: str,
    customer_id: str,
    prediccion: Dict[str, Any],
    cluster: Dict[str, Any]
) -> str:
    """
    Guarda la predicción y el cluster en MongoDB Atlas.
    
    Args:
        id_pedido_sql: ID del pedido en SQL Server
        order_id: Identificador único del pedido
        customer_id: Identificador único del cliente
        prediccion: Diccionario con los resultados de la predicción supervisada
        cluster: Diccionario con los resultados del cluster K-Means
        
    Returns:
        str: ID del documento insertado en MongoDB
        
    Raises:
        Exception: Si falla la inserción
    """
    try:
        collection = get_mongo_collection()
        
        documento = {
            "id_pedido_sql": id_pedido_sql,
            "order_id": order_id,
            "customer_id": customer_id,
            "prediccion": {
                "estado": prediccion.get("estado"),
                "probabilidad_complete": float(prediccion.get("probabilidad_complete", 0)),
                "probabilidad_canceled": float(prediccion.get("probabilidad_canceled", 0)),
                "porcentaje_complete": float(prediccion.get("porcentaje_complete", 0)),
                "porcentaje_canceled": float(prediccion.get("porcentaje_canceled", 0)),
                "nivel_riesgo": prediccion.get("nivel_riesgo"),
                "alerta": bool(prediccion.get("alerta", False))
            },
            "cluster": {
                "cluster": cluster.get("cluster"),
                "perfil": cluster.get("perfil", {}).get("nombre"),
                "perfil_completo": cluster.get("perfil", {}),
                "anomalia": bool(cluster.get("es_anomalia", False)),
                "distancia_centroide": float(cluster.get("distancia_centroide", 0)),
                "umbral_anomalias": float(cluster.get("umbral_anomalias", 0))
            },
            "fecha": datetime.now(timezone.utc)
        }
        
        result = collection.insert_one(documento)
        logger.info(f"Predicción guardada en MongoDB (ID: {result.inserted_id})")
        return str(result.inserted_id)
        
    except Exception as e:
        logger.error(f"Error en guardar_prediccion_mongo: {e}")
        raise


# =============================================================================
# FUNCIÓN DE PRUEBA COMPLETA
# =============================================================================

def test_connections() -> Dict[str, Any]:
    """
    Prueba todas las conexiones y retorna un resumen.
    
    Returns:
        Dict[str, Any]: Diccionario con los resultados de las pruebas
    """
    results = {
        "sql_server": {"success": False, "message": "No probado"},
        "mongodb": {"success": False, "message": "No probado"},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Probar SQL Server
    sql_success, sql_message = test_sql_connection()
    results["sql_server"]["success"] = sql_success
    results["sql_server"]["message"] = sql_message
    
    # Probar MongoDB
    mongo_success, mongo_message = test_mongo_connection()
    results["mongodb"]["success"] = mongo_success
    results["mongodb"]["message"] = mongo_message
    
    return results