import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Obtener URI
uri = os.getenv('MONGODB_URI')

print("Probando conexión a MongoDB Atlas")

try:
    # Conectar
    client = MongoClient(uri)
    client.admin.command('ping')
    print(" Conexión exitosa a MongoDB Atlas")
    
    # Ver datos
    db = client[os.getenv('DATABASE_NAME')]
    collection = db[os.getenv('COLLECTION_NAME')]
    count = collection.count_documents({})
    print(f"Total de documentos en la colección: {count}")
    
    # Mostrar si hay datos
    if count > 0:
        sample = collection.find().limit(1)
        for doc in sample:
            print("\nDATA BASE")
            print(f"   {list(doc.keys())}")
    
except Exception as e:
    print(f"Error: {e}")