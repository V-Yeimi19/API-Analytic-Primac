import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from s3_data_manager import s3_manager
import logging

logger = logging.getLogger(__name__)

class MySQLAnalytics:
    """Análisis de datos MySQL desde S3 - Versión Simplificada"""
    
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
    
    # QUERY ESPECÍFICA: Análisis de crecimiento de usuarios por estado
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
    

# Instancia global
mysql_analytics = MySQLAnalytics()
