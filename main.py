from fastapi import FastAPI, HTTPException, Query
import boto3
import pandas as pd
import os
from datetime import datetime, date
from typing import Optional

# Importar módulos de análisis S3
from .s3_data_manager import s3_manager
from .mysql_s3_analytics import mysql_analytics
from .postgresql_s3_analytics import postgresql_analytics
from .cassandra_s3_analytics import cassandra_analytics
from .cross_microservice_analytics import cross_analytics

app = FastAPI(
    title="API Analytics - Primac S3",
    description="API para análisis de datos desde S3 - MySQL, PostgreSQL y Cassandra con consultas cruzadas",
    version="3.0.0"
)

# Configuración S3 (mantenida para compatibilidad)
BUCKET = os.getenv("S3_BUCKET", "ingesta-de-datos")
s3 = boto3.client('s3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

def load_csv(key: str) -> pd.DataFrame:
    """Carga CSV desde S3 y retorna un DataFrame (función legacy)"""
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return pd.read_csv(obj["Body"])

# ===== HEALTH CHECK =====

@app.get("/", tags=["health"])
def root():
    return {
        "message": "API Analytics - Primac S3", 
        "version": "3.0.0", 
        "status": "OK",
        "data_source": "S3 Bucket",
        "available_databases": ["MySQL", "PostgreSQL", "Cassandra"]
    }

@app.get("/health", tags=["health"])
def health_check():
    """Verifica el estado de disponibilidad de datos en S3"""
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

@app.get("/data/info", tags=["health"])
def get_data_info():
    """Información sobre los datos disponibles"""
    return {
        "available_data": s3_manager.list_available_data(),
        "data_paths": s3_manager.data_paths
    }

# ===== LEGACY S3/CASSANDRA ANALYTICS (Compatibilidad) =====

@app.get("/claims/stats", tags=["legacy-analytics"])
def claims_stats():
    """Estadísticas de reclamos desde S3/Cassandra (Legacy)"""
    try:
        df = load_csv("cassandra/reclamos/reclamos.csv")
        return df["estado"].value_counts().to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/payments/avg", tags=["legacy-analytics"])
def payments_avg():
    """Promedio de pagos desde S3/Cassandra (Legacy)"""
    try:
        df = load_csv("cassandra/pagos/pagos.csv")
        return {"avg_monto": df["monto"].mean()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/audits/top-services", tags=["legacy-analytics"])
def audits_top_services():
    """Top servicios desde auditoría S3/Cassandra (Legacy)"""
    try:
        df = load_csv("cassandra/transaction_audit/transaction_audit.csv")
        return df["servicio"].value_counts().head(5).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ===== MYSQL ANALYTICS FROM S3 =====

# General Analytics
@app.get("/mysql/analytics/users", tags=["mysql-analytics"])
def get_mysql_user_statistics():
    """Análisis completo de usuarios desde S3"""
    try:
        return mysql_analytics.get_user_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mysql/analytics/clients/demographics", tags=["mysql-analytics"])
def get_mysql_client_demographics():
    """Análisis demográfico de clientes desde S3"""
    try:
        return mysql_analytics.get_client_demographics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mysql/analytics/agents/performance", tags=["mysql-analytics"])
def get_mysql_agent_performance():
    """Análisis de rendimiento de agentes desde S3"""
    try:
        return mysql_analytics.get_agent_performance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mysql/analytics/beneficiaries/relationships", tags=["mysql-analytics"])
def get_mysql_beneficiary_relationships():
    """Análisis de relaciones de beneficiarios desde S3"""
    try:
        return mysql_analytics.get_beneficiary_relationships()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Specialized Queries
@app.get("/mysql/analytics/growth-by-state", tags=["mysql-specialized"])
def get_mysql_user_growth_by_state(months: int = Query(12, ge=1, le=36)):
    """Query especializada: Crecimiento de usuarios por estado"""
    try:
        return mysql_analytics.get_user_growth_by_state(months)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mysql/analytics/data-quality-report", tags=["mysql-specialized"])
def get_mysql_data_quality_report():
    """Query especializada: Reporte de calidad de datos MySQL"""
    try:
        return mysql_analytics.get_data_quality_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== POSTGRESQL ANALYTICS FROM S3 =====

# General Analytics
@app.get("/postgresql/analytics/products", tags=["postgresql-analytics"])
def get_postgresql_product_analysis():
    """Análisis completo de productos desde S3"""
    try:
        return postgresql_analytics.get_product_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/postgresql/analytics/policies", tags=["postgresql-analytics"])
def get_postgresql_policy_insights():
    """Análisis detallado de pólizas desde S3"""
    try:
        return postgresql_analytics.get_policy_insights()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/postgresql/analytics/coverages", tags=["postgresql-analytics"])
def get_postgresql_coverage_analysis():
    """Análisis de coberturas de pólizas desde S3"""
    try:
        return postgresql_analytics.get_coverage_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Specialized Queries
@app.get("/postgresql/analytics/product-profitability", tags=["postgresql-specialized"])
def get_postgresql_product_profitability():
    """Query especializada: Análisis de rentabilidad por producto"""
    try:
        return postgresql_analytics.get_product_profitability_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/postgresql/analytics/policy-trends", tags=["postgresql-specialized"])
def get_postgresql_policy_trends(months: int = Query(12, ge=1, le=36)):
    """Query especializada: Análisis de tendencias temporales de pólizas"""
    try:
        return postgresql_analytics.get_policy_trends_analysis(months)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CASSANDRA ANALYTICS FROM S3 =====

# General Analytics
@app.get("/cassandra/analytics/claims", tags=["cassandra-analytics"])
def get_cassandra_claims_analysis():
    """Análisis completo de reclamos desde S3"""
    try:
        return cassandra_analytics.get_claims_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cassandra/analytics/payments", tags=["cassandra-analytics"])
def get_cassandra_payments_analysis():
    """Análisis completo de pagos desde S3"""
    try:
        return cassandra_analytics.get_payments_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cassandra/analytics/transaction-audit", tags=["cassandra-analytics"])
def get_cassandra_transaction_audit_analysis():
    """Análisis de auditoría de transacciones desde S3"""
    try:
        return cassandra_analytics.get_transaction_audit_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Specialized Queries
@app.get("/cassandra/analytics/claims-payments-correlation", tags=["cassandra-specialized"])
def get_cassandra_claims_payments_correlation():
    """Query especializada: Análisis de correlación entre reclamos y pagos"""
    try:
        return cassandra_analytics.get_claims_payments_correlation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cassandra/analytics/activity-patterns", tags=["cassandra-specialized"])
def get_cassandra_activity_patterns(hours: int = Query(168, ge=24, le=720)):
    """Query especializada: Análisis de patrones de actividad por hora y servicio"""
    try:
        return cassandra_analytics.get_activity_patterns_analysis(hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CROSS-MICROSERVICE ANALYTICS =====

@app.get("/cross/analytics/customer-policy-profile", tags=["cross-analytics"])
def get_cross_customer_policy_profile():
    """Análisis cruzado: Perfil de clientes y sus pólizas (MySQL + PostgreSQL)"""
    try:
        return cross_analytics.get_customer_policy_profile()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cross/analytics/agent-performance", tags=["cross-analytics"])
def get_cross_agent_performance():
    """Análisis cruzado: Rendimiento de agentes (MySQL + PostgreSQL)"""
    try:
        return cross_analytics.get_agent_performance_across_systems()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cross/analytics/claims-vs-policies", tags=["cross-analytics"])
def get_cross_claims_vs_policies():
    """Análisis cruzado: Análisis de siniestralidad (PostgreSQL + Cassandra)"""
    try:
        return cross_analytics.get_claims_vs_policies_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cross/analytics/customer-journey", tags=["cross-analytics"])
def get_cross_customer_journey():
    """Análisis cruzado: Customer journey completo (MySQL + PostgreSQL + Cassandra)"""
    try:
        return cross_analytics.get_complete_customer_journey()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

