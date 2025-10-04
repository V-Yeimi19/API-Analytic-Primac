import boto3
import pandas as pd
import os
import logging
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError
from datetime import datetime
import json

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3DataManager:
    """Gestor de datos de S3 para análisis de datos de múltiples bases de datos"""
    
    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET", "ingesta-de-datos")
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        
        # Estructura esperada de archivos en S3
        self.data_paths = {
            'mysql': {
                'users': 'mysql/users/users.csv',
                'clients': 'mysql/clients/clients.csv',
                'agents': 'mysql/agents/agents.csv',
                'beneficiaries': 'mysql/beneficiaries/beneficiaries.csv'
            },
            'postgresql': {
                'products': 'postgresql/products/products.csv',
                'policies': 'postgresql/policies/policies.csv',
                'policy_coverage': 'postgresql/policy_coverage/policy_coverage.csv',
                'policy_beneficiaries': 'postgresql/beneficiaries/beneficiaries.csv'
            },
            'cassandra': {
                'reclamos': 'cassandra/reclamos/reclamos.csv',
                'pagos': 'cassandra/pagos/pagos.csv',
                'transaction_audit': 'cassandra/transaction_audit/transaction_audit.csv'
            }
        }
    
    def load_csv_from_s3(self, key: str, **kwargs) -> pd.DataFrame:
        """Carga un archivo CSV desde S3 y retorna un DataFrame"""
        try:
            logger.info(f"Loading CSV from S3: {key}")
            obj = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            df = pd.read_csv(obj["Body"], **kwargs)
            logger.info(f"Loaded {len(df)} rows from {key}")
            return df
        except ClientError as e:
            logger.error(f"Error loading {key} from S3: {e}")
            raise Exception(f"Could not load {key}: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing {key}: {e}")
            raise Exception(f"Error processing {key}: {str(e)}")
    
    def get_mysql_data(self, table: str) -> pd.DataFrame:
        """Obtiene datos de una tabla MySQL desde S3"""
        if table not in self.data_paths['mysql']:
            raise ValueError(f"MySQL table '{table}' not found. Available: {list(self.data_paths['mysql'].keys())}")
        
        path = self.data_paths['mysql'][table]
        return self.load_csv_from_s3(path)
    
    def get_postgresql_data(self, table: str) -> pd.DataFrame:
        """Obtiene datos de una tabla PostgreSQL desde S3"""
        if table not in self.data_paths['postgresql']:
            raise ValueError(f"PostgreSQL table '{table}' not found. Available: {list(self.data_paths['postgresql'].keys())}")
        
        path = self.data_paths['postgresql'][table]
        return self.load_csv_from_s3(path)
    
    def get_cassandra_data(self, table: str) -> pd.DataFrame:
        """Obtiene datos de una tabla Cassandra desde S3"""
        if table not in self.data_paths['cassandra']:
            raise ValueError(f"Cassandra table '{table}' not found. Available: {list(self.data_paths['cassandra'].keys())}")
        
        path = self.data_paths['cassandra'][table]
        return self.load_csv_from_s3(path)
    
    def list_available_data(self) -> Dict[str, List[str]]:
        """Lista todos los datos disponibles por base de datos"""
        return {
            'mysql': list(self.data_paths['mysql'].keys()),
            'postgresql': list(self.data_paths['postgresql'].keys()),
            'cassandra': list(self.data_paths['cassandra'].keys())
        }
    
    def check_data_availability(self) -> Dict[str, Dict[str, bool]]:
        """Verifica qué archivos están disponibles en S3"""
        availability = {'mysql': {}, 'postgresql': {}, 'cassandra': {}}
        
        for db_type, tables in self.data_paths.items():
            for table, path in tables.items():
                try:
                    self.s3_client.head_object(Bucket=self.bucket, Key=path)
                    availability[db_type][table] = True
                except ClientError:
                    availability[db_type][table] = False
        
        return availability
    
    def get_data_info(self, db_type: str, table: str) -> Dict[str, Any]:
        """Obtiene información básica de un dataset"""
        try:
            df = None
            if db_type == 'mysql':
                df = self.get_mysql_data(table)
            elif db_type == 'postgresql':
                df = self.get_postgresql_data(table)
            elif db_type == 'cassandra':
                df = self.get_cassandra_data(table)
            else:
                raise ValueError(f"Invalid db_type: {db_type}")
            
            return {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'memory_usage': df.memory_usage(deep=True).sum(),
                'null_counts': df.isnull().sum().to_dict()
            }
        except Exception as e:
            logger.error(f"Error getting info for {db_type}.{table}: {e}")
            return {'error': str(e)}
    
    def execute_cross_database_join(self, 
                                  left_db: str, left_table: str, left_key: str,
                                  right_db: str, right_table: str, right_key: str,
                                  join_type: str = 'inner') -> pd.DataFrame:
        """Ejecuta un JOIN entre tablas de diferentes bases de datos"""
        try:
            # Cargar datos de la izquierda
            if left_db == 'mysql':
                left_df = self.get_mysql_data(left_table)
            elif left_db == 'postgresql':
                left_df = self.get_postgresql_data(left_table)
            elif left_db == 'cassandra':
                left_df = self.get_cassandra_data(left_table)
            else:
                raise ValueError(f"Invalid left_db: {left_db}")
            
            # Cargar datos de la derecha
            if right_db == 'mysql':
                right_df = self.get_mysql_data(right_table)
            elif right_db == 'postgresql':
                right_df = self.get_postgresql_data(right_table)
            elif right_db == 'cassandra':
                right_df = self.get_cassandra_data(right_table)
            else:
                raise ValueError(f"Invalid right_db: {right_db}")
            
            # Realizar el JOIN
            result = pd.merge(left_df, right_df, 
                            left_on=left_key, right_on=right_key, 
                            how=join_type, suffixes=('_left', '_right'))
            
            logger.info(f"JOIN completed: {len(result)} rows from {left_db}.{left_table} + {right_db}.{right_table}")
            return result
            
        except Exception as e:
            logger.error(f"Error in cross-database join: {e}")
            raise Exception(f"Cross-database join failed: {str(e)}")
    
    def get_s3_bucket_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del bucket S3"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket, MaxKeys=1000)
            
            if 'Contents' not in response:
                return {'total_objects': 0, 'total_size': 0, 'databases': {}}
            
            objects = response['Contents']
            total_size = sum(obj['Size'] for obj in objects)
            
            # Agrupar por base de datos
            db_summary = {'mysql': [], 'postgresql': [], 'cassandra': [], 'other': []}
            
            for obj in objects:
                key = obj['Key']
                if key.startswith('mysql/'):
                    db_summary['mysql'].append(key)
                elif key.startswith('postgresql/'):
                    db_summary['postgresql'].append(key)
                elif key.startswith('cassandra/'):
                    db_summary['cassandra'].append(key)
                else:
                    db_summary['other'].append(key)
            
            return {
                'total_objects': len(objects),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'databases': {
                    'mysql': len(db_summary['mysql']),
                    'postgresql': len(db_summary['postgresql']),
                    'cassandra': len(db_summary['cassandra']),
                    'other': len(db_summary['other'])
                },
                'file_list': db_summary
            }
        except Exception as e:
            logger.error(f"Error getting S3 bucket summary: {e}")
            return {'error': str(e)}

# Instancia global del gestor
s3_manager = S3DataManager()