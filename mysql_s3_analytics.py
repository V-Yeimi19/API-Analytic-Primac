import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .s3_data_manager import s3_manager
import logging

logger = logging.getLogger(__name__)

class MySQLAnalytics:
    """Análisis de datos MySQL desde S3"""
    
    def __init__(self):
        self.s3_manager = s3_manager
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Análisis completo de usuarios"""
        try:
            users_df = self.s3_manager.get_mysql_data('users')
            
            # Estadísticas básicas
            total_users = len(users_df)
            
            # Usuarios por rol
            users_by_role = users_df['role'].value_counts().to_dict() if 'role' in users_df.columns else {}
            
            # Usuarios por estado
            users_by_state = users_df['state'].value_counts().head(10).to_dict() if 'state' in users_df.columns else {}
            
            # Registros recientes (últimos 30 días)
            if 'created_at' in users_df.columns:
                users_df['created_at'] = pd.to_datetime(users_df['created_at'])
                recent_date = datetime.now() - timedelta(days=30)
                recent_users = len(users_df[users_df['created_at'] >= recent_date])
            else:
                recent_users = 0
            
            # Top ciudades
            top_cities = users_df['city'].value_counts().head(10).to_dict() if 'city' in users_df.columns else {}
            
            # Distribución de creación por mes (últimos 12 meses)
            monthly_registrations = {}
            if 'created_at' in users_df.columns:
                users_df['month_year'] = users_df['created_at'].dt.to_period('M')
                monthly_registrations = users_df['month_year'].value_counts().sort_index().tail(12).to_dict()
                monthly_registrations = {str(k): v for k, v in monthly_registrations.items()}
            
            return {
                "total_users": total_users,
                "users_by_role": users_by_role,
                "users_by_state": users_by_state,
                "recent_registrations": recent_users,
                "top_cities": top_cities,
                "monthly_registrations": monthly_registrations,
                "data_quality": {
                    "missing_emails": users_df['email'].isnull().sum() if 'email' in users_df.columns else 0,
                    "missing_phones": users_df['phone'].isnull().sum() if 'phone' in users_df.columns else 0,
                    "duplicate_emails": users_df['email'].duplicated().sum() if 'email' in users_df.columns else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in user statistics: {e}")
            raise Exception(f"Error analyzing users: {str(e)}")
    
    def get_client_demographics(self) -> Dict[str, Any]:
        """Análisis demográfico de clientes"""
        try:
            clients_df = self.s3_manager.get_mysql_data('clients')
            
            total_clients = len(clients_df)
            
            # Distribución por tipo de documento
            document_types = clients_df['document_type'].value_counts().to_dict() if 'document_type' in clients_df.columns else {}
            
            # Análisis de edad
            age_stats = {}
            if 'birth_date' in clients_df.columns:
                clients_df['birth_date'] = pd.to_datetime(clients_df['birth_date'])
                clients_df['age'] = (datetime.now() - clients_df['birth_date']).dt.days // 365
                
                age_stats = {
                    "average_age": round(clients_df['age'].mean(), 1),
                    "median_age": clients_df['age'].median(),
                    "min_age": clients_df['age'].min(),
                    "max_age": clients_df['age'].max()
                }
                
                # Distribución por grupos de edad
                bins = [0, 25, 35, 45, 55, 65, 100]
                labels = ['<25', '25-34', '35-44', '45-54', '55-64', '65+']
                clients_df['age_group'] = pd.cut(clients_df['age'], bins=bins, labels=labels, include_lowest=True)
                age_distribution = clients_df['age_group'].value_counts().to_dict()
                age_stats["age_distribution"] = {str(k): v for k, v in age_distribution.items()}
            
            # Análisis de nombres más comunes
            common_names = {}
            if 'first_name' in clients_df.columns:
                common_names['first_names'] = clients_df['first_name'].value_counts().head(10).to_dict()
            if 'last_name' in clients_df.columns:
                common_names['last_names'] = clients_df['last_name'].value_counts().head(10).to_dict()
            
            return {
                "total_clients": total_clients,
                "document_types": document_types,
                "age_statistics": age_stats,
                "common_names": common_names,
                "data_completeness": {
                    "has_birth_date": (~clients_df['birth_date'].isnull()).sum() if 'birth_date' in clients_df.columns else 0,
                    "has_first_name": (~clients_df['first_name'].isnull()).sum() if 'first_name' in clients_df.columns else 0,
                    "has_last_name": (~clients_df['last_name'].isnull()).sum() if 'last_name' in clients_df.columns else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in client demographics: {e}")
            raise Exception(f"Error analyzing clients: {str(e)}")
    
    def get_agent_performance(self) -> Dict[str, Any]:
        """Análisis de rendimiento de agentes"""
        try:
            agents_df = self.s3_manager.get_mysql_data('agents')
            
            total_agents = len(agents_df)
            
            # Agentes activos vs inactivos
            status_distribution = agents_df['is_active'].value_counts().to_dict() if 'is_active' in agents_df.columns else {}
            
            # Análisis de códigos de agente
            code_analysis = {}
            if 'code' in agents_df.columns:
                # Patrones en los códigos
                agents_df['code_length'] = agents_df['code'].str.len()
                code_analysis = {
                    "avg_code_length": round(agents_df['code_length'].mean(), 1),
                    "code_length_distribution": agents_df['code_length'].value_counts().to_dict(),
                    "unique_codes": agents_df['code'].nunique()
                }
            
            return {
                "total_agents": total_agents,
                "active_agents": status_distribution.get(True, 0),
                "inactive_agents": status_distribution.get(False, 0),
                "status_distribution": status_distribution,
                "code_analysis": code_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in agent performance: {e}")
            raise Exception(f"Error analyzing agents: {str(e)}")
    
    def get_beneficiary_relationships(self) -> Dict[str, Any]:
        """Análisis de relaciones de beneficiarios"""
        try:
            beneficiaries_df = self.s3_manager.get_mysql_data('beneficiaries')
            
            total_beneficiaries = len(beneficiaries_df)
            
            # Distribución por tipo de relación
            relationship_distribution = beneficiaries_df['relationship'].value_counts().to_dict() if 'relationship' in beneficiaries_df.columns else {}
            
            # Beneficiarios por cliente
            beneficiaries_per_client = {}
            if 'client_id' in beneficiaries_df.columns:
                client_counts = beneficiaries_df['client_id'].value_counts()
                beneficiaries_per_client = {
                    "avg_beneficiaries_per_client": round(client_counts.mean(), 2),
                    "max_beneficiaries_per_client": client_counts.max(),
                    "clients_with_multiple_beneficiaries": len(client_counts[client_counts > 1]),
                    "distribution": client_counts.value_counts().to_dict()
                }
            
            # Análisis de edad de beneficiarios
            age_analysis = {}
            if 'birth_date' in beneficiaries_df.columns:
                beneficiaries_df['birth_date'] = pd.to_datetime(beneficiaries_df['birth_date'])
                beneficiaries_df['age'] = (datetime.now() - beneficiaries_df['birth_date']).dt.days // 365
                
                age_analysis = {
                    "average_age": round(beneficiaries_df['age'].mean(), 1),
                    "age_by_relationship": beneficiaries_df.groupby('relationship')['age'].mean().round(1).to_dict() if 'relationship' in beneficiaries_df.columns else {}
                }
            
            return {
                "total_beneficiaries": total_beneficiaries,
                "relationship_distribution": relationship_distribution,
                "beneficiaries_per_client": beneficiaries_per_client,
                "age_analysis": age_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in beneficiary relationships: {e}")
            raise Exception(f"Error analyzing beneficiaries: {str(e)}")
    
    # QUERY ESPECÍFICA 1: Análisis de crecimiento de usuarios por estado
    def get_user_growth_by_state(self, months: int = 12) -> Dict[str, Any]:
        """Análisis de crecimiento de usuarios por estado en los últimos N meses"""
        try:
            users_df = self.s3_manager.get_mysql_data('users')
            
            if 'created_at' not in users_df.columns or 'state' not in users_df.columns:
                return {"error": "Missing required columns: created_at or state"}
            
            # Convertir fecha
            users_df['created_at'] = pd.to_datetime(users_df['created_at'])
            cutoff_date = datetime.now() - timedelta(days=30 * months)
            recent_users = users_df[users_df['created_at'] >= cutoff_date].copy()
            
            # Agregar columna de periodo
            recent_users['period'] = recent_users['created_at'].dt.to_period('M')
            
            # Crecimiento por estado y período
            growth_pivot = recent_users.pivot_table(
                index='period', 
                columns='state', 
                aggfunc='size', 
                fill_value=0
            )
            
            # Top estados con más crecimiento
            state_totals = recent_users['state'].value_counts()
            
            # Tendencia de crecimiento
            monthly_totals = recent_users.groupby('period').size()
            
            return {
                "period_analyzed": f"Last {months} months",
                "total_new_users": len(recent_users),
                "top_growing_states": state_totals.head(10).to_dict(),
                "monthly_growth": {str(k): v for k, v in monthly_totals.items()},
                "growth_by_state_and_month": {
                    str(period): row.to_dict() 
                    for period, row in growth_pivot.iterrows()
                },
                "growth_rate": {
                    "current_month": monthly_totals.iloc[-1] if len(monthly_totals) > 0 else 0,
                    "previous_month": monthly_totals.iloc[-2] if len(monthly_totals) > 1 else 0,
                    "change_percent": round(
                        ((monthly_totals.iloc[-1] - monthly_totals.iloc[-2]) / monthly_totals.iloc[-2] * 100) 
                        if len(monthly_totals) > 1 and monthly_totals.iloc[-2] > 0 else 0, 2
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error in user growth analysis: {e}")
            raise Exception(f"Error analyzing user growth: {str(e)}")
    
    # QUERY ESPECÍFICA 2: Análisis de calidad de datos y duplicados
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Análisis completo de calidad de datos MySQL"""
        try:
            # Cargar todos los datasets
            users_df = self.s3_manager.get_mysql_data('users')
            clients_df = self.s3_manager.get_mysql_data('clients')
            agents_df = self.s3_manager.get_mysql_data('agents')
            beneficiaries_df = self.s3_manager.get_mysql_data('beneficiaries')
            
            quality_report = {
                "users": self._analyze_table_quality(users_df, "users"),
                "clients": self._analyze_table_quality(clients_df, "clients"),
                "agents": self._analyze_table_quality(agents_df, "agents"),
                "beneficiaries": self._analyze_table_quality(beneficiaries_df, "beneficiaries")
            }
            
            # Análisis de integridad referencial
            referential_integrity = {}
            
            # Verificar si client_id en clients existe en users.id
            if 'user_id' in clients_df.columns and 'id' in users_df.columns:
                valid_client_refs = clients_df['user_id'].isin(users_df['id']).sum()
                total_clients = len(clients_df)
                referential_integrity['clients_users'] = {
                    "valid_references": int(valid_client_refs),
                    "total_clients": total_clients,
                    "integrity_percentage": round((valid_client_refs / total_clients) * 100, 2) if total_clients > 0 else 0,
                    "orphaned_clients": total_clients - int(valid_client_refs)
                }
            
            # Verificar beneficiarios con clientes válidos
            if 'client_id' in beneficiaries_df.columns and 'user_id' in clients_df.columns:
                valid_beneficiary_refs = beneficiaries_df['client_id'].isin(clients_df['user_id']).sum()
                total_beneficiaries = len(beneficiaries_df)
                referential_integrity['beneficiaries_clients'] = {
                    "valid_references": int(valid_beneficiary_refs),
                    "total_beneficiaries": total_beneficiaries,
                    "integrity_percentage": round((valid_beneficiary_refs / total_beneficiaries) * 100, 2) if total_beneficiaries > 0 else 0,
                    "orphaned_beneficiaries": total_beneficiaries - int(valid_beneficiary_refs)
                }
            
            # Resumen general
            total_records = len(users_df) + len(clients_df) + len(agents_df) + len(beneficiaries_df)
            overall_completeness = np.mean([
                quality_report[table]["completeness_score"] 
                for table in quality_report.keys()
            ])
            
            return {
                "summary": {
                    "total_records": total_records,
                    "overall_completeness_score": round(overall_completeness, 2),
                    "timestamp": datetime.now().isoformat()
                },
                "table_quality": quality_report,
                "referential_integrity": referential_integrity,
                "recommendations": self._generate_quality_recommendations(quality_report, referential_integrity)
            }
            
        except Exception as e:
            logger.error(f"Error in data quality report: {e}")
            raise Exception(f"Error analyzing data quality: {str(e)}")
    
    def _analyze_table_quality(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Analiza la calidad de una tabla específica"""
        total_rows = len(df)
        total_columns = len(df.columns)
        
        # Valores nulos por columna
        null_counts = df.isnull().sum().to_dict()
        null_percentages = {col: round((count / total_rows) * 100, 2) for col, count in null_counts.items()}
        
        # Duplicados
        duplicate_rows = df.duplicated().sum()
        
        # Completeness score (promedio de columnas completas)
        completeness_scores = [(total_rows - null_count) / total_rows for null_count in null_counts.values()]
        overall_completeness = np.mean(completeness_scores) * 100
        
        # Tipos de datos
        dtype_distribution = df.dtypes.value_counts().to_dict()
        dtype_distribution = {str(k): v for k, v in dtype_distribution.items()}
        
        return {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "null_counts": null_counts,
            "null_percentages": null_percentages,
            "duplicate_rows": int(duplicate_rows),
            "duplicate_percentage": round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0,
            "completeness_score": round(overall_completeness, 2),
            "dtype_distribution": dtype_distribution,
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }
    
    def _generate_quality_recommendations(self, quality_report: Dict, integrity_report: Dict) -> List[str]:
        """Genera recomendaciones basadas en el análisis de calidad"""
        recommendations = []
        
        # Revisar completeness por tabla
        for table, report in quality_report.items():
            if report["completeness_score"] < 90:
                recommendations.append(f"Mejorar completeness de datos en tabla {table} ({report['completeness_score']:.1f}%)")
            
            if report["duplicate_percentage"] > 1:
                recommendations.append(f"Revisar y eliminar duplicados en tabla {table} ({report['duplicate_rows']} registros)")
        
        # Revisar integridad referencial
        for relationship, integrity in integrity_report.items():
            if integrity.get("integrity_percentage", 100) < 95:
                recommendations.append(f"Corregir referencias huérfanas en relación {relationship}")
        
        if not recommendations:
            recommendations.append("La calidad de datos está en buen estado general")
        
        return recommendations

# Instancia global
mysql_analytics = MySQLAnalytics()