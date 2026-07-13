"""
Servicio para leer el esquema de la base de datos en vivo desde Postgres.

En lugar de mantener a mano un archivo JSON con los esquemas de las tablas,
este módulo se conecta a la base de datos (usando DATABASE_URL) e introspecta
`information_schema` + los comentarios de Postgres para construir, de forma
dinámica, la misma estructura de metadatos que consume el servicio RAG:

    [{ "table_name": str, "schema_info": str, "description": str }, ...]

De esta manera la base de datos es la única fuente de verdad del esquema.
"""

import psycopg2

from app.config import settings


def _format_column_type(col: dict) -> str:
    """Reconstruye un tipo legible tipo DDL a partir de information_schema."""
    data_type = col["data_type"]
    char_len = col["character_maximum_length"]
    num_precision = col["numeric_precision"]
    num_scale = col["numeric_scale"]

    if char_len:
        type_str = f"{data_type.upper()}({char_len})"
    elif data_type in ("numeric", "decimal") and num_precision:
        if num_scale:
            type_str = f"{data_type.upper()}({num_precision}, {num_scale})"
        else:
            type_str = f"{data_type.upper()}({num_precision})"
    else:
        type_str = data_type.upper()

    return type_str


def _build_schema_info(columns: list, primary_keys: set) -> str:
    """Construye una descripción de esquema estilo DDL para una tabla.

    Ejemplo de salida:
        "id INT PRIMARY KEY, nombre VARCHAR(100) NOT NULL, email VARCHAR(100)"
    """
    parts = []
    for col in columns:
        piece = f"{col['column_name']} {_format_column_type(col)}"
        if col["column_name"] in primary_keys:
            piece += " PRIMARY KEY"
        elif col["is_nullable"] == "NO":
            piece += " NOT NULL"
        parts.append(piece)
    return ", ".join(parts)


def fetch_schema_metadata() -> list[dict]:
    """
    Introspecta la base de datos y devuelve los metadatos de todas las tablas
    del esquema configurado (por defecto "public").

    Lanza una excepción si no hay DATABASE_URL o si la conexión falla, para que
    la capa que lo invoca pueda decidir usar el respaldo (metadata_seed.json).
    """
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL no está configurada.")

    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(settings.DATABASE_URL)
    try:
        with conn.cursor() as cur:
            # 1. Columnas de todas las tablas base del esquema.
            cur.execute(
                """
                SELECT c.table_name,
                       c.column_name,
                       c.data_type,
                       c.character_maximum_length,
                       c.numeric_precision,
                       c.numeric_scale,
                       c.is_nullable
                FROM information_schema.columns c
                JOIN information_schema.tables t
                  ON t.table_schema = c.table_schema
                 AND t.table_name = c.table_name
                WHERE c.table_schema = %s
                  AND t.table_type = 'BASE TABLE'
                ORDER BY c.table_name, c.ordinal_position
                """,
                (schema,),
            )
            columns_by_table: dict[str, list] = {}
            for row in cur.fetchall():
                (table_name, column_name, data_type, char_len,
                 num_precision, num_scale, is_nullable) = row
                columns_by_table.setdefault(table_name, []).append({
                    "column_name": column_name,
                    "data_type": data_type,
                    "character_maximum_length": char_len,
                    "numeric_precision": num_precision,
                    "numeric_scale": num_scale,
                    "is_nullable": is_nullable,
                })

            # 2. Claves primarias por tabla.
            cur.execute(
                """
                SELECT tc.table_name, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                  AND tc.table_schema = %s
                """,
                (schema,),
            )
            primary_keys_by_table: dict[str, set] = {}
            for table_name, column_name in cur.fetchall():
                primary_keys_by_table.setdefault(table_name, set()).add(column_name)

            # 3. Comentarios de tabla (COMMENT ON TABLE ...) como descripción.
            cur.execute(
                """
                SELECT c.relname AS table_name,
                       obj_description(c.oid) AS description
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = %s
                  AND c.relkind = 'r'
                """,
                (schema,),
            )
            descriptions_by_table = {
                table_name: description
                for table_name, description in cur.fetchall()
            }
    finally:
        conn.close()

    metadata = []
    for table_name, columns in columns_by_table.items():
        primary_keys = primary_keys_by_table.get(table_name, set())
        description = descriptions_by_table.get(table_name)
        if not description:
            # Si la tabla no tiene un COMMENT en Postgres, generamos una
            # descripción mínima a partir de sus columnas.
            column_names = ", ".join(col["column_name"] for col in columns)
            description = (
                f"Tabla '{table_name}' del esquema '{schema}'. "
                f"Contiene las columnas: {column_names}."
            )

        metadata.append({
            "table_name": table_name,
            "schema_info": _build_schema_info(columns, primary_keys),
            "description": description,
        })

    return metadata
