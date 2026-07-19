from sqlalchemy import create_engine

SERVER = "OMEGA-DELL"          # Lo confirmaremos con la consulta anterior
DATABASE = "ML_DATABASE"
DRIVER = "ODBC Driver 18 for SQL Server"

connection_string = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    f"?driver={DRIVER.replace(' ', '+')}"
    "&trusted_connection=yes"
    "&TrustServerCertificate=yes"
)

engine = create_engine(connection_string)