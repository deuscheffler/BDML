import pymongo
import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBConnection:
    def __init__(self):
        try:
            # Obtener credenciales del archivo .env
            self.uri = os.getenv('MONGODB_URI')
            self.db_name = os.getenv('DATABASE_NAME')
            self.collection_name = os.getenv('COLLECTION_NAME')
            
            if not self.uri:
                raise ValueError("❌ MONGODB_URI no encontrada en .env")
            
            # Conectar a MongoDB
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            # Verificar conexión
            self.client.admin.command('ping')
            logger.info(f"✅ Conexión exitosa a MongoDB: {self.db_name}")
            
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            raise
    
    def get_dataframe(self, query={}, limit=None):
        """
        Obtiene datos de MongoDB y los convierte a DataFrame.
        
        Args:
            query (dict): Filtro de MongoDB (ej: {"Order Status": "Late delivery"})
            limit (int): Número máximo de documentos a recuperar
        
        Returns:
            pandas.DataFrame: Datos de la colección
        """
        try:
            # Ejecutar consulta
            cursor = self.collection.find(query)
            
            # Aplicar límite si existe
            if limit:
                cursor = cursor.limit(limit)
            
            # Convertir a DataFrame
            df = pd.DataFrame(list(cursor))
            
            # Eliminar columna _id (no es necesaria)
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)
            
            logger.info(f"✅ {len(df)} registros obtenidos de MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error al obtener datos: {e}")
            return None
    
    def get_collection(self):
        """Retorna la colección de MongoDB para operaciones avanzadas"""
        return self.collection
    
    def close(self):
        """Cierra la conexión a MongoDB"""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("🔒 Conexión cerrada")