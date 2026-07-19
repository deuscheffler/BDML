import pandas as pd
from conexion import engine

try:
    df = pd.read_sql(
        "SELECT TOP 5 * FROM dbo.DataCoSupplyChain",
        engine
    )

    print("Conexión exitosa.\n")
    print(df)

except Exception as e:
    print("Error al conectar:")
    print(e)