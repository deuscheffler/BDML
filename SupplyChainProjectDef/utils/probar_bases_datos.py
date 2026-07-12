"""
Prueba de conexiones - GDLM

Verifica SQL Server y MongoDB Atlas sin insertar,
actualizar ni eliminar registros.
"""

from database_nuevo import (
    ENV_PATH,
    MONGODB_URI,
    test_sql_connection,
    test_mongo_connection,
)


def main():
    print("=" * 60)
    print("DEPURACIÓN DEL .env")
    print("=" * 60)
    print("Ruta del .env:", ENV_PATH)
    print("¿Existe?:", ENV_PATH.exists())
    print("Mongo URI cargada:", bool(MONGODB_URI))

    print("\n" + "=" * 60)
    print("PRUEBA DE CONEXIONES - GDLM")
    print("=" * 60)

    print("\nSQL Server")
    sql_ok, sql_mensaje = test_sql_connection()
    print(f"{'✅' if sql_ok else '❌'} {sql_mensaje}")

    print("\nMongoDB Atlas")
    mongo_ok, mongo_mensaje = test_mongo_connection()
    print(f"{'✅' if mongo_ok else '❌'} {mongo_mensaje}")


if __name__ == "__main__":
    main()