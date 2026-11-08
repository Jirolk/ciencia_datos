"""Verifica los datos cargados en DuckDB con consultas SQL básicas."""

import duckdb

DB = "data.duckdb"


def consultar(query):
    """Ejecuta una consulta SQL en DuckDB y devuelve todas las filas."""
    con = duckdb.connect(DB, read_only=True)
    try:
        return con.sql(query).fetchall()
    finally:
        con.close()


if __name__ == "__main__":
    total = consultar("select count(*) from jsonplaceholder.users")[0][0]
    print(f"Usuarios cargados: {total}")

    query = """
        select id, name, address__city 
        from jsonplaceholder.users 
        order by id 
        limit 3
    """
    print("Primeros 3 usuarios (id, nombre, ciudad):")
    for fila in consultar(query):
        print(fila)

    print("Columnas que creó dlt:")
    for fila in consultar("describe jsonplaceholder.users"):
        print(f" {fila[0]}: {fila[1]}")
