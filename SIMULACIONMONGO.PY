# prueba_mongo.py
from mongo_logger import asegurar_indices, registrar_prediccion, obtener_historial_predicciones

asegurar_indices()

resultado_ejemplo = {
    "cluster_kmeans": 1, "cluster_etiqueta": "Predominantemente COMPLETE",
    "es_anomalia": False, "es_outlier": False,
    "probabilidad_completado": 0.90, "prediccion": "COMPLETE",
    "alerta_riesgo": False,
}
pedido_ejemplo = {"categoria": "Cleats", "modo_envio": "Standard Class"}

id_doc = registrar_prediccion(resultado_ejemplo, pedido_ejemplo, usuario="prueba")
print("Insertado:", id_doc)
print(obtener_historial_predicciones(usuario="prueba"))