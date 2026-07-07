import sqlalchemy
import pyodbc
from sqlalchemy import create_engine

SERVER = "localhost"          # Cambia si tu instancia tiene otro nombre
DATABASE = "ML_DATABASE"

engine = create_engine(
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)



print(pyodbc.drivers())