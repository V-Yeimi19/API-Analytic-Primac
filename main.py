from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import os
from datetime import datetime
from typing import Optional

# Importar módulos de análisis S3
from s3_data_manager import s3_manager
from mysql_s3_analytics import mysql_analytics
from postgresql_s3_analytics import postgresql_analytics
from cassandra_s3_analytics import cassandra_analytics
from cross_microservice_analytics import cross_analytics

app = FastAPI(
    title="API Analytics - Primac S3",
    description="""
## API de Análisis de Datos - Sistema Primac

Esta API proporciona acceso a análisis de datos desde archivos almacenados en S3,
provenientes de 3 microservicios con sus respectivas bases de datos:

### Bases de Datos Integradas:
- **MySQL**: Gestión de usuarios, clientes, agentes y beneficiarios
- **PostgreSQL**: Gestión de productos, pólizas y coberturas
- **Cassandra**: Registro de reclamos, pagos y auditoría de transacciones

### Funcionalidades:
1. **Análisis por Base de Datos**: Consultas analíticas específicas para cada microservicio
2. **Análisis Cruzado**: Combinación de datos de múltiples microservicios
3. **Queries con AWS Athena**: Procesamiento de datos desde S3

### Proceso de Ingesta:
Los datos son extraídos mediante 3 contenedores Docker independientes (estrategia pull)
que exportan el 100% de los registros de cada base de datos a archivos CSV/JSON en S3,
catalogados automáticamente en AWS Glue.

### Documentación Técnica:
- **Bucket S3**: Almacenamiento centralizado de datos
- **AWS Glue**: Catálogo de datos automático
- **Balanceador de carga**: Nginx para distribución de tráfico
- **Despliegue**: Docker Compose en 2 VMs de producción
    """,
    version="2.0.0",
    contact={
        "name": "Equipo Primac Analytics",
        "email": "analytics@primac.com"
    },
    license_info={
        "name": "MIT",
    }
)

# ===== HEALTH CHECK =====

@app.get("/",
    tags=["health"],
    summary="Información general de la API",
    description="Endpoint raíz que proporciona información general sobre la API, incluyendo versión, estado y bases de datos disponibles.",
    response_description="Información general del servicio"
)
def root():
    """
    Endpoint de bienvenida que muestra:
    - Nombre y versión de la API
    - Estado del servicio
    - Fuente de datos (S3)
    - Bases de datos disponibles
    - Cantidad de endpoints por categoría
    """
    return {
        "message": "API Analytics - Primac S3",
        "version": app.version,
        "status": "OK",
        "data_source": "S3 Bucket",
        "available_databases": ["MySQL", "PostgreSQL", "Cassandra"],
        "endpoints": {
            "mysql": 2,
            "postgresql": 2,
            "cassandra": 2,
            "cross_microservice": 3
        }
    }

@app.get("/health",
    tags=["health"],
    summary="Health check del servicio",
    description="Verifica el estado de salud del servicio y la disponibilidad de datos en S3",
    response_description="Estado del servicio y disponibilidad de datos"
)
def health_check():
    """
    Verifica el estado de disponibilidad de datos en S3.

    Retorna:
    - Estado del servicio (OK/ERROR)
    - Timestamp de la verificación
    - Disponibilidad de archivos por base de datos
    - Resumen del bucket S3 (cantidad de objetos, tamaño total)
    """
    try:
        data_availability = s3_manager.check_data_availability()
        bucket_summary = s3_manager.get_s3_bucket_summary()

        return {
            "status": "OK",
            "timestamp": datetime.now().isoformat(),
            "data_availability": data_availability,
            "bucket_summary": bucket_summary
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# ===== MYSQL ANALYTICS FROM S3 =====

@app.get("/mysql/analytics/users",
    tags=["MySQL Analytics"],
    summary="Estadísticas de usuarios (MySQL)",
    description="Análisis completo de usuarios del microservicio MySQL almacenado en S3",
    response_description="Estadísticas generales de usuarios"
)
def get_mysql_user_statistics():
    """
    [QUERY GENERAL] Análisis completo de usuarios desde S3.

    Este endpoint analiza datos de la tabla 'users' de MySQL que fueron ingestados
    hacia S3 mediante el contenedor de ingesta MySQL.

    Retorna:
    - Total de usuarios registrados
    - Distribución por estado/región
    - Estadísticas demográficas
    - Análisis temporal de registros
    """
    try:
        return mysql_analytics.get_user_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mysql/analytics/growth-by-state",
    tags=["MySQL Analytics"],
    summary="Crecimiento de usuarios por estado (MySQL)",
    description="Análisis de crecimiento temporal de usuarios agrupado por estado",
    response_description="Serie temporal de crecimiento por estado"
)
def get_mysql_user_growth_by_state(
    months: int = Query(
        12,
        ge=1,
        le=36,
        description="Número de meses a analizar (1-36)"
    )
):
    """
    [QUERY ESPECÍFICA] Crecimiento de usuarios por estado.

    Analiza la evolución temporal del registro de usuarios agrupado por estado
    geográfico, permitiendo identificar patrones de crecimiento regional.

    Parámetros:
    - months: Ventana temporal en meses para el análisis (1-36)

    Retorna:
    - Serie temporal de registros por estado
    - Tasa de crecimiento por región
    - Estados con mayor crecimiento
    """
    try:
        return mysql_analytics.get_user_growth_by_state(months)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== POSTGRESQL ANALYTICS FROM S3 =====

@app.get("/postgresql/analytics/products",
    tags=["PostgreSQL Analytics"],
    summary="Análisis de productos (PostgreSQL)",
    description="Análisis completo de productos y pólizas del microservicio PostgreSQL almacenado en S3",
    response_description="Estadísticas de productos y pólizas"
)
def get_postgresql_product_analysis():
    """
    [QUERY GENERAL] Análisis completo de productos desde S3.

    Este endpoint analiza datos de las tablas 'products' y 'policies' de PostgreSQL
    que fueron ingestados hacia S3 mediante el contenedor de ingesta PostgreSQL.

    Retorna:
    - Total de productos disponibles
    - Distribución de pólizas por tipo de producto
    - Estadísticas de cobertura
    - Análisis de productos más vendidos
    """
    try:
        return postgresql_analytics.get_product_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/postgresql/analytics/product-profitability",
    tags=["PostgreSQL Analytics"],
    summary="Rentabilidad por producto (PostgreSQL)",
    description="Análisis de rentabilidad y performance de productos de seguros",
    response_description="Métricas de rentabilidad por producto"
)
def get_postgresql_product_profitability():
    """
    [QUERY ESPECÍFICA] Análisis de rentabilidad por producto.

    Analiza métricas de rentabilidad para cada producto de seguros,
    combinando datos de pólizas, coberturas y primas.

    Retorna:
    - Ingresos por producto
    - Número de pólizas activas por producto
    - Valor promedio de primas
    - ROI y métricas de rentabilidad
    - Productos más y menos rentables
    """
    try:
        return postgresql_analytics.get_product_profitability_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CASSANDRA ANALYTICS FROM S3 =====

@app.get("/cassandra/analytics/claims",
    tags=["Cassandra Analytics"],
    summary="Análisis de reclamos (Cassandra)",
    description="Análisis completo de reclamos y siniestros del microservicio Cassandra almacenado en S3",
    response_description="Estadísticas de reclamos"
)
def get_cassandra_claims_analysis():
    """
    [QUERY GENERAL] Análisis completo de reclamos desde S3.

    Este endpoint analiza datos de la tabla 'reclamos' de Cassandra que fueron
    ingestados hacia S3 mediante el contenedor de ingesta Cassandra.

    Retorna:
    - Total de reclamos registrados
    - Distribución por tipo de reclamo
    - Estados de los reclamos (pendiente, aprobado, rechazado)
    - Montos promedio de reclamos
    - Análisis temporal de reclamos
    """
    try:
        return cassandra_analytics.get_claims_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cassandra/analytics/claims-payments-correlation",
    tags=["Cassandra Analytics"],
    summary="Correlación reclamos-pagos (Cassandra)",
    description="Análisis de correlación entre reclamos registrados y pagos efectuados",
    response_description="Métricas de correlación y eficiencia de pagos"
)
def get_cassandra_claims_payments_correlation():
    """
    [QUERY ESPECÍFICA] Correlación entre reclamos y pagos.

    Analiza la relación entre reclamos registrados y pagos efectuados,
    identificando patrones de aprobación y tiempos de procesamiento.

    Retorna:
    - Tasa de aprobación de reclamos
    - Tiempo promedio entre reclamo y pago
    - Monto promedio pagado vs reclamado
    - Distribución de pagos por categoría
    - Eficiencia del proceso de reclamos
    """
    try:
        return cassandra_analytics.get_claims_payments_correlation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CROSS-MICROSERVICE ANALYTICS =====

@app.get("/cross/analytics/customer-policy-profile",
    tags=["Cross-Microservice Analytics"],
    summary="Perfil cliente-póliza (MySQL + PostgreSQL)",
    description="Análisis integrado de clientes y sus pólizas combinando datos de MySQL y PostgreSQL",
    response_description="Perfil completo de clientes con sus pólizas asociadas"
)
def get_cross_customer_policy_profile():
    """
    [CROSS-DATABASE QUERY 1] Perfil de clientes y sus pólizas.

    Combina datos de MySQL (clientes/usuarios) y PostgreSQL (pólizas) para crear
    un perfil completo de cada cliente con sus productos contratados.

    Origen de datos:
    - MySQL: Tabla 'clients' y 'users'
    - PostgreSQL: Tablas 'policies' y 'products'

    Retorna:
    - Perfil demográfico de clientes
    - Pólizas activas por cliente
    - Productos contratados por cliente
    - Valor total de cobertura por cliente
    - Segmentación de clientes por productos
    """
    try:
        return cross_analytics.get_customer_policy_profile()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cross/analytics/agent-performance",
    tags=["Cross-Microservice Analytics"],
    summary="Rendimiento de agentes (MySQL + PostgreSQL)",
    description="Análisis de performance de agentes de ventas integrando datos de múltiples sistemas",
    response_description="Métricas de rendimiento por agente"
)
def get_cross_agent_performance():
    """
    [CROSS-DATABASE QUERY 2] Rendimiento de agentes.

    Analiza el performance de agentes de ventas combinando información de
    agentes (MySQL) con las pólizas que han vendido (PostgreSQL).

    Origen de datos:
    - MySQL: Tabla 'agents'
    - PostgreSQL: Tabla 'policies'

    Retorna:
    - Número de pólizas vendidas por agente
    - Valor total de primas generadas por agente
    - Productos más vendidos por agente
    - Ranking de agentes por performance
    - Tasa de conversión y retención
    """
    try:
        return cross_analytics.get_agent_performance_across_systems()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cross/analytics/claims-vs-policies",
    tags=["Cross-Microservice Analytics"],
    summary="Análisis de siniestralidad (PostgreSQL + Cassandra)",
    description="Análisis de relación entre pólizas emitidas y reclamos registrados",
    response_description="Métricas de siniestralidad y ratio loss"
)
def get_cross_claims_vs_policies():
    """
    [CROSS-DATABASE QUERY 3] Análisis de siniestralidad.

    Analiza la relación entre pólizas emitidas (PostgreSQL) y reclamos
    registrados (Cassandra) para calcular métricas de siniestralidad.

    Origen de datos:
    - PostgreSQL: Tablas 'policies' y 'products'
    - Cassandra: Tablas 'reclamos' y 'pagos'

    Retorna:
    - Ratio de siniestralidad por producto
    - Frecuencia de reclamos por tipo de póliza
    - Loss ratio (pagos/primas)
    - Productos con mayor/menor siniestralidad
    - Análisis de rentabilidad por siniestralidad
    """
    try:
        return cross_analytics.get_claims_vs_policies_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

