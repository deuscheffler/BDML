import pandas as pd
from conexion import engine

query = """
SELECT TOP 5 *
FROM [dbo].[dbo.DataCoSupplyChain]
"""

df = pd.read_sql(query, engine)

print(df)