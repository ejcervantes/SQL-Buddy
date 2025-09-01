import requests
import json

# URL del endpoint en tu servidor local
url = "https://sql-buddy-backend-g3cu.onrender.com/metadata"

# Metadatos de la tabla que quieres añadir.
# ¡Asegúrate de que la descripción y el esquema sean detallados!
table_metadata = {
    "table_name": "clientes",
    "schema_info": """
        id INT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE,
        fecha_registro DATE,
        pais VARCHAR(50)
    """,
    "description": "Esta tabla almacena información sobre los clientes de la empresa. Contiene datos personales como nombre y email, la fecha en que se registraron y su país de origen. El campo 'id' es el identificador único para cada cliente."
}

# Cabeceras de la petición
headers = {
    "Content-Type": "application/json"
}

try:
    # Realizar la petición POST
    response = requests.post(url, headers=headers, data=json.dumps(table_metadata))

    # Verificar si la petición fue exitosa (código 200)
    if response.status_code == 200:
        print("✅ ¡Metadatos añadidos con éxito!")
        print("Respuesta del servidor:")
        print(response.json())
    else:
        print(f"❌ Error al añadir metadatos. Código de estado: {response.status_code}")
        print("Respuesta del servidor:")
        print(response.text)

except requests.exceptions.ConnectionError as e:
    print(f"❌ Error de conexión: No se pudo conectar al servidor en {url}")
    print("Asegúrate de que el backend de FastAPI esté en ejecución.")

