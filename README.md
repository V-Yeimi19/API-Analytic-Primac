# API Analítica de Ciencia de Datos - Primac S3

## Resumen General

Esta API basada en FastAPI proporciona endpoints avanzados de análisis de datos para procesar y analizar datos empresariales almacenados en AWS S3. La API se especializa en procesar datos de la empresa Primac de múltiples fuentes de bases de datos (MySQL, PostgreSQL y Cassandra) que han sido ingeridas y almacenadas en S3 para análisis unificado.

## Características Principales

### 📊 Análisis Multi-Base de Datos
- **MySQL Analytics**: Análisis de usuarios, clientes, agentes y beneficiarios
- **PostgreSQL Analytics**: Análisis de productos, pólizas y coberturas
- **Cassandra Analytics**: Análisis de reclamos, pagos y auditoría de transacciones

### 🔗 Análisis Cruzados
- **Customer Journey**: Análisis completo del recorrido del cliente entre sistemas
- **Agent Performance**: Rendimiento de agentes combinando datos de varias fuentes
- **Claims vs Policies**: Análisis de siniestralidad cruzando pólizas y reclamos

### 🎨 Características Técnicas
- **Alto Rendimiento**: Construida con FastAPI para rendimiento óptimo
- **Integración S3**: Procesamiento directo desde AWS S3 sin conexiones directas a BD
- **Queries Especializadas**: Consultas avanzadas con parámetros personalizables
- **Contenerizada**: Contenedor Docker listo para despliegue
- **Documentación Interactiva**: Swagger UI y ReDoc incluidos

## Arquitectura

```
┌────────────────────────┐    ┌──────────────────────┐    ┌─────────────────────────┐
│     Fuentes de Datos     │    │    Bucket AWS S3    │    │     API Analytics     │
│                        │───▶│                      │───▶│                       │
│ • MySQL (Usuarios)     │    │ • mysql/*.csv        │    │ • MySQL Analytics     │
│ • PostgreSQL (Pólizas) │    │ • postgresql/*.csv   │    │ • PostgreSQL Analytics│
│ • Cassandra (Pagos)   │    │ • cassandra/*.csv    │    │ • Cassandra Analytics │
│                        │    │                      │    │ • Cross-Analytics     │
└────────────────────────┘    └──────────────────────┘    └─────────────────────────┘
```

### Flujo de Datos
1. **Ingesta**: Los datos de MySQL, PostgreSQL y Cassandra son ingeridos en AWS S3
2. **Almacenamiento**: Los datos se almacenan como archivos CSV organizados por fuente
3. **Análisis**: La API lee directamente desde S3 y procesa los datos usando Pandas
4. **Respuesta**: Los resultados se devuelven como JSON estructurado

## Documentación Completa de Endpoints

**Base URL**: `http://localhost:8000`  
**Versión**: `3.0.0` (S3 Analytics Optimizada)

### 🟢 Health Check

#### GET `/`
**Descripción**: Información general de la API  
**Response**:
```json
{
    "message": "API Analytics - Primac S3",
    "version": "3.0.0",
    "status": "OK",
    "data_source": "S3 Bucket",
    "available_databases": ["MySQL", "PostgreSQL", "Cassandra"]
}
```

#### GET `/health`
**Descripción**: Estado de disponibilidad de datos en S3  
**Response**:
```json
{
    "status": "OK",
    "timestamp": "2024-10-04T20:39:08Z",
    "data_availability": {
        "mysql": {"users": true, "clients": true, "agents": true, "beneficiaries": true},
        "postgresql": {"products": true, "policies": true, "policy_coverage": true, "beneficiaries": true},
        "cassandra": {"reclamos": true, "pagos": true, "transaction_audit": true}
    },
    "bucket_summary": {
        "total_objects": 9,
        "total_size_mb": 156.7,
        "databases": {"mysql": 4, "postgresql": 4, "cassandra": 3}
    }
}
```

#### GET `/data/info`
**Descripción**: Información sobre datasets disponibles  
**Response**:
```json
{
    "available_data": {
        "mysql": ["users", "clients", "agents", "beneficiaries"],
        "postgresql": ["products", "policies", "policy_coverage", "beneficiaries"],
        "cassandra": ["reclamos", "pagos", "transaction_audit"]
    },
    "data_paths": {
        "mysql": {"users": "mysql/users/users.csv"},
        "postgresql": {"products": "postgresql/products/products.csv"},
        "cassandra": {"reclamos": "cassandra/reclamos/reclamos.csv"}
    }
}
```

### 📊 MySQL Analytics (Usuarios y Clientes)

**Endpoints Generales:**
- **GET** `/mysql/analytics/users` - Estadísticas completas de usuarios
- **GET** `/mysql/analytics/clients/demographics` - Análisis demográfico de clientes
- **GET** `/mysql/analytics/agents/performance` - Rendimiento de agentes
- **GET** `/mysql/analytics/beneficiaries/relationships` - Relaciones de beneficiarios

**Queries Especializadas:**
- **GET** `/mysql/analytics/growth-by-state?months=12` - Crecimiento por estado
- **GET** `/mysql/analytics/data-quality-report` - Reporte de calidad de datos

### 📄 PostgreSQL Analytics (Productos y Pólizas)

**Endpoints Generales:**
- **GET** `/postgresql/analytics/products` - Análisis completo de productos
- **GET** `/postgresql/analytics/policies` - Análisis detallado de pólizas
- **GET** `/postgresql/analytics/coverages` - Análisis de coberturas

**Queries Especializadas:**
- **GET** `/postgresql/analytics/product-profitability` - Rentabilidad por producto
- **GET** `/postgresql/analytics/policy-trends?months=12` - Tendencias temporales

### 💰 Cassandra Analytics (Pagos y Reclamos)

**Endpoints Generales:**
- **GET** `/cassandra/analytics/claims` - Análisis completo de reclamos
- **GET** `/cassandra/analytics/payments` - Análisis completo de pagos
- **GET** `/cassandra/analytics/transaction-audit` - Auditoría de transacciones

**Queries Especializadas:**
- **GET** `/cassandra/analytics/claims-payments-correlation` - Correlación reclamos-pagos
- **GET** `/cassandra/analytics/activity-patterns?hours=168` - Patrones de actividad

### 🔗 Cross-Microservice Analytics (Análisis Cruzados)

- **GET** `/cross/analytics/customer-policy-profile` - Perfil de clientes y pólizas (MySQL + PostgreSQL)
- **GET** `/cross/analytics/agent-performance` - Rendimiento de agentes (MySQL + PostgreSQL)
- **GET** `/cross/analytics/claims-vs-policies` - Siniestralidad (PostgreSQL + Cassandra)
- **GET** `/cross/analytics/customer-journey` - Customer journey completo (MySQL + PostgreSQL + Cassandra)

### 🔄 Legacy Analytics (Compatibilidad)

#### GET `/claims/stats`
**Descripción**: Estadísticas de reclamos desde S3/Cassandra (Legacy)  
**Response**:
```json
{
    "aprobado": 150,
    "pendiente": 75,
    "rechazado": 25,
    "en_revision": 50
}
```

#### GET `/payments/avg`
**Descripción**: Promedio de pagos desde S3/Cassandra (Legacy)  
**Response**:
```json
{
    "avg_monto": 1250.75
}
```

#### GET `/audits/top-services`
**Descripción**: Top 5 servicios más utilizados desde auditoría  
**Response**:
```json
{
    "servicio_pagos": 342,
    "autenticacion_usuario": 298,
    "respaldo_datos": 187,
    "servicio_notificaciones": 156,
    "generacion_reportes": 134
}
```

## 📝 Formato de Respuestas y Códigos HTTP

### Códigos de Estado HTTP

- **200**: OK - Solicitud exitosa
- **404**: Not Found - Recurso no encontrado 
- **422**: Validation Error - Error en parámetros de entrada
- **500**: Internal Server Error - Error interno del servidor (problema con S3 o procesamiento)

### Formato de Error
```json
{
    "detail": "Error: Could not load mysql/users/users.csv: NoSuchKey"
}
```

### Ejemplos de Respuesta de Analytics

#### MySQL User Statistics Response
```json
{
    "total_users": 1500,
    "users_by_role": {"USER": 1200, "ADMIN": 50, "AGENT": 250},
    "users_by_state": {"LIMA": 800, "AREQUIPA": 300, "CUSCO": 200},
    "recent_registrations": 45,
    "top_cities": {"Lima": 800, "Arequipa": 300, "Cusco": 200},
    "monthly_registrations": {"2024-09": 123, "2024-10": 89},
    "data_quality": {
        "missing_emails": 12,
        "missing_phones": 45,
        "duplicate_emails": 3
    }
}
```

#### PostgreSQL Product Analysis Response
```json
{
    "total_products": 50,
    "product_types": {"VIDA": 20, "SALUD": 15, "AUTO": 15},
    "premium_statistics": {
        "average_premium": 250.75,
        "median_premium": 200.0,
        "max_premium": 1500.0,
        "premium_distribution": {"< 100": 10, "100-499": 25, "500-999": 10}
    },
    "data_completeness": {
        "products_with_premium": 48,
        "products_with_description": 45
    }
}
```

#### Cross-Analytics Customer Journey Response
```json
{
    "conversion_funnel": {
        "total_users": 10000,
        "users_to_clients": 8500,
        "clients_to_policyholders": 6200,
        "conversion_rates": {
            "user_to_client": 85.0,
            "client_to_policy": 72.9,
            "overall_conversion": 62.0
        }
    },
    "journey_timing": {
        "avg_days_user_to_client": 3.2,
        "avg_days_client_to_policy": 15.7
    },
    "customer_segments": {
        "by_state": {
            "LIMA": {"total_users": 5000, "with_policies": 3200, "conversion_rate": 64.0}
        }
    }
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

## Gestión de Bases de Datos

### Orchestrator Unificado

El proyecto incluye un script de orquestación mejorado que gestiona MySQL, PostgreSQL y Cassandra:

**Ubicación:** `../../databases/Primac-Claims-Payments-DB/orchestrator.py`

```bash
# Levantar todas las bases de datos + setup + seed
python orchestrator.py all

# Levantar bases de datos individuales
python orchestrator.py mysql
python orchestrator.py postgresql  
python orchestrator.py cassandra

# Levantar base + configurar schema
python orchestrator.py mysql+setup
python orchestrator.py postgresql+setup
python orchestrator.py cassandra+setup

# Solo datos fake (requiere BDs ya configuradas)
python orchestrator.py faker
```

### Estructura de Proyectos de BD

```
databases/
├── BD_Users_Primac/           # MySQL - Usuarios y Clientes
├── proyecto_postgresql/       # PostgreSQL - Productos y Pólizas
└── Primac-Claims-Payments-DB/ # Cassandra - Pagos y Reclamos
    └── orchestrator.py        # Script de orquestación unificado
```

## Instalación y Configuración de la API

### Prerequisitos

- Python 3.11+
- Docker y Docker Compose
- Credenciales de AWS con acceso a S3
- Bucket S3 configurado con datos CSV

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

### 📊 Analíticas de MySQL

```bash
# Análisis de usuarios
curl "http://localhost:8000/mysql/analytics/users"

# Demografía de clientes
curl "http://localhost:8000/mysql/analytics/clients/demographics"

# Crecimiento por estado (6 meses)
curl "http://localhost:8000/mysql/analytics/growth-by-state?months=6"
```

### 📄 Analíticas de PostgreSQL

```bash
# Análisis de productos
curl "http://localhost:8000/postgresql/analytics/products"

# Rentabilidad por producto
curl "http://localhost:8000/postgresql/analytics/product-profitability"

# Tendencias de pólizas (3 meses)
curl "http://localhost:8000/postgresql/analytics/policy-trends?months=3"
```

### 💰 Analíticas de Cassandra

```bash
# Análisis de reclamos
curl "http://localhost:8000/cassandra/analytics/claims"

# Correlación reclamos-pagos
curl "http://localhost:8000/cassandra/analytics/claims-payments-correlation"

# Patrones de actividad (72 horas)
curl "http://localhost:8000/cassandra/analytics/activity-patterns?hours=72"
```

### 🔗 Análisis Cruzados

```bash
# Customer journey completo
curl "http://localhost:8000/cross/analytics/customer-journey"

# Rendimiento de agentes
curl "http://localhost:8000/cross/analytics/agent-performance"

# Siniestralidad (claims vs policies)
curl "http://localhost:8000/cross/analytics/claims-vs-policies"
```

### 🐍 Usando Python

```python
import requests
import json

base_url = "http://localhost:8000"

# Análisis completo de customer journey
response = requests.get(f"{base_url}/cross/analytics/customer-journey")
journey_data = response.json()

print(f"Conversión general: {journey_data['conversion_funnel']['conversion_rates']['overall_conversion']}%")
print(f"Usuarios totales: {journey_data['conversion_funnel']['total_users']}")
print(f"Clientes con pólizas: {journey_data['conversion_funnel']['clients_to_policyholders']}")

# Análisis de rentabilidad por producto
response = requests.get(f"{base_url}/postgresql/analytics/product-profitability")
profitability = response.json()

print("\nTop productos por volumen:")
for product in profitability['top_products_by_volume'][:3]:
    print(f"- {product['name']}: {product['policy_number_count']} pólizas")
```

## 📚 Documentación Interactiva

Una vez que la API esté ejecutándose, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs` - Documentación interactiva con pruebas en vivo
- **ReDoc**: `http://localhost:8000/redoc` - Documentación alternativa con mejor legibilidad
- **Esquema OpenAPI**: `http://localhost:8000/openapi.json` - Especificación técnica completa

## 🚽 Troubleshooting

### Problemas Comunes

#### Error de Credenciales de AWS
```
Detail: Error: An error occurred (InvalidAccessKeyId) when calling the GetObject operation
```
**Solución:**
- Verificar que `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` estén correctamente configuradas
- Comprobar permisos IAM para acceso a S3
- Usar el endpoint `/health` para diagnosticar conexión

#### Error de Acceso a S3
```
Detail: Error: Could not load mysql/users/users.csv: NoSuchKey
```
**Solución:**
- Verificar el nombre del bucket y la región en `S3_BUCKET` y `AWS_DEFAULT_REGION`
- Comprobar que los archivos CSV existan en las rutas esperadas de S3
- Usar `/data/info` para ver la disponibilidad de datasets

#### Error de Procesamiento de Datos
```
Detail: Error analyzing users: 'estado' column not found
```
**Solución:**
- Verificar formato de archivos CSV y nombres de columnas
- Comprobar que no haya archivos vacíos o corruptos
- Revisar la estructura esperada en la sección "Campos Principales por Dataset"

#### Error 422 - Validation Error
```
{
    "detail": [
        {
            "loc": ["query", "months"],
            "msg": "ensure this value is greater than or equal to 1",
            "type": "value_error.number.not_ge"
        }
    ]
}
```
**Solución:**
- Verificar que los parámetros estén en el formato correcto
- `months` debe estar entre 1 y 36
- `hours` debe estar entre 24 y 720

### Comandos de Diagnóstico

```bash
# Verificar estado general
curl http://localhost:8000/health

# Listar datasets disponibles
curl http://localhost:8000/data/info

# Probar un endpoint simple
curl http://localhost:8000/claims/stats

# Verificar logs del contenedor
docker logs <container_name>
```

## Estructura de Datos S3

### Organización del Bucket S3

```
s3://ingesta-de-datos/
├── mysql/
│   ├── users/
│   │   └── users.csv
│   ├── clients/
│   │   └── clients.csv
│   ├── agents/
│   │   └── agents.csv
│   └── beneficiaries/
│       └── beneficiaries.csv
├── postgresql/
│   ├── products/
│   │   └── products.csv
│   ├── policies/
│   │   └── policies.csv
│   ├── policy_coverage/
│   │   └── policy_coverage.csv
│   └── beneficiaries/
│       └── beneficiaries.csv
└── cassandra/
    ├── reclamos/
    │   └── reclamos.csv
    ├── pagos/
    │   └── pagos.csv
    └── transaction_audit/
        └── transaction_audit.csv
```

### Campos Principales por Dataset

**MySQL:**
- `users`: id, username, email, role, phone, state, city, created_at
- `clients`: user_id, first_name, last_name, document_type, birth_date
- `agents`: id, code, first_name, last_name, is_active
- `beneficiaries`: client_id, relationship, birth_date

**PostgreSQL:**
- `products`: id, code, name, product_type, base_premium
- `policies`: id, policy_number, customer_id, agent_id, premium, sum_insured
- `policy_coverage`: policy_id, coverage_name, coverage_limit, deductible
- `beneficiaries`: policy_id, client_id, full_name, relationship

**Cassandra:**
- `reclamos`: id, policy_number, estado, monto, fecha_reclamo
- `pagos`: id, customer_id, monto, metodo_pago, fecha_pago
- `transaction_audit`: timestamp, servicio, operacion, user_id

## Despliegue

### Ejemplo de Despliegue en AWS ECS

```bash
# Construir y subir a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t API-Analytic-Primac .
docker tag API-Analytic-Primac:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/API-Analytic-Primac:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/API-Analytic-Primac:latest
```

## Dependencias Principales

- **FastAPI 0.100.0+**: Framework web moderno para construir APIs
- **Uvicorn 0.23.2+**: Servidor ASGI de alto rendimiento
- **Boto3 1.26.150+**: SDK de AWS para integración con S3
- **Pandas 2.1.1+**: Biblioteca de manipulación y análisis de datos
- **NumPy 1.26.0+**: Computación numérica y operaciones matriciales
- **python-dotenv 1.1.1+**: Gestión de variables de entorno

## Módulos de Análisis

- **s3_data_manager**: Gestor unificado de datos S3
- **mysql_s3_analytics**: Análisis de datos MySQL desde S3
- **postgresql_s3_analytics**: Análisis de datos PostgreSQL desde S3
- **cassandra_s3_analytics**: Análisis de datos Cassandra desde S3
- **cross_microservice_analytics**: Análisis cruzados entre sistemas

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

## Tipos de Análisis Disponibles

### 📊 Análisis Descriptivos
- Estadísticas básicas y distribuciones
- Conteos y promedios por categorías
- Análisis de completitud de datos

### 📈 Análisis Temporales
- Tendencias mensuales y estacionales
- Patrones de actividad por hora
- Crecimiento y cambios temporales

### 🔗 Análisis Relacionales
- JOINs entre diferentes fuentes de datos
- Customer journey completo
- Correlaciones entre métricas

### 🎯 Análisis Especializados
- Rentabilidad por producto
- Siniestralidad y riesgo
- Rendimiento de agentes
- Calidad de datos

---

**Versión de la API:** 3.0.0  
**Última actualización:** Octubre 2024  
**Estado:** Funcional y optimizada para análisis S3

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
