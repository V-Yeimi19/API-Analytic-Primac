from fastapi import FastAPI
import boto3
import pandas as pd
import os

app = FastAPI(title="Data Science API")

# Configuración S3
BUCKET = os.getenv("S3_BUCKET", "ingesta-de-datos")
s3 = boto3.client('s3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

def load_csv(key: str) -> pd.DataFrame:
    """Carga CSV desde S3 y retorna un DataFrame"""
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return pd.read_csv(obj["Body"])

# --- Endpoints de ejemplo ---

@app.get("/claims/stats")
def claims_stats():
    df = load_csv("cassandra/reclamos.csv")
    return df["estado"].value_counts().to_dict()

@app.get("/payments/avg")
def payments_avg():
    df = load_csv("cassandra/pagos.csv")
    return {"avg_monto": df["monto"].mean()}

@app.get("/audits/top-services")
def audits_top_services():
    df = load_csv("cassandra/transaction_audit.csv")
    return df["servicio"].value_counts().head(5).to_dict()

