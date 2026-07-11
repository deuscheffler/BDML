from predictor_supervisado import (
    comprobar_motor,
    obtener_opciones_modelo,
)

print("Comprobando motor...")
print(comprobar_motor())

print("\nOpciones disponibles:")
opciones = obtener_opciones_modelo()

for nombre, valores in opciones.items():
    print(f"{nombre}: {len(valores)} opciones")
    print(valores[:5])