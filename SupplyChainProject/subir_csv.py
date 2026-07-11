import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Conectar a MongoDB Atlas
uri = os.getenv('MONGODB_URI')
db_name = os.getenv('DATABASE_NAME')
collection_name = os.getenv('COLLECTION_NAME')

print("📁 Conectando a MongoDB Atlas...")
client = MongoClient(uri)
db = client[db_name]
collection = db[collection_name]

# Limpiar colección
print("🧹 Limpiando colección existente...")
collection.delete_many({})

# Cargar tu CSV - CON ENCODING CORRECTO
print("📁 Cargando archivo CSV...")

# Probar diferentes codificaciones
try:
    df = pd.read_csv('data/DataCoSupplyChainDataset.csv', encoding='latin-1')
    print("✅ Usando encoding: latin-1")
except:
    try:
        df = pd.read_csv('data/DataCoSupplyChainDataset.csv', encoding='utf-8-sig')
        print("✅ Usando encoding: utf-8-sig")
    except:
        df = pd.read_csv('data/DataCoSupplyChainDataset.csv', encoding='cp1252')
        print("✅ Usando encoding: cp1252")

print(f"✅ {len(df)} filas cargadas")

# Mostrar primeras columnas para verificar
print(f"📋 Columnas: {list(df.columns)[:5]}...")

# Convertir a diccionario
data = df.to_dict('records')

# Subir a MongoDB
print("📤 Subiendo datos a MongoDB Atlas...")
result = collection.insert_many(data)

print(f"✅ {len(result.inserted_ids)} documentos subidos exitosamente")
print("🎉 ¡Datos subidos!")

# Verificar
count = collection.count_documents({})
print(f"📊 Total de documentos en la colección: {count}")