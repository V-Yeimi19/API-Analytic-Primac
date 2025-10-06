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
    description="API para análisis de datos desde S3",
    version="2.0.0"
)

# ===== HEALTH CHECK =====

@app.get("/", tags=["health"])
def root():
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

# ===== MYSQL ANALYTICS FROM S3 =====

@app.get("/mysql/analytics/users", tags=["mysql-analytics"])
def get_mysql_user_statistics():
    """[GENERAL] Análisis completo de usuarios desde S3"""
    try:
        return mysql_analytics.get_user_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mysql/analytics/growth-by-state", tags=["mysql-specialized"])
def get_mysql_user_growth_by_state(months: int = Query(12, ge=1, le=36)):
    """[ESPECÍFICA] Crecimiento de usuarios por estado"""
    try:
        return mysql_analytics.get_user_growth_by_state(months)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== POSTGRESQL ANALYTICS FROM S3 =====

@app.get("/postgresql/analytics/products", tags=["postgresql-analytics"])
def get_postgresql_product_analysis():
    """[GENERAL] Análisis completo de productos desde S3"""
    try:
        return postgresql_analytics.get_product_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/postgresql/analytics/product-profitability", tags=["postgresql-specialized"])
def get_postgresql_product_profitability():
    """[ESPECÍFICA] Análisis de rentabilidad por producto"""
    try:
        return postgresql_analytics.get_product_profitability_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CASSANDRA ANALYTICS FROM S3 =====

@app.get("/cassandra/analytics/claims", tags=["cassandra-analytics"])
def get_cassandra_claims_analysis():
    """[GENERAL] Análisis completo de reclamos desde S3"""
    try:
        return cassandra_analytics.get_claims_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cassandra/analytics/claims-payments-correlation", tags=["cassandra-specialized"])
def get_cassandra_claims_payments_correlation():
    """[ESPECÍFICA] Correlación entre reclamos y pagos"""
    try:
        return cassandra_analytics.get_claims_payments_correlation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CROSS-MICROSERVICE ANALYTICS =====

@app.get("/cross/analytics/customer-policy-profile", tags=["cross-analytics"])
def get_cross_customer_policy_profile():
    """[CROSS 1] Perfil de clientes y sus pólizas (MySQL + PostgreSQL)"""
    try:
        return cross_analytics.get_customer_policy_profile()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cross/analytics/agent-performance", tags=["cross-analytics"])
def get_cross_agent_performance():
    """[CROSS 2] Rendimiento de agentes (MySQL + PostgreSQL)"""
    try:
        return cross_analytics.get_agent_performance_across_systems()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cross/analytics/claims-vs-policies", tags=["cross-analytics"])
def get_cross_claims_vs_policies():
    """[CROSS 3] Siniestralidad (PostgreSQL + Cassandra)"""
    try:
        return cross_analytics.get_claims_vs_policies_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

