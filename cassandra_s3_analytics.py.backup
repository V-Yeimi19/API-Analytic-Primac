import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .s3_data_manager import s3_manager
import logging

logger = logging.getLogger(__name__)

class CassandraAnalytics:
    """Análisis de datos Cassandra desde S3"""
    
    def __init__(self):
        self.s3_manager = s3_manager
    
    def get_claims_analysis(self) -> Dict[str, Any]:
        """Análisis completo de reclamos"""
        try:
            claims_df = self.s3_manager.get_cassandra_data('reclamos')
            
            total_claims = len(claims_df)
            
            # Análisis por estado de reclamo
            status_distribution = claims_df['estado'].value_counts().to_dict() if 'estado' in claims_df.columns else {}
            
            # Análisis de montos
            amount_stats = {}
            if 'monto' in claims_df.columns:
                valid_amounts = claims_df['monto'].dropna()
                
                amount_stats = {
                    "total_claimed_amount": round(valid_amounts.sum(), 2),
                    "average_claim_amount": round(valid_amounts.mean(), 2),
                    "median_claim_amount": round(valid_amounts.median(), 2),
                    "max_claim_amount": round(valid_amounts.max(), 2),
                    "min_claim_amount": round(valid_amounts.min(), 2),
                    "std_claim_amount": round(valid_amounts.std(), 2)
                }
                
                # Distribución por rangos de monto
                bins = [0, 1000, 5000, 10000, 50000, float('inf')]
                labels = ['< 1K', '1K-5K', '5K-10K', '10K-50K', '50K+']
                claims_df['amount_range'] = pd.cut(valid_amounts, bins=bins, labels=labels, include_lowest=True)
                amount_distribution = claims_df['amount_range'].value_counts().to_dict()
                amount_stats["amount_distribution"] = {str(k): v for k, v in amount_distribution.items()}
            
            # Análisis temporal
            temporal_analysis = {}
            if 'fecha_reclamo' in claims_df.columns:
                claims_df['fecha_reclamo'] = pd.to_datetime(claims_df['fecha_reclamo'])
                
                # Reclamos por mes
                claims_df['month_year'] = claims_df['fecha_reclamo'].dt.to_period('M')
                monthly_claims = claims_df['month_year'].value_counts().sort_index().tail(12)
                temporal_analysis['monthly_claims'] = {str(k): v for k, v in monthly_claims.items()}
                
                # Reclamos recientes
                recent_date = datetime.now() - timedelta(days=30)
                recent_claims = len(claims_df[claims_df['fecha_reclamo'] >= recent_date])
                temporal_analysis['recent_claims'] = recent_claims
                
                # Día de la semana más común para reclamos
                claims_df['day_of_week'] = claims_df['fecha_reclamo'].dt.day_name()
                day_distribution = claims_df['day_of_week'].value_counts()
                temporal_analysis['claims_by_day_of_week'] = day_distribution.to_dict()
            
            # Análisis por tipo de reclamo (si existe campo tipo)
            type_analysis = {}
            if 'tipo_reclamo' in claims_df.columns:
                type_distribution = claims_df['tipo_reclamo'].value_counts()
                type_analysis = {
                    "most_common_types": type_distribution.head(10).to_dict(),
                    "total_claim_types": claims_df['tipo_reclamo'].nunique()
                }
            
            return {
                "total_claims": total_claims,
                "status_distribution": status_distribution,
                "amount_statistics": amount_stats,
                "temporal_analysis": temporal_analysis,
                "type_analysis": type_analysis,
                "data_quality": {
                    "claims_with_amount": (~claims_df['monto'].isnull()).sum() if 'monto' in claims_df.columns else 0,
                    "claims_with_date": (~claims_df['fecha_reclamo'].isnull()).sum() if 'fecha_reclamo' in claims_df.columns else 0,
                    "claims_with_status": (~claims_df['estado'].isnull()).sum() if 'estado' in claims_df.columns else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in claims analysis: {e}")
            raise Exception(f"Error analyzing claims: {str(e)}")
    
    def get_payments_analysis(self) -> Dict[str, Any]:
        """Análisis completo de pagos"""
        try:
            payments_df = self.s3_manager.get_cassandra_data('pagos')
            
            total_payments = len(payments_df)
            
            # Análisis de montos de pagos
            amount_stats = {}
            if 'monto' in payments_df.columns:
                valid_amounts = payments_df['monto'].dropna()
                
                amount_stats = {
                    "total_payment_amount": round(valid_amounts.sum(), 2),
                    "average_payment": round(valid_amounts.mean(), 2),
                    "median_payment": round(valid_amounts.median(), 2),
                    "max_payment": round(valid_amounts.max(), 2),
                    "min_payment": round(valid_amounts.min(), 2)
                }
                
                # Distribución por rangos
                percentiles = [0, 25, 50, 75, 90, 95, 100]
                percentile_values = np.percentile(valid_amounts, percentiles)
                amount_stats["percentiles"] = {
                    f"p{p}": round(v, 2) for p, v in zip(percentiles, percentile_values)
                }
            
            # Análisis por método de pago
            payment_method_analysis = {}
            if 'metodo_pago' in payments_df.columns:
                method_distribution = payments_df['metodo_pago'].value_counts()
                payment_method_analysis = {
                    "payment_methods": method_distribution.to_dict(),
                    "most_popular_method": method_distribution.index[0] if len(method_distribution) > 0 else None
                }
                
                # Monto promedio por método
                if 'monto' in payments_df.columns:
                    avg_by_method = payments_df.groupby('metodo_pago')['monto'].mean().round(2)
                    payment_method_analysis['avg_amount_by_method'] = avg_by_method.to_dict()
            
            # Análisis temporal de pagos
            temporal_analysis = {}
            if 'fecha_pago' in payments_df.columns:
                payments_df['fecha_pago'] = pd.to_datetime(payments_df['fecha_pago'])
                
                # Pagos por mes
                payments_df['month_year'] = payments_df['fecha_pago'].dt.to_period('M')
                monthly_payments = payments_df['month_year'].value_counts().sort_index().tail(12)
                temporal_analysis['monthly_payments'] = {str(k): v for k, v in monthly_payments.items()}
                
                # Análisis de estacionalidad
                payments_df['month'] = payments_df['fecha_pago'].dt.month
                seasonal_payments = payments_df['month'].value_counts().sort_index()
                temporal_analysis['seasonal_distribution'] = seasonal_payments.to_dict()
                
                # Pagos por día de la semana
                payments_df['day_of_week'] = payments_df['fecha_pago'].dt.day_name()
                weekly_distribution = payments_df['day_of_week'].value_counts()
                temporal_analysis['payments_by_day'] = weekly_distribution.to_dict()
            
            # Análisis de frecuencia de pagos por cliente
            customer_analysis = {}
            if 'customer_id' in payments_df.columns:
                customer_payment_counts = payments_df['customer_id'].value_counts()
                customer_analysis = {
                    "total_customers": payments_df['customer_id'].nunique(),
                    "avg_payments_per_customer": round(customer_payment_counts.mean(), 2),
                    "max_payments_per_customer": customer_payment_counts.max(),
                    "customers_with_single_payment": len(customer_payment_counts[customer_payment_counts == 1]),
                    "customers_with_multiple_payments": len(customer_payment_counts[customer_payment_counts > 1])
                }
                
                # Top clientes por volumen de pagos
                if 'monto' in payments_df.columns:
                    customer_amounts = payments_df.groupby('customer_id')['monto'].sum().sort_values(ascending=False)
                    customer_analysis['top_customers_by_amount'] = customer_amounts.head(10).to_dict()
            
            return {
                "total_payments": total_payments,
                "amount_statistics": amount_stats,
                "payment_method_analysis": payment_method_analysis,
                "temporal_analysis": temporal_analysis,
                "customer_analysis": customer_analysis,
                "data_completeness": {
                    "payments_with_amount": (~payments_df['monto'].isnull()).sum() if 'monto' in payments_df.columns else 0,
                    "payments_with_date": (~payments_df['fecha_pago'].isnull()).sum() if 'fecha_pago' in payments_df.columns else 0,
                    "payments_with_method": (~payments_df['metodo_pago'].isnull()).sum() if 'metodo_pago' in payments_df.columns else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in payments analysis: {e}")
            raise Exception(f"Error analyzing payments: {str(e)}")
    
    def get_transaction_audit_analysis(self) -> Dict[str, Any]:
        """Análisis de auditoría de transacciones"""
        try:
            audit_df = self.s3_manager.get_cassandra_data('transaction_audit')
            
            total_transactions = len(audit_df)
            
            # Análisis por servicio
            service_analysis = {}
            if 'servicio' in audit_df.columns:
                service_distribution = audit_df['servicio'].value_counts()
                service_analysis = {
                    "top_services": service_distribution.head(10).to_dict(),
                    "total_services": audit_df['servicio'].nunique(),
                    "service_usage_distribution": service_distribution.to_dict()
                }
            
            # Análisis temporal
            temporal_analysis = {}
            if 'timestamp' in audit_df.columns:
                audit_df['timestamp'] = pd.to_datetime(audit_df['timestamp'])
                
                # Transacciones por hora del día
                audit_df['hour'] = audit_df['timestamp'].dt.hour
                hourly_distribution = audit_df['hour'].value_counts().sort_index()
                temporal_analysis['hourly_distribution'] = hourly_distribution.to_dict()
                
                # Picos de actividad
                temporal_analysis['peak_hour'] = hourly_distribution.idxmax()
                temporal_analysis['lowest_activity_hour'] = hourly_distribution.idxmin()
            
            # Análisis de tipos de operación
            operation_analysis = {}
            if 'operacion' in audit_df.columns:
                operation_distribution = audit_df['operacion'].value_counts()
                operation_analysis = {
                    "operation_types": operation_distribution.to_dict(),
                    "most_common_operation": operation_distribution.index[0] if len(operation_distribution) > 0 else None
                }
            
            return {
                "total_transactions": total_transactions,
                "service_analysis": service_analysis,
                "temporal_analysis": temporal_analysis,
                "operation_analysis": operation_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in transaction audit analysis: {e}")
            raise Exception(f"Error analyzing transaction audit: {str(e)}")
    
    # QUERY ESPECÍFICA 1: Análisis de correlación entre reclamos y pagos
    def get_claims_payments_correlation(self) -> Dict[str, Any]:
        """Análisis de correlación entre patrones de reclamos y pagos"""
        try:
            claims_df = self.s3_manager.get_cassandra_data('reclamos')
            payments_df = self.s3_manager.get_cassandra_data('pagos')
            
            # Preparar datos temporales
            if 'fecha_reclamo' in claims_df.columns:
                claims_df['fecha_reclamo'] = pd.to_datetime(claims_df['fecha_reclamo'])
                claims_df['month_year'] = claims_df['fecha_reclamo'].dt.to_period('M')
            
            if 'fecha_pago' in payments_df.columns:
                payments_df['fecha_pago'] = pd.to_datetime(payments_df['fecha_pago'])
                payments_df['month_year'] = payments_df['fecha_pago'].dt.to_period('M')
            
            # Análisis mensual comparativo
            monthly_comparison = {}
            if 'month_year' in claims_df.columns and 'month_year' in payments_df.columns:
                # Contar reclamos por mes
                monthly_claims = claims_df.groupby('month_year').size()
                monthly_claims_amount = claims_df.groupby('month_year')['monto'].sum() if 'monto' in claims_df.columns else pd.Series()
                
                # Contar pagos por mes  
                monthly_payments = payments_df.groupby('month_year').size()
                monthly_payment_amount = payments_df.groupby('month_year')['monto'].sum() if 'monto' in payments_df.columns else pd.Series()
                
                # Crear DataFrame comparativo
                comparison_df = pd.DataFrame({
                    'claims_count': monthly_claims,
                    'payments_count': monthly_payments,
                    'claims_amount': monthly_claims_amount,
                    'payment_amount': monthly_payment_amount
                }).fillna(0)
                
                # Calcular correlaciones
                correlations = {}
                if len(comparison_df) > 1:
                    correlations = {
                        'count_correlation': round(comparison_df['claims_count'].corr(comparison_df['payments_count']), 3),
                        'amount_correlation': round(comparison_df['claims_amount'].corr(comparison_df['payment_amount']), 3) if not comparison_df['claims_amount'].empty and not comparison_df['payment_amount'].empty else 0
                    }
                
                # Resumen mensual (últimos 12 meses)
                recent_comparison = comparison_df.tail(12)
                monthly_comparison = {
                    'correlations': correlations,
                    'monthly_data': {
                        str(period): {
                            'claims_count': int(row['claims_count']),
                            'payments_count': int(row['payments_count']),
                            'claims_amount': round(row['claims_amount'], 2),
                            'payment_amount': round(row['payment_amount'], 2),
                            'claims_to_payments_ratio': round(row['claims_count'] / row['payments_count'], 2) if row['payments_count'] > 0 else 0
                        }
                        for period, row in recent_comparison.iterrows()
                    }
                }
            
            # Análisis por día de la semana
            weekday_analysis = {}
            if 'fecha_reclamo' in claims_df.columns and 'fecha_pago' in payments_df.columns:
                claims_df['weekday'] = claims_df['fecha_reclamo'].dt.day_name()
                payments_df['weekday'] = payments_df['fecha_pago'].dt.day_name()
                
                claims_by_weekday = claims_df['weekday'].value_counts()
                payments_by_weekday = payments_df['weekday'].value_counts()
                
                weekday_analysis = {
                    'claims_by_weekday': claims_by_weekday.to_dict(),
                    'payments_by_weekday': payments_by_weekday.to_dict(),
                    'highest_claims_day': claims_by_weekday.idxmax(),
                    'highest_payments_day': payments_by_weekday.idxmax()
                }
            
            # Análisis de rangos de monto
            amount_range_analysis = {}
            if 'monto' in claims_df.columns and 'monto' in payments_df.columns:
                # Definir rangos similares para comparar
                bins = [0, 1000, 5000, 10000, 50000, float('inf')]
                labels = ['< 1K', '1K-5K', '5K-10K', '10K-50K', '50K+']
                
                claims_df['amount_range'] = pd.cut(claims_df['monto'], bins=bins, labels=labels)
                payments_df['amount_range'] = pd.cut(payments_df['monto'], bins=bins, labels=labels)
                
                claims_by_range = claims_df['amount_range'].value_counts()
                payments_by_range = payments_df['amount_range'].value_counts()
                
                amount_range_analysis = {
                    'claims_by_amount_range': {str(k): v for k, v in claims_by_range.items()},
                    'payments_by_amount_range': {str(k): v for k, v in payments_by_range.items()},
                    'dominant_claims_range': str(claims_by_range.idxmax()),
                    'dominant_payments_range': str(payments_by_range.idxmax())
                }
            
            # Estadísticas comparativas generales
            general_stats = {
                'total_claims': len(claims_df),
                'total_payments': len(payments_df),
                'claims_to_payments_ratio': round(len(claims_df) / len(payments_df), 2) if len(payments_df) > 0 else 0,
                'avg_claim_amount': round(claims_df['monto'].mean(), 2) if 'monto' in claims_df.columns else 0,
                'avg_payment_amount': round(payments_df['monto'].mean(), 2) if 'monto' in payments_df.columns else 0,
                'total_claims_amount': round(claims_df['monto'].sum(), 2) if 'monto' in claims_df.columns else 0,
                'total_payments_amount': round(payments_df['monto'].sum(), 2) if 'monto' in payments_df.columns else 0
            }
            
            if general_stats['total_payments_amount'] > 0:
                general_stats['loss_ratio'] = round((general_stats['total_claims_amount'] / general_stats['total_payments_amount']) * 100, 2)
            
            return {
                'general_statistics': general_stats,
                'monthly_comparison': monthly_comparison,
                'weekday_analysis': weekday_analysis,
                'amount_range_analysis': amount_range_analysis,
                'insights': self._generate_claims_payments_insights(general_stats, monthly_comparison),
                'data_sources': {
                    'cassandra_tables': ['reclamos', 'pagos'],
                    'analysis_type': 'correlation_analysis'
                }
            }
            
        except Exception as e:
            logger.error(f"Error in claims-payments correlation analysis: {e}")
            raise Exception(f"Error analyzing claims-payments correlation: {str(e)}")
    
    # QUERY ESPECÍFICA 2: Análisis de patrones de actividad por hora y servicio
    def get_activity_patterns_analysis(self, hours_lookback: int = 168) -> Dict[str, Any]:  # 7 días por defecto
        """Análisis de patrones de actividad por hora y servicio usando transaction_audit"""
        try:
            audit_df = self.s3_manager.get_cassandra_data('transaction_audit')
            
            if 'timestamp' not in audit_df.columns:
                return {"error": "timestamp column not found in transaction_audit data"}
            
            # Preparar datos temporales
            audit_df['timestamp'] = pd.to_datetime(audit_df['timestamp'])
            
            # Filtrar por las últimas N horas
            cutoff_time = datetime.now() - timedelta(hours=hours_lookback)
            recent_audit = audit_df[audit_df['timestamp'] >= cutoff_time].copy()
            
            if len(recent_audit) == 0:
                return {"error": f"No data found in the last {hours_lookback} hours"}
            
            # Extraer componentes temporales
            recent_audit['hour'] = recent_audit['timestamp'].dt.hour
            recent_audit['day_of_week'] = recent_audit['timestamp'].dt.day_name()
            recent_audit['date'] = recent_audit['timestamp'].dt.date
            
            # Análisis por hora del día
            hourly_patterns = {}
            hourly_activity = recent_audit.groupby('hour').size()
            
            if 'servicio' in recent_audit.columns:
                # Actividad por servicio y hora
                service_hourly = recent_audit.pivot_table(
                    index='hour', 
                    columns='servicio', 
                    aggfunc='size', 
                    fill_value=0
                )
                
                # Top servicios por hora
                peak_services_by_hour = {}
                for hour in service_hourly.index:
                    hour_data = service_hourly.loc[hour]
                    if hour_data.sum() > 0:
                        peak_services_by_hour[str(hour)] = {
                            'most_active_service': hour_data.idxmax(),
                            'activity_count': int(hour_data.max()),
                            'total_activity': int(hour_data.sum())
                        }
                
                hourly_patterns = {
                    'total_activity_by_hour': hourly_activity.to_dict(),
                    'peak_activity_hour': int(hourly_activity.idxmax()),
                    'lowest_activity_hour': int(hourly_activity.idxmin()),
                    'peak_services_by_hour': peak_services_by_hour,
                    'service_activity_matrix': {
                        str(hour): row.to_dict() 
                        for hour, row in service_hourly.iterrows()
                    }
                }
            else:
                hourly_patterns = {
                    'total_activity_by_hour': hourly_activity.to_dict(),
                    'peak_activity_hour': int(hourly_activity.idxmax()),
                    'lowest_activity_hour': int(hourly_activity.idxmin())
                }
            
            # Análisis de patrones de carga de trabajo
            workload_analysis = {}
            
            # Distribución de carga por día de la semana
            daily_workload = recent_audit.groupby('day_of_week').size()
            workload_analysis['workload_by_day'] = daily_workload.to_dict()
            workload_analysis['busiest_day'] = daily_workload.idxmax()
            workload_analysis['quietest_day'] = daily_workload.idxmin()
            
            # Análisis de picos de actividad
            hourly_activity_stats = hourly_activity.describe()
            peak_threshold = hourly_activity_stats['mean'] + hourly_activity_stats['std']
            peak_hours = hourly_activity[hourly_activity > peak_threshold]
            
            workload_analysis['peak_hours'] = {
                'hours': peak_hours.index.tolist(),
                'threshold': round(peak_threshold, 2),
                'peak_hours_activity': {str(hour): int(count) for hour, count in peak_hours.items()}
            }
            
            # Análisis de eficiencia por servicio
            service_efficiency = {}
            if 'servicio' in recent_audit.columns:
                service_stats = recent_audit.groupby('servicio').agg({
                    'timestamp': ['count', 'nunique']  # Transacciones y días únicos
                })
                
                service_stats.columns = ['_'.join(col).strip() for col in service_stats.columns.values]
                service_stats = service_stats.reset_index()
                
                # Calcular transacciones por día para cada servicio
                service_stats['transactions_per_day'] = (
                    service_stats['timestamp_count'] / service_stats['timestamp_nunique']
                ).round(2)
                
                # Ranking de servicios por actividad
                top_services = service_stats.nlargest(10, 'timestamp_count')
                most_consistent_services = service_stats.nlargest(10, 'transactions_per_day')
                
                service_efficiency = {
                    'top_services_by_volume': top_services[['servicio', 'timestamp_count']].to_dict('records'),
                    'most_consistent_services': most_consistent_services[['servicio', 'transactions_per_day']].to_dict('records'),
                    'service_distribution': recent_audit['servicio'].value_counts().head(15).to_dict()
                }
            
            # Análisis de tendencias temporales
            temporal_trends = {}
            daily_activity = recent_audit.groupby('date').size()
            
            if len(daily_activity) > 1:
                # Calcular tendencia (incremento/decremento diario promedio)
                daily_changes = daily_activity.diff().dropna()
                avg_daily_change = daily_changes.mean()
                
                temporal_trends = {
                    'daily_activity': {str(date): int(count) for date, count in daily_activity.items()},
                    'average_daily_change': round(avg_daily_change, 2),
                    'trend_direction': 'increasing' if avg_daily_change > 0 else 'decreasing' if avg_daily_change < 0 else 'stable',
                    'most_active_date': str(daily_activity.idxmax()),
                    'least_active_date': str(daily_activity.idxmin())
                }
            
            # Métricas de resumen
            summary_metrics = {
                'total_transactions_analyzed': len(recent_audit),
                'analysis_period_hours': hours_lookback,
                'unique_services': recent_audit['servicio'].nunique() if 'servicio' in recent_audit.columns else 0,
                'transactions_per_hour': round(len(recent_audit) / hours_lookback, 2),
                'peak_activity_multiplier': round(hourly_activity.max() / hourly_activity.mean(), 2),
                'activity_consistency_score': round(100 - (hourly_activity.std() / hourly_activity.mean() * 100), 2)
            }
            
            return {
                'summary_metrics': summary_metrics,
                'hourly_patterns': hourly_patterns,
                'workload_analysis': workload_analysis,
                'service_efficiency': service_efficiency,
                'temporal_trends': temporal_trends,
                'recommendations': self._generate_activity_recommendations(hourly_patterns, workload_analysis, summary_metrics),
                'data_sources': {
                    'cassandra_tables': ['transaction_audit'],
                    'analysis_period': f'{hours_lookback} hours',
                    'analysis_type': 'activity_patterns'
                }
            }
            
        except Exception as e:
            logger.error(f"Error in activity patterns analysis: {e}")
            raise Exception(f"Error analyzing activity patterns: {str(e)}")
    
    def _generate_claims_payments_insights(self, general_stats: Dict, monthly_comparison: Dict) -> List[str]:
        """Genera insights basados en el análisis de correlación reclamos-pagos"""
        insights = []
        
        # Insight sobre loss ratio
        if 'loss_ratio' in general_stats:
            loss_ratio = general_stats['loss_ratio']
            if loss_ratio > 80:
                insights.append(f"Alto índice de siniestralidad ({loss_ratio}%) - Revisar políticas de suscripción")
            elif loss_ratio < 30:
                insights.append(f"Bajo índice de siniestralidad ({loss_ratio}%) - Excelente control de riesgos")
            else:
                insights.append(f"Índice de siniestralidad moderado ({loss_ratio}%) - Dentro de rangos normales")
        
        # Insight sobre volumen de reclamos vs pagos
        ratio = general_stats.get('claims_to_payments_ratio', 0)
        if ratio > 0.5:
            insights.append("Alta frecuencia de reclamos - Considerar revisar procesos de satisfacción del cliente")
        elif ratio < 0.1:
            insights.append("Baja frecuencia de reclamos - Buena experiencia del cliente o posible sub-reporte")
        
        # Insight sobre correlaciones temporales
        if 'correlations' in monthly_comparison and monthly_comparison['correlations']:
            count_corr = monthly_comparison['correlations'].get('count_correlation', 0)
            if abs(count_corr) > 0.7:
                correlation_type = "fuerte" if count_corr > 0 else "fuerte inversa"
                insights.append(f"Correlación {correlation_type} entre volumen de reclamos y pagos ({count_corr})")
        
        return insights
    
    def _generate_activity_recommendations(self, hourly_patterns: Dict, workload_analysis: Dict, summary_metrics: Dict) -> List[str]:
        """Genera recomendaciones basadas en patrones de actividad"""
        recommendations = []
        
        # Recomendación basada en picos de actividad
        if 'peak_hours' in workload_analysis:
            peak_hours = workload_analysis['peak_hours']['hours']
            if len(peak_hours) > 0:
                peak_range = f"{min(peak_hours)}:00-{max(peak_hours)}:00"
                recommendations.append(f"Considerar escalado automático durante horas pico ({peak_range})")
        
        # Recomendación sobre consistencia de actividad
        consistency_score = summary_metrics.get('activity_consistency_score', 0)
        if consistency_score < 50:
            recommendations.append("Alta variabilidad en patrones de actividad - Implementar balanceado de carga dinámico")
        elif consistency_score > 80:
            recommendations.append("Patrones de actividad muy consistentes - Óptimo para planificación de capacidad")
        
        # Recomendación sobre el día más ocupado
        if 'busiest_day' in workload_analysis:
            busiest_day = workload_analysis['busiest_day']
            recommendations.append(f"Planificar recursos adicionales para {busiest_day}")
        
        # Recomendación sobre multiplicador de picos
        peak_multiplier = summary_metrics.get('peak_activity_multiplier', 1)
        if peak_multiplier > 3:
            recommendations.append(f"Picos de actividad {peak_multiplier}x promedio - Implementar auto-scaling agresivo")
        
        return recommendations

# Instancia global
cassandra_analytics = CassandraAnalytics()