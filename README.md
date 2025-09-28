# API Analítica de Ciencia de Datos

## Resumen General

Esta API basada en FastAPI proporciona endpoints de análisis de datos para procesar y analizar datos empresariales almacenados en AWS S3. La API se especializa en procesar datos de la empresa Primac de varias fuentes de bases de datos (Cassandra, MySQL y PostgreSQL) que han sido ingeridas en S3.

## Características

- **Analíticas de Reclamos**: Análisis estadístico de datos de reclamos de seguros
- **Analíticas de Pagos**: Análisis de datos de pagos financieros y promedios
- **Analíticas de Auditoría**: Reportes de auditoría de transacciones y análisis de servicios principales
- **Integración en la Nube**: Integración directa con AWS S3 para procesamiento de datos
- **Alto Rendimiento**: Construida con FastAPI para rendimiento óptimo
- **Contenerizada**: Contenedor Docker listo para despliegue

## Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Fuentes de Datos│    │  Bucket AWS S3  │    │  API Analytics  │
│                 │───▶│                 │───▶│                 │
│ Cassandra/MySQL │    │ Archivos CSV    │    │ Servicio FastAPI│
│ PostgreSQL      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Endpoints de la API

### 1. Estadísticas de Reclamos
**GET** `/claims/stats`

- **Descripción**: Devuelve análisis estadístico de reclamos de seguros agrupados por estado
- **Fuente de Datos**: `cassandra/reclamos/reclamos.csv`
- **Respuesta**: Objeto JSON con conteos de estados de reclamos

**Ejemplo de Respuesta:**
```json
{
  "aprobado": 150,
  "pendiente": 75,
  "rechazado": 25,
  "en_revision": 50
}
```

### 2. Promedios de Pagos
**GET** `/payments/avg`

- **Descripción**: Calcula el monto promedio de pagos de los datos de pagos
- **Fuente de Datos**: `cassandra/pagos/pagos.csv`
- **Respuesta**: Objeto JSON con el monto promedio de pagos

**Ejemplo de Respuesta:**
```json
{
  "avg_monto": 1250.75
}
```

### 3. Principales Servicios de Auditoría
**GET** `/audits/top-services`

- **Descripción**: Devuelve los 5 servicios más utilizados de las auditorías de transacciones
- **Fuente de Datos**: `cassandra/transaction_audit/transaction_audit.csv`
- **Respuesta**: Objeto JSON con nombres de servicios y sus conteos de uso

**Ejemplo de Respuesta:**
```json
{
  "servicio_pagos": 342,
  "autenticacion_usuario": 298,
  "respaldo_datos": 187,
  "servicio_notificaciones": 156,
  "generacion_reportes": 134
}
```

## Variables de Entorno

La API requiere las siguientes variables de entorno para la integración con AWS S3:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `AWS_ACCESS_KEY_ID` | ID de Clave de Acceso de AWS | Requerido |
| `AWS_SECRET_ACCESS_KEY` | Clave de Acceso Secreta de AWS | Requerido |
| `AWS_SESSION_TOKEN` | Token de Sesión de AWS (si usa credenciales temporales) | Opcional |
| `AWS_DEFAULT_REGION` | Región de AWS | `us-east-1` |
| `S3_BUCKET` | Nombre del bucket S3 que contiene los datos | `nombre-del-bucket` |

## Instalación y Configuración

### Prerequisitos

- Python 3.11+
- Docker (opcional)
- Credenciales de AWS con acceso a S3
- Acceso al bucket S3 que contiene los archivos de datos CSV

### Configuración de Desarrollo Local

1. **Clonar y navegar al proyecto:**
   ```bash
   cd API-Analytic-Primac
   ```

2. **Crear un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```bash
   export AWS_ACCESS_KEY_ID="tu_clave_de_acceso"
   export AWS_SECRET_ACCESS_KEY="tu_clave_secreta"
   export AWS_DEFAULT_REGION="us-east-1"
   export S3_BUCKET="nombre-del-bucket"
   ```

5. **Ejecutar la aplicación:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Configuración con Docker

1. **Construir la imagen de Docker:**
   ```bash
   docker build -t API-Analytic-Primac .
   ```

2. **Ejecutar con Docker:**
   ```bash
   docker run -p 8000:8000 \
     -e AWS_ACCESS_KEY_ID="tu_clave_de_acceso" \
     -e AWS_SECRET_ACCESS_KEY="tu_clave_secreta" \
     -e AWS_DEFAULT_REGION="us-east-1" \
     -e S3_BUCKET="nombre-del-bucket" \
     API-Analytic-Primac
   ```

### Configuración con Docker Compose

Desde el directorio raíz del proyecto:

1. **Crear un archivo `.env` con tus credenciales de AWS:**
   ```env
   AWS_ACCESS_KEY_ID=tu_clave_de_acceso
   AWS_SECRET_ACCESS_KEY=tu_clave_secreta
   AWS_DEFAULT_REGION=us-east-1
   S3_BUCKET=nombre-del-bucket
   ```

2. **Iniciar el servicio:**
   ```bash
   docker-compose up API-Analytic-Primac
   ```

## Ejemplos de Uso

### Usando curl

```bash
# Obtener estadísticas de reclamos
curl http://localhost:8000/claims/stats

# Obtener promedios de pagos
curl http://localhost:8000/payments/avg

# Obtener principales servicios de auditoría
curl http://localhost:8000/audits/top-services
```

### Usando Python requests

```python
import requests

base_url = "http://localhost:8000"

# Obtener estadísticas de reclamos
response = requests.get(f"{base_url}/claims/stats")
print(response.json())

# Obtener promedios de pagos
response = requests.get(f"{base_url}/payments/avg")
print(response.json())

# Obtener principales servicios de auditoría
response = requests.get(f"{base_url}/audits/top-services")
print(response.json())
```

## Documentación de la API

Una vez que la API esté ejecutándose, puedes acceder a:

- **Documentación interactiva de la API (Swagger UI)**: `http://localhost:8000/docs`
- **Documentación alternativa de la API (ReDoc)**: `http://localhost:8000/redoc`
- **Esquema OpenAPI**: `http://localhost:8000/openapi.json`

## Fuentes de Datos y Esquema

### Estructura S3 Esperada

```
s3://nombre-del-bucket/
├── cassandra/
│   ├── reclamos/
│   │   └── reclamos.csv
│   ├── pagos/
│   │   └── pagos.csv
│   └── transaction_audit/
│       └── transaction_audit.csv
```

## Despliegue

### Ejemplo de Despliegue en AWS ECS

```bash
# Construir y subir a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t API-Analytic-Primac .
docker tag API-Analytic-Primac:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/API-Analytic-Primac:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/API-Analytic-Primac:latest
```

## Dependencias

- **FastAPI 0.100.0**: Framework web moderno para construir APIs
- **Uvicorn 0.23.2**: Implementación de servidor ASGI
- **Boto3 1.26.150**: SDK de AWS para Python
- **Pandas 2.1.1**: Biblioteca de manipulación y análisis de datos
- **NumPy 1.26.0**: Biblioteca de computación numérica
- **python-dotenv 1.1.1**: Gestión de variables de entorno

## Solución de Problemas

### Problemas Comunes

1. **Error de Credenciales de AWS**
   - Asegúrate de que las credenciales de AWS estén configuradas correctamente
   - Verifica los permisos de IAM para acceso a S3

2. **Error de Acceso a S3**
   - Verifica el nombre del bucket y la región
   - Verifica si los archivos CSV existen en las rutas esperadas de S3

3. **Error de Procesamiento de Datos**
   - Verifica el formato de archivos CSV y nombres de columnas
   - Verifica archivos vacíos o corruptos

### Verificación de Estado

Añadir un endpoint de verificación de estado visitando: `http://localhost:8000/docs`

## Contribuciones

1. Hacer fork del repositorio
2. Crear una rama de característica
3. Hacer tus cambios
4. Añadir pruebas si es aplicable
5. Enviar un pull request

## Licencia

Este proyecto está licenciado bajo los términos especificados en el archivo LICENSE.

## Soporte

Para soporte y preguntas, por favor contacta al equipo de desarrollo o crea un issue en el repositorio del proyecto.

---

## Comandos Útiles

### Desarrollo Local
```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
uvicorn main:app --reload

# Ejecutar pruebas (si existen)
pytest

# Formatear código
black main.py

# Verificar linting
flake8 main.py
```

### Docker
```bash
# Construir imagen
docker build -t API-Analytic-Primac .

# Ejecutar contenedor
docker run -p 8000:8000 API-Analytic-Primac

# Ver logs del contenedor
docker logs <container_id>

# Acceder al contenedor
docker exec -it <container_id> /bin/bash
```

### AWS CLI
```bash
# Configurar credenciales
aws configure

# Listar objetos en S3
aws s3 ls s3://nombre-del-bucket/

# Descargar archivo de S3
aws s3 cp s3://nombre-del-bucket/cassandra/reclamos/reclamos.csv ./

# Verificar permisos de bucket
aws s3api get-bucket-policy --bucket nombre-del-bucket
```
