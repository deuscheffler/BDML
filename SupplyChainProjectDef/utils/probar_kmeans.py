from pathlib import Path

import pandas as pd

from predictor_no_supervisado import (
    comprobar_motor_kmeans,
    predecir_cluster,
)


RUTA_BDML = Path(__file__).resolve().parents[2]
RUTA_CSV = RUTA_BDML / "DataCoSupplyChain_Limpio.csv"


print("Comprobando motor K-Means...")
print(comprobar_motor_kmeans())


df = pd.read_csv(
    RUTA_CSV,
    usecols=[
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
    ],
)

fila_real = df.iloc[0].to_dict()

# Convertir los tipos de NumPy a tipos básicos de Python.
datos_prueba = {
    "dias_envio_real": float(fila_real["dias_envio_real"]),
    "dias_envio_prog": float(fila_real["dias_envio_prog"]),
    "beneficio_pedido": float(fila_real["beneficio_pedido"]),
    "ventas_cliente": float(fila_real["ventas_cliente"]),
    "precio_base": float(fila_real["precio_base"]),
    "margen_ganancia_item": float(
        fila_real["margen_ganancia_item"]
    ),
    "cantidad": float(fila_real["cantidad"]),
    "ventas": float(fila_real["ventas"]),
    "riesgo_retraso": int(fila_real["riesgo_retraso"]),
    "tipo_transaccion": str(fila_real["tipo_transaccion"]),
    "modo_envio": str(fila_real["modo_envio"]),
    "categoria": str(fila_real["categoria"]),
    "region_destino": str(fila_real["region_destino"]),
}

print("\nDatos reales utilizados:")
for clave, valor in datos_prueba.items():
    print(f"{clave}: {valor}")

print("\nResultado K-Means:")
resultado = predecir_cluster(datos_prueba)

for clave, valor in resultado.items():
    print(f"{clave}: {valor}")