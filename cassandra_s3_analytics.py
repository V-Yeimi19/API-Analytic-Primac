import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from s3_data_manager import s3_manager
import logging

logger = logging.getLogger(__name__)

class CassandraAnalytics:
    """Análisis de datos Cassandra desde S3 - Versión Simplificada"""
    
    def __init__(self):
        self.s3_manager = s3_manager
    
    def get_claims_analysis(self) -> Dict[str, Any]:
        """[GENERAL] Análisis completo de reclamos"""
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
    
    def get_claims_payments_correlation(self) -> Dict[str, Any]:
        """[ESPECÍFICA] Análisis de correlación entre patrones de reclamos y pagos"""
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

# Instancia global
cassandra_analytics = CassandraAnalytics()
